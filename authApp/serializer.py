from .models import *
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'


class MyUserSerializer(UserSerializer):
    designation = DesignationSerializer(read_only=True, allow_null=True, required=False)
    facility = FacilitySerializer(read_only=True, allow_null=True, required=False)
    class Meta:
        model=Users
        fields = ['id', 'msisdn', 'email', 'f_name', 'l_name', 'designation', 'facility', "access_level"]
        
    def to_representation(self, value):
        data = super().to_representation(value)
        if data["access_level"] == 3:
            data.update({"facility": {"id": 3, "name": "N/A"}})
            data.update({"designation": {"id": 3, "name": "National User"}})
        elif data["access_level"] == 2:
            data.update({"facility": {"id": 2, "name": "N/A"}})
            data.update({"designation": {"id": 2, "name": "Implementing Partner"}})
        elif data["access_level"] == 5:
            data.update({"facility": {"id": 5, "name": "N/A"}})
            data.update({"designation": {"id": 5, "name": "Implementing Partner"}})

        return data


class MyUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = Users
        fields = ['id', 'msisdn', 'password', 'email', 'f_name', 'l_name', 'designation', 'facility', 'access_level']
