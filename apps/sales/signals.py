from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SaleInvoiceOrders

@receiver(post_save, sender=SaleInvoiceOrders)
def update_balance_amount(sender, instance, created, **kwargs):
    """
    Signal to update balance_amount with total_amount when a new SaleInvoiceOrders record is created.
    """
    if created:  # Ensure it's a new record
        instance.balance_amount = instance.total_amount  # Copy total_amount to balance_amount
        instance.save(update_fields=['balance_amount'])  # Save only the balance_amount field
