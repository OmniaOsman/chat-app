import json 
import jwt
from .models import Chat
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authenticate the user using JWT token
        query_string = self.scope['query_string'].decode()
        token = parse_qs(query_string).get('token', [''])[0]
        if not token:
            await self.close()
        else:
            user = await self.get_user_from_token(token)
            if user is None:
                await self.close()
            else:
                self.user = user
                await self.accept()

    async def disconnect(self, close_code):
        # Perform any cleanup tasks when the WebSocket connection is closed
        pass

    async def receive(self, text_data):
        # Handle incoming WebSocket messages
        try:
            data = json.loads(text_data)
            message = data['message']
            chat_id = data['chat_id']
            await self.save_message(chat_id, message)
            await self.send_message(chat_id, message)
        except (json.JSONDecodeError, KeyError):
            # Handle the case when the JSON data is empty or invalid
            # You can log an error message or take appropriate action here
            pass

    @database_sync_to_async
    def get_user_from_token(self, token):
        # Retrieve the user from the JWT token
        try:
            user_id = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])['user_id']
            return User.objects.get(id=user_id)
        except (jwt.DecodeError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def save_message(self, chat_id, message):
        # Save the message to the Chat model
        chat = Chat.objects.get(id=chat_id)
        chat.messages.create(sender=self.user, content=message)

    async def send_message(self, chat_id, message):
        # Send the message to all connected clients in the chat room
        await self.channel_layer.group_send(
            f'chat_{chat_id}',
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        # Receive the message from the group and send it to the WebSocket
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
