from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('', views.business_list, name='business_list'),
    path('create/', views.business_create, name='business_create'),
    path('<int:business_id>/', views.business_detail, name='business_detail'),
    path('<int:business_id>/edit/', views.business_edit, name='business_edit'),
    path('<int:business_id>/delete/', views.business_delete, name='business_delete'),

    # yeni eklediklerimiz
    path('general/', views.general_metrics, name='general_metrics'),
    path('<int:business_id>/activate/', views.activate_business, name='business_activate'),
    path('<int:business_id>/branches/add/', views.branch_add, name='branch_add'),
    path('<int:business_id>/branches/<int:contact_id>/primary/', views.branch_make_primary, name='branch_make_primary'),
    path('ecommerce/<str:platform_name>/', views.ecommerce_platform_detail, name='ecommerce_platform_detail'),
    path('ecommerce/<str:platform_name>/add/', views.ecommerce_business_add, name='ecommerce_business_add'),

    # Excel import
    path('import-excel/', views.import_excel, name='import_excel'),
]

