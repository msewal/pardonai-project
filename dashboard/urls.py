from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_page, name='dashboard'),
    path('pareto/', views.pareto_page, name='pareto'),
  
]