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
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        # Lấy tham số từ request
        day = request.GET.get("day")
        semester_code = request.GET.get("semester_code")
        room_code = request.GET.get("room_code")
        teacher_id = request.GET.get("teacher_id")
        subject_code = request.GET.get("subject_code")

        # Kiểm tra định dạng ngày
        try:
            start_date = datetime.strptime(day, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        end_date = start_date + timedelta(days=6)  # 7 ngày liên tiếp

        # Xây dựng điều kiện lọc động
        filters = ["s.day BETWEEN %s AND %s"]
        params = [start_date, end_date]

        if semester_code:
            filters.append("s.semester_code_id = %s")
            params.append(semester_code)
        if room_code:
            filters.append("s.room_code_id = %s")
            params.append(room_code)
        if teacher_id:
            filters.append("s.teacher_id = %s")
            params.append(teacher_id)
        if subject_code:
            filters.append("s.subject_code_id = %s")
            params.append(subject_code)

        where_clause = " AND ".join(filters)

        # Raw SQL query
        query = f"""
            SELECT 
                s.id, 
                r.name AS room_name, 
                ts.start_time || ' - ' || ts.end_time AS time_slot, 
                sub.name AS subject_name, 
                s.lesson_name, 
                s.status
            FROM session s
            JOIN room r ON s.room_code_id = r.code
            JOIN time_slot ts ON s.time_slot_id = ts.code
            JOIN subject sub ON s.subject_code_id = sub.code
            WHERE {where_clause}
            ORDER BY s.day, ts.start_time
        """

        # Thực thi query
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"data": results})
    @action(detail=False, methods=["get"], url_path="filtered",permission_classes = [AllowAny])
    def filter_sessions(self, request, *args, **kwargs):
        """API 2: Lọc theo học kỳ, lớp, giáo viên hoặc môn học"""
        semester_code = request.GET.get("semester_code")
        room_code = request.GET.get("room_code")
        teacher_id = request.GET.get("teacher_id")
        subject_code = request.GET.get("subject_code")

        # Kiểm tra ít nhất một tham số được truyền vào
        if not any([semester_code, room_code, teacher_id, subject_code]):
            return Response({"error": "At least one filter parameter is required"}, status=400)

        # Xây dựng điều kiện lọc động
        filters = []
        params = []

        if semester_code:
            filters.append("s.semester_code_id = %s")
            params.append(semester_code)
        if room_code:
            filters.append("s.room_code_id = %s")
            params.append(room_code)
        if teacher_id:
            filters.append("s.teacher_id = %s")
            params.append(teacher_id)
        if subject_code:
            filters.append("s.subject_code_id = %s")
            params.append(subject_code)

        where_clause = " AND ".join(filters)

        # Raw SQL query
        query = f"""
            SELECT 
                s.id, 
                r.name AS room_name, 
                ts.start_time || ' - ' || ts.end_time AS time_slot, 
                sub.name AS subject_name, 
                s.lesson_name, 
                s.status
            FROM session s
            JOIN room r ON s.room_code_id = r.code
            JOIN time_slot ts ON s.time_slot_id = ts.code
            JOIN subject sub ON s.subject_code_id = sub.code
            WHERE {where_clause}
            ORDER BY s.day, ts.start_time
        """

        # Thực thi query
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"data": results})
    @action(detail=False, methods=['get'], url_path='filtered-status')
    def filtered_status(self, request):
        semester_code = request.GET.get('semester_code')
        room_code = request.GET.get('room_code')
        teacher_id = request.GET.get('teacher_id')
        subject_code = request.GET.get('subject_code')
        status = request.GET.get('status')
        day = request.GET.get('day')

        # Xây dựng SQL query động
        query = """
            SELECT id, status
            FROM session
            WHERE 1=1
        """
        params = []

        if semester_code:
            query += " AND semester_code_id = %s"
            params.append(semester_code)

        if room_code:
            query += " AND room_code_id = %s"
            params.append(room_code)

        if teacher_id:
            query += " AND teacher_id = %s"
            params.append(teacher_id)

        if subject_code:
            query += " AND subject_code_id = %s"
            params.append(subject_code)

        if status is not None:  # Trường boolean có thể là True/False
            query += " AND status = %s"
            params.append(status.lower() == 'true')  # Chuyển đổi 'true' -> True, 'false' -> False

        if day:
            query += " AND day = %s"
            params.append(day)

        # Thực thi SQL truy vấn
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"data": results})

# Teacher Assignment ViewSet
class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = Teacher_assignment.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]
    @action(detail=False, methods=['get'], url_path='search',permission_classes = [AllowAny])
    def search_assignments(self, request):
        """
        API: `/api/teacher-assignments/search/`
        → Lấy thông tin phân công giáo viên theo các tham số truyền lên.
        """
        semester_code = request.query_params.get("semester_code")
        subject_code = request.query_params.get("subject_code")
        room_code = request.query_params.get("room_code")
        teacher_id = request.query_params.get("teacher")

        # Điều kiện lọc động
        filters = []
        params = []
        
        if semester_code:
            filters.append("ta.semester_code_id = %s")
            params.append(semester_code)
        if subject_code:
            filters.append("ta.subject_code_id = %s")
            params.append(subject_code)
        if room_code:
            filters.append("ta.room_code_id = %s")
            params.append(room_code)
        if teacher_id:
            filters.append("ta.teacher_id = %s")
            params.append(teacher_id)

        # Xây dựng câu truy vấn SQL tối ưu
        query = """
            SELECT 
                ta.id, 
                ta.semester_code_id, 
                s.name AS semester_name,
                ta.subject_code_id, 
                sub.name AS subject_name,
                ta.room_code_id, 
                r.name AS room_name,
                ta.teacher_id, 
                cu.full_name AS teacher_name,
                cu.image AS teacher_image
            FROM teacher_assignment ta
            LEFT JOIN semester s ON ta.semester_code_id = s.code
            LEFT JOIN subject sub ON ta.subject_code_id = sub.code
            LEFT JOIN room r ON ta.room_code_id = r.code
            LEFT JOIN teacher t ON ta.teacher_id = t.user_id
            LEFT JOIN custom_user cu ON t.user_id = cu.user_id
        """
        
        if filters:
            query += " WHERE " + " AND ".join(filters)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Xử lý đường dẫn ảnh cho giáo viên
        for result in results:
            if result["teacher_image"]:
                result["teacher_image"] = request.build_absolute_uri(result["teacher_image"])

        return Response(results, status=status.HTTP_200_OK)


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
    
class SessionByWeekAPIView(APIView):
    def get(self, request):
        # Lấy tham số từ request
        day = request.GET.get("day")
        semester_code = request.GET.get("semester_code")
        room_code = request.GET.get("room_code")
        teacher_id = request.GET.get("teacher_id")
        subject_code = request.GET.get("subject_code")

        # Kiểm tra định dạng ngày
        try:
            start_date = datetime.strptime(day, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        end_date = start_date + timedelta(days=6)  # 7 ngày liên tiếp

        # Xây dựng điều kiện lọc động
        filters = ["s.day BETWEEN %s AND %s"]
        params = [start_date, end_date]

        if semester_code:
            filters.append("s.semester_code_id = %s")
            params.append(semester_code)
        if room_code:
            filters.append("s.room_code_id = %s")
            params.append(room_code)
        if teacher_id:
            filters.append("s.teacher_id = %s")
            params.append(teacher_id)
        if subject_code:
            filters.append("s.subject_code_id = %s")
            params.append(subject_code)

        where_clause = " AND ".join(filters)

        # Raw SQL query
        query = f"""
            SELECT 
                s.id, 
                r.name AS room_name, 
                ts.start_time || ' - ' || ts.end_time AS time_slot, 
                sub.name AS subject_name, 
                s.lesson_name, 
                s.status
            FROM session s
            JOIN room r ON s.room_code_id = r.code
            JOIN time_slot ts ON s.time_slot_id = ts.code
            JOIN subject sub ON s.subject_code_id = sub.code
            WHERE {where_clause}
            ORDER BY s.day, ts.start_time
        """

        # Thực thi query
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"data": results})