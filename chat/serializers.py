from rest_framework import serializers
from .models import ImageFile, Chat, Room
from rest_framework.serializers import Serializer, ValidationError


class ImageFileSerializer(serializers.Serializer):
    id = serializers.CharField()
    uploaded_date = serializers.DateTimeField()
    image_name = serializers.CharField(max_length=100)
    resized_image = serializers.FileField(allow_null=True, required=False)
    image_file = serializers.FileField()

    def create(self, validated_data):
        return ImageFile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.uploaded_date = validated_data.get('uploaded_date', instance.uploaded_date)
        instance.image_name = validated_data.get('image_name', instance.image_name)
        instance.resized_image = validated_data.get('resized_image', instance.resized_image)
        instance.image_file = validated_data.get('image_file', instance.image_file)
        instance.save()
        return instance


class ChatSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=50)
    receiver = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()
    message = serializers.CharField()
    chat_room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    chat_image = ImageFileSerializer(allow_null=True, required=False)

    def create(self, validated_data):
        return Chat.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.sender = validated_data.get('sender', instance.sender)
        instance.receiver = validated_data.get('receiver', instance.receiver)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.message = validated_data.get('message', instance.message)
        instance.chat_room = validated_data.get('chat_room', instance.chat_room)
        instance.chat_image = validated_data.get('chat_image', instance.chat_image)
        instance.save()
        return instance
    

class RoomSerializer(serializers.Serializer):
    room_name = serializers.CharField(max_length=50)
    room_slug = serializers.SlugField(max_length=50)

    def create(self, validated_data):
        return Room.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.room_name = validated_data.get('room_name', instance.room_name)
        instance.room_slug = validated_data.get('room_slug', instance.room_slug)
        instance.save()
        return instance