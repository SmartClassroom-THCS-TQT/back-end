from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeploymentViewSet

router = DefaultRouter()
router.register(r'deployment', DeploymentViewSet, basename='deployment')

urlpatterns = [
    path('', include(router.urls)),
] 