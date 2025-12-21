from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GuideProfileViewSet,
    CertificationViewSet,
    LanguageListView,
    WilayaListView,
    CommuneListView
)

router = DefaultRouter()
router.register(r'profiles', GuideProfileViewSet, basename='guide-profile')
router.register(r'certifications', CertificationViewSet, basename='certification')

urlpatterns = [
    path('', include(router.urls)),
    path('languages/', LanguageListView.as_view(), name='language-list'),
    path('wilayas/', WilayaListView.as_view(), name='wilaya-list'),
    path('communes/', CommuneListView.as_view(), name='commune-list'),
]