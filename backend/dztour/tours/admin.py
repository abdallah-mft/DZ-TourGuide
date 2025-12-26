from django.contrib import admin
from .models import Tour, TourPicture, Booking, CustomTour

admin.site.register(Tour)
admin.site.register(TourPicture)
admin.site.register(Booking)
admin.site.register(CustomTour)

