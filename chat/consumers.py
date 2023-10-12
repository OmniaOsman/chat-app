from websocket import WebSocketApp
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models.fields.files import FieldFile
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
import os
from PIL import Image

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            user_id = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])['user_id']
            return User.objects.get(id=user_id)
        except (jwt.DecodeError, User.DoesNotExist):
            return None

        
    @database_sync_to_async
    def get_room(self):
        try:
            room = Room.objects.get(room_slug=self.room_slug)
            return room
        except Room.DoesNotExist:
            logger.warning(f"Room {self.room_slug} not found.")
            return None
    
    
    @database_sync_to_async
    def create_room(self, room_slug):
        room = Room(room_name=room_slug, room_slug=room_slug)
        room.save()
        return room

    
    @database_sync_to_async
    def create_chat(self, message, image_file=None):
        """Creates a new chat object.
        Args:
            message: The message text.
            thumbnail_size: The size of the thumbnail image in pixels.

        Returns:
            A Chat object.
        """

        chat = Chat(sender=self.user.username,
                    receiver=self.room.room_name,
                    message=message,
                    chat_room=self.room,
                    timestamp=timezone.now())

        try:
            if image_file:
                # Save the image file temporarily on the disk
                file_path = f'static/{image_file.name}'
                with open(file_path, 'wb') as file:
                    for chunk in image_file.chunks():
                        file.write(chunk)

                # Start the Celery task
                result = resize_image.delay(chat.image)

                # Define a callback function to handle the result
                def on_task_done(task):
                    chat.image = task.get()
                    chat.save()
                    logger.info(f"Chat object created: {message}")

                # Attach the callback function to the task result
                result.then(on_task_done)

            chat.save()
            logger.info(f"Chat object created: {message}")
        except Exception as e:
            # Catch any exceptions and log them
            logger.error(f"Error creating chat object: {e}")
            # Handle the exception gracefully
            # For example, return None or a default chat object

        return chat
 

    
    async def connect(self):
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
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Print the received message to the console
        logger.info(f"Received message in room {self.room_slug}: {message}")

        # Check if an image file was uploaded
        if self.scope.get('message'):
            image_file = self.scope['message'].get('image')
            # Convert the image field to a string before sending it to the room group.
            if isinstance(chat.image, FieldFile):
                chat.image = chat.image.url

            # Save the image file
            chat = await self.create_chat(message, image_file)
        else:
            chat = await self.create_chat(message, None)

        # Send the chat message to the room group
        await self.channel_layer.group_send(
            self.room_slug,
            {
                'type': 'chat_message',
                'chat_id': chat.id,
                'sender': chat.sender,
                'image': chat.image,
                'message': chat.message,
                'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )



    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
