from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from django.urls import path

urlpatterns = [
    #web urls
    path('web/dashboard/', views.index, name='dashboard'),
    path('web/questionnaires/', views.questionnaire, name='questionnaires'),
    path('web/new-questionnaire/', views.new_questionnaire, name='new-questionnaires'),
    path('web/edit-questionnaire/<int:q_id>/', views.edit_questionnaire, name='edit-questionnaires'),
    path('web/add-question/<int:q_id>/', views.add_question, name='add-question'),
    path('web/edit-question/<int:q_id>/', views.edit_question, name='edit-question'),
    path('web/question-list/<int:q_id>/', views.question_list, name='questions'),
    path('resp-chart/', views.resp_chart, name='all-resp-chart'),

    #Api urls
    path('api/questionnaire/all/', views.all_questionnaire_api, name='questionnaire_api'),
    path('api/questionnaire/active/', views.active_questionnaire_api, name='active_questionnaire_api'),
    path('api/questions/all/', views.all_question_api, name='all_question_api'),
    path('api/questions/list/', views.list_question_api, name='list_question_api'),
    path('api/questionnaire/start/', views.start_questionnaire, name='provide_consent_api'),
    path('api/questions/answer/', views.answer_question, name='provide_response_api'),

]
urlpatterns += staticfiles_urlpatterns()