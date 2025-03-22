from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import connection
from .models import *
from .serializers import *
from rest_framework.decorators import action
from users.models import Account
from rest_framework.permissions import IsAuthenticated,AllowAny
from django_filters.rest_framework import DjangoFilterBackend

class SeatingViewSet(viewsets.ModelViewSet):
    queryset = Seating.objects.all()
    serializer_class = SeatingSerializer
    authention_classes = [AllowAny]
    permission_classes = [AllowAny]

    # Action để hoán đổi chỗ ngồi của 2 học sinh
    @action(detail=False, methods=['post'])
    def swap_seats(self, request):
        user_id_1 = request.data.get('user_id_1')
        user_id_2 = request.data.get('user_id_2')

        if not user_id_1 or not user_id_2:
            return Response({'error': 'Both user_id_1 and user_id_2 are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Sử dụng raw SQL để lấy thông tin chỗ ngồi của 2 học sinh
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT s.id, s.student_id, s.room_id, s.row, s.column
                    FROM seating s
                    JOIN custom_user cu1 ON cu1.user_id = %s AND cu1.id = s.student_id
                    JOIN custom_user cu2 ON cu2.user_id = %s AND cu2.id = s.student_id
                    """, [user_id_1, user_id_2])

                seating_data = cursor.fetchall()

            if len(seating_data) != 2:
                return Response({'error': 'One or both students do not have seating positions'}, status=status.HTTP_400_BAD_REQUEST)

            # Hoán đổi vị trí của hai học sinh
            student_1 = seating_data[0]
            student_2 = seating_data[1]
            room_1, row_1, column_1 = student_1[2], student_1[3], student_1[4]
            room_2, row_2, column_2 = student_2[2], student_2[3], student_2[4]

            # Xóa hai chỗ ngồi hiện tại
            Seating.objects.filter(student_id=student_1[1]).delete()
            Seating.objects.filter(student_id=student_2[1]).delete()

            # Tạo lại chỗ ngồi sau khi hoán đổi
            Seating.objects.create(student_id=student_2[1], room_id=room_1, row=row_1, column=column_1)
            Seating.objects.create(student_id=student_1[1], room_id=room_2, row=row_2, column=column_2)

            return Response({
                'message': 'Seats swapped successfully',
                'student_1_new_position': {'room': room_2, 'row': row_2, 'column': column_2},
                'student_2_new_position': {'room': room_1, 'row': row_1, 'column': column_1},
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ViewSets cho các model
class SeatingViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Seating.objects.all()
    serializer_class = SeatingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'row', 'column']
    odering_fields = '__all__'


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    authention_classes = [AllowAny]
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student', 'session', 'status']
    ordering_fields = '__all__'


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authention_classes = [AllowAny]
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room']
    ordering_fields = '__all__'