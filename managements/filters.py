import django_filters
from .models import Session

class SessionFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='day', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='day', lookup_expr='lte')

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
