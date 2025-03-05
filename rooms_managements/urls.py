from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SeatingViewSet

# Tạo router và đăng ký viewset
router = DefaultRouter()
router.register(r'seatings', SeatingViewSet)

urlpatterns = [
    path('', include(router.urls)),  
]