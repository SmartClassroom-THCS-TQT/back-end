from rest_framework import serializers
from .models import Document, DocumentType, Tag
from managements.models import Room, Subject
from users.models import Student  # assuming your custom student model is in users app
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class DocumentSerializer(serializers.ModelSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    document_type_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.all(), source='document_type', write_only=True
    )

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
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )

    file_extension = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'document_type', 'document_type_id',
            'file', 'file_extension',
            'description',
            'uploaded_by', 'date_uploaded',
            'rooms', 'subjects',
            'access_type', 'allowed_groups', 'allowed_users',
            'is_active', 'archived',
            'tags', 'tag_ids',
        ]
        read_only_fields = ['id', 'date_uploaded', 'uploaded_by', 'file_extension']

    def create(self, validated_data):
        tags = validated_data.pop('tag_ids', [])
        document = super().create(validated_data)
        if tags:
            document.tags.set(tags)
        return document

    def update(self, instance, validated_data):
        tags = validated_data.pop('tag_ids', None)
        document = super().update(instance, validated_data)
        if tags is not None:
            document.tags.set(tags)
        return document

    def validate(self, attrs):
        access_type = attrs.get('access_type', getattr(self.instance, 'access_type', None))
        if access_type == 'restricted':
            has_permissions = attrs.get('allowed_users') or attrs.get('allowed_groups')
            if not has_permissions:
                raise serializers.ValidationError(
                    "Tài liệu hạn chế phải chỉ định allowed_users hoặc allowed_groups."
                )
        return attrs
