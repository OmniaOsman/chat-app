from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authenticate the user using JWT token
        token = self.scope['query_string'].decode().split('=')[1]
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
        data = json.loads(text_data)
        message = data['message']
        chat_id = data['chat_id']
        await self.save_message(chat_id, message)
        await self.send_message(chat_id, message)

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
