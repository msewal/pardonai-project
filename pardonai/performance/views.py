from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import PerformanceMetric, SalesReport, CustomerAnalytics, BusinessDashboard, Goal
from pardonai.dashboard.models import Businesses as CoreBusinesses


def performance_dashboard(request):
    """Performans dashboard ana sayfası"""
    # Örnek dashboard verileri
    dashboard_data = {
        'total_businesses': CoreBusinesses.objects.count(),
        'active_businesses': CoreBusinesses.objects.filter(status='active').count(),
        'total_metrics': PerformanceMetric.objects.count(),
        'total_goals': Goal.objects.count(),
        'achieved_goals': Goal.objects.filter(is_achieved=True).count(),
    }
    
    context = {'dashboard_data': dashboard_data}
    return render(request, 'performance/performance_dashboard.html', context)


def metrics_list(request):
    """Metrik listesi"""
    metrics = PerformanceMetric.objects.all().order_by('-created_date')
    context = {
        'metrics': metrics,
        'total_metrics': metrics.count(),
        'metrics_by_type': {},  # Tipe göre gruplandırma
    }
    return render(request, 'performance/metrics_list.html', context)


def metrics_create(request):
    """Yeni metrik oluşturma"""
    if request.method == 'POST':
        # Form işleme kodları burada olacak
        messages.success(request, 'Metrik başarıyla oluşturuldu.')
        return redirect('performance:metrics_list')
    
    businesses = CoreBusinesses.objects.filter(status='active')
    context = {'businesses': businesses}
    return render(request, 'performance/metrics_form.html', context)


def reports_list(request):
    """Rapor listesi"""
    sales_reports = SalesReport.objects.all().order_by('-report_date')
    customer_analytics = CustomerAnalytics.objects.all().order_by('-period_start')
    
    context = {
        'sales_reports': sales_reports,
        'customer_analytics': customer_analytics,
        'total_reports': sales_reports.count() + customer_analytics.count(),
    }
    return render(request, 'performance/reports_list.html', context)


def analytics_view(request):
    """Analitik görünümü"""
    # Örnek analitik verileri
    analytics_data = {
        'revenue_trend': [],
        'order_trend': [],
        'customer_trend': [],
        'top_performing_businesses': [],
        'performance_summary': {},
    }
    
    context = {'analytics': analytics_data}
    return render(request, 'performance/analytics_view.html', context)


@require_http_methods(["GET"])
def performance_data(request, business_id):
    """Performans verileri - AJAX endpoint"""
    business = get_object_or_404(CoreBusinesses, business_id=business_id)
    
    # Örnek performans verileri
    performance_data = {
        'business_name': business.business_name,
        'total_revenue': 0,  # Hesaplanacak
        'total_orders': 0,   # Hesaplanacak
        'customer_count': 0, # Hesaplanacak
        'satisfaction_score': 0, # Hesaplanacak
    }
    
    return JsonResponse(performance_data)


@require_http_methods(["GET"])
def goal_progress(request, goal_id):
    """Hedef ilerlemesi - AJAX endpoint"""
    goal = get_object_or_404(Goal, id=goal_id)
    
    progress_data = {
        'goal_title': goal.title,
        'current_value': float(goal.current_value),
        'target_value': float(goal.target_value),
        'progress_percentage': (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0,
        'is_achieved': goal.is_achieved,
    }
    
    return JsonResponse(progress_data)
