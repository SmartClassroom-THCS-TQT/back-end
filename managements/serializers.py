# serializers.py
from rest_framework import serializers
from .models import *
from users.models import Student,Teacher

class ManagerSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='account.user_id')  # ✅ Lấy user_id từ CustomUser
    class Meta:
        model = Teacher
        fields = ['user_id', 'full_name', 'image']  # ✅ Trả về object chứa 3 trường này

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'
 
class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['academic_year','code', 'start_date', 'weeks_count', 'end_date']

class RoomSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(read_only=True)
    class Meta:
        model = Room
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ClassTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time_slot
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
class TeacherAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher_assignment
        fields = '__all__'


