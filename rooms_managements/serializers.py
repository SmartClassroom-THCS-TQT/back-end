from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin
from .models import *
from users.serializers import StudentSerializer

class SeatingSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    class Meta:
        model = Seating
        fields = '__all__'

class AttendanceSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class DeviceSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'