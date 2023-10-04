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
        pass

    @database_sync_to_async
    def get_user_from_token(self, token):
        # Retrieve the user from the JWT token
        try:
            user_id = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])['user_id']
            return User.objects.get(id=user_id)
        except (jwt.DecodeError, User.DoesNotExist):
            return None
