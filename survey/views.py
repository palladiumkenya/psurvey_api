from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response as Res
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializer import *
from authApp.serializer import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_questionnaire_api(request):
    quest = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id)
    list = []
    for i in quest:
        queryset = Questionnaire.objects.filter(id=i.questionnaire.id)
        serializer =  QuestionnaireSerializer(queryset, many=True)
        list.append(serializer.data[0])
    print(list)
    return Res({"data": list}, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_questionnaire_api (request):
    quest = Facility_Questionnaire.objects.filter(facility_id=request.user.facility.id)
    list = []
    for i in quest:
        queryset = Questionnaire.objects.filter(id=i.questionnaire.id, is_active=True)
        serializer =  QuestionnaireSerializer(queryset, many=True)
        list.append(serializer.data[0])
    print(list)
    return Res({"data": list}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def all_question_api (request):
    quest = Question.objects.filter(questionnaire_id=request.data['questionnaire_id'])
    serializer = QuestionSerializer(quest, many=True)

    return Res({"data": serializer.data}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def list_question_api (request):
    quest = Answer.objects.filter(question_id=request.data['question_id'])
    serializer = QuestionResponseSerializer(quest, many=True)

    return Res({"data": serializer.data}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_questionnaire (request):
    quest = Question.objects.filter(questionnaire_id=request.data['question_id'])[:1]
    for q in quest:
        serializer = QuestionSerializer(q)
        queryset =  Answer.objects.filter(question_id=q.id)
        ser = ResponseSerializer(queryset, many=True)

    return Res({"Question": serializer.data, "Ans": ser.data}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_question (request):
    quest = Question.objects.filter(questionnaire_id=request.data['question_id'])
    serializer = QuestionSerializer(quest, many=True)

    return Res({"data": serializer.data}, status.HTTP_200_OK)


@login_required
def index (request):
    user = request.user
    context = {'u': user}
    return render(request, 'survey/dashboard.html', context)


@login_required
def new_questionnaire (request):
    user = request.user
    u = user
    if request.method == 'POST':
        name = request.POST.get('title')
        facility = request.POST.getlist('facility')
        desc = request.POST.get('description')
        dateTill = request.POST.get('date-till')
        isActive = request.POST.get('isActive')


        if isActive == "inactive":
            isActive = False
        else:
            isActive = True
        create_quest = Questionnaire.objects.create(name=name, is_active=isActive, description=desc,
                                                    active_till=dateTill, created_by=request.user)
        create_quest.save()
        trans_one = transaction.savepoint()
        q_id = create_quest.pk
        print(q_id)

        if q_id:
            try:
                for f in facility:
                    fac_save = Facility_Questionnaire.objects.create(facility_id=f, questionnaire_id=q_id)
                    fac_save.save()
            except IntegrityError:
                transaction.savepoint_rollback(trans_one)
                return HttpResponse("error")

    if user.access_level.id == 3:
        facilities = Facility.objects.all()
        context = {
            'u': u,
            'fac': facilities,
        }
        return render(request, 'survey/new_questionnaire.html', context)
    if user.access_level == 2:
        facp = Partner_Facility.objects.filter(partner__user=user)
        facilities = []
        for f in facp:
            facilities.append(Facility.objects.filter(id=facp.id))
        print(facilities)
        context = {
            'u': u,
            'fac': facilities,
        }
        return render(request, 'survey/new_questionnaire.html', context)


@login_required
def questionnaire (request):
    user = request.user
    u = user
    if user.access_level.id == 3:
        quest = Questionnaire.objects.all().order_by('-created_at')
        context = {
            'u': u,
            'quest': quest
        }
        return render(request, 'survey/questionnaires.html', context)
    elif user.access_level.id == 2:
        facility = Partner_Facility.objects.filter(user=user)
        quest = []
        for f in facility:
            quest.append(Facility_Questionnaire.objects.filter(facility=f.facility))

        context = {
            'u': u,
            'quest': quest
        }
        return render(request, 'survey/questionnaires.html', context)


@login_required
def add_question (request, q_id):
    user = request.user
    u = user
    if request.method == 'POST':
        question = request.POST.get('question')
        q_type = request.POST.get('q_type') #For q_type 1 is opened ended 2 Radio 3 is Checkbox
        answers = request.POST.get('answers')
        if q_type == '1':
            answers = "Open Text"
        answers_list = answers.split(',')
        print(question,q_type, answers_list)

        q_save = Question.objects.create(question=question, question_type=q_type, created_by=user , questionnaire_id=q_id)
        trans_one = transaction.savepoint()
        question_id = q_save.pk

        if question_id:
            try:
                for f in answers_list:
                    fac_save = Answer.objects.create(question_id=question_id, created_by=user ,option=f)
                    fac_save.save()
            except IntegrityError:
                transaction.savepoint_rollback(trans_one)
                return HttpResponse("error")
    context = {
        'u': u,
        'questionnaire': q_id
    }
    return render(request, 'survey/new_questions.html', context)


@login_required
def question_list (request, q_id):
    user = request.user
    u = user
    if user.access_level.id == 3:
        quest = Question.objects.filter(questionnaire_id=q_id).order_by('-created_at')
        context = {
            'u': u,
            'quest': quest,
            'questionnaire': q_id,
        }
        print(quest)
        return render(request, 'survey/question_list.html', context)
    elif user.access_level.id == 2:
        facility = Partner_Facility.objects.filter(user=user)
        quest = Question.objects.filter(questionnaire_id=q_id).order_by('-created_at')
        # fac_link = []
        # quest = []
        # for f in facility:
        #     fac_link.append(Facility_Questionnaire.objects.filter(facility=f.facility))
        # for q in fac_link:
        #     quest.append(Question.objects.filter(questionnaire=q))
        context = {
            'u': u,
            'quest': quest,
            'questionnaire': q_id,
        }
        return render(request, 'survey/question_list.html', context)

