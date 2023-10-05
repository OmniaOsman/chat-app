from djongo import models
from accounts.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


def validate_image_size(value):
    limit = 2 * 1024 * 1024 # e.g. 2MB
    if value.size > limit:
        raise ValidationError('File too large. Image should not exceed 2MB.')
    
def validate_image_format(value):
    valid_extension = ['jpg']
    FileExtensionValidator(allowed_extensions=valid_extension)(value)
    
    

# Create your models here.
class Chat(models.Model):
    sender    = models.CharField(max_length=50)
    receiver  = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    message   = models.TextField()
    image     = models.FileField(upload_to='chat_images', 
                                  blank=True, 
                                  null=True,
                                  validators=[validate_image_format,
                                              validate_image_format])

    class Meta:
        app_label = 'chat'

    def __str__(self):
        return f"Chat {self.id}"
    
