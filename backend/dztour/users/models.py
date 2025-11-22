from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from cloudinary.models import CloudinaryField
from django.utils import timezone
from datetime import timedelta
import random
# Create your models here.




class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
            
        return self.create_user(email, password, **extra_fields)  


class User(AbstractUser):
    ROLE_CHOICES = (
        ('tourist',"Tourist"),
        ('guide',"Guide"),
    )
    username = None  # Using email instead of username
    email = models.EmailField(unique=True)
    role  = models.CharField(max_length=20 , choices=ROLE_CHOICES, default='tourist')
    @property # Enforcing validation so the user cannot be created with an invalid string also in the db level 
    def is_guide(self):
        return self.role == 'guide'
    phone = models.CharField(max_length=20 , blank=True )
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    profile_picture = CloudinaryField('image', folder='profile_pics', blank=True, null=True)
    
    class Meta :
        db_table = 'users'

    def __str__(self):
        return self.email                       

