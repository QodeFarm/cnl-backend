from .models import SaleCreditNotes, SaleInvoiceOrders, PaymentTransactions, SaleReturnOrders
from apps.finance.models import JournalEntryLines, ChartOfAccounts
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from decimal import Decimal, InvalidOperation
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
        # total_pending = SaleInvoiceOrders.objects.filter(customer_id=instance.customer_id).aggregate(total_pending=Sum('pending_amount'))['total_pending'] or 0.00
        existing_balance = (JournalEntryLines.objects.filter(customer_id=instance.customer_id)
                                                                            .order_by('-created_at')                   # most recent entry first
                                                                            .values_list('balance', flat=True)         # get only the balance field
                                                                            .first()) or Decimal('0.00')               # grab the first result
        new_balance =  Decimal(instance.total_amount) + Decimal(existing_balance)

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
            balance=new_balance 
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


from django.db.models import F
@receiver(post_save, sender=SaleCreditNotes)
def update_balance_after_credit(sender, instance, created, **kwargs):
    """
    Signal to update when a new SaleCreditNote record is created.
    """
    if created:  # Ensuring it's a new record
        try:

            existing_balance = (
                JournalEntryLines.objects
                .filter(customer_id=instance.customer_id)       # filter by your customer
                .order_by('-created_at')                   # most recent entry first
                .values_list('balance', flat=True)         # get only the balance field
                .first()                                   # grab the first result
            )or Decimal('0.00')
            bal_amt = Decimal(existing_balance) - Decimal(instance.total_amount)
            sale_account = ChartOfAccounts.objects.get(account_name__iexact="Sale Account", is_active=True)
        
        except ChartOfAccounts.DoesNotExist:
            sale_account = None  
        except (InvalidOperation, TypeError, ValueError) as e:
            return Decimal('0.00')              

        # Step 3: Creating JournalEntryLines record
        print("total_pending ==>", bal_amt)
        JournalEntryLines.objects.create(
            account_id=sale_account,  
            debit=0.00,
            voucher_no = instance.credit_note_number,
            credit=instance.total_amount,
            description=f"Credit note gives to {instance.customer_id.name}",
            customer_id=instance.customer_id,
            balance=bal_amt
        )
        
        
@receiver(post_save, sender=SaleReturnOrders)
def update_balance_after_return(sender, instance, created, **kwargs):
    """
    Signal to update when a new SaleReturnOrders record is created.
    """
    if created:  # Ensuring it's a new record
        try:
            existing_balance = (JournalEntryLines.objects.filter(customer_id=instance.customer_id)
                                                                            .order_by('-created_at')                   # most recent entry first
                                                                            .values_list('balance', flat=True)         # get only the balance field
                                                                            .first() ) or Decimal('0.00')          
            bal_amt = Decimal(existing_balance) - Decimal(instance.total_amount)
            sale_account = ChartOfAccounts.objects.get(account_name__iexact="Sale Account", is_active=True)
        except ChartOfAccounts.DoesNotExist:
            sale_account = None  
        except (InvalidOperation, TypeError, ValueError) as e:
            return Decimal('0.00')          

        # Step 3: Creating JournalEntryLines record
        JournalEntryLines.objects.create(
            account_id=sale_account,  
            debit=instance.total_amount,
            voucher_no = instance.return_no,
            credit=0.00,
            description=f"Return gives to {instance.customer_id.name}",
            customer_id=instance.customer_id,
            balance=bal_amt
        )