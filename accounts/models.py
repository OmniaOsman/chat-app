from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email           = models.EmailField(max_length=254, unique=True)
    username        = models.CharField(max_length=50, unique=True)
    is_active       = models.BooleanField(default=True)
    REQUIRED_FIELDS = ('first_name', 'last_name', 'email')
    USERNAME_FIELD  = 'username'
     
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
