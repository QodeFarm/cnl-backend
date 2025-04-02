from .models import SaleInvoiceOrders, PaymentTransactions
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

@receiver(post_save, sender=SaleInvoiceOrders)
def update_balance_after_invoice(sender, instance, created, **kwargs):
    """
    Signal to update balance_amount with total_amount when a new SaleInvoiceOrders record is created.
    """
    if created:  # Ensure it's a new record
        instance.balance_amount = instance.total_amount  # Copy total_amount to balance_amount
        instance.save(update_fields=['balance_amount'])  # Save only the balance_amount field


@receiver(post_save, sender=PaymentTransactions)
def update_Sale_Invoice_balance_after_payment_transaction(sender, instance, created, **kwargs):
    """
    Signal to update paid_amount with amount and balance_amount with outstanding_amount when a new PaymentTransactions record is created.
    """
    if created:
        with transaction.atomic():
            sale_invoice_id = instance.sale_invoice_id
            
            try:
                # Retrieving the related SaleInvoiceOrders record
                sale_invoice_orders_data = SaleInvoiceOrders.objects.get(sale_invoice_id=sale_invoice_id)
            except ObjectDoesNotExist:
                logger.info(f"SaleInvoiceOrders with sale_invoice_id {sale_invoice_id} does not exist.")
                return
            
            # Calling the model method to update balance and paid amount
            sale_invoice_orders_data.update_paid_amount_balance_amount_after_payment_transactions(instance.amount, instance.outstanding_amount)