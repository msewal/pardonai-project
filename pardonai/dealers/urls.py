from django.urls import path
from . import views

app_name = 'dealers'

urlpatterns = [
    path('', views.dealer_list, name='dealer_list'),
    path('create/', views.dealer_create, name='dealer_create'),
    path('<int:dealer_id>/', views.dealer_detail, name='dealer_detail'),
    path('<int:dealer_id>/edit/', views.dealer_edit, name='dealer_edit'),
    path('<int:dealer_id>/delete/', views.dealer_delete, name='dealer_delete'),
    path('experiences/', views.experience_list, name='experience_list'),
    path('experiences/create/', views.experience_create, name='experience_create'),
] 