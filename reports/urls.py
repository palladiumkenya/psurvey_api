from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers

from . import views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'albums/(?P<question_id>\d+)', views.RespViewSet, basename='Response')

urlpatterns = [
    #web urls
    path('web/reports/response/<int:q_id>', views.index, name='response_report'),
    path('web/reports/open_resp/<int:q_id>', views.open_end, name='open_resp_report'),
    url('^api/', include(router.urls)),

]
urlpatterns += staticfiles_urlpatterns()