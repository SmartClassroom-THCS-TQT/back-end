# serializers.py
from rest_framework import serializers
from .models import *

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['name', 'start_date', 'weeks_count', 'end_date']
