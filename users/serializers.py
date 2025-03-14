
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Account, Teacher, Admin, Student

class AccountSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)
    class Meta:
        model = Account
        fields = ['user_id', 'email',  'role']
        read_only_fields = ['user_id']

class TeacherSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Teacher
        fields = '__all__'



class AdminSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Admin
        fields = '__all__'



class StudentSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Student
        fields = '__all__'



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
