
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'subjects', SubjectViewSet) 
router.register(r'lessons', LessonViewSet)
router.register(r'class_times', ClassTimeViewSet)
router.register(r'sessions', SessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('check-semester/', CheckCurrentSemester.as_view(), name='check_current_semester'),
]
