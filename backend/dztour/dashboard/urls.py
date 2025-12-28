from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dashboard.views import GuideDashboardViewSet

router = DefaultRouter()
router.register(r'dashboard', GuideDashboardViewSet, basename='guide-dashboard')

urlpatterns = [
    path('guides/', include(router.urls)),
]