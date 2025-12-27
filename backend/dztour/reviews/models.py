from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from users.models import User
from tours.models import Booking

class Review(models.Model):
    tourist = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    guide = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')

    tour_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        blank=True,
        null=True
    )
    guide_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        blank=True,
        null=True
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.tourist.email} - Tour: {self.tour_rating}, Guide: {self.guide_rating}"

    def save(self, *args, **kwargs):
        if self.booking:
            self.tourist = self.booking.tourist
            guide_profile = self.booking.get_tour_object().guide
            self.guide = guide_profile.user if hasattr(guide_profile, 'user') else guide_profile

        super().save(*args, **kwargs)
