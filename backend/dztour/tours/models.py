from decimal import Decimal
from django.db import models
from cloudinary.models import CloudinaryField
from guides.models import GuideProfile, Wilaya
from users.models import User

class Tour(models.Model):    
    title = models.CharField(max_length=200)
    description = models.TextField()
    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='tours')
    wilaya = models.ForeignKey(Wilaya, on_delete=models.SET_NULL, null=True, related_name='tours')
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # start_place = models.CharField(max_length=200)
    # max_participants = models.PositiveIntegerField(default=10)

    def save(self, *args, **kwargs):
        tour_hours = Decimal(self.duration.total_seconds() / 3600)
        if tour_hours <= 4:
            self.price = self.guide.price_for_half_day
        elif tour_hours <= 8:
            self.price = self.guide.price_for_day
        else:
            extra_hours = tour_hours - 8
            self.price = self.guide.price_for_day + (self.guide.price_for_sup_hours * extra_hours)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title

class TourPicture(models.Model):    
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='pictures')
    image = CloudinaryField(folder='tour_pics')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tour.title} - Picture {self.id}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("negotiated", "Negotiated")
    )

    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, related_name='requests')
    tourist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tour_requests')
    requested_time = models.DateTimeField()
    number_of_participants = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tourist.username} - {self.tour.title} ({self.requested_time})"
