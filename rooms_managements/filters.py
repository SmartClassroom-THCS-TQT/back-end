from django_filters import FilterSet, CharFilter, NumberFilter
from .models import Seating, Attendance, Device

class SeatingFilter(FilterSet):
    class Meta:
        model = Seating
        fields = {
            'room': ['exact'],
            'row': ['exact'],
            'column': ['exact']
        }

class AttendanceFilter(FilterSet):
    class Meta:
        model = Attendance
        fields = {
            'student': ['exact'],
            'session': ['exact'],
            'status': ['exact']
        }

class DeviceFilter(FilterSet):
    class Meta:
        model = Device
        fields = {
            'room': ['exact']
        } 