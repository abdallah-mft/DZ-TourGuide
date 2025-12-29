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
    start_point_latitude = models.DecimalField(max_digits=10,decimal_places=6)
    start_point_longitude = models.DecimalField(max_digits=11,decimal_places=6)
    
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

class CustomTour(models.Model):
    tourist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_tours')
    title = models.CharField(max_length=200)
    description = models.TextField()
    guide = models.ForeignKey(GuideProfile, on_delete=models.SET_NULL, null=True, related_name='custom_tours')
    wilaya = models.ForeignKey(Wilaya, on_delete=models.SET_NULL, null=True, related_name='custom_tours')
    start_point_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    start_point_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Custom: {self.title} by {self.tourist.username}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
        ("negotiated", "Negotiated")
    )

    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    custom_tour = models.ForeignKey(CustomTour, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    tourist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tour_requests')
    date_time = models.DateTimeField()
    number_of_participants = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(tour__isnull=False, custom_tour__isnull=True) |
                    models.Q(tour__isnull=True, custom_tour__isnull=False)
                ),
                name='booking_tour_xor_custom_tour'
            )
        ]

    def __str__(self):
        tour_title = self.custom_tour.title if self.is_custom_tour else self.tour.title
        return f"{self.tourist.first_name} {self.tourist.last_name} - {tour_title} ({self.date_time})"

    def get_tour_object(self):
        return self.tour if self.tour else self.custom_tour

    @property
    def is_custom_tour(self):
        return self.custom_tour is not None
