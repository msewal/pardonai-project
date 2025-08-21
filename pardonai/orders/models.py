from django.db import models
from pardonai.dashboard.models import Businesses as CoreBusinesses
from pardonai.menu.models import Product, Extra


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Beklemede"
    CONFIRMED = "confirmed", "Onaylandı"
    PREPARING = "preparing", "Hazırlanıyor"
    READY = "ready", "Hazır"
    DELIVERED = "delivered", "Teslim Edildi"
    CANCELLED = "cancelled", "İptal Edildi"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Beklemede"
    PAID = "paid", "Ödendi"
    FAILED = "failed", "Başarısız"
    REFUNDED = "refunded", "İade Edildi"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Nakit"
    CREDIT_CARD = "credit_card", "Kredi Kartı"
    DEBIT_CARD = "debit_card", "Banka Kartı"
    ONLINE = "online", "Online Ödeme"
    MOBILE = "mobile", "Mobil Ödeme"


class Order(models.Model):
    """Sipariş ana tablosu"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    customer_address = models.TextField(blank=True)
    
    # Sipariş detayları
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Durum bilgileri
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, blank=True)
    
    # Zaman bilgileri
    order_date = models.DateTimeField(auto_now_add=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    
    # Notlar
    special_instructions = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.order_number}"


class OrderItem(models.Model):
    """Sipariş kalemleri"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.name} x{self.quantity}"


class OrderItemExtra(models.Model):
    """Sipariş kalemi ekstraları"""
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='extras')
    extra = models.ForeignKey(Extra, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.order_item} + {self.extra.name} x{self.quantity}"


class OrderHistory(models.Model):
    """Sipariş geçmişi"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20, choices=OrderStatus.choices)
    notes = models.TextField(blank=True)
    changed_by = models.CharField(max_length=100, blank=True)  # Kullanıcı adı
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status} at {self.changed_at}"


class Customer(models.Model):
    """Müşteri bilgileri"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # İstatistikler
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_order_date = models.DateTimeField(null=True, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.name}"
