from django.db import models
from pardonai.dashboard.models import Businesses as CoreBusinesses


class Category(models.Model):
    """Menü kategorileri"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome icon class
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class Menu(models.Model):
    """İşletme menüleri"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)  # Varsayılan menü
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.name}"


class Product(models.Model):
    """Menü ürünleri"""
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  # Öne çıkan ürün
    sort_order = models.IntegerField(default=0)
    
    # Besin değerleri
    calories = models.IntegerField(null=True, blank=True)
    protein = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    carbs = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'sort_order', 'name']
    
    def __str__(self):
        return f"{self.menu.name} - {self.name}"


class Extra(models.Model):
    """Ekstra ürünler (sos, içecek vb.)"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='extras')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.name}"


class ProductExtra(models.Model):
    """Ürün-ekstra ilişkisi"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='available_extras')
    extra = models.ForeignKey(Extra, on_delete=models.CASCADE, related_name='products')
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # Fiyat değişimi
    
    class Meta:
        unique_together = ['product', 'extra']
    
    def __str__(self):
        return f"{self.product.name} + {self.extra.name}"
