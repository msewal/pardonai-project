from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Menu, Product, Category, Extra, ProductExtra
from pardonai.dashboard.models import Businesses as CoreBusinesses


def menu_list(request):
    """Menü listesi"""
    menus = Menu.objects.all().order_by('-created_date')
    context = {
        'menus': menus,
        'total_menus': menus.count(),
        'active_menus': menus.filter(is_active=True).count(),
    }
    return render(request, 'menu/menu_list.html', context)


def menu_detail(request, menu_id):
    """Menü detay sayfası"""
    menu = get_object_or_404(Menu, id=menu_id)
    products = menu.products.all().order_by('category', 'sort_order')
    
    # Kategorilere göre grupla
    products_by_category = {}
    for product in products:
        category_name = product.category.name
        if category_name not in products_by_category:
            products_by_category[category_name] = []
        products_by_category[category_name].append(product)
    
    context = {
        'menu': menu,
        'products_by_category': products_by_category,
        'total_products': products.count(),
    }
    return render(request, 'menu/menu_detail.html', context)


def menu_create(request):
    """Yeni menü oluşturma"""
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Menü başarıyla oluşturuldu.')
        return redirect('menu:menu_list')
    
    businesses = CoreBusinesses.objects.filter(status='active')
    context = {'businesses': businesses}
    return render(request, 'menu/menu_form.html', context)


def menu_edit(request, menu_id):
    """Menü düzenleme"""
    menu = get_object_or_404(Menu, id=menu_id)
    
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Menü başarıyla güncellendi.')
        return redirect('menu:menu_detail', menu_id=menu_id)
    
    businesses = CoreBusinesses.objects.filter(status='active')
    context = {
        'menu': menu,
        'businesses': businesses,
    }
    return render(request, 'menu/menu_form.html', context)


def menu_delete(request, menu_id):
    """Menü silme"""
    menu = get_object_or_404(Menu, id=menu_id)
    
    if request.method == 'POST':
        menu.delete()
        messages.success(request, 'Menü başarıyla silindi.')
        return redirect('menu:menu_list')
    
    context = {'menu': menu}
    return render(request, 'menu/menu_confirm_delete.html', context)


def product_list(request):
    """Ürün listesi"""
    products = Product.objects.all().order_by('menu', 'category', 'name')
    context = {
        'products': products,
        'total_products': products.count(),
        'available_products': products.filter(is_available=True).count(),
    }
    return render(request, 'menu/product_list.html', context)


def product_create(request):
    """Yeni ürün oluşturma"""
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Ürün başarıyla oluşturuldu.')
        return redirect('menu:product_list')
    
    menus = Menu.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    context = {
        'menus': menus,
        'categories': categories,
    }
    return render(request, 'menu/product_form.html', context)


@require_http_methods(["GET"])
def product_analytics(request, product_id):
    """Ürün analitikleri - AJAX endpoint"""
    product = get_object_or_404(Product, id=product_id)
    
    # Örnek analitik verileri
    analytics_data = {
        'product_name': product.name,
        'total_orders': 0,  # OrderItem.objects.filter(product=product).count()
        'total_revenue': 0,  # Hesaplanacak
        'average_rating': 0,  # Hesaplanacak
    }
    
    return JsonResponse(analytics_data)
