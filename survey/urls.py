from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from django.urls import path

urlpatterns = [

    #Api urls
    path('api/questionnaire/all/', views.all_questionnaire_api, name='questionnaire_api'),
    path('api/questionnaire/active/', views.active_questionnaire_api, name='active_questionnaire_api'),
    path('api/questionnaire/active/<int:q_mfl_code>/<str:q_ccc_no>/', views.active_questionnaire_nishauri_api, name='active_questionnaire_nishauri_api'),
    path('api/questionnaire/data/<int:q_id>/<int:q_mfl_code>/', views.questionnaire_data, name='questionnaire_data'),
    path('api/questions/all/', views.all_question_api, name='all_question_api'),
    path('api/questions/list/', views.list_question_api, name='list_question_api'),
    path('api/questionnaire/start/', views.get_consent, name='provide_consent_api'),
    path('api/questions/answer/', views.answer_question, name='provide_response_api'),
    path('api/questions/answer/<int:q_id>/<int:session_id>', views.start_questionnaire_new, name='provide_response_one_api'),
    path('api/previous_question/answer/<int:q_id>/<int:session_id>', views.previous_question, name='previous_question_api'),
    path('api/initial/consent/', views.initial_consent, name='initial_consent_api'),
    path('api/questionnaire/participants/', views.questionnaire_participants, name='questionnaire_participants_api'),

    #new api to fetch all questions
    path('api/questions_all/<int:q_id>/', views.get_questionnaire_all, name='get_questionnaire_all_api'),
    path('api/answers_options/<int:qn_id>/', views.get_answers_all, name='get_answers_all_api'),
    path('api/qdependancy_options/<int:qn_id>/', views.get_qdependancy_all, name='get_qdependancy_all_api'),
    
    path('api/questions/dep/all', views.get_question_ans_dep, name='get_qdependancy_all_api'),


]
urlpatterns += staticfiles_urlpatterns()