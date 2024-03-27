from re import A
from django.http import HttpResponse
from django.db import transaction
from django.db import connection
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

# holder to check app health


def home(request):
    return HttpResponse(status.HTTP_200_OK)


def informed(request):
    return render(request, 'authApp/informed.html')


def privacy(request):
    return render(request, 'authApp/privacy.html')


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


@api_view(['POST'])
def forgot_password(request):
    if request.method == 'POST':
        email = request.data['email']
        msisdn = request.data['msisdn']
        password = request.data['password']

        user_rec = Users.objects.filter(email=email, msisdn=msisdn)
        if user_rec.exists():
            trans_one = transaction.savepoint()
            user = user_rec[0]
            try:
                # create the user with the changed password
                msisdn_ = f"{msisdn}_"
                email_ = f"{email}_"
                new_user = Users.objects.create_user(
                    msisdn=msisdn_, password=password, email=email_)

                # upate the user record with the new password
                user.password = new_user.password
                user.save()

                # delete the new user record
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM \"User\" WHERE id = %s ", [new_user.id])

                return Res({"success": True, "message": "Password changed successfully"}, status.HTTP_200_OK)

            except IntegrityError:
                transaction.savepoint_rollback(trans_one)
                return Res({'success': False, 'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                transaction.savepoint_rollback(trans_one)
                return Res({'success': False, 'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Res({'success': False, 'message': 'invalid details'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_nishauri(request, q_mfl_code, q_ccc_no):
    if request.method == "GET":
        queryset = Users.objects.get(id=request.user.id)
        serializer = MyUserSerializer(queryset)

        fac = Facility.objects.get(mfl_code=q_mfl_code)
        quest = Facility_Questionnaire.objects.filter(facility_id__in=Facility.objects.filter(
            mfl_code=q_mfl_code).values_list('id', flat=True))

        aq = Questionnaire.objects.filter(id__in=quest.values_list('questionnaire_id', flat=True), is_active=True, is_published=True, target_app='Patient', active_till__gte=date.today()).exclude(
            id__in=End_Questionnaire.objects.filter(session_id__in=Started_Questionnaire.objects.filter(
                ccc_number=q_ccc_no).values_list('id', flat=True)).values_list('questionnaire_id', flat=True)
        ).count()

        # aq = Questionnaire.objects.filter(is_active=True, is_published=True, target_app='Patient', active_till__gte=date.today()).order_by('-created_at').count()

        serializer.data.update(
            {"designation": {"id": 6, "name": "Nishauri User"}})
        serializer.data.update({"facility": {"id": fac.id, "name": fac.name}})

        cs = End_Questionnaire.objects.filter(session_id__in=Started_Questionnaire.objects.filter(
            ccc_number=q_ccc_no).values_list('id', flat=True)).count()

        return Res({'user': serializer.data, 'Active_questionnaires': aq, 'Completed_surveys': cs},
                   status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.method == "GET":
        queryset = Users.objects.get(id=request.user.id)
        serializer = MyUserSerializer(queryset)
        if request.user.access_level.id == 1:
            aq = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id,
                                                       questionnaire__is_active=True,
                                                       questionnaire__is_published=True,
                                                       questionnaire__target_app='Facility',
                                                       questionnaire__active_till__gte=date.today()).count()

        elif request.user.access_level.id == 2:
            fac = Partner_Facility.objects.filter(
                partner__in=Partner_User.objects.filter(user=request.user).values_list('name', flat=True))
            aq = Facility_Questionnaire.objects.filter(facility_id__in=fac.values_list('facility_id', flat=True),
                                                       questionnaire__is_active=True,
                                                       questionnaire__is_published=True,
                                                       questionnaire__target_app='Facility',
                                                       questionnaire__active_till__gte=date.today()).count()
            serializer.data.update(
                {"designation": {"id": 2, "name": "Implementing Partner"}})
            serializer.data.update({"facility": {"id": 2, "name": Partner.objects.get(
                id=Partner_User.objects.get(user=request.user).name).name}})
        elif request.user.access_level.id == 3:
            aq = Questionnaire.objects.filter(
                is_active=True, is_published=True, active_till__gte=date.today()).order_by('-created_at').count()
            serializer.data.update(
                {"designation": {"id": 3, "name": "National User"}})
            serializer.data.update({"facility": {"id": 2, "name": "N/A"}})
        elif request.user.access_level.id == 4:
            q = Facility_Questionnaire.objects.filter(
                facility_id=request.user.facility.id).values_list('questionnaire_id').distinct()
            aq = Questionnaire.objects.filter(id__in=q, is_active=True, is_published=True,
                                              target_app='Facility', active_till__gte=date.today()).order_by('-created_at').count()
            serializer.data.update(
                {"designation": {"id": 2, "name": "Facility User"}})
        elif request.user.access_level.id == 5:
            fac = Partner_Facility.objects.filter(
                partner__in=Partner_User.objects.filter(user=request.user).values_list('name', flat=True))
            q = Facility_Questionnaire.objects.filter(facility_id__in=fac.values_list('facility_id', flat=True)
                                                      ).values_list('questionnaire_id').distinct()
            aq = Questionnaire.objects.filter(id__in=q, is_active=True, is_published=True,
                                              target_app='Facility', active_till__gte=date.today()).order_by('-created_at').count()
            serializer.data.update(
                {"designation": {"id": 5, "name": "Implementing Partner"}})
            serializer.data.update({"facility": {"id": 2, "name": Partner.objects.get(
                id=Partner_User.objects.get(user=request.user).name).name}})
        elif request.user.access_level.id == 6:
            aq = Questionnaire.objects.filter(
                is_active=True, is_published=True, target_app='Patient', active_till__gte=date.today()).order_by('-created_at').count()
            serializer.data.update(
                {"designation": {"id": 6, "name": "Nishauri User"}})
            serializer.data.update({"facility": {"id": 2, "name": "N/A"}})

        cs = End_Questionnaire.objects.filter(
            session__started_by=request.user).count()
        return Res({'user': serializer.data, 'Active_questionnaires': aq, 'Completed_surveys': cs},
                   status=status.HTTP_200_OK)
