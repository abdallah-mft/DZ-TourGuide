from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review
from guides.models import GuideProfile

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_ratings(sender, instance, **kwargs):
    # Update Guide Ratings
    guide_user = instance.guide
    if hasattr(guide_user, 'profile'):
        guide_profile = guide_user.profile
        guide_reviews = Review.objects.filter(guide=guide_user, guide_rating__isnull=False)
        
        guide_agg = guide_reviews.aggregate(
            avg=Avg('guide_rating'),
            count=Count('id')
        )
        
        guide_profile.average_rating = guide_agg['avg'] or 0.0
        guide_profile.review_count = guide_agg['count'] or 0
        guide_profile.save()

    # Update Tour Ratings
    # Check if the review is for a standard tour (not custom)
    booking = instance.booking
    if booking and booking.tour:
        tour = booking.tour
        tour_reviews = Review.objects.filter(booking__tour=tour, tour_rating__isnull=False)
        
        tour_agg = tour_reviews.aggregate(
            avg=Avg('tour_rating'),
            count=Count('id')
        )
        
        tour.average_rating = tour_agg['avg'] or 0.0
        tour.review_count = tour_agg['count'] or 0
        tour.save()
