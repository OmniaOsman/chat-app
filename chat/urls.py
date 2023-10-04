from django.urls import path
from .views import ChatView

urlpatterns = [
    path('chat/<str:sender>/<str:receiver>/', ChatView.as_view(), name='chat-list'),
]
