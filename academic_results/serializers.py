from rest_framework import serializers
from .models import Grade, GradeType

class GradeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeType
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'
