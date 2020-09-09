from django.urls import path

from . import views,test_views

urlpatterns = [
    path('', views.index, name='index'),
    path('af',views.allele_freak,name='allele_freak'),
    path('pg',views.population_growth, name = 'population_growth'),
    path('be',views.breeders_equation, name = 'breeders_equation'),
    path('hw',views.hardy_weinberg, name = 'hardy_weinberg'),
    path('cross_map',views.cross_map,name='cross_map'),
    path('test_plot',test_views.plot_test,name='test_plot'),
    path('cross_sim', views.cross_sim, name='cross_sim'),
    path('pa', views.ped_an, name='ped_an'),
    path('quiz', views.quiz, name ='quiz'),
    path('support',views.support,name='support'),
    path('about',views.about,name='about'),
    path('gcm_update_type', views.gcm_update_type, name='gcm_update_type'),

]