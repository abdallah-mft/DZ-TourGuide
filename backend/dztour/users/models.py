from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

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
    phone = models.CharField(max_length=20 , blank=True )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    class Meta :
        db_table = 'users'

    def __str__(self):
        return self.email                       





