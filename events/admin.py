from django.contrib import admin
from .models import Event , TicketType, Order,OrderItem

class EventAdmin(admin.ModelAdmin):
    list_display = ['title','capacity']

class TicketAdmin(admin.ModelAdmin):
    list_display = ['event', 'name', 'price', 'capacity']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'status', 'created_at']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'ticket_type', 'quantity', 'price']



admin.site.register(Event,EventAdmin)
admin.site.register(TicketType,TicketAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
# Register your models here.
