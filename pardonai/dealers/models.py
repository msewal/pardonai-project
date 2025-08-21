from django.db import models
from pardonai.dashboard.models import Businesses as CoreBusinesses


class Dealer(models.Model):
    """Bayiler"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='dealers')
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    region = models.CharField(max_length=100)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Komisyon oranı (%)
    is_active = models.BooleanField(default=True)
    
    # Performans metrikleri
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    customer_count = models.IntegerField(default=0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.name}"


class DealerExperience(models.Model):
    """Bayi deneyimleri"""
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=200)
    description = models.TextField()
    experience_date = models.DateField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 arası puan
    customer_feedback = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)  # Müşteri yorumları için
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.dealer.name} - {self.title}"


class DealerCommission(models.Model):
    """Bayi komisyon kayıtları"""
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='commissions')
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    order_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.dealer.name} - {self.commission_amount} TL"


class DealerPerformance(models.Model):
    """Bayi performans metrikleri"""
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='performance_records')
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Metrikler
    total_orders = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    customer_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # 0-5 arası
    response_time = models.IntegerField(default=0)  # Dakika cinsinden
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['dealer', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.dealer.name} - {self.period_start} to {self.period_end}"
