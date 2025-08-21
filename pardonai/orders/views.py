from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Order, OrderItem, OrderItemExtra, OrderHistory, Customer
from pardonai.dashboard.models import Businesses as CoreBusinesses


def order_list(request):
    """Sipariş listesi"""
    orders = Order.objects.all().order_by('-order_date')
    context = {
        'orders': orders,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(order_status='pending').count(),
        'completed_orders': orders.filter(order_status='delivered').count(),
    }
    return render(request, 'orders/order_list.html', context)


def order_detail(request, order_id):
    """Sipariş detay sayfası"""
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    history = order.history.all()
    
    context = {
        'order': order,
        'items': items,
        'history': history,
    }
    return render(request, 'orders/order_detail.html', context)


def order_create(request):
    """Yeni sipariş oluşturma"""
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Sipariş başarıyla oluşturuldu.')
        return redirect('orders:order_list')
    
    businesses = CoreBusinesses.objects.filter(status='active')
    context = {'businesses': businesses}
    return render(request, 'orders/order_form.html', context)


def order_edit(request, order_id):
    """Sipariş düzenleme"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Sipariş başarıyla güncellendi.')
        return redirect('orders:order_detail', order_id=order_id)
    
    businesses = CoreBusinesses.objects.filter(status='active')
    context = {
        'order': order,
        'businesses': businesses,
    }
    return render(request, 'orders/order_form.html', context)


def order_delete(request, order_id):
    """Sipariş silme"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Sipariş başarıyla silindi.')
        return redirect('orders:order_list')
    
    context = {'order': order}
    return render(request, 'orders/order_confirm_delete.html', context)


def order_analytics(request):
    """Sipariş analitikleri"""
    # Örnek analitik verileri
    analytics_data = {
        'total_orders': Order.objects.count(),
        'total_revenue': sum(order.final_amount for order in Order.objects.all()),
        'average_order_value': 0,  # Hesaplanacak
        'orders_by_status': {},  # Duruma göre gruplandırma
    }
    
    context = {'analytics': analytics_data}
    return render(request, 'orders/order_analytics.html', context)


@require_http_methods(["GET"])
def order_status_update(request, order_id):
    """Sipariş durumu güncelleme - AJAX endpoint"""
    order = get_object_or_404(Order, id=order_id)
    
    # Durum güncelleme kodları burada olacak
    
    return JsonResponse({'status': 'success', 'message': 'Sipariş durumu güncellendi'})
