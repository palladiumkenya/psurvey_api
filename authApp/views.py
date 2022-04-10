from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response as Res
from rest_framework.views import APIView
from datetime import date

from .forms import LoginForm
from .serializer import *
from .models import *
from survey.models import *


def informed(request):
    return render(request, 'informed.html')


def privacy(request):
    return render(request, 'privacy.html')


# api
@api_view(['GET'])
def facilities(request):
    if request.method == "GET":
        queryset = Facility.objects.all()
        serializer = FacilitySerializer(queryset, many=True)
        return Res(data={"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def counties(request):
    if request.method == "GET":
        queryset = Facility.objects.all().distinct('county')
        serializer = FacilitySerializer(queryset, many=True)
        return Res(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def facility_single(request):
    if request.method == "POST":
        queryset = Facility.objects.get(id=request.data['id'])
        serializer = FacilitySerializer(queryset)
        return Res(data={"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def designation(request):
    if request.method == "GET":
        queryset = Designation.objects.all()
        serializer = DesignationSerializer(queryset, many=True)
        return Res({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.method == "GET":
        queryset = Users.objects.get(id=request.user.id)
        serializer = MyUserSerializer(queryset)
        aq = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id,
                                                   questionnaire__is_active=True,
                                                   questionnaire__active_till__gte=date.today()).count()
        cs = End_Questionnaire.objects.filter(session__started_by=request.user).count()
        return Res({'user': serializer.data, 'Active_questionnaires': aq, 'Completed_surveys': cs},
                   status=status.HTTP_200_OK)
