
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Grade, GradeType
from .serializers import GradeSerializer, GradeTypeSerializer
from .filters import GradeFilter, GradeTypeFilter  # Đã viết trước đó

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GradeFilter


class GradeTypeViewSet(viewsets.ModelViewSet):
    queryset = GradeType.objects.all()
    serializer_class = GradeTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GradeTypeFilter
