from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin
from .models import *
from users.models import Student
from managements.models import Session

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

class AttendanceSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    student = StudentSerializer()
    session = SessionSerializer()
    class Meta:
        model = Attendance
        fields = '__all__'

class DeviceSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'