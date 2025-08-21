from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('create/', views.menu_create, name='menu_create'),
    path('<int:menu_id>/', views.menu_detail, name='menu_detail'),
    path('<int:menu_id>/edit/', views.menu_edit, name='menu_edit'),
    path('<int:menu_id>/delete/', views.menu_delete, name='menu_delete'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
] 