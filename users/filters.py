import django_filters
from .models import Teacher, Admin, Student

class TeacherFilter(django_filters.FilterSet):
    user_id = django_filters.CharFilter(field_name='user__user_id', lookup_expr='icontains')  # Lọc theo user_id của CustomUser
    full_name = django_filters.CharFilter(field_name='user__full_name', lookup_expr='icontains')  # Lọc theo full_name của CustomUser
    active_status = django_filters.CharFilter(field_name='active_status', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')
    sex = django_filters.CharFilter(field_name='sex', lookup_expr='icontains')
    nation = django_filters.CharFilter(field_name='nation', lookup_expr='icontains')
    contract_types = django_filters.CharFilter(field_name='contract_types', lookup_expr='icontains')
    expertise_levels = django_filters.CharFilter(field_name='expertise_levels', lookup_expr='icontains')
    subjects = django_filters.CharFilter(field_name='subjects', lookup_expr='icontains')

    class Meta:
        model = Teacher
        fields = ['user_id', 'full_name', 'active_status', 'phone_number', 'sex', 'nation', 'contract_types', 'expertise_levels', 'subjects']


class AdminFilter(django_filters.FilterSet):
    user_id = django_filters.CharFilter(field_name='user__user_id', lookup_expr='icontains')  # Lọc theo user_id của CustomUser
    full_name = django_filters.CharFilter(field_name='user__full_name', lookup_expr='icontains')  # Lọc theo full_name của CustomUser
    active_status = django_filters.CharFilter(field_name='active_status', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')
    sex = django_filters.CharFilter(field_name='sex', lookup_expr='icontains')
    nation = django_filters.CharFilter(field_name='nation', lookup_expr='icontains')
    contract_types = django_filters.CharFilter(field_name='contract_types', lookup_expr='icontains')
    expertise_levels = django_filters.CharFilter(field_name='expertise_levels', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Admin
        fields = ['user_id', 'full_name', 'active_status', 'phone_number', 'sex', 'nation', 'contract_types', 'expertise_levels', 'description']


class StudentFilter(django_filters.FilterSet):
    user_id = django_filters.CharFilter(field_name='user__user_id', lookup_expr='icontains')  # Lọc theo user_id của CustomUser
    full_name = django_filters.CharFilter(field_name='user__full_name', lookup_expr='icontains')  # Lọc theo full_name của CustomUser
    active_status = django_filters.CharFilter(field_name='active_status', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')
    sex = django_filters.CharFilter(field_name='sex', lookup_expr='icontains')
    nation = django_filters.CharFilter(field_name='nation', lookup_expr='icontains')
    classroom = django_filters.CharFilter(field_name='classroom__name', lookup_expr='icontains')  # Lọc theo tên lớp (giả sử 'Room' có trường 'name')

    class Meta:
        model = Student
        fields = ['user_id', 'full_name', 'active_status', 'phone_number', 'sex', 'nation', 'classroom']
