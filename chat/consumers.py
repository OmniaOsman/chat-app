from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import User
import json
from urllib.parse import parse_qs
from django.utils import timezone
import jwt
import logging
from django.conf import settings
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import Room, Chat

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            user_id = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])['user_id']
            return User.objects.get(id=user_id)
        except (jwt.DecodeError, User.DoesNotExist):
            return None

        
    @sync_to_async
    def get_room(self):
        try:
            room = Room.objects.get(room_slug=self.room_slug)
            return room
        except Room.DoesNotExist:
            logger.warning(f"Room {self.room_slug} not found.")
            return None
    
    
    @sync_to_async
    def create_room(self, room_slug):
        room = Room(room_name=room_slug, room_slug=room_slug)
        room.save()
        return room


    @sync_to_async
    def create_chat(self, message):
        chat = Chat(sender=self.user.username, 
                    receiver=self.room.room_name, 
                    message=message, 
                    chat_room=self.room,
                    timestamp=timezone.now())
        try:
            if chat.image:
                chat.image = str(chat.image)
            chat.save()
            logger.info(f"Chat object created: {message}")
        except Exception as e:
            logger.error(f"Error creating chat object: {e}")
        return chat

    
    async def connect(self):
        # Get the room_slug from the URL parameters
        
        self.room_slug = self.scope['url_route']['kwargs'].get('room_slug')

        if not self.room_slug:
            # Room slug is not provided, close the connection
            await self.close()
            return

        self.room = await self.get_room()

        if self.room is None:
            # Room does not exist, create the room dynamically
            self.room = await self.create_room(self.room_slug)

        # Authenticate the user using JWT
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
            

        # Join the room group
        await self.channel_layer.group_add(
            self.room_slug,
            self.channel_name
        )

        await self.accept() 

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_slug,
            self.channel_name
        )

    async def receive(self, text_data):
        logger.info(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Print the received message to the console
        logger.info(f"Received message in room {self.room_slug}: {message}")

        # Create a new chat message
        chat = await self.create_chat(message)

        # Convert the image attribute to a string representation
        image_str = str(chat.image) if chat.image else None

        # Send the chat message to the room group
        await self.channel_layer.group_send(
            self.room_slug,
            {
                'type': 'chat_message',
                'chat_id': chat.id,
                'sender': chat.sender,
                'image': image_str,
                'message': chat.message,
                'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )


    async def chat_message(self, event):
        # Extract the chat message details from the event
        chat_id = event['chat_id']
        sender = event['sender']
        image = event['image']
        message = event['message']
        timestamp = event['timestamp']
