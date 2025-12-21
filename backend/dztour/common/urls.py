from django.urls import path
from .views import WilayaListView

urlpatterns = [
    path('wilayas/', WilayaListView.as_view(), name='wilaya-list'),
]