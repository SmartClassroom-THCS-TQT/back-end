import subprocess
import os
from datetime import datetime
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth import authenticate
from .models import DeploymentLog
from .serializers import (
    DeploymentLogSerializer,
    DeploySerializer,
    SwitchEnvSerializer,
    RestartSerializer
)

class DeploymentViewSet(viewsets.ViewSet):
    authentication_classes = [BasicAuthentication]
    
    def get_permissions(self):
        if self.action == 'status':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

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

    def _get_git_info(self):
        info = {}
        
        # Get commit hash
        success, commit_hash = self._run_command('git rev-parse HEAD')
        info['commit_hash'] = commit_hash.strip() if success else 'Unknown'
        
        # Get commit message
        success, commit_message = self._run_command('git log -1 --pretty=%B')
        info['commit_message'] = commit_message.strip() if success else 'Unknown'
        
        # Get commit date
        success, commit_date = self._run_command('git log -1 --pretty=%cd')
        info['commit_date'] = commit_date.strip() if success else 'Unknown'
        
        # Get author
        success, author = self._run_command('git log -1 --pretty=%an')
        info['author'] = author.strip() if success else 'Unknown'
        
        # Get branch
        success, branch = self._run_command('git rev-parse --abbrev-ref HEAD')
        info['branch'] = branch.strip() if success else 'Unknown'
        
        # Get version from git tags
        success, version = self._run_command('git describe --tags --abbrev=0')
        if not success:
            # Try to get version from VERSION file
            version_file = os.path.join(settings.BASE_DIR, 'VERSION')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    version = f.read().strip()
            else:
                version = 'Unknown'
        info['version'] = version.strip() if version != 'Unknown' else version
        
        return info

    def _get_service_status(self):
        services = {}
        
        # Get nginx status
        success, nginx_status = self._run_command('systemctl is-active nginx')
        services['nginx'] = {
            'status': nginx_status.strip() if success else 'Unknown',
            'uptime': self._get_service_uptime('nginx'),
            'version': self._get_service_version('nginx')
        }
        
        # Get gunicorn status
        success, gunicorn_status = self._run_command('systemctl is-active gunicorn')
        services['gunicorn'] = {
            'status': gunicorn_status.strip() if success else 'Unknown',
            'uptime': self._get_service_uptime('gunicorn'),
            'version': self._get_service_version('gunicorn')
        }
        
        return services

    def _get_service_uptime(self, service):
        success, uptime = self._run_command(f'systemctl show {service} -p ActiveEnterTimestamp')
        if success:
            try:
                timestamp = uptime.split('=')[1].strip()
                return timestamp
            except:
                return 'Unknown'
        return 'Unknown'

    def _get_service_version(self, service):
        if service == 'nginx':
            success, version = self._run_command('nginx -v')
        elif service == 'gunicorn':
            success, version = self._run_command('gunicorn --version')
        else:
            return 'Unknown'
        
        if success:
            try:
                return version.strip()
            except:
                return 'Unknown'
        return 'Unknown'

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

        try:
            # Chạy script deploy-backend.sh
            success, output = self._run_command('bash /home/minhtien/back-end/deploy-backend.sh')
            
            if not success:
                log.status = 'failed'
                log.message = f'Deployment failed: {output}'
                log.save()
                return Response({'error': output}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            log.status = 'success'
            log.message = 'Deployment completed successfully'
            log.completed_at = datetime.now()
            log.save()

            return Response({
                'message': 'Deployment completed successfully',
                'details': output
            })

        except Exception as e:
            log.status = 'failed'
            log.message = f'Deployment failed with error: {str(e)}'
            log.save()
            return Response(
                {'error': f'Deployment failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        # Get git information
        git_info = self._get_git_info()
        
        # Get service status
        services = self._get_service_status()
        
        # Get latest deployment
        latest_deployment = DeploymentLog.objects.order_by('-created_at').first()
        deployment_info = None
        if latest_deployment:
            deployment_info = {
                'action': latest_deployment.action,
                'status': latest_deployment.status,
                'message': latest_deployment.message,
                'created_at': latest_deployment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'completed_at': latest_deployment.completed_at.strftime('%Y-%m-%d %H:%M:%S') if latest_deployment.completed_at else None,
                'created_by': latest_deployment.created_by.username if latest_deployment.created_by else None
            }

        return Response({
            'application': {
                'name': 'Smart Classroom Backend',
                'version': git_info['version'],
                'environment': os.getenv('DJANGO_ENV', 'development'),
                'last_updated': git_info['commit_date']
            },
            'git': {
                'branch': git_info['branch'],
                'commit': {
                    'hash': git_info['commit_hash'],
                    'message': git_info['commit_message'],
                    'author': git_info['author'],
                    'date': git_info['commit_date']
                }
            },
            'services': services,
            'latest_deployment': deployment_info,
            'server': {
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'Unknown',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': settings.TIME_ZONE
            }
        }) 