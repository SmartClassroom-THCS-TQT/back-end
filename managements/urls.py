
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

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
]
