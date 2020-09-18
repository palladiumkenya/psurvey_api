from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from django.urls import path

urlpatterns = [
    #web urls
    path('web/reports/response', views.index, name='response_report'),

]
urlpatterns += staticfiles_urlpatterns()