from django_filters import rest_framework as filters
from .models import *

class SessionFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='day', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='day', lookup_expr='lte')

    class Meta:
        model = Session
        fields = {
            'semester_code': ['exact'],
            'room_id': ['exact'],
            'teacher': ['exact'],
            'subject_code': ['exact'],
            'time_slot__code': ['exact'],
            'day': ['exact'],  # vẫn giữ nếu cần lọc đúng 1 ngày
        }

# Academic Year Filter
class AcademicYearFilter(filters.FilterSet):
    class Meta:
        model = AcademicYear
        fields = ['year_name']

# Semester Filter
class SemesterFilter(filters.FilterSet):
    academic_year__year_name = filters.CharFilter(field_name="academic_year__year_name", lookup_expr='icontains')

    class Meta:
        model = Semester
        fields = ['code', 'academic_year__year_name']

# Room Filter
class RoomFilter(filters.FilterSet):
    academic_year__year_name = filters.CharFilter(field_name="academic_year__year_name", lookup_expr='icontains')
    manager__account = filters.CharFilter(field_name="manager__account__user_id", lookup_expr='exact')
    students__account = filters.CharFilter(field_name="students__account__user_id", lookup_expr='exact')

    class Meta:
        model = Room
        fields = ['id', 'academic_year__year_name', 'manager__account', 'students__account']
# Subject Filter
class SubjectFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Subject
        fields = ['code', 'name']
# Time Slot Filter
class TimeSlotFilter(filters.FilterSet):
    start_time = filters.TimeFilter()
    end_time = filters.TimeFilter()

    class Meta:
        model = Time_slot
        fields = ['code', 'start_time', 'end_time']

# Teacher Assignment Filter
class TeacherAssignmentFilter(filters.FilterSet):
    semester_code__code = filters.CharFilter(field_name='semester_code__code', lookup_expr='exact')
    subject_code__code = filters.CharFilter(field_name='subject_code__code', lookup_expr='exact')
    room_id__id = filters.NumberFilter(field_name='room_id__id', lookup_expr='exact')
    teacher__account = filters.CharFilter(field_name='teacher__account__user_id', lookup_expr='exact')

    class Meta:
        model = Teacher_assignment
        fields = ['id', 'semester_code__code', 'subject_code__code', 'room_id__id', 'teacher__account']