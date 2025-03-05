from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import connection
from .models import Seating
from .serializers import SeatingSerializer
from rest_framework.decorators import action
from accounts.models import CustomUser
from rest_framework.permissions import IsAuthenticated

class SeatingViewSet(viewsets.ModelViewSet):
    queryset = Seating.objects.all()
    serializer_class = SeatingSerializer
    permission_classes = [IsAuthenticated]

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

    # Action để lấy danh sách học sinh trong phòng
    @action(detail=False, methods=['get'])
    def seating_list(self, request):
        room_name = request.query_params.get('room_name')

        try:
            # Sử dụng raw SQL để lấy danh sách học sinh trong phòng học
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT s.id, cu.user_id, cu.full_name, cu.image
                    FROM seating s
                    JOIN room r ON r.id = s.room_id
                    JOIN custom_user cu ON cu.id = s.student_id
                    WHERE r.name = %s
                    """, [room_name])

                seating_data = cursor.fetchall()

            if not seating_data:
                return Response({"detail": "Room not found or no seating positions available."}, status=status.HTTP_404_NOT_FOUND)

            # Chuyển dữ liệu thành response với thông tin user_id, fullname, và image của học sinh
            students = [
                {
                    'user_id': row[1],
                    'fullname': row[2],
                    'image': row[3]
                }
                for row in seating_data
            ]

            return Response(students, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # class AttendanceViewSet(viewsets.ModelViewSet):
# #     authentication_classes = []
# #     permission_classes = []
# #     queryset = Attendance.objects.all()
# #     serializer_class = AttendanceSerializer
# #     filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
# #     filterset_class = AttendanceFilter
# #     ordering_fields = '__all__'
# #     ordering = ['attendance_time']
# #     def create(self, request, *args, **kwargs):
# #         user_id = request.data.get("student_id")  
# #         device_id = request.data.get("device_id")

# #         if not user_id:
# #             return Response({"error": "Cần có ID người dùng."}, status=status.HTTP_400_BAD_REQUEST)
# #         try:
# #             current_time = timezone.localtime(timezone.now())
# #             lesson = get_current_lesson(device_id, current_time)
            
# #             if lesson:
# #                 user = get_object_or_404(CustomUser, user_id=user_id)
# #                 if Attendance.objects.filter(user=user, lesson=lesson).exists():
# #                     return Response({"error": "Thông tin điểm danh đã tồn tại."}, status=status.HTTP_400_BAD_REQUEST)

# #                 attendance_time = current_time
# #                 lesson_start_time = timezone.datetime.combine(lesson.day, lesson.period.start_time)
# #                 lesson_start_time = lesson_start_time.replace(tzinfo=timezone.get_current_timezone())

# #                 status_value = 1 if attendance_time <= lesson_start_time + timedelta(minutes=10) else 2       

# #                 attendance = Attendance(
# #                     user=user,
# #                     lesson=lesson,
# #                     status=status_value
# #                 )
# #                 attendance.save()  
# #                 serializer = self.get_serializer(attendance)
# #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
# #             else:
# #                 return Response({"error": "Không có tiết học nào đang hoạt động vào thời điểm này."}, status=status.HTTP_400_BAD_REQUEST)
# #         except Device.DoesNotExist:
# #             return Response({"error": "Không tìm thấy thiết bị."}, status=status.HTTP_404_NOT_FOUND)
# #         except ValidationError as e:
# #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# #     @action(detail=False, methods=['post'], url_path='update')
# #     def update_attendance(self, request):
# #         lesson_id = request.data.get("lesson_id")
# #         student_id = request.data.get("student_id")
# #         new_status = request.data.get("new_status")

# #         try:
# #             attendance = Attendance.objects.get(
# #                 lesson_id=lesson_id,
# #                 user__user_id=student_id
# #             )
# #             attendance.status = new_status
# #             attendance.save()
# #             serializer = self.get_serializer(attendance)
# #             return Response(serializer.data, status=status.HTTP_200_OK)
# #         except Attendance.DoesNotExist:
# #             return Response({"error": "Không tìm thấy thông tin điểm danh."}, status=status.HTTP_404_NOT_FOUND)
# #         except ValidationError as e:
# #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# # class DeviceViewSet(viewsets.ViewSet):
# #     authentication_classes = []
# #     permission_classes = []
# #     queryset = Device.objects.all()
# #     serializer_class = DeviceSerializer

# #     def create(self, request, *args, **kwargs):
# #         device_id = request.data.get('device_id')

# #         if not device_id or len(device_id) != 9:
# #             return Response({"error": "Device ID must be 9 characters long."}, status=status.HTTP_400_BAD_REQUEST)

# #         device, created = Device.objects.get_or_create(device_id=device_id)

# #         if created:
# #             return Response(DeviceSerializer(device).data, status=status.HTTP_201_CREATED)
# #         else:
# #             return Response({"error": "Device already exists."}, status=status.HTTP_400_BAD_REQUEST)

# #     @action(detail=False, methods=['post'], url_path='update-room')
# #     def update_room(self, request):
# #         device_id = request.data.get('device_id')
# #         room_id = request.data.get('room_id')

# #         if not device_id or not room_id:
# #             return Response({"error": "Device ID and Room ID are required."}, status=status.HTTP_400_BAD_REQUEST)

# #         try:
# #             device = Device.objects.get(device_id=device_id)
# #             device.room_id = room_id
# #             device.save()
# #             return Response({"message": "Room updated successfully."}, status=status.HTTP_200_OK)
# #         except Device.DoesNotExist:
# #             return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)


# # # Hệ thống ghi id vào thẻ 
# # class RFIDViewSet(viewsets.ViewSet):
# #     authentication_classes = []
# #     permission_classes = []
# #     def start(self, request):
# #         device_id = request.data.get('device_id')
# #         try:
# #             device = Device.objects.get(device_id=device_id)
# #             room = device.room
# #             students = room.student.all().values('user__user_id', 'full_name')
# #             student_list = list(students)  
# #             return Response({"message": "Đã gửi nhận dữ liệu.", "students": student_list}, status=status.HTTP_200_OK)

# #         except Device.DoesNotExist:
# #             return Response({"error": "Không tìm thấy thiết bị."}, status=status.HTTP_404_NOT_FOUND)

# #     def complete(self, request):
# #         return Response({"message": "Quá trình ghi RFID đã hoàn thành."}, status=status.HTTP_200_OK)

