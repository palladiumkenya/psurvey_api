from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from django.urls import path

urlpatterns = [
    path('web/dashboard/', views.index, name='dashboard'),
    path('web/questionnaires/', views.questionnaire, name='questionnaires'),
    path('web/new-questionnaire/', views.new_questionnaire, name='new-questionnaires'),
    path('web/add-question/<int:q_id>/', views.add_question, name='add-question'),
    path('web/question-list/<int:q_id>/', views.question_list, name='questions'),

    #Api urls
    path('api/questionnaire/all/', views.all_questionnaire_api, name='questionnaire_api'),
    # path('designation/', views.designation),
    # path('current/user/', views.current_user),
]
urlpatterns += staticfiles_urlpatterns()
