from django.urls import path
from . import views

app_name = 'performance'

urlpatterns = [
    path('', views.performance_dashboard, name='performance_dashboard'),
    path('metrics/', views.metrics_list, name='metrics_list'),
    path('metrics/create/', views.metrics_create, name='metrics_create'),
    path('reports/', views.reports_list, name='reports_list'),
    path('analytics/', views.analytics_view, name='analytics_view'),
] 