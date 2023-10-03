from djongo import models
from accounts.models import User

# Create your models here.
class Chat(models.Model):
    sender   = models.ForeignKey(User, 
                                 related_name='sent_messages', 
                                 on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, 
                                 related_name='received_messages', 
                                 on_delete=models.CASCADE)
    image    = models.ImageField(upload_to='chat_images', 
                              blank=True, 
                              null=True)
    message   = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'chat'

    def __str__(self):
        return f"Chat {self.id}"

