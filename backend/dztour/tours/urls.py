from rest_framework.routers import DefaultRouter
from .views import TourViewSet

router = DefaultRouter()
router.register(r'', TourViewSet)

urlpatterns = router.urls