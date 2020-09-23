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

    # Web
    path('web/', views.web_login, name='web-login'),
    path('web/logout/', views.logout_request, name='web-logout'),
    path('web/profile/', views.profile, name='profile'),
    path('web/facility-partner/', views.facility_partner_list, name='facility-partner-list'),
    path('web/facility-partner-link/', views.facility_partner_link, name='facility-partner-link'),
    path('web/designation-list/', views.designation_list, name='designation-list'),
    path('web/register-partner/', views.register_partner, name='register-partner'),
    path('web/edit-partner/<int:p_id>/', views.edit_partner, name='edit-partner'),
]

urlpatterns += staticfiles_urlpatterns()
