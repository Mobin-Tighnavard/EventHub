from celery import shared_task
from .models import Order
from django.utils import timezone

@shared_task
def expire_pending_orders():
    now = timezone.now()
    updated_count = Order.objects.filter(
        status = Order.Status.PENDING,
        expires_at__lte = now
    ).update(status=Order.Status.EXPIRED,
             updated_at = now)
    return updated_count