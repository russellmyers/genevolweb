from django.urls import path

from . import views

urlpatterns = [
          path('pg', views.population_growth, name='population_growth'),
          path('be', views.breeders_equation, name='breeders_equation'),
          path('hw', views.hardy_weinberg, name='hardy_weinberg'),
          path('cross_map', views.cross_map, name='cross_map'),
          path('gcm_update_type', views.gcm_update_type, name='gcm_update_type'),

]
