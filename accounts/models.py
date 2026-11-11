from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER" , "Customer"
        ORGANIZER = "ORGANIZER" , "Organizer"
        ADMIN = "ADMIN" , "Admin"
    role = models.CharField(max_length=20,choices=Role.choices,default=Role.CUSTOMER)
# Create your models here.
