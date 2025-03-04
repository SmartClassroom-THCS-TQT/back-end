
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'sessions', SessionViewSet)
router.register(r'teacher-assignments', TeacherAssignmentViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('check-semester/', CheckCurrentSemester.as_view(), name='check_current_semester'),
    path('generate-timetable/', GenerateTimetableAPIView.as_view(), name='generate_timetable'),
    path('<str:code>/students/', StudentsInRoomView.as_view(), name='room-students'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
