from .models import *
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = '__all__'
