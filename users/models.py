from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('officer', 'Officer'),
        ('collector', 'Collector'),
        ('vendor', 'Vendor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


class VendorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='vendor_profile'
    )
    shop_name = models.CharField(max_length=100)
    ward = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    qr_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.shop_name} - Ward {self.ward}"


class PickupLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('collected', 'Collected'),
        ('disputed', 'Disputed'),
    ]
    collector = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='collections'
    )
    vendor = models.ForeignKey(
        VendorProfile, on_delete=models.CASCADE, related_name='pickups'
    )
    declared_weight = models.FloatField(default=0.0)
    verified_weight = models.FloatField(null=True, blank=True)
    photo = models.ImageField(upload_to='pickups/', null=True, blank=True)
    qr_scanned = models.BooleanField(default=False)
    collector_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    collector_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    is_flagged = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.collector} → {self.vendor} [{self.status}]"
