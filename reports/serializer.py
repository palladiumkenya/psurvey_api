from rest_framework import serializers

from authApp.serializer import *
from survey.models import Response, Answer, End_Questionnaire, Started_Questionnaire


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

    def to_representation(self, value):
        data = super().to_representation(value)
        data.update({'facility': data['facility']['name']})
        data.update({'designation': data['designation']['name']})
        data.update({'cs': End_Questionnaire.objects.filter(session__started_by=data['id']).count()})
        return data


class ResponsesSerilizer(serializers.ModelSerializer):
    class Meta:
        model=Response
        fields = '__all__'


class PatientSer(serializers.ModelSerializer):
    class Meta:
        model=Started_Questionnaire
        fields = '__all__'

    def to_representation(self, value):
        data = super().to_representation(value)
        resp = Response.objects.filter(session=data['id']).order_by('-created_at')

        data.update({'responses': ResponsesSerilizer(resp, many=True).data})

        return data
