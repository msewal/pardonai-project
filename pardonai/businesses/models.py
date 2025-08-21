from django.db import models
from pardonai.dashboard.models import Businesses as CoreBusinesses, ServiceType, ServiceDuration, BusinessType, Status


class BusinessProfile(models.Model):
    """İşletme profil bilgileri"""
    business = models.OneToOneField(CoreBusinesses, on_delete=models.CASCADE, related_name='profile')
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    social_media = models.JSONField(default=dict, blank=True)  # Instagram, Facebook, Twitter vb.
    operating_hours = models.JSONField(default=dict, blank=True)
    special_features = models.TextField(blank=True)  # Özel özellikler (WiFi, otopark vb.)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business.business_name} - Profile"


class BusinessContact(models.Model):
    """İşletme iletişim bilgileri"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=50)  # 'phone', 'email', 'address'
    contact_value = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.contact_type}"


class BusinessDocument(models.Model):
    """İşletme belgeleri"""
    business = models.ForeignKey(CoreBusinesses, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=100)  # 'contract', 'invoice', 'license' vb.
    file = models.FileField(upload_to='business_documents/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.business.business_name} - {self.title}"
