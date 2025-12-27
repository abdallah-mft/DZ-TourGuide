from django.db import models
from cloudinary.models import CloudinaryField
from users.models import User

# Create your models here.


class Language(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Wilaya(models.Model):
    code = models.CharField(max_length=2, unique=True, primary_key=True) 
    name_fr = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.code} - {self.name_fr}'

class Commune(models.Model):
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, related_name='communes')
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name_fr = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.wilaya.code} / {self.name_fr}'


class GuideProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'guide'}, related_name='profile')
    id_document = CloudinaryField(folder='guides/id')
    bio = models.TextField()
    languages_spoken = models.ManyToManyField(Language)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    # === PRICING ===
    price_for_half_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_for_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_for_sup_hours = models.DecimalField(max_digits=10, decimal_places=2)

    # === COVRED WILAYAS AND COMMUNES ===
    wilaya_covered = models.ManyToManyField(Wilaya, related_name='guides')
    commune_covered = models.ManyToManyField(Commune, related_name='guides')

    # === CONTACT INFO ===
    phone_number = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    instagram_account = models.CharField(max_length=50, blank=True, null=True)

    # === STATS ===
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.PositiveIntegerField(default=0)

    # === TIMESTAMPS ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'profile: {self.user.username}'

class Certifications(models.Model):
    guide_profile = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=255)
    file =  CloudinaryField(folder='guides/certifications' , resource_type = 'auto' , blank = True , null = True )

    def __str__(self):
        return f"{self.name}"
