# views.py
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import timedelta
from django.utils.dateparse import parse_date
from django.db import connection
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

# Academic Year ViewSet
class AcademicYearViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['year_name']
    ordering_fields = '__all__'

# Semester ViewSet
class SemesterViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'academic_year__year_name']
    ordering_fields = '__all__'

# Room ViewSet
class RoomViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'academic_year__year_name', 'manager__account']
    ordering_fields = '__all__'


# Subject ViewSet
class SubjectViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'name']
    ordering_fields = '__all__'


# Time Slot ViewSet
class TimeSlotViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Time_slot.objects.all()
    serializer_class = TimeSlotSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'start_time', 'end_time']
    ordering_fields = '__all__'

# Session ViewSet
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['semester_code', 'room_id', 'teacher', 'subject_code']
    ordering_fields = '__all__'

# Teacher Assignment ViewSet
class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = Teacher_assignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id','semester_code__code', 'subject_code__code', 'room_id__id', 'teacher__account']
    ordering_fields = '__all__'

class CheckCurrentSemester(APIView):
    permission_classes = [AllowAny]
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
    

class GenerateTimetableAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            semester_code = request.data.get('semester_code')
            room_id = request.data.get('room_id')
            subject_code = request.data.get('subject_code')
            day = parse_date(request.data.get('day'))
            time_slot_code = request.data.get('time_slot_code')

            if not all([semester_code, room_id, subject_code, day, time_slot_code]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                cursor.execute("SELECT start_date, weeks_count FROM semester WHERE code = %s", [semester_code])
                semester = cursor.fetchone()
                if not semester:
                    return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)

                start_date, weeks_count = semester
                end_date = start_date + timedelta(weeks=weeks_count)
                sessions = []

                for week in range(weeks_count):
                    session_date = day + timedelta(weeks=week)
                    if session_date > end_date:
                        break
                    sessions.append((semester_code, room_id, subject_code, session_date, time_slot_code, week + 1, f"Lesson {week + 1}"))
                
                cursor.executemany("""
                    INSERT INTO session 
                    (semester_code_id, room_id_id, subject_code_id, day, time_slot_id, lesson_number, lesson_name, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE);

                """, sessions)

            return Response({'message': f'{len(sessions)} sessions created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

