from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Chat
from .serializers import ChatSerializer

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve all chat messages
        chats = Chat.objects.all()
        # Serialize the chat messages
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

    def post(self, request, sender, receiver):
        # Create a new chat message
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=sender, receiver=receiver)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
