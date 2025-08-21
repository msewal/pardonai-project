from django.conf import settings
from django.db import models

class Businesses(models.Model):
    business_name = models.CharField(max_length=128)

class BusinessRole(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    VIEWER = "viewer", "Viewer"

class BusinessMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    business = models.ForeignKey(Businesses, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=BusinessRole.choices, default=BusinessRole.ADMIN)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "business")

    def __str__(self):
        return f"{self.user} @ {self.business.business_name} ({self.role})"



# Aşağıdaki satırları terminalde çalıştırın:
# python manage.py makemigrations accounts
# python manage.py migrate