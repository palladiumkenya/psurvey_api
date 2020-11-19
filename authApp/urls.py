from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from pSurvey_api import settings
from . import views
from django.urls import path

urlpatterns = [
    # api
    path('api/facilities/', views.facilities),
    path('api/facility/single/', views.facility_single),
    path('api/designation/', views.designation),
    path('api/current/user/', views.current_user),
    path('api/counties/', views.counties),
]

urlpatterns += staticfiles_urlpatterns()
