
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Grade, GradeType
from .serializers import GradeSerializer, GradeTypeSerializer
from .filters import GradeFilter, GradeTypeFilter  # Đã viết trước đó
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

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


class GradeDistributionAPIView(APIView):
    def get(self, request):
        # Dùng bộ lọc để lọc theo các tham số GET
        grades = Grade.objects.all()
        filterset = GradeFilter(request.GET, queryset=grades)

        if filterset.is_valid():
            grades = filterset.qs
        else:
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        # Tạo bins: [(0.0, 0.5), (0.5, 1.0), ..., (9.5, 10.0)]
        bins = [(Decimal(i) / 2, Decimal(i + 1) / 2) for i in range(20)]
        distribution = [0] * 20

        for grade in grades:
            if grade.score is None:
                continue
            for i, (start, end) in enumerate(bins):
                if start <= grade.score < end or (i == 19 and grade.score == end):
                    distribution[i] += 1
                    break

        return Response(distribution, status=status.HTTP_200_OK)