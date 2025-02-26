from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from .models import *


class CustomUserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'phone_number', 'role']

    
class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Teacher
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Admin
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Student
        fields = '__all__'


        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

