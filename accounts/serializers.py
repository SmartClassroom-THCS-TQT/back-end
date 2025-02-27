
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Teacher, Admin, Student

class CustomUserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'phone_number', 'role', 'full_name', 'sex', 'day_of_birth', 'nation', 'active_status']
        read_only_fields = ['user_id']

class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Teacher
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user')  # Không còn là dict, chỉ là object
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

class AdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Admin
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user')
        admin = Admin.objects.create(user=user, **validated_data)
        return admin

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Student
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user')
        student = Student.objects.create(user=user, **validated_data)
        return student

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
