from django.db import models
from cloudinary.models import CloudinaryField
from guides.models import GuideProfile

class Tour(models.Model):    
    title = models.CharField(max_length=200)
    description = models.TextField()
    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='tours')
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # start_place = models.CharField(max_length=200)
    # max_participants = models.PositiveIntegerField(default=10)

    def save(self, *args, **kwargs):
        tour_hours = self.duration.total_seconds() / 3600
        if tour_hours <= 4:
            self.price = self.guide.price_for_half_day
        elif tour_hours <= 8:
            self.price = self.guide.price_for_day
        else:
            self.price = self.guide.price_for_day + (self.guide.price_for_sup_hours * (tour_hours - 8))

        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title
    

class TourPicture(models.Model):    
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='pictures')
    image = CloudinaryField(folder='tour_pics')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.tour.title} - Picture {self.id}"

