import django_filters
from django.db.models import Q
from .models import Grade, GradeType

class GradeFilter(django_filters.FilterSet):
    student_id = django_filters.NumberFilter(field_name='student__id', lookup_expr='exact')
    student_name = django_filters.CharFilter(field_name='student__full_name', lookup_expr='icontains')
    subject = django_filters.CharFilter(field_name='subject__name', lookup_expr='icontains')
    semester = django_filters.NumberFilter(field_name='semester__id', lookup_expr='exact')
    grade_type = django_filters.CharFilter(field_name='grade_type__name', lookup_expr='icontains')
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte')
    date_assigned = django_filters.DateFromToRangeFilter(field_name='date_assigned')

    class Meta:
        model = Grade
        fields = ['student_id', 'student_name', 'subject', 'semester', 'grade_type', 'score_min', 'score_max', 'date_assigned']


class GradeTypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    weight_min = django_filters.NumberFilter(field_name='weight', lookup_expr='gte')
    weight_max = django_filters.NumberFilter(field_name='weight', lookup_expr='lte')
    is_global = django_filters.BooleanFilter(field_name='is_global')
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    room = django_filters.NumberFilter(field_name='room__id')

    class Meta:
        model = GradeType
        fields = ['name', 'weight_min', 'weight_max', 'is_global', 'created_by', 'room']
