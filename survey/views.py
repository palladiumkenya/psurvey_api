import json
import requests
from datetime import date

# from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers import serialize
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.db.models.functions import Cast, TruncMonth
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from docutils.nodes import status
from rest_framework import status
from rest_framework.response import Response as Res
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializer import *
from authApp.serializer import *


# api

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def questionnaire_participants(request):
    if request.method == "GET":
        queryset = Questionnaire_Participants.objects.all()
        serializer = QuestionnaireParticipantsSerializer(queryset, many=True)
        return Res(data={"data": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_questionnaire_api(request):
    if request.user.access_level.id == 1:
            q = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id).values_list('questionnaire_id').distinct()
            quest = Questionnaire.objects.filter(id__in=q).order_by('-created_at')
    elif request.user.access_level.id == 2:
        fac = Partner_Facility.objects.filter(
            partner__in=Partner_User.objects.filter(user=request.user).values_list('name', flat=True))
        q = Facility_Questionnaire.objects.filter(facility_id__in=fac.values_list('facility_id', flat=True)
                                                    ).values_list('questionnaire_id').distinct()
        quest = Questionnaire.objects.filter(id__in=q).order_by('-created_at')
    elif request.user.access_level.id == 3:
        quest = Questionnaire.objects.filter().order_by('-created_at')
    elif request.user.access_level.id == 4:
            q = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id).values_list('questionnaire_id').distinct()
            quest = Questionnaire.objects.filter(id__in=q).order_by('-created_at')
    elif request.user.access_level.id == 5:
        fac = Partner_Facility.objects.filter(
            partner__in=Partner_User.objects.filter(user=request.user).values_list('name', flat=True))
        q = Facility_Questionnaire.objects.filter(facility_id__in=fac.values_list('facility_id', flat=True)
                                                    ).values_list('questionnaire_id').distinct()
        quest = Questionnaire.objects.filter(id__in=q).order_by('-created_at')
        
    serializer = QuestionnaireSerializer(quest, many=True)
    
    return Res({"data": serializer.data}, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_questionnaire_api(request):
    if request.user.access_level.id == 1:
        quest = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id)

        queryset = Questionnaire.objects.filter(id__in=quest.values_list('questionnaire_id', flat=True), is_active=True,
                                            active_till__gte=date.today())
    elif request.user.access_level.id == 2:
        fac = Partner_Facility.objects.filter(
            partner__in=Partner_User.objects.filter(user=request.user).values_list('name', flat=True))
        q = Facility_Questionnaire.objects.filter(facility_id__in=fac.values_list('facility_id', flat=True)
                                                    ).values_list('questionnaire_id').distinct()
        queryset = Questionnaire.objects.filter(id__in=q, is_active=True,
                                            active_till__gte=date.today()).order_by('-created_at')
    elif request.user.access_level.id == 3:
        queryset = Questionnaire.objects.filter(is_active=True, active_till__gte=date.today()).order_by('-created_at')
    elif request.user.access_level.id == 4:
        q = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id).values_list('questionnaire_id').distinct()
        queryset = Questionnaire.objects.filter(id__in=q, is_active=True, active_till__gte=date.today()).order_by('-created_at')
    elif request.user.access_level.id == 5:
        fac = Partner_Facility.objects.filter(
            partner__in=Partner_User.objects.filter(user=request.user).values_list('name', flat=True))
        q = Facility_Questionnaire.objects.filter(facility_id__in=fac.values_list('facility_id', flat=True)
                                                    ).values_list('questionnaire_id').distinct()
        queryset = Questionnaire.objects.filter(id__in=q, is_active=True, active_till__gte=date.today()).order_by('-created_at')
    
    serializer = QuestionnaireSerializer(queryset, many=True)
    return Res({"data": serializer.data}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def all_question_api(request):
    quest = Question.objects.filter(questionnaire_id=request.data['questionnaire_id']).order_by('question_order')
    serializer = QuestionSerializer(quest, many=True)

    return Res({"data": serializer.data}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def list_question_api(request):
    quest = Answer.objects.filter(question_id=request.data['question_id'])
    serializer = QuestionResponseSerializer(quest, many=True)

    return Res({"data": serializer.data}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_consent(request):
    quest = Question.objects.filter(questionnaire_id=request.data['questionnaire_id']).order_by('question_order')[:1]
    a_id = 0
    for q in quest:
        a_id =q.id
    try:
        consent = Patient_Consent.objects.create(
            questionnaire_id=request.data['questionnaire_id'],
            informed_consent=request.data['informed_consent'],
            privacy_policy=request.data['privacy_policy'],
            interviewer_statement=request.data['interviewer_statement'],
            ccc_number=request.data['ccc_number'])
        consent.save()
        session = Started_Questionnaire.objects.create(questionnaire_id=request.data['questionnaire_id'],
                                                        questionnaire_participant_id=request.data['questionnaire_participant_id'],
                                                   started_by=request.user,
                                                   ccc_number=request.data['ccc_number'],
                                                   firstname=request.data['first_name'])
        session.save()
    except KeyError:
        return Res({'error': False, 'message': 'Cannot start Questionnaire, Provide consent again'}, status.HTTP_400_BAD_REQUEST)
        
    return JsonResponse({
        'link': 'https://psurvey-api.mhealthkenya.co.ke/api/questions/answer/{}'.format(a_id),
        'session': session.pk
    })
    # return Res({"Question": serializer.data, "Ans": ser.data, "session_id": session.pk}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initial_consent(request):
    if request.data['ccc_number'] == "":
        return Res({'success': True, 'message': "You can now start questionnaire"}, status.HTTP_200_OK)
    else:
        check = check_ccc(request.data['ccc_number'])
    if not check:
        return Res({'error': False, 'message': 'ccc number doesnt exist'}, status=status.HTTP_200_OK)
    if check['f_name'].upper() != request.data['first_name'].upper():
        return Res({'error': False, 'message': 'client verification failed'}, status.HTTP_200_OK)
    return Res({'success': True, 'message': "You can now start questionnaire"}, status.HTTP_200_OK)



def check_ccc(value):
    user = {
        "ccc_number": value
    }

    url = "http://ushaurinode.mhealthkenya.org/api/mlab/get/one/client"
    headers = {
        'content-type': "application/json",
        'Accept': 'application/json'
    }
    response = requests.post(url, data=user, json=headers)
    try:
        return response.json()["clients"][0]
    except IndexError:
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_questionnaire_new(request, q_id):
    quest = Question.objects.get(id=q_id)
    serializer = QuestionSerializer(quest)
    queryset = Answer.objects.filter(question_id=quest)
    ser = AnswerSerializer(queryset, many=True)

    return Res({"Question": serializer.data, "Ans": ser.data}, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def previous_question(request, q_id, session_id):
    if q_id == 0:
        return Res({'error': False, 'message': 'no previous question'}, status.HTTP_200_OK)
    quest = Question.objects.get(id=q_id)
    serializer = QuestionSerializer(quest)
    queryset = Answer.objects.filter(question_id=quest)
    ser = AnswerSerializer(queryset, many=True)
    # if previous response exist
    resp = Response.objects.filter(question_id=q_id, session_id=session_id)
    respserializer = ResponseSerializer(resp, many=True)

    return Res({"Question": serializer.data, "Ans": ser.data, "responses": respserializer.data}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_question(request):
    q = Question.objects.get(id=request.data['question'])
    is_responded = Response.objects.filter(question_id=request.data['question'], session_id=request.data['session'])
    
    if is_responded.exists:
        is_responded.delete()
        
    if q.question_type == 3:
        a = request.data.copy()
        trans_one = transaction.savepoint()
        b = a['answer'].replace(" ", '').replace('[', '').replace(']', '').split(',')

        for i in b:
            a.update({'answer': i})
            serializer = ResponseSerializer(data=a)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                transaction.savepoint_rollback(trans_one)
                return Res({'success': False, 'error': 'Unknown error, try again'}, status=status.HTTP_400_BAD_REQUEST)

        q = Question.objects.get(id=serializer.data['question'])
        quest = Questionnaire.objects.get(id=q.questionnaire_id)    
        question_depends_on = QuestionDependance.objects.filter(
                question__in=Question.objects.filter(questionnaire=quest).order_by("question_order")
            ).exclude(
                answer_id__in=Response.objects.filter(session_id=serializer.data['session']).values_list('answer_id', flat=True)
            )
    
    
        if question_depends_on.exists():
            questions = Question.objects.filter(questionnaire=quest).order_by("question_order").exclude(id__in=question_depends_on.values_list('question_id', flat=True))
        else:
            questions = Question.objects.filter(questionnaire=quest).order_by("question_order")

        foo = q
        previous = next_ = None
        l = len(questions)
        for index, obj in enumerate(questions):
            if obj == foo:
                if index > 0:
                    previous = questions[index - 1]
                if index < (l - 1):
                    next_ = questions[index + 1]
                    return JsonResponse({
                        'link': 'https://psurvey-api.mhealthkenya.co.ke/api/questions/answer/{}'.format(next_.id),
                        'prevlink': 'https://psurvey-api.mhealthkenya.co.ke/api/previous_question/answer/{}/{}'.format(previous, serializer.data['session']) if previous else None, # TODO:: Add previous link
                        "session_id": serializer.data['session']
                    })

                elif next_ == None:
                    end = End_Questionnaire.objects.create(questionnaire=quest, session_id=serializer.data['session'])
                    end.save()
                    return Res({
                        "success": True,
                        "Message": "Questionnaire complete, Thank You👌!"
                    }, status.HTTP_200_OK)
        return Res({'success': False, 'error': 'Unknown error, try again'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        serializer = ResponseSerializer(data=request.data)
        print(serializer.is_valid(raise_exception=True))
        try:
            if serializer.is_valid():
                data = check_answer_algo(serializer)
            else:
                return Res({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("error", e)
            return Res(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return data


def check_answer_algo(ser):
    ser.save()
    q = Question.objects.get(id=ser.data['question'])
    quest = Questionnaire.objects.get(id=q.questionnaire_id)
    question_depends_on = QuestionDependance.objects.filter(
            question__in=Question.objects.filter(questionnaire=quest).order_by("question_order")
        ).exclude(
            answer_id__in=Response.objects.filter(session_id=ser.data['session']).values_list('answer_id', flat=True)
        )
    
    if question_depends_on.exists():
        questions = Question.objects.filter(questionnaire=quest).order_by("question_order").exclude(id__in=question_depends_on.values_list('question_id', flat=True))
    else:
        questions = Question.objects.filter(questionnaire=quest).order_by("question_order")

    foo = q
    previous = next_ = None
    l = len(questions)
    for index, obj in enumerate(questions):
        if obj == foo:
            if index > 0:
                previous = questions[index - 1]
            if index < (l - 1):
                next_ = questions[index + 1]
                serializer = QuestionSerializer(next_)
                queryset = Answer.objects.filter(question=next_)
                ans_ser = AnswerSerializer(queryset, many=True)
                return JsonResponse({
                    'link': 'https://psurvey-api.mhealthkenya.co.ke/api/questions/answer/{}'.format(next_.id),
                    'prevlink': 'https://psurvey-api.mhealthkenya.co.ke/api/previous_question/answer/{}/{}'.format(previous, serializer.data['session']) if previous else None, # TODO:: Add previous link
                    "session_id": ser.data['session']
                })

            elif next_ == None:
                end = End_Questionnaire.objects.create(questionnaire=quest, session_id=ser.data['session'])
                end.save()
                return Res({
                    "success": True,
                    "Message": "Questionnaire complete, Thank You👌!"
                }, status.HTTP_200_OK)
    return Res({'success': False, 'error': 'Unknown error, try again'}, status=status.HTTP_400_BAD_REQUEST)

