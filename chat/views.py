import redis
import logging
from io import BytesIO
from rest_framework import status
from .tasks import resize_image
from .models import ImageFile, Chat
from celery.result import AsyncResult
from rest_framework.response import Response
from .serializers import ImageFilesSerializer, ChatSerializer
from django.core.files.base import ContentFile
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView
from django.views.decorators.csrf import csrf_exempt



class ImageFilesView(CreateAPIView, LoginRequiredMixin):
    queryset = ImageFile.objects.all()
    serializer_class = ImageFilesSerializer 
    
    @csrf_exempt
    def post(self, request, *args, **kwargs) -> Response:
        """ This function handles the POST request to upload an image file. """
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
        thumbnail_image = resize_image.delay(image_id)
        thumbnail_image_result = thumbnail_image.get()
        
        # save the thumbnail image in the database
        image.resized_image.save(f"{image_id}-thumbnail.jpeg", 
                                 ContentFile(thumbnail_image_result),
                                 save=False)
        image.save()

        return Response({'message': 'File uploaded successfully'}, 
                        status=status.HTTP_201_CREATED)
        
        
    
class ChatListView(ListAPIView, LoginRequiredMixin): 
    serializer_class = ChatSerializer  
    lookup_field = 'id'

    def get_queryset(self) -> list[Chat]:
        """ Retrieves a list of chat objects based on the specified room slug. """
        room_slug = self.kwargs['room_slug']
        return Chat.objects.filter(chat_room__room_slug=room_slug)
     