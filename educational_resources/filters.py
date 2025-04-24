from django_filters import rest_framework as filters
from .models import Document, LessonPlan
from django.db import models

class BaseDocumentFilter(filters.FilterSet):
    room_id = filters.NumberFilter(field_name='rooms__id')
    subject_id = filters.NumberFilter(field_name='subjects__id')
    is_active = filters.BooleanFilter()
    archived = filters.BooleanFilter()
    access_type = filters.CharFilter()

    class Meta:
        model = None
        fields = ['room_id', 'subject_id', 'is_active', 'archived', 'access_type']

class DocumentFilter(BaseDocumentFilter):
    document_type_id = filters.NumberFilter(field_name='document_type__id')

    class Meta(BaseDocumentFilter.Meta):
        model = Document
        fields = BaseDocumentFilter.Meta.fields + ['document_type_id']

class LessonPlanFilter(BaseDocumentFilter):
    status = filters.CharFilter()

    class Meta(BaseDocumentFilter.Meta):
        model = LessonPlan
        fields = BaseDocumentFilter.Meta.fields + ['status'] 