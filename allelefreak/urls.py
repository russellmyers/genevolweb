from django.urls import path

from . import views

urlpatterns = [
    path('',views.allele_freak,name='allele_freak'),
]