from .models import ImageFile, Chat
from django.urls import path
from . import views


urlpatterns = [
    path('<str:room_slug>/', views.ChatListView.as_view()),
    path('<str:room_slug>/upload/', views.ImageFilesView.as_view()),
]
