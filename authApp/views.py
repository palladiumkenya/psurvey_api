from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import LoginForm
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
        serializer = MyUserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

def home(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            user = authenticate(username=clean['msisdn'], password=clean['password'])
            print(user)
            if user is not None:
                if user.is_active:
                    if user.access_level.id != 1:
                        login(request, user)
                        return HttpResponse('/web/dashboard')
                    else:
                        return HttpResponse('Not an admin')
                # else:
                #     return render(request, "authApp/login.html", {'form': form})
                else:
                    return HttpResponse('Account is Disabled')
            else:
                return HttpResponse("invalid credentials")
    else:
        form = LoginForm()
    return render(request, "authApp/login.html", {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, "User is logged out", fail_silently=True)
    return redirect('web-login')
