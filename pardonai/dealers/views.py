from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Dealer, DealerExperience, DealerCommission, DealerPerformance
from pardonai.dashboard.models import Businesses as CoreBusinesses


def dealer_list(request):
    """Bayi listesi"""
    dealers = Dealer.objects.all().order_by('-created_date')
    context = {
        'dealers': dealers,
        'total_dealers': dealers.count(),
        'active_dealers': dealers.filter(is_active=True).count(),
    }
    return render(request, 'dealers/dealer_list.html', context)


def dealer_detail(request, dealer_id):
    """Bayi detay sayfası"""
    dealer = get_object_or_404(Dealer, id=dealer_id)
    experiences = dealer.experiences.all().order_by('-experience_date')
    commissions = dealer.commissions.all().order_by('-order_date')
    performance_records = dealer.performance_records.all().order_by('-period_start')
    
    context = {
        'dealer': dealer,
        'experiences': experiences,
        'commissions': commissions,
        'performance_records': performance_records,
    }
    return render(request, 'dealers/dealer_detail.html', context)


def dealer_create(request):
    """Yeni bayi oluşturma"""
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Bayi başarıyla oluşturuldu.')
        return redirect('dealers:dealer_list')
    
    businesses = CoreBusinesses.objects.filter(status='active')
    context = {'businesses': businesses}
    return render(request, 'dealers/dealer_form.html', context)


def dealer_edit(request, dealer_id):
    """Bayi düzenleme"""
    dealer = get_object_or_404(Dealer, id=dealer_id)
    
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Bayi başarıyla güncellendi.')
        return redirect('dealers:dealer_detail', dealer_id=dealer_id)
    
    businesses = CoreBusinesses.objects.filter(status='active')
    context = {
        'dealer': dealer,
        'businesses': businesses,
    }
    return render(request, 'dealers/dealer_form.html', context)


def dealer_delete(request, dealer_id):
    """Bayi silme"""
    dealer = get_object_or_404(Dealer, id=dealer_id)
    
    if request.method == 'POST':
        dealer.delete()
        messages.success(request, 'Bayi başarıyla silindi.')
        return redirect('dealers:dealer_list')
    
    context = {'dealer': dealer}
    return render(request, 'dealers/dealer_confirm_delete.html', context)


def experience_list(request):
    """Deneyim listesi"""
    experiences = DealerExperience.objects.all().order_by('-experience_date')
    context = {
        'experiences': experiences,
        'total_experiences': experiences.count(),
        'public_experiences': experiences.filter(is_public=True).count(),
    }
    return render(request, 'dealers/experience_list.html', context)


def experience_create(request):
    """Yeni deneyim oluşturma"""
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Deneyim başarıyla oluşturuldu.')
        return redirect('dealers:experience_list')
    
    dealers = Dealer.objects.filter(is_active=True)
    context = {'dealers': dealers}
    return render(request, 'dealers/experience_form.html', context)


@require_http_methods(["GET"])
def dealer_analytics(request, dealer_id):
    """Bayi analitikleri - AJAX endpoint"""
    dealer = get_object_or_404(Dealer, id=dealer_id)
    
    # Örnek analitik verileri
    analytics_data = {
        'dealer_name': dealer.name,
        'total_sales': float(dealer.total_sales),
        'total_orders': dealer.total_orders,
        'customer_count': dealer.customer_count,
        'commission_rate': float(dealer.commission_rate),
    }
    
    return JsonResponse(analytics_data)
