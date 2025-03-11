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
from django.conf import settings
from rest_framework.decorators import action
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend

# Semester ViewSet
class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

# Room ViewSet
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'semesters', 'manager__user']


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
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['semester_code', 'room_code', 'teacher', 'subject_code']
    

# Teacher Assignment ViewSet
class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = Teacher_assignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['semester_code__code', 'subject_code__code', 'room_code__code', 'teacher__user']

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
            room_code = request.data.get('room_code')
            subject_code = request.data.get('subject_code')
            day = parse_date(request.data.get('day'))
            time_slot_code = request.data.get('time_slot_code')

            if not all([semester_code, room_code, subject_code, day, time_slot_code]):
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
                    sessions.append((semester_code, room_code, subject_code, session_date, time_slot_code, week + 1, f"Lesson {week + 1}"))
                
                cursor.executemany("""
                    INSERT INTO session 
                    (semester_code_id, room_code_id, subject_code_id, day, time_slot_id, lesson_number, lesson_name, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE);

                """, sessions)

            return Response({'message': f'{len(sessions)} sessions created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentsInRoomView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code, format=None):
        try:
            # Kiểm tra xem phòng học có tồn tại không
            room = Room.objects.get(code=code)
        except Room.DoesNotExist:
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Sử dụng truy vấn SQL trực tiếp để lấy danh sách học sinh trong lớp, bao gồm image
        query = """
            SELECT 
                s.user_id, s.full_name, s.email, s.phone_number, s.sex, s.day_of_birth, 
                s.nation, s.active_status, s.image
            FROM 
                student st  -- Bảng students
            INNER JOIN custom_user s ON st.user_id = s.user_id  -- Bảng custom_user
            WHERE st.classroom_id = %s
        """
                
        with connection.cursor() as cursor:
            cursor.execute(query, [room.code])
            result = cursor.fetchall()

        # Chuyển đổi kết quả SQL thành dạng JSON, bao gồm cả trường image
        students_data = [
            {
                "user_id": row[0],
                "full_name": row[1],
                "email": row[2],
                "phone_number": row[3],
                "sex": row[4],
                "day_of_birth": row[5],
                "nation": row[6],
                "active_status": row[7],
                "image_url": f"{settings.MEDIA_URL}{row[8]}" if row[8] else None  # Thêm MEDIA_URL vào đường dẫn ảnh
            }
            for row in result
        ]

        return Response(students_data)
    