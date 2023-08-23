from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from pSurvey_api import settings
from . import views
from django.urls import path

urlpatterns = [
    path('', views.home,name='home'),
    path('api/informed', views.informed, name='informed'),
    path('api/privacy', views.privacy, name='privacy'),
    # api
    path('api/facilities/', views.facilities),
    path('api/facility/single/', views.facility_single),
    path('api/designation/', views.designation),
    path('api/current/user/', views.current_user),
    path('api/current/user/<int:q_mfl_code>/<str:q_ccc_no>/', views.current_user_nishauri),
    path('api/counties/', views.counties),
]

urlpatterns += staticfiles_urlpatterns()
