from rest_framework.routers import DefaultRouter
from .views import GradeViewSet, GradeTypeViewSet

router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'grade-types', GradeTypeViewSet, basename='grade-type')

urlpatterns = router.urls
