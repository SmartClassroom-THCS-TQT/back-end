from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Tạo router và đăng ký viewset
router = DefaultRouter()
router.register(r'seatings', SeatingViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'devices', DeviceViewSet)

urlpatterns = [
    path('rooms_managements', include(router.urls)),  
]