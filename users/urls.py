from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'admins', AdminViewSet)



urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-dangky'),
    path('login/', ApiLoginView.as_view(), name='api-dangnhap'),
    path('csrf-token/', CSRFTokenView.as_view(), name='csrf_token'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/', ResetPasswordByAdminView.as_view(), name='reset-password-admin'),
    path('', include(router.urls)),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
