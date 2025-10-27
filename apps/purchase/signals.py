from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal, InvalidOperation
from django.db.models import Sum, F

from .models import PurchaseInvoiceOrders, BillPaymentTransactions
from apps.finance.models import JournalEntryLines, ChartOfAccounts
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@receiver(post_save, sender=PurchaseInvoiceOrders)
def update_pending_amount_after_invoice_creation(sender, instance, created, **kwargs):
    """
    When a new PurchaseInvoiceOrders is created, initialize pending_amount = total_amount.
    Also create a Journal Entry for purchase expense.
    """
    if created:
        instance.pending_amount = instance.total_amount
        instance.save(update_fields=['pending_amount'])

        # Fetch existing balance (most recent)
        existing_balance = (
            JournalEntryLines.objects.filter(vendor_id=instance.vendor_id)
            .order_by('is_deleted', '-created_at')
            .values_list('balance', flat=True)
            .first()
        ) or Decimal('0.00')

        # Vendor owes us (increase payable)
        new_balance = Decimal(existing_balance) + Decimal(instance.total_amount)

        # Fetch Purchase Account
        try:
            purchase_account = ChartOfAccounts.objects.get(account_name__iexact="Purchase Account", is_active=True)
        except ChartOfAccounts.DoesNotExist:
            purchase_account = None

        # Create Journal Entry
        JournalEntryLines.objects.create(
            account_id=purchase_account,
            debit=instance.total_amount,
            voucher_no=instance.invoice_no,
            credit=0.00,
            description=f"Goods purchased from {instance.vendor_id.name}",
            vendor_id=instance.vendor_id,
            balance=new_balance
        )

        logger.info(f"Pending amount initialized for purchase invoice {instance.invoice_no} = {instance.total_amount}")


@receiver(post_save, sender=BillPaymentTransactions)
def update_purchase_invoice_balance_after_bill_payment(sender, instance, created, **kwargs):
    """
    When a new BillPaymentTransactions is created, update PurchaseInvoiceOrders' paid_amount and pending_amount.
    """
    if created:
        with transaction.atomic():
            purchase_invoice = instance.purchase_invoice

            try:
                # Ensure invoice exists
                purchase_invoice_obj = PurchaseInvoiceOrders.objects.get(purchase_invoice_id=purchase_invoice.purchase_invoice_id)
            except ObjectDoesNotExist:
                logger.warning(f"PurchaseInvoiceOrders not found for BillPaymentTransactions {instance.transaction_id}")
                return

            # Call model method to update amounts
            purchase_invoice_obj.update_paid_amount_and_pending_amount_after_bill_payment(
                payment_amount=instance.adjusted_now or instance.total_amount,
                outstanding_amount=instance.outstanding_amount,
                adjusted_now_amount=instance.adjusted_now or 0
            )

            logger.info(f"Updated PurchaseInvoice {purchase_invoice_obj.invoice_no} after bill payment of {instance.adjusted_now}.")


# @receiver(post_save, sender=PurchaseReturnOrders)
# def update_balance_after_purchase_return(sender, instance, created, **kwargs):
#     """
#     When a PurchaseReturnOrders is created, update the vendor balance and Journal Entry.
#     """
#     if created:
#         try:
#             existing_balance = (
#                 JournalEntryLines.objects.filter(vendor_id=instance.vendor_id)
#                 .order_by('is_deleted', '-created_at')
#                 .values_list('balance', flat=True)
#                 .first()
#             ) or Decimal('0.00')

#             new_balance = Decimal(existing_balance) - Decimal(instance.total_amount)

#             purchase_account = ChartOfAccounts.objects.filter(account_name__iexact="Purchase Account", is_active=True).first()

#             JournalEntryLines.objects.create(
#                 account_id=purchase_account,
#                 debit=0.00,
#                 voucher_no=instance.return_no,
#                 credit=instance.total_amount,
#                 description=f"Purchase return to {instance.vendor_id.name} ({instance.return_reason})",
#                 vendor_id=instance.vendor_id,
#                 balance=new_balance
#             )

#         except (ChartOfAccounts.DoesNotExist, InvalidOperation, TypeError, ValueError) as e:
#             logger.error(f"Error in PurchaseReturn signal: {e}")


# @receiver(post_save, sender=PurchaseDebitNotes)
# def update_balance_after_debit_note(sender, instance, created, **kwargs):
#     """
#     When a new PurchaseDebitNote record is created, adjust vendor balance accordingly.
#     """
#     if created:
#         try:
#             existing_balance = (
#                 JournalEntryLines.objects.filter(vendor_id=instance.vendor_id)
#                 .order_by('is_deleted', '-created_at')
#                 .values_list('balance', flat=True)
#                 .first()
#             ) or Decimal('0.00')

#             new_balance = Decimal(existing_balance) - Decimal(instance.total_amount)

#             purchase_account = ChartOfAccounts.objects.filter(account_name__iexact="Purchase Account", is_active=True).first()

#             JournalEntryLines.objects.create(
#                 account_id=purchase_account,
#                 debit=0.00,
#                 voucher_no=instance.debit_note_number,
#                 credit=instance.total_amount,
#                 description=f"Purchase debit note from {instance.vendor_id.name} ({instance.reason})",
#                 vendor_id=instance.vendor_id,
#                 balance=new_balance
#             )

#         except (ChartOfAccounts.DoesNotExist, InvalidOperation, TypeError, ValueError) as e:
#             logger.error(f"Error in PurchaseDebitNotes signal: {e}")
