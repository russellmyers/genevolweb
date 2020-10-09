from django.urls import path

from . import views

urlpatterns = [
    path('', views.ped_an, name='ped_an'),

]