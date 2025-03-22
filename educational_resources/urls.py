from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Tạo router và đăng ký viewsets
router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'document-types', DocumentTypeViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  
]
