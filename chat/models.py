import os
import zipfile
from PIL import Image
from djongo import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
import uuid


def validate_image_size(value) -> None:
    """Validates the size of an image file.
    Args:
        value: A file object or a path to an image file.
    Raises:
        ValidationError: If the image file is too large or if it is a compression bomb.
    """
    MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_WIDTH = 3000  # pixels
    MAX_HEIGHT = 2000  # pixels

    file_size = value.size
    width, height = Image.open(value).size

    if file_size > MAX_SIZE or width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValidationError(f"The image file is too large. The maximum size is {MAX_SIZE} \
            bytes and the maximum dimensions are {MAX_WIDTH} x {MAX_HEIGHT} pixels.")

    compression_ratio = file_size / (width * height)
    print(file_size, width, height, compression_ratio)
    if compression_ratio < 0.1:
        raise ValidationError(f"The image file is a compression bomb. \
            The compression ratio is {compression_ratio:.2f}, which is too low.")

    

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
        raise ValidationError('Invalid file extension. Allowed extensions are: jpg, jpeg, png.')



class Room(models.Model):
    room_name = models.CharField(max_length=50)
    room_slug = models.SlugField(max_length=50,
                                 unique=True,
                                 primary_key=True)
    
    class Meta:
        app_label = 'chat'

    def __str__(self):
        return self.room_slug

    
class ImageFile(models.Model):
    id = models.TextField(primary_key=True, default=uuid.uuid4)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    image_name = models.CharField(max_length=100, 
                                     default='image') 
    resized_image = models.FileField(upload_to='media/resized_images',
                                     null=True,
                                     blank=True)
    image_file= models.FileField(upload_to='images/', 
                                      validators=[validate_image_size, 
                                                 validate_image_format])
    
    class Meta:
        app_label = 'chat' 
        
    def __str__(self):
        return self.image_name

    
class Chat(models.Model): 
    sender    = models.CharField(max_length=50)
    receiver  = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    message   = models.TextField()
    chat_room = models.ForeignKey(Room,
                                  on_delete=models.CASCADE)  
    image     = models.ForeignKey(ImageFile, 
                                  on_delete=models.CASCADE, 
                                  null=True)  

    class Meta:
        app_label = 'chat'

    def __str__(self):
        return f"Chat {self.chat_room}"
    
