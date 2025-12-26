from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TourViewSet, BookingViewSet, create_regular_booking, create_custom_tour_booking

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'', TourViewSet, basename='tour')

urlpatterns = [
    path('<int:tour_id>/book/', create_regular_booking),
    path('book-custom/', create_custom_tour_booking),
    path('', include(router.urls)),
]