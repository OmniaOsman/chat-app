import jwt
import logging
import json
from .models import Room, Chat
from websocket import WebSocketApp
from accounts.models import User
from urllib.parse import parse_qs
from django.utils import timezone
from django.conf import settings
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_from_token(self, token:str) -> User|None:
        """ Retrieves a user object based on a given token. """
        try:
            user_id = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])['user_id']
            return User.objects.get(id=user_id)
        except (jwt.DecodeError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def get_room(self) -> Room|None:
        """ Retrieves the room with the specified room slug. """
        try:
            room = Room.objects.get(room_slug=self.room_slug)
            return room
        except Room.DoesNotExist:
            logger.warning(f"Room {self.room_slug} not found.")
            return None
    
    @database_sync_to_async
    def create_room(self, room_slug:str) -> Room:
        """ Create a new room with the given room slug. """
        room = Room(room_name=room_slug, room_slug=room_slug)
        room.save()
        return room
    
    @database_sync_to_async
    def create_chat(self, message: str) -> Chat:
        """Creates a new chat object."""
        chat = Chat(sender=self.user.username,
                    receiver=self.room.room_name,
                    message=message,
                    chat_room=self.room,
                    timestamp=timezone.now())

        try:
            chat.save()
            logger.info(f"Chat object created: {message}")
        except Exception as e:
            # Catch any exceptions and log them
            logger.error(f"Error creating chat object: {e}")
            
        return chat

    async def connect(self) -> None:
        """ 
        Connects the websocket client to the server.
        This method is responsible for establishing a connection between the websocket
        client and the server. It performs the following steps:
            1. Retrieves the room slug from the URL route parameters.
            2. Closes the connection if the room slug is not provided.
            3. Retrieves the room object based on the room slug.
            4. Creates the room dynamically if it does not exist.
            5. Authenticates the user using a JSON Web Token (JWT).
            6. Closes the connection if the token is not provided.
            7. Retrieves the user object based on the token.
            8. Closes the connection if the user is not found.
            9. Sets the user object for the websocket client.
            10. Joins the websocket client to the room group.
            11. Accepts the websocket connection.
        """
        # Get room slug from URL route
        self.room_slug = self.scope['url_route']['kwargs'].get('room_slug')
        
        if not self.room_slug:
            await self.close()
            return

        self.room = await self.get_room()

        if self.room is None:
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

    async def disconnect(self, close_code:int) -> None:
        """ Disconnects the client from the WebSocket connection."""
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_slug,
            self.channel_name
        )

    async def receive(self, text_data:str) -> None:
        """ Receives text data and processes it. """
        if isinstance(text_data, str):
            message = text_data
        else:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

        # Print the received message to the console
        logger.info(f"Received message in room {self.room_slug}: {message}")

        # Create a new chat object
        chat = await self.create_chat(message)
            
        # Send the chat message to the room group
        await self.channel_layer.group_send(
            self.room_slug,
            {
                'type': 'chat_message',
                'chat_id': chat.id,
                'sender': chat.sender,
                'message': chat.message,
                'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    async def chat_message(self, event:dict) -> None:
        """ A function that handles a chat message event. """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
