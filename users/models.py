from django contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
  role_choices = ( 
    ('officer', 'Officer'), ('collector', 'Collector'), ('vendor', 'Vendor')
  )
  role = models.CharField(choices=role_choices)
  phone = models.CharField(max_length=15)
  isVerified = models.BooleanField(default=False)

  def __str__(self):
    return f"{self.username} ({self.role})"
