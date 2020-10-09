from django.urls import path

from . import views

urlpatterns = [
    path('', views.cross_sim, name='cross_sim'),
]