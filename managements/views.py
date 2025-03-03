# views.py
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Semester ViewSet
class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

# Room ViewSet
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

# Subject ViewSet
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


# Time Slot ViewSet
class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = Time_slot.objects.all()
    serializer_class = ClassTimeSerializer

# Session ViewSet
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

# Teacher Assignment ViewSet
class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = Teacher_assignment.objects.all()
    serializer_class = SessionSerializer


class CheckCurrentSemester(APIView):
    def get(self, request):
        today = date.today()
        semester = Semester.objects.filter(start_date__lte=today).order_by('-start_date').first()
        
        if semester and semester.end_date >= today:
            return Response({
                "semester": semester.code,
                "start_date": semester.start_date,
                "end_date": semester.end_date,
                "current_week": semester.get_week(today)
            }, status=status.HTTP_200_OK)
        
        return Response({"message": "No active semester found."}, status=status.HTTP_404_NOT_FOUND)
    