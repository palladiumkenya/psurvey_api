from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Count

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
    user = request.user
    keywords = request.POST.get('keywords')
    print(keywords)
    words = keywords.split(',')

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