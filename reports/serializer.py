from rest_framework import serializers

from authApp.serializer import *
from survey.models import Response, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class RespSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Response
        fields = '__all__'


class AllUserSerializer(serializers.ModelSerializer):
    designation = DesignationSerializer(read_only=True)
    facility = FacilitySerializer(read_only=True)
    class Meta:
        model=Users
        fields = '__all__'
