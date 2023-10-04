from djongo import models
from accounts.models import User

# Create your models here.
class Chat(models.Model):
    sender    = models.CharField(max_length=50)
    receiver  = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    message   = models.TextField()
    image     = models.ImageField(upload_to='chat_images', 
                                  blank=True, 
                                  null=True)

    class Meta:
        app_label = 'chat'

    def __str__(self):
        return f"Chat {self.id}"

