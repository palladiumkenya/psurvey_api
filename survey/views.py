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
        queryset = Questionnaire_Participants.objects.filter(is_active=True)
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
    question = Question.objects.filter().values_list('questionnaire_id', flat=True)
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
                                            active_till__gte=date.today())
    elif request.user.access_level.id == 3:
        queryset = Questionnaire.objects.filter(is_active=True, active_till__gte=date.today())
    elif request.user.access_level.id == 4:
        q = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id).values_list('questionnaire_id').distinct()
        queryset = Questionnaire.objects.filter(id__in=q, is_active=True, active_till__gte=date.today())
        
    elif request.user.access_level.id == 5:
        fac = Partner_Facility.objects.filter(
            partner__in=Partner_User.objects.filter(user=request.user).values_list('name', flat=True))
        q = Facility_Questionnaire.objects.filter(facility_id__in=fac.values_list('facility_id', flat=True)
                                                    ).values_list('questionnaire_id').distinct()
        queryset = Questionnaire.objects.filter(id__in=q, is_active=True, active_till__gte=date.today())
    queryset.filter(id__in=question).order_by('-created_at')
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
        
    return JsonResponse({
        #'link': 'https://psurvey-api.mhealthkenya.co.ke/api/questions/answer/{}'.format(a_id),
        'link': 'https://psurveyapi.kenyahmis.org/api/questions/answer/{}'.format(a_id),


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
def start_questionnaire_new(request, q_id, session_id):
    quest = Question.objects.get(id=q_id)

    repeat_count = 0
    answer_id = 0
    resp_answer_id = 0
    dep_q_id = 0

    # if this question is repeatable
    if quest.is_repeatable:
        # get the question dependancy details
        dep_questions = QuestionDependance.objects.filter(question=quest)
        for dep_question in dep_questions:
            answer_id = dep_question.answer_id
            dep_q_id = dep_question.id

        # get the parent question from Answers
        parent_quest = Answer.objects.get(id = answer_id)
        parent_quest_id = parent_quest.question_id

        # get the parent question's response
        responses = Response.objects.filter(question_id=parent_quest_id, session_id=session_id)
        for response in responses:
            resp_answer_id = response.answer_id

         # get the response's answer value
        resp_answer = Answer.objects.get(id = resp_answer_id)
        repeat_count = resp_answer.option        

    serializer = QuestionSerializer(quest)
    queryset = Answer.objects.filter(question_id=quest)
    ser = AnswerSerializer(queryset, many=True)

    return Res({"Question": serializer.data, "Ans": ser.data,"repeat_count" : repeat_count}, status.HTTP_200_OK)


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
                else:
                    previous = questions[index]

                if index < (l - 1):
                    next_ = questions[index + 1]
                    return JsonResponse({
                        #'link': 'https://psurvey-api.mhealthkenya.co.ke/api/questions/answer/{}'.format(next_.id),
                        #'prevlink': 'https://psurvey-api.mhealthkenya.co.ke/api/previous_question/answer/{}/{}'.format(previous.id, serializer.data['session']) if previous else None, # TODO:: Add previous link
                        
                        'link': 'https://psurveyapi.kenyahmis.org/api/questions/answer/{}'.format(next_.id),
                        'prevlink': 'https://psurveyapi.kenyahmis.org/api/previous_question/answer/{}/{}'.format(previous.id, serializer.data['session']) if previous else None, # TODO:: Add previous link

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
    questions = Question.objects.filter(questionnaire=quest).order_by("question_order")

    question_depends_on = QuestionDependance.objects.filter(
            question__in=Question.objects.filter(questionnaire=quest).order_by("question_order")
        ).exclude(
            answer_id__in=Response.objects.filter(session_id=ser.data['session']).values_list('answer_id', flat=True)
        )

    if question_depends_on.exists():
        questions = Question.objects.filter(questionnaire=quest).order_by("question_order").exclude(id__in=question_depends_on.values_list('question_id', flat=True))

        # perform the repeatable check
        # get all answers for the current question
        ans = Answer.objects.filter(question_id=q.id)

        #check if the answers are in the dependancy table
        ans_dep = QuestionDependance.objects.filter(answer_id__in=ans.values_list('id', flat=True))

        if ans_dep.exists():
            # get the questions connected by this dependancy
            que_dep = Question.objects.filter(id__in=ans_dep.values_list('question_id', flat=True))

            #check if any of these questions are repeatable
            q_is_repeatable = False
            for que in que_dep:
                if que.is_repeatable:
                    q_is_repeatable = True
        
            if q_is_repeatable:
                questions = Question.objects.filter(questionnaire=quest).order_by("question_order") 
        else:
            # check if this question is in the dependancy table and has a response
             if QuestionDependance.objects.filter(question_id=q.id).exists():
                if Response.objects.filter(session_id=ser.data['session'],question_id=q.id).exists():
                    questions = Question.objects.filter(questionnaire=quest).order_by("question_order")

                
    foo = q
    previous = next_ = None
    l = len(questions)
    for index, obj in enumerate(questions):
        if obj == foo:
            if index > 0:
                previous = questions[index - 1]                   
            else:
                previous = questions[index]

            if index < (l - 1):
                next_ = questions[index + 1]
                serializer = QuestionSerializer(next_)
                queryset = Answer.objects.filter(question=next_)
                ans_ser = AnswerSerializer(queryset, many=True)
                return JsonResponse({
                    #'link': 'https://psurvey-api.mhealthkenya.co.ke/api/questions/answer/{}'.format(next_.id),
                    #'prevlink': 'https://psurvey-api.mhealthkenya.co.ke/api/previous_question/answer/{}/{}'.format(previous.id, ser.data['session']) if previous else None, # TODO:: Add previous link

                    'link': 'https://psurveyapi.kenyahmis.org/api/questions/answer/{}'.format(next_.id),
                    'prevlink': 'https://psurveyapi.kenyahmis.org/api/previous_question/answer/{}/{}'.format(previous.id, ser.data['session']) if previous else None, # TODO:: Add previous link

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



#fetch all questions

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questionnaire_all(request, q_id):
    quest = Question.objects.filter(questionnaire=q_id)
    q_details = QuestionSetSerializer(quest,many=True)
    return Res({"Questions":q_details.data}, status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_answers_all(request, qn_id):
    qn_answer = Answer.objects.filter(question_id=qn_id)
    answers_details = AnswerAllSerializer(qn_answer,many=True)
    
    return Res({"Answers":answers_details.data}, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_qdependancy_all(request, qn_id):
    dep_answer = QuestionDependance.objects.filter(question_id=qn_id)
    dependancy_details= DependancySerializer(dep_answer,many=True)
    
    return Res({"Dependancy":dependancy_details.data}, status.HTTP_200_OK)


@api_view(['GET'])
def get_question_ans_dep(request):
    quest = Questionnaire.objects.filter(is_active=True)
    
    data = QuestionAnswDepSerializer(quest, many=True)
    return Res(data.data, status.HTTP_200_OK)
    