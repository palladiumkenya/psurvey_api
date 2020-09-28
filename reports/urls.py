from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from django.urls import path

urlpatterns = [
    #web urls
    path('web/reports/response/<int:q_id>', views.index, name='response_report'),
    path('web/reports/open_resp/<int:q_id>', views.open_end, name='open_resp_report'),

]
urlpatterns += staticfiles_urlpatterns()