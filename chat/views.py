import redis
import logging
from PIL import Image
from io import BytesIO
from rest_framework import status
from .tasks import resize_image
from .models import ImageFile, Chat
from celery.result import AsyncResult
from rest_framework.response import Response
from .serializers import ImageFileSerializer, ChatSerializer
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST


def validate_image_size(value) -> None:
    """Validates the size of an image file.
    Args:
        value: A file object or a path to an image file.
    Raises:
        ValidationError: If the image file is too large or if it is a compression bomb.
    """
    MAX_SIZE = 5 * 1024 * 1024  # 10 MB
    MAX_WIDTH = 2000  # pixels
    MAX_HEIGHT = 1000  # pixels

    file_size = value.size
    width, height = Image.open(value).size
    logging.warning(f"file_size: {file_size}, width: {width}, height: {height}")

    if file_size > MAX_SIZE:
        raise ValidationError({
            "success": False,
            "message": "image file is exceded the maximum size 5MB"
        })
    
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValidationError({
            "success": False,
            "message": "Maximum image size is 2000x1000 pixels"
        })

    compression_ratio = file_size / (width * height)

    if compression_ratio < 0.1:
        raise ValidationError({
            "success": False,
            "message": "image file has a compression bomb"
        })
    
def validate_image_format(value) -> None:
    """
    Validates the image format of a given file.

    Parameters:
        value: The file to be validated.

    Raises:
        ValidationError: If the file has an invalid format.
    """
    try:
        valid_extensions = ['jpg', 'jpeg', 'png']
        FileExtensionValidator(allowed_extensions=valid_extensions)(value)
    except ValidationError:
        raise ValidationError({
            "success": False,
            "message": "file not an image file"
        })
 

class ImageFilesView(CreateAPIView):
    queryset = ImageFile.objects.all()
    serializer_class = ImageFileSerializer 
    permission_classes = (IsAuthenticated,)
    
    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            error_message = exc.args[0] if exc.args else None
            return Response(data={
                "message": error_message
            }, status=HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)

    @csrf_exempt
    def post(self, request, *args, **kwargs) -> Response:
        """ This function handles the POST request to upload an image file. """
        image_file = request.FILES.get('image_file')
        
        # Check if the image_file exists
        if not image_file:
            errors = {'image_file': ['No file was submitted.']}
            raise ValidationError(errors)

        # Validate the image file size and format
        validate_image_format(image_file)
        validate_image_size(image_file)
        
        # Save the uploaded file in the database            
        image = ImageFile(image_file=image_file)
        image.image_name = image_file.name
        image.save()

        # Save the uploaded file in Redis
        redis_client = redis.Redis()
        image_data = BytesIO()
        for chunk in image_file.chunks():
            image_data.write(chunk)
        image_data.seek(0)
        image_id = str(image.id)
        redis_client.set(image_id, image_data.getvalue())
        logging.warning(f'Saved image with ID: {image_id}')

        # Call the resize_image task asynchronously
        thumbnail_image = resize_image.delay(image_id)
        thumbnail_image_result = thumbnail_image.get()
        
        logging.warning(thumbnail_image_result)
        
        # Save the thumbnail image in the database
        image.resized_image.save(f"{image_id}-thumbnail.jpeg", 
                                 ContentFile(thumbnail_image_result),
                                 save=False)
        image.save()

        return Response({'success': 'true', 
                         'message': 'File uploaded successfully'}, 
                          status=status.HTTP_201_CREATED)
        
        
class ChatListView(ListAPIView): 
    serializer_class = ChatSerializer  
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'

    def get_queryset(self) -> list[Chat]:
        """ Retrieves a list of chat objects based on the specified room slug. """
        room_slug = self.kwargs['room_slug']
        return Chat.objects.filter(chat_room__room_slug=room_slug)
     