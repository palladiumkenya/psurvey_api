from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from psycopg2._psycopg import IntegrityError
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
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.method == "GET":
        queryset = Users.objects.get(id=request.user.id)
        serializer = MyUserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


def web_login (request):

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


@login_required
def facility_partner_list (request):
    user = request.user
    partner = Partner.objects.all()
    context = {
        'u': user,
        'partner': partner
    }
    return render(request, 'authApp/partner_facility_list.html', context)


@login_required
def facility_partner_link (request):
    user = request.user
    par_fac = Partner_Facility.objects.all()
    facilities = Facility.objects.all().exclude(id__in=par_fac.values_list('facility_id', flat=True))

    if request.method == 'POST':
        fac = request.POST.getlist('facility')
        partner = request.POST.get('partner-user')

        try:
            for i in fac:
                p_user = Partner_Facility.objects.create(facility_id=i, created_by=user, partner_id=partner)
                p_user.save()
        except IntegrityError:
            return HttpResponse("error")

    partner_users = Partner.objects.filter(user__access_level_id=2)
    context = {
        'u': user,
        'fac': facilities,
        'p_users':partner_users,
    }
    return render(request, 'authApp/new_partner_link.html', context)


@login_required
def register_partner (request):
    u = request.user
    facilities = Facility.objects.all()
    if request.method == 'POST':
        trans_one = transaction.savepoint()
        f_name = request.POST.get('f_name')
        l_name = request.POST.get('l_name')
        email = request.POST.get('email')
        msisdn = request.POST.get('msisdn')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        partner = request.POST.get('partner')
        if password != re_password:
            return HttpResponse("Password error")
        user = Users.objects.create_user(msisdn=msisdn, password=password, email=email)
        user.f_name = f_name
        user.l_name = l_name
        user.access_level_id = 2
        print(user.id)
        user.save()
        try:
            if user.pk:
                admin = Partner.objects.create(name=partner, user=user, created_by=u)
                admin.save()
        except IntegrityError:
                transaction.savepoint_rollback(trans_one)
                return HttpResponse("error")

    partner_users = Partner.objects.filter(user__access_level_id=2)
    for p in partner_users:
        print(p.user)
    context = {
        'u': u,
        'fac': facilities,
        'p_users':partner_users,
    }
    return render(request, 'authApp/new_partner_link.html', context)


@login_required
def profile (request):
    u = request.user
    context = {
        'u': u,
    }
    return  render(request, 'authApp/profile.html', context)

def logout_request(request):
    logout(request)
    messages.info(request, "User is logged out", fail_silently=True)
    return redirect('web-login')
