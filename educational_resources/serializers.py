from rest_framework import serializers
from .models import Document, DocumentType, LessonPlan
from managements.models import Room, Subject
from users.models import Student
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'description']


class BaseDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    allowed_groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False
    )
    allowed_users = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), many=True, required=False
    )
    rooms = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), many=True, required=False
    )
    subjects = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), many=True, required=False
    )
    file_extension = serializers.ReadOnlyField()

    class Meta:
        fields = [
            'id',
            'title',
            'file', 'file_extension',
            'description',
            'uploaded_by', 'date_uploaded',
            'rooms', 'subjects',
            'access_type', 'allowed_groups', 'allowed_users',
            'is_active', 'archived'
        ]
        read_only_fields = ['id', 'date_uploaded', 'uploaded_by', 'file_extension']

    def create(self, validated_data):
        document = super().create(validated_data)
        return document

    def update(self, instance, validated_data):
        document = super().update(instance, validated_data)
        return document

    def validate(self, attrs):
        access_type = attrs.get('access_type', getattr(self.instance, 'access_type', None))
        if access_type == 'restricted':
            has_permissions = attrs.get('allowed_users') or attrs.get('allowed_groups')
            if not has_permissions:
                raise serializers.ValidationError(
                    "Restricted documents must specify allowed_users or allowed_groups."
                )
        return attrs


class DocumentSerializer(BaseDocumentSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    document_type_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.all(), source='document_type', write_only=True
    )

    class Meta(BaseDocumentSerializer.Meta):
        model = Document
        fields = BaseDocumentSerializer.Meta.fields + ['document_type', 'document_type_id']


class LessonPlanSerializer(BaseDocumentSerializer):
    reviewed_by = serializers.StringRelatedField(read_only=True)

    class Meta(BaseDocumentSerializer.Meta):
        model = LessonPlan
        fields = BaseDocumentSerializer.Meta.fields + [
            'status',
            'reviewed_by', 'review_date', 'review_comment'
        ]
        read_only_fields = BaseDocumentSerializer.Meta.read_only_fields + ['reviewed_by', 'review_date']
