import logging
import redis
from io import BytesIO
import logging
from .models import ImageFile, Chat
from celery.result import AsyncResult
from rest_framework.response import Response
from rest_framework import status
from .tasks import resize_image
from .serializers import ImageFilesSerializer, ChatSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView

class ImageFilesView(CreateAPIView, LoginRequiredMixin):
    queryset = ImageFile.objects.all()
    serializer_class = ImageFilesSerializer 
    
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image_file')
        
        # Save the uploaded file in the database
        image = ImageFile(image_file=image_file)
        image.save()

        # Save the uploaded file in Redis
        redis_client = redis.Redis()
        image_data = BytesIO()
        for chunk in image_file.chunks():
            image_data.write(chunk)
        image_data.seek(0)
        image_id = str(image.id)
        redis_client.set(image_id, image_data.getvalue())

        # Call the resize_image task asynchronously
        resize_image.delay(image_id)
        logging.warning(f'Task started for image with ID: {image_id}')

        return Response({'message': 'File uploaded successfully'}, 
                        status=status.HTTP_201_CREATED)
        
        
    
class ChatListView(ListAPIView, LoginRequiredMixin): 
    serializer_class = ChatSerializer  
    lookup_field = 'id'

    def get_queryset(self) -> list[Chat]:
        room_slug = self.kwargs['room_slug']
        return Chat.objects.filter(chat_room__room_slug=room_slug)
     