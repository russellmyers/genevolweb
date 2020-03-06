from django.urls import path

from . import views,test_views

urlpatterns = [
    path('', views.index, name='index'),
    path('af',views.allele_freak,name='allele_freak'),
    path('cross_map',views.cross_map,name='cross_map'),
    path('test_plot',test_views.plot_test,name='test_plot')

]