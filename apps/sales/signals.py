from apps.finance.models import JournalEntryLines, ChartOfAccounts
from .models import SaleInvoiceOrders, PaymentTransactions
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Sum
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

@receiver(post_save, sender=SaleInvoiceOrders)
def update_balance_after_invoice(sender, instance, created, **kwargs):
    """
    Signal to update pending_amount with total_amount when a new SaleInvoiceOrders record is created.
    """
    if created:  # Ensuring it's a new record
        instance.pending_amount = instance.total_amount  # Copy total_amount to pending_amount
        instance.save(update_fields=['pending_amount'])  # Save only the pending_amount field

        # Step 2: Calculating total pending (balance_amount) for that customer
        total_pending = SaleInvoiceOrders.objects.filter(customer_id=instance.customer_id).aggregate(
            total_pending=Sum('pending_amount'))['total_pending'] or 0.00

        # Step 3: Get "sale account" from ChartOfAccounts
        try:
            sale_account = ChartOfAccounts.objects.get(account_name__iexact="Sale Account", is_active=True)
        except ChartOfAccounts.DoesNotExist:
            sale_account = None  

        # Step 3: Creating JournalEntryLines record
        JournalEntryLines.objects.create(
            account_id=sale_account,  
            debit=instance.total_amount,
            voucher_no = instance.invoice_no,
            credit=0.00,
            description=f"Goods sold to {instance.customer_id.name}",
            customer_id=instance.customer_id,
            balance=total_pending
        )


@receiver(post_save, sender=PaymentTransactions)
def update_Sale_Invoice_balance_after_payment_transaction(sender, instance, created, **kwargs):
    """
    Signal to update paid_amount with amount and pending_amount with outstanding_amount when a new PaymentTransactions record is created.
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
            sale_invoice_orders_data.update_paid_amount_balance_amount_after_payment_transactions(instance.amount, instance.outstanding_amount, instance.adjusted_now)