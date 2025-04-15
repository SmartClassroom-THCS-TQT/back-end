from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin
from .models import *
from users.models import Student
from managements.models import Session
from rest_framework.exceptions import ValidationError

class StudentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class SessionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = '__all__'


class SeatingSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Seating
        fields = '__all__'

# class AttendanceSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
#     student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
#     session = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all())

#     class Meta:
#         model = Attendance
#         fields = '__all__'
# trường hợp khi thêm attribute cho GET mà bị lỗi POST thì sẽ tạo ra 2 attribute khác nhau
class AttendanceSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    # Sử dụng PrimaryKeyRelatedField để gửi ID cho POST
    student_account = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),source='student')
    session_id = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all(),source='session')

    # Sử dụng StudentSerializer và SessionSerializer để đọc dữ liệu cho GET
    student = StudentSerializer(read_only=True)
    session = SessionSerializer(read_only=True)
    def create(self, validated_data):
        student = validated_data['student']
        session = validated_data['session']

        if Attendance.objects.filter(student=student, session=session).exists():
            raise ValidationError({"detail": "You have already checked in."})  # ✅ DRF hiểu và trả về JSON 400

        return Attendance.objects.create(**validated_data)
    class Meta:
        model = Attendance
        fields = '__all__'


class DeviceSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'