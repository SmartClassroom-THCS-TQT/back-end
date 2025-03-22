from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentType, Tag
from .serializers import DocumentSerializer, DocumentTypeSerializer, TagSerializer

class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name', 'description']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name']


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'access_type', 'archived', 'is_active', 'rooms', 'subjects', 'tags']
    search_fields = ['title', 'description']
    ordering_fields = ['date_uploaded', 'title']
    ordering = ['-date_uploaded']

    def get_queryset(self):
        user = self.request.user

        base_qs = Document.objects.filter(is_active=True)

        if user.is_superuser:
            return base_qs

        # Restricted documents - show only allowed
        return base_qs.filter(
            access_type='public'
        ) | base_qs.filter(
            access_type='restricted',
            allowed_users__user=user
        ) | base_qs.filter(
            access_type='restricted',
            allowed_groups__in=user.groups.all()
        )

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def archive(self, request, pk=None):
        doc = self.get_object()
        doc.archived = True
        doc.save()
        return Response({'status': 'Document archived'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def restore(self, request, pk=None):
        doc = self.get_object()
        doc.archived = False
        doc.save()
        return Response({'status': 'Document restored'})

    def destroy(self, request, *args, **kwargs):
        # Soft delete: set is_active=False
        document = self.get_object()
        document.is_active = False
        document.save()
        return Response({'status': 'Document deleted (soft)'})
