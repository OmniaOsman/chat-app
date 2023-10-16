from django.contrib import admin
from .models import  Room, Chat, ImageFile

# Register your models here.
admin.site.register(Chat)
admin.site.register(Room)
admin.site.register(ImageFile) 