from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView


from .serializer import *
from .models import *


@api_view(['GET'])
def facilities(request):
    if request.method == "GET":
        queryset = Facility.objects.all()
        serializer = FacilitySerializer(queryset, many=True)
        return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def designation(request):
    if request.method == "GET":
        queryset = Designation.objects.all()
        serializer = DesignationSerializer(queryset, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def current_user(request):
    if request.method == "GET":
        queryset = Users.objects.get(id=request.user.id)
        serializer = UserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
