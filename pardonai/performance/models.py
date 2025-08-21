from django.db import models
from pardonai.dashboard.models import Businesses as CoreBusinesses


class MetricType(models.TextChoices):
    SALES = "sales", "Satış"
    ORDERS = "orders", "Sipariş"
    CUSTOMERS = "customers", "Müşteri"
    REVENUE = "revenue", "Gelir"
    PROFIT = "profit", "Kar"
    CONVERSION = "conversion", "Dönüşüm"
    SATISFACTION = "satisfaction", "Memnuniyet"


class PerformanceMetric(models.Model):
    """Performans metrikleri"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='performance_metrics')
    metric_type = models.CharField(max_length=20, choices=MetricType.choices)
    metric_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True)  # TL, adet, % vb.
    period_start = models.DateField()
    period_end = models.DateField()
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['business', 'metric_type', 'metric_name', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.business.business_name} - {self.metric_name} ({self.period_start})"


class SalesReport(models.Model):
    """Satış raporları"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='sales_reports')
    report_date = models.DateField()
    
    # Günlük metrikler
    total_orders = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    
    # Ürün performansı
    top_selling_product = models.CharField(max_length=200, blank=True)
    top_selling_category = models.CharField(max_length=100, blank=True)
    
    # Zaman analizi
    peak_hour = models.TimeField(null=True, blank=True)
    average_preparation_time = models.IntegerField(default=0)  # Dakika
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['business', 'report_date']
    
    def __str__(self):
        return f"{self.business.business_name} - Sales Report {self.report_date}"


class CustomerAnalytics(models.Model):
    """Müşteri analitikleri"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='customer_analytics')
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Müşteri segmentasyonu
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    churned_customers = models.IntegerField(default=0)
    
    # Müşteri değeri
    average_customer_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    customer_lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Memnuniyet
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    satisfaction_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['business', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.business.business_name} - Customer Analytics ({self.period_start})"


class BusinessDashboard(models.Model):
    """İşletme dashboard verileri"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='dashboard_data')
    date = models.DateField()
    
    # KPI'lar
    daily_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    daily_orders = models.IntegerField(default=0)
    daily_customers = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # %
    
    # Trend göstergeleri
    revenue_trend = models.CharField(max_length=20, blank=True)  # 'up', 'down', 'stable'
    orders_trend = models.CharField(max_length=20, blank=True)
    customers_trend = models.CharField(max_length=20, blank=True)
    
    # Uyarılar
    alerts = models.JSONField(default=list, blank=True)  # Düşük performans uyarıları
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['business', 'date']
    
    def __str__(self):
        return f"{self.business.business_name} - Dashboard {self.date}"


class Goal(models.Model):
    """Hedefler ve hedefler"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric_type = models.CharField(max_length=20, choices=MetricType.choices)
    target_value = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    deadline = models.DateField()
    is_achieved = models.BooleanField(default=False)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.title}"
