import os 
import uuid
import logging
from djongo import models
from django.utils.text import slugify



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
    id = models.TextField(primary_key=True, 
                          default=uuid.uuid4)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    image_name = models.CharField(max_length=100, 
                                  default='image') 
    resized_image = models.FileField(upload_to='resized_images',
                                     null=True,
                                     blank=True)
    image_file = models.FileField(upload_to='images/')
    
    class Meta:
        app_label = 'chat' 
        
    def __str__(self):
        return self.image_name
 
    
class Chat(models.Model): 
    sender     = models.CharField(max_length=50)
    receiver   = models.CharField(max_length=50)
    timestamp  = models.DateTimeField(auto_now_add=True)
    message    = models.TextField()
    chat_room  = models.ForeignKey(Room,
                                  on_delete=models.CASCADE)  
    chat_image = models.ForeignKey(ImageFile, 
                                  on_delete=models.CASCADE, 
                                  null=True)  

    class Meta:
        app_label = 'chat'

    def __str__(self):
        return f"Chat {self.chat_room}"
    
