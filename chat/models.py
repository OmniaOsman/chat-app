from djongo import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify


def validate_image_size(value):
    try:
        limit = 2 * 1024 * 1024 # e.g. 2MB
        if value.size > limit:
            raise ValidationError('File too large. Image should not exceed 2MB.')
    except AttributeError:
        raise ValidationError('Invalid value. Expected a file.')

def validate_image_format(value):
    try:
        valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
        FileExtensionValidator(allowed_extensions=valid_extensions)(value)
    except ValidationError:
        raise ValidationError('Invalid file extension. Allowed extensions are: jpg, jpeg, png, gif.')


class Room(models.Model):
    room_name = models.CharField(max_length=50)
    room_slug = models.SlugField(max_length=50,
                             unique=True,
                             primary_key=True)
    
    class Meta:
        app_label = 'chat'

    def __str__(self):
        return self.room_slug

    
    
class Chat(models.Model): 
    sender    = models.CharField(max_length=50)
    receiver  = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    message   = models.TextField()
    image     = models.FileField(upload_to='chat_images', 
                                  blank=True, 
                                  null=True,
                                  validators=[validate_image_format,
                                              validate_image_size])
    chat_room = models.ForeignKey(Room,
                                  on_delete=models.CASCADE)   

    class Meta:
        app_label = 'chat'

    def __str__(self):
        return f"Chat {self.chat_room}"
    
