from django.conf.urls import url
from . import views
from django.urls import path

urlpatterns = [
    path('facilities/', views.facilities),
    path('designation/', views.designation),
    path('current/user/', views.current_user),
]
