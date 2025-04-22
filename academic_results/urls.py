from rest_framework.routers import DefaultRouter
from .views import GradeViewSet, GradeTypeViewSet, GradeDistributionAPIView
from django.urls import path, include

router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'grade-types', GradeTypeViewSet, basename='grade-type')

urlpatterns = [
    path('', include(router.urls)),
    path('grades/distribution/', GradeDistributionAPIView.as_view(), name='grade-distribution'),
]