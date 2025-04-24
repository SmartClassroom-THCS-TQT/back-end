from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentTypeViewSet, DocumentViewSet, LessonPlanViewSet
)

# Tạo router và đăng ký viewsets
router = DefaultRouter()
router.register(r'document-types', DocumentTypeViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'lesson-plans', LessonPlanViewSet)

urlpatterns = [
    path('', include(router.urls)),  
]
