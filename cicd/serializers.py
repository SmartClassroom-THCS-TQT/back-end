from rest_framework import serializers
from .models import DeploymentLog

class DeploymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentLog
        fields = ['id', 'action', 'status', 'message', 'created_by', 'created_at', 'completed_at']
        read_only_fields = ['created_by', 'created_at', 'completed_at']

class DeploySerializer(serializers.Serializer):
    branch = serializers.CharField(max_length=100, required=False, default='main')

class SwitchEnvSerializer(serializers.Serializer):
    environment = serializers.ChoiceField(choices=['dev', 'prod'])

class RestartSerializer(serializers.Serializer):
    services = serializers.MultipleChoiceField(
        choices=['nginx', 'gunicorn', 'all'],
        required=True
    ) 