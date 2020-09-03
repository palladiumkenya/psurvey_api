import requests

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from .models import *
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = Users
        fields = ['id', 'msisdn', 'password', 'designation', 'facility', 'email', 'f_name', 'l_name']


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'
