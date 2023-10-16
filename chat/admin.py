from django.contrib import admin
from .models import  Room, Chat, ImageFile

# Register your models here.
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass
    
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass

@admin.register(ImageFile) 
class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_date', 'image_name')
    ordering = ('-uploaded_date',)