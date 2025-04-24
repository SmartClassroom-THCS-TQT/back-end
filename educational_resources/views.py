from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentType, LessonPlan
from .serializers import (
    DocumentSerializer, DocumentTypeSerializer, LessonPlanSerializer
)
from .filters import DocumentFilter, LessonPlanFilter
from managements.models import Room, Subject
from users.models import Student
from django.contrib.auth.models import Group
from django.db import models

User = get_user_model()

class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentFilter

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Apply access control
        if not user.is_staff:
            queryset = queryset.filter(
                models.Q(access_type='public') |
                models.Q(allowed_users=user) |
                models.Q(allowed_groups__in=user.groups.all())
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_room(self, request, pk=None):
        document = self.get_object()
        room_id = request.data.get('room_id')
        if not room_id:
            return Response(
                {"error": "room_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room = get_object_or_404(Room, id=room_id)
        document.rooms.add(room)
        return Response({"status": "room added"})

    @action(detail=True, methods=['post'])
    def remove_room(self, request, pk=None):
        document = self.get_object()
        room_id = request.data.get('room_id')
        if not room_id:
            return Response(
                {"error": "room_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        room = get_object_or_404(Room, id=room_id)
        document.rooms.remove(room)
        return Response({"status": "room removed"})

    @action(detail=True, methods=['post'])
    def add_subject(self, request, pk=None):
        document = self.get_object()
        subject_id = request.data.get('subject_id')
        if not subject_id:
            return Response(
                {"error": "subject_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subject = get_object_or_404(Subject, id=subject_id)
        document.subjects.add(subject)
        return Response({"status": "subject added"})

    @action(detail=True, methods=['post'])
    def remove_subject(self, request, pk=None):
        document = self.get_object()
        subject_id = request.data.get('subject_id')
        if not subject_id:
            return Response(
                {"error": "subject_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subject = get_object_or_404(Subject, id=subject_id)
        document.subjects.remove(subject)
        return Response({"status": "subject removed"})

    @action(detail=True, methods=['post'])
    def add_user(self, request, pk=None):
        document = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(Student, id=user_id)
        document.allowed_users.add(user)
        return Response({"status": "user added"})

    @action(detail=True, methods=['post'])
    def remove_user(self, request, pk=None):
        document = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(Student, id=user_id)
        document.allowed_users.remove(user)
        return Response({"status": "user removed"})

    @action(detail=True, methods=['post'])
    def add_group(self, request, pk=None):
        document = self.get_object()
        group_id = request.data.get('group_id')
        if not group_id:
            return Response(
                {"error": "group_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        group = get_object_or_404(Group, id=group_id)
        document.allowed_groups.add(group)
        return Response({"status": "group added"})

    @action(detail=True, methods=['post'])
    def remove_group(self, request, pk=None):
        document = self.get_object()
        group_id = request.data.get('group_id')
        if not group_id:
            return Response(
                {"error": "group_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        group = get_object_or_404(Group, id=group_id)
        document.allowed_groups.remove(group)
        return Response({"status": "group removed"})

class LessonPlanViewSet(viewsets.ModelViewSet):
    queryset = LessonPlan.objects.all()
    serializer_class = LessonPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonPlanFilter

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Apply access control
        if not user.is_staff:
            queryset = queryset.filter(
                models.Q(access_type='public') |
                models.Q(allowed_users=user) |
                models.Q(allowed_groups__in=user.groups.all())
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        lesson_plan = self.get_object()
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff members can review lesson plans"},
                status=status.HTTP_403_FORBIDDEN
            )

        status = request.data.get('status')
        comment = request.data.get('comment', '')

        if not status:
            return Response(
                {"error": "status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        lesson_plan.status = status
        lesson_plan.review_comment = comment
        lesson_plan.reviewed_by = request.user
        lesson_plan.save()

        return Response({"status": "lesson plan reviewed"})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        lesson_plan = self.get_object()
        lesson_plan.archived = True
        lesson_plan.save()
        return Response({'status': 'archived'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        lesson_plan = self.get_object()
        lesson_plan.archived = False
        lesson_plan.save()
        return Response({'status': 'restored'})

    def destroy(self, request, *args, **kwargs):
        # Soft delete: set is_active=False
        lesson_plan = self.get_object()
        lesson_plan.is_active = False
        lesson_plan.save()
        return Response({'status': 'Lesson plan deleted (soft)'})
