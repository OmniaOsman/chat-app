from djoser.serializers import UserCreateSerializer 
from .models import User


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model  = User
        fields = ('email', 'username', 'password',  
                  'first_name', 'last_name')
        
