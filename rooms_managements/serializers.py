from rest_framework import serializers
from .models import Seating

class SeatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seating
        fields = ('student', 'room', 'row', 'column')

    # Tùy chỉnh để lấy tên đầy đủ của sinh viên thay vì chỉ ID
    student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = Seating
        fields = ('student', 'student_full_name', 'room', 'room_name', 'row', 'column')

