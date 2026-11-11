from django.db import models
from django.conf import settings

class Event(models.Model):
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='event',
        null=True,blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Status(models.TextChoices):
        DRAFT = "DRAFT" , "Draft"
        PUBLISHED = "PUBLISHED" , "published"
        FINISHED = "FINISHED" , "Finished"
        CANCELED = "CANCELED" , "Canceled"


    status = models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)

    def __str__(self):
        return self.title

class TicketType(models.Model):
    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING" , "Pending"
        PAID = "PAID" , "Paid"
        CANCELED = "CANCELED" , "Canceled"
        EXPIRED = "EXPIRED" , "Expired"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='orders')
    status = models.CharField(max_length=10, choices=Status.choices,default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"order {self.id} - {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order , on_delete = models.PROTECT,related_name='items')

    ticket_type = models.ForeignKey(TicketType, on_delete = models.PROTECT,related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.ticket_type.name} x {self.quantity}"
# Create your models here.
