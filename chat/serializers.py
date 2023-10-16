from rest_framework.serializers import ModelSerializer
from .models import ImageFile, Chat


class ImageFilesSerializer(ModelSerializer):
    class Meta:
        model  = ImageFile
        fields = '__all__'
        

class ChatSerializer(ModelSerializer):
    class Meta:
        model  = Chat
        fields = '__all__'