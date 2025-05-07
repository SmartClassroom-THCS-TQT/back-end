import subprocess
import os
from datetime import datetime
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from .models import DeploymentLog
from .serializers import (
    DeploymentLogSerializer,
    DeploySerializer,
    SwitchEnvSerializer,
    RestartSerializer
)

class DeploymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def _create_log(self, action, status, message, user):
        return DeploymentLog.objects.create(
            action=action,
            status=status,
            message=message,
            created_by=user
        )

    def _run_command(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, str(e)

    @action(detail=False, methods=['post'])
    def deploy(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Only superusers can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DeploySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        branch = serializer.validated_data['branch']
        log = self._create_log('deploy', 'in_progress', f'Starting deployment from branch {branch}', request.user)

        # Pull latest code
        success, output = self._run_command(f'git pull origin {branch}')
        if not success:
            log.status = 'failed'
            log.message = f'Failed to pull code: {output}'
            log.save()
            return Response({'error': output}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Install requirements
        success, output = self._run_command('pip install -r requirements.txt')
        if not success:
            log.status = 'failed'
            log.message = f'Failed to install requirements: {output}'
            log.save()
            return Response({'error': output}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Run migrations
        success, output = self._run_command('python manage.py migrate')
        if not success:
            log.status = 'failed'
            log.message = f'Failed to run migrations: {output}'
            log.save()
            return Response({'error': output}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Restart services
        success, output = self._run_command('sudo systemctl restart gunicorn')
        if not success:
            log.status = 'failed'
            log.message = f'Failed to restart gunicorn: {output}'
            log.save()
            return Response({'error': output}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        log.status = 'success'
        log.message = 'Deployment completed successfully'
        log.completed_at = datetime.now()
        log.save()

        return Response({'message': 'Deployment completed successfully'})

    @action(detail=False, methods=['post'])
    def switch_env(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Only superusers can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SwitchEnvSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        environment = serializer.validated_data['environment']
        log = self._create_log('switch_env', 'in_progress', f'Switching to {environment} environment', request.user)

        # Run the switch environment script
        success, output = self._run_command(f'./switch_env.sh {environment}')
        if not success:
            log.status = 'failed'
            log.message = f'Failed to switch environment: {output}'
            log.save()
            return Response({'error': output}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        log.status = 'success'
        log.message = f'Successfully switched to {environment} environment'
        log.completed_at = datetime.now()
        log.save()

        return Response({'message': f'Successfully switched to {environment} environment'})

    @action(detail=False, methods=['post'])
    def restart(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Only superusers can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RestartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        services = serializer.validated_data['services']
        log = self._create_log('restart', 'in_progress', f'Restarting services: {services}', request.user)

        commands = []
        if 'all' in services or 'nginx' in services:
            commands.append('sudo systemctl restart nginx')
        if 'all' in services or 'gunicorn' in services:
            commands.append('sudo systemctl restart gunicorn')

        for command in commands:
            success, output = self._run_command(command)
            if not success:
                log.status = 'failed'
                log.message = f'Failed to restart services: {output}'
                log.save()
                return Response({'error': output}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        log.status = 'success'
        log.message = 'Services restarted successfully'
        log.completed_at = datetime.now()
        log.save()

        return Response({'message': 'Services restarted successfully'})

    @action(detail=False, methods=['get'])
    def status(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Only superusers can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get git version
        success, git_version = self._run_command('git rev-parse HEAD')
        if not success:
            git_version = 'Unknown'

        # Get service status
        success, nginx_status = self._run_command('systemctl is-active nginx')
        success, gunicorn_status = self._run_command('systemctl is-active gunicorn')

        # Get latest deployment
        latest_deployment = DeploymentLog.objects.order_by('-created_at').first()
        deployment_status = DeploymentLogSerializer(latest_deployment).data if latest_deployment else None

        return Response({
            'git_version': git_version,
            'services': {
                'nginx': nginx_status.strip(),
                'gunicorn': gunicorn_status.strip()
            },
            'latest_deployment': deployment_status
        }) 