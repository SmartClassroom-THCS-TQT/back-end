# serializers.py
from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin
from users.serializers import *

from .models import *
from users.models import Student,Teacher

class ManagerSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    user_id = serializers.CharField(source='account.user_id')  # ✅ Lấy user_id từ CustomUser
    class Meta:
        model = Teacher
        fields = ['user_id', 'full_name', 'image']  # ✅ Trả về object chứa 3 trường này

class AcademicYearSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'
 
class SemesterSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

class RoomSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    manager = ManagerSerializer()
    students = StudentSerializer(many=True)
    academic_year = AcademicYearSerializer()

    class Meta:
        model = Room
        fields = '__all__'
class RoomWriteSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True,required=False)
    academic_year = serializers.PrimaryKeyRelatedField(queryset=AcademicYear.objects.all())

    class Meta:
        model = Room
        fields = '__all__'
class SubjectSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class TimeSlotSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Time_slot
        fields = '__all__'

class SessionSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    semester_code = SemesterSerializer()
    teacher = TeacherSerializer() 
    room_id = RoomSerializer()
    subject_code = SubjectSerializer()
    time_slot = TimeSlotSerializer()
    class Meta:
        model = Session
        fields = '__all__'

class TeacherAssignmentSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    semester_code = SemesterSerializer()
    subject_code = SubjectSerializer()
    room_id = RoomSerializer()
    teacher = TeacherSerializer()
    class Meta:
        model = Teacher_assignment
        fields = '__all__'


