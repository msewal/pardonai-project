"""pardonai URL Configuration"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pardonai.dashboard.urls')),
    path('businesses/', include('pardonai.businesses.urls')),
    path('menu/', include('pardonai.menu.urls')),
    path('dealers/', include('pardonai.dealers.urls')),
    path('orders/', include('pardonai.orders.urls')),
    path('performance/', include('pardonai.performance.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]
