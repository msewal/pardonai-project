from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/edit/', views.order_edit, name='order_edit'),
    path('<int:order_id>/delete/', views.order_delete, name='order_delete'),
    path('analytics/', views.order_analytics, name='order_analytics'),
] 