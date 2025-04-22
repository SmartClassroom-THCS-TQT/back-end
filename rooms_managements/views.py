from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import connection
from .models import *
from .serializers import *
from rest_framework.decorators import action
from users.models import Account
from rest_framework.permissions import IsAuthenticated,AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from users.models import Student
from rest_framework.views import APIView
from managements.models import Session
from django.utils.timezone import localtime, localdate
from .filters import SeatingFilter, AttendanceFilter, DeviceFilter


class SeatingViewSet(viewsets.ModelViewSet):
    queryset = Seating.objects.all()
    serializer_class = SeatingSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SeatingFilter
    ordering_fields = '__all__'

    # Action để hoán đổi chỗ ngồi của 2 học sinh
    @action(detail=False, methods=['post'])
    def swap_seats(self, request):
        user_id_1 = request.data.get('user_id_1')
        user_id_2 = request.data.get('user_id_2')

        if not user_id_1 or not user_id_2:
            return Response({'error': 'Both user_id_1 and user_id_2 are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_1 = Student.objects.get(account__user_id=user_id_1)
            student_2 = Student.objects.get(account__user_id=user_id_2)

            seating_1 = Seating.objects.get(student=student_1)
            seating_2 = Seating.objects.get(student=student_2)

            # Lưu lại vị trí gốc
            room_1, row_1, col_1 = seating_1.room, seating_1.row, seating_1.column
            room_2, row_2, col_2 = seating_2.room, seating_2.row, seating_2.column

            # Bước 1: chuyển seating_1 về vị trí tạm (-1, -1) không hợp lệ
            seating_1.row, seating_1.column = -1, -1
            seating_1.save()

            # Bước 2: chuyển seating_2 vào chỗ của seating_1
            seating_2.room, seating_2.row, seating_2.column = room_1, row_1, col_1
            seating_2.save()

            # Bước 3: chuyển seating_1 vào chỗ cũ của seating_2
            seating_1.room, seating_1.row, seating_1.column = room_2, row_2, col_2
            seating_1.save()

            return Response({
                'message': 'Seats swapped successfully',
                'student_1_new_position': {'room': room_2.id, 'row': row_2, 'column': col_2},
                'student_2_new_position': {'room': room_1.id, 'row': row_1, 'column': col_1},
            }, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response({'error': 'One or both students not found'}, status=status.HTTP_404_NOT_FOUND)
        except Seating.DoesNotExist:
            return Response({'error': 'One or both students do not have seating positions'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    authention_classes = [AllowAny]
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AttendanceFilter
    ordering_fields = '__all__'


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authention_classes = [AllowAny]
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DeviceFilter
    ordering_fields = '__all__'

class DeviceAttendanceAPIView(APIView):
    permission_classes = []  # hoặc cho phép cụ thể sau

    def post(self, request):
        student_id = request.data.get('student_id')
        device_code = request.data.get('device_code')

        if not student_id or not device_code:
            return Response({'detail': 'Missing student_id or device_code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lấy student và thiết bị
        try:
            student = Student.objects.get(account__user_id=student_id)
        except Student.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            device = Device.objects.get(code=device_code)
        except Device.DoesNotExist:
            return Response({'detail': 'Device not found.'}, status=status.HTTP_404_NOT_FOUND)

        room = device.room
        if not room.students.filter(account__user_id=student_id).exists():
            return Response({'detail': 'Student not assigned to this room.'}, status=status.HTTP_403_FORBIDDEN)

        # Lọc session hôm nay trong room
        today = localdate()
        sessions_today = Session.objects.filter(
            room_id=room,
            day=today
        )

        attendances_marked = []
        for session in sessions_today:
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                session=session,
                defaults={'status': True}
            )
            if not created:
                attendance.status = True
                attendance.save()
            attendances_marked.append({
                'session_id': session.id,
                'lesson_name': session.lesson_name,
                'status': attendance.status,
                'time': localtime(attendance.attendance_time)
            })

        return Response({
            'detail': 'Attendance marked successfully.',
            'student': student.full_name,
            'sessions_marked': attendances_marked
        }, status=status.HTTP_200_OK)