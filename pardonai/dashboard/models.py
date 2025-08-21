from django.db import models


class ProductMetric(models.Model):
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=128)
    click = models.IntegerField()
    sales = models.IntegerField()
    click_per_sale = models.FloatField()
    cost = models.FloatField()
    sales_price = models.FloatField()
    unit_profit = models.FloatField()
    total_profit = models.FloatField()
    profit_per_click = models.FloatField()
    ts = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'product_metric'


class ServiceType(models.TextChoices):
    BASIC = "Basic", "Basic"
    PARDON_PLUS = "Pardon+", "Pardon+"
    ELITE = "Elite", "Elite"


class ServiceDuration(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class PosSystemStatus(models.TextChoices):
    NONE = "none", "None"
    SOFTWARE_ONLY = "software_only", "Software Only"
    FULL_SYSTEM = "full_system", "Full System"


class PosDuration(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class BusinessType(models.TextChoices):
    RESTAURANT = "restaurant", "Restaurant"
    CAFE = "cafe", "Cafe"
    HOTEL = "hotel", "Hotel"
    BEACH = "beach", "Beach"
    BAR = "bar", "Bar"


class Status(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class Businesses(models.Model):
    business_id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    owner_first_name = models.CharField(max_length=100)
    owner_last_name = models.CharField(max_length=100)
    business_phone = models.CharField(max_length=20)
    owner_phone = models.CharField(max_length=20)
    interest_solutions = models.TextField()
    subject = models.CharField(max_length=255)
    interest_products = models.TextField()
    email = models.EmailField(unique=True)
    notes = models.TextField(null=True, blank=True)
    qr_code_url = models.CharField(max_length=255, null=True, blank=True)
    service_type = models.CharField(
        max_length=20, choices=ServiceType.choices, default=ServiceType.BASIC
    )
    service_duration = models.CharField(
        max_length=10, choices=ServiceDuration.choices, default=ServiceDuration.MONTHLY
    )
    service_start_date = models.DateField(null=True, blank=True)
    service_end_date = models.DateField(null=True, blank=True)
    pos_system_status = models.CharField(
        max_length=20, choices=PosSystemStatus.choices, default=PosSystemStatus.NONE
    )
    pos_duration = models.CharField(
        max_length=10, choices=PosDuration.choices, null=True, blank=True
    )
    pos_start_date = models.DateField(null=True, blank=True)
    pos_end_date = models.DateField(null=True, blank=True)
    tax_number = models.CharField(max_length=50, unique=True)
    business_type = models.CharField(
        max_length=20, choices=BusinessType.choices, default=BusinessType.RESTAURANT
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    registration_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name 