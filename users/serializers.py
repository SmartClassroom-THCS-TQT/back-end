
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Account, Teacher, Admin, Student
from django_restql.mixins import DynamicFieldsMixin
from rooms_managements.serializers import SeatingSerializer
from managements.models import Room

class AccountSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)
    class Meta:
        model = Account
        fields = ['user_id','username', 'role']
        read_only_fields = ['user_id']

class TeacherSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Teacher
        fields = '__all__'



class AdminSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Admin
        fields = '__all__'



class StudentSerializer(DynamicFieldsMixin,serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)
    seating = SeatingSerializer(read_only=True)
    rooms = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=True)
    def update(self, instance, validated_data):
        rooms = validated_data.pop('rooms', None)
        instance = super().update(instance, validated_data)

        if rooms is not None:
            # Nếu bạn muốn thêm vào chứ không thay thế:
            instance.rooms.add(*rooms)

            # Nếu bạn muốn thay toàn bộ rooms (xoá cũ, thêm mới):
            # instance.rooms.set(rooms)

        return instance

    class Meta:
        model = Student
        fields = '__all__'



class ChangePasswordSerializer(DynamicFieldsMixin,serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
