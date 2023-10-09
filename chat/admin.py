from django.contrib import admin
from .models import  Room, Chat

# Register your models here.
admin.site.register(Chat)
admin.site.register(Room)