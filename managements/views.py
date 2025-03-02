# views.py
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class ClassTimeViewSet(viewsets.ModelViewSet):
    queryset = Time_slot.objects.all()
    serializer_class = ClassTimeSerializer

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class CheckCurrentSemester(APIView):
    def get(self, request):
        today = date.today()
        semester = Semester.objects.filter(start_date__lte=today).order_by('-start_date').first()
        
        if semester and semester.end_date >= today:
            return Response({
                "semester": semester.name,
                "start_date": semester.start_date,
                "end_date": semester.end_date,
                "current_week": semester.get_week(today)
            }, status=status.HTTP_200_OK)
        
        return Response({"message": "No active semester found."}, status=status.HTTP_404_NOT_FOUND)