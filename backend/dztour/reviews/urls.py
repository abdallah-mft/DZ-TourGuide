from django.urls import path, include
from .views import CreateReview, DestroyUpdateReview

urlpatterns = [
    path('', CreateReview.as_view()),
    path('<int:id>/', DestroyUpdateReview.as_view()),
]
