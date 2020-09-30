from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response as Res
from datetime import date
from django.shortcuts import render
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from reports.serializer import *
from survey.models import *


@login_required
def index (request, q_id):
    user =  request.user
    question = Question.objects.get(id=q_id)
    respo = Response.objects.filter(question_id=q_id).order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(respo, 20)
    try:
        resp = paginator.page(page)
    except PageNotAnInteger:
        resp = paginator.page(1)
    except EmptyPage:
        resp = paginator.page(paginator.num_pages)

    labels = []
    data = []

    queryset = Response.objects.filter(question_id=q_id).values('answer__option').annotate(count=Count('answer'))

    for city in queryset:
        labels.append(city['answer__option'])
        data.append(city['count'])

    context = {
        'u': user,
        'items': paginator.count,
        'quest': question,
        'resp': resp,
        'labels': labels,
        'data': data,
    }
    return render(request, 'reports/response_report.html', context)


def open_end (request, q_id):
    keywords = request.POST.get('keywords')
    print(keywords)
    words = keywords.replace(' ', '').split(',')

    labels = []
    data = []
    result = []
    for word in words:
        queryset = Response.objects.filter(question_id=q_id, open_text__icontains=word)
        result.append({'name': word, 'freq': queryset.count()})

    print(result)
    for re in result:
        labels.append(re['name'])
        data.append(re['freq'])

    context = {
        'labels': labels,
        'data': data,
    }

    return JsonResponse(context)


def pie_chart (request):
    labels = []
    data = []

    queryset = Response.objects.order_by('question')[:5]
    for city in queryset:
        labels.append(city.answer.option)
        data.append(city.id)

    return render(request, 'pie_chart.html', {
        'labels': labels,
        'data': data,
    })


def users_report (request):
    return render(request, 'reports/user_report.html', {'u': request.user})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    queryset = Users.objects.filter(access_level_id=1)
    li = []
    for q in queryset:
        serializer = AllUserSerializer(q)
        aq = Facility_Questionnaire.objects.filter(
            facility=q.facility, questionnaire__active_till__gte=date.today()).count()
        serializer.data.update({'facilit': q.facility})
        cs = End_Questionnaire.objects.filter(session__started_by=q).count()
        li.append({'user': serializer.data, 'questionnaires': aq, 'Completed_surveys': cs, 'facility': q.facility.name, 'designation': q.designation.name})
    return Res(li, status=status.HTTP_200_OK)


class RespViewSet(viewsets.ModelViewSet):
    serializer_class = RespSerializer


    def get_queryset(self):
        nome = self.kwargs['question_id']
        return Response.objects.filter(question_id=nome).order_by('-id')

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            for q in qs:
                if q.question.question_type == 1:
                    return qs.filter(open_text__icontains=search)
                else:
                    return qs.filter(answer__option__icontains=search)

        return qs

