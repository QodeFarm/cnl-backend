"""
Journal Voucher Signals - Auto-create JournalEntryLines (Account Ledger entries)

Similar to how Sales (SaleInvoiceOrders, PaymentTransactions, etc.) creates 
JournalEntryLines records for Account Ledger, this module handles:

1. JournalVoucher CREATE - Creates JournalEntryLines for each voucher line
2. JournalVoucher UPDATE - Updates corresponding JournalEntryLines
3. JournalVoucher DELETE - Soft-deletes corresponding JournalEntryLines

Tables/Models involved:
- JournalVoucher (Header)
- JournalVoucherLine (Line items with Debit/Credit)
- JournalEntryLines (Account Ledger - target table for all financial entries)
- LedgerAccounts (Ledger account reference)
- Customer, Vendor (Party references)

API Endpoints:
- POST /api/v1/finance/journal_vouchers/ - Creates voucher + auto-creates ledger entries
- PUT /api/v1/finance/journal_vouchers/<pk>/ - Updates voucher + updates ledger entries
- DELETE /api/v1/finance/journal_vouchers/<pk>/ - Soft deletes voucher + ledger entries
"""

from decimal import Decimal, InvalidOperation
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Sum
import logging

from .models import JournalVoucher, JournalVoucherLine, JournalEntryLines

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)


def get_existing_balance(customer_id=None, vendor_id=None, ledger_account_id=None):
    """
    Get existing balance for customer/vendor/ledger account from JournalEntryLines.
    Similar pattern used in apps.sales.signals.
    """
    try:
        queryset = JournalEntryLines.objects.filter(is_deleted=False)
        
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        elif vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
        elif ledger_account_id:
            queryset = queryset.filter(ledger_account_id=ledger_account_id)
        else:
            return Decimal('0.00')
        
        existing_balance = (queryset
                          .order_by('-created_at')
                          .values_list('balance', flat=True)
                          .first()) or Decimal('0.00')
        
        return Decimal(existing_balance)
    except (InvalidOperation, TypeError, ValueError) as e:
        logger.error(f"Error getting existing balance: {str(e)}")
        return Decimal('0.00')


def calculate_new_balance(existing_balance, debit_amount, credit_amount):
    """
    Calculate new balance after debit/credit entry.
    Balance increases with Debit, decreases with Credit.
    """
    return Decimal(existing_balance) + Decimal(debit_amount) - Decimal(credit_amount)


@receiver(post_save, sender=JournalVoucherLine)
def create_ledger_entry_on_voucher_line_save(sender, instance, created, **kwargs):
    """
    Signal to create/update JournalEntryLines when a JournalVoucherLine is saved.
    
    This ensures every Journal Voucher line item is reflected in the Account Ledger
    (JournalEntryLines table), similar to how Sales operations work.
    
    Flow:
    1. Get the parent JournalVoucher details
    2. Calculate existing balance for customer/vendor/ledger
    3. Calculate new balance based on Debit/Credit
    4. Create JournalEntryLines record
    """
    try:
        # Get the parent voucher
        voucher = instance.journal_voucher_id
        
        if not voucher:
            logger.warning(f"JournalVoucherLine {instance.journal_voucher_line_id} has no parent voucher")
            return
        
        # Skip if voucher is deleted
        if voucher.is_deleted:
            return
        
        # Determine debit and credit amounts
        debit_amount = instance.amount if instance.entry_type == 'Debit' else Decimal('0.00')
        credit_amount = instance.amount if instance.entry_type == 'Credit' else Decimal('0.00')
        
        # Get existing balance based on party type
        if instance.customer_id:
            existing_balance = get_existing_balance(customer_id=instance.customer_id)
        elif instance.vendor_id:
            existing_balance = get_existing_balance(vendor_id=instance.vendor_id)
        else:
            existing_balance = get_existing_balance(ledger_account_id=instance.ledger_account_id)
        
        # Calculate new balance
        new_balance = calculate_new_balance(existing_balance, debit_amount, credit_amount)
        
        # Build description
        description = instance.remark or voucher.narration or f"Journal Voucher {voucher.voucher_no}"
        
        if created:
            # CREATE: New JournalEntryLines record
            JournalEntryLines.objects.create(
                ledger_account_id=instance.ledger_account_id,
                voucher_no=voucher.voucher_no,
                debit=debit_amount,
                credit=credit_amount,
                description=description,
                customer_id=instance.customer_id,
                vendor_id=instance.vendor_id,
                balance=new_balance,
                is_deleted=False
            )
            logger.info(f"Created JournalEntryLine for voucher {voucher.voucher_no}, "
                       f"Ledger: {instance.ledger_account_id}, "
                       f"Debit: {debit_amount}, Credit: {credit_amount}")
        else:
            # UPDATE: Find and update existing JournalEntryLines record
            # Match by voucher_no and ledger_account_id
            existing_entry = JournalEntryLines.objects.filter(
                voucher_no=voucher.voucher_no,
                ledger_account_id=instance.ledger_account_id,
                customer_id=instance.customer_id,
                vendor_id=instance.vendor_id,
                is_deleted=False 
            ).first()
            
            if existing_entry:
                existing_entry.debit = debit_amount
                existing_entry.credit = credit_amount
                existing_entry.description = description
                existing_entry.balance = new_balance
                existing_entry.save()
                logger.info(f"Updated JournalEntryLine for voucher {voucher.voucher_no}")
            else:
                # Entry doesn't exist, create new one
                JournalEntryLines.objects.create(
                    ledger_account_id=instance.ledger_account_id,
                    voucher_no=voucher.voucher_no,
                    debit=debit_amount,
                    credit=credit_amount,
                    description=description,
                    customer_id=instance.customer_id,
                    vendor_id=instance.vendor_id,
                    balance=new_balance,
                    is_deleted=False
                )
                logger.info(f"Created new JournalEntryLine for updated voucher {voucher.voucher_no}")
                
    except Exception as e:
        logger.error(f"Error creating/updating JournalEntryLine: {str(e)}")


@receiver(pre_delete, sender=JournalVoucherLine)
def soft_delete_ledger_entry_on_voucher_line_delete(sender, instance, **kwargs):
    """
    Signal to soft-delete JournalEntryLines when a JournalVoucherLine is deleted.
    
    This ensures the Account Ledger stays in sync when voucher lines are removed.
    Uses soft delete (is_deleted=True) to maintain audit trail.
    """
    try:
        voucher = instance.journal_voucher_id
        
        if not voucher:
            return
        
        # Find and soft-delete corresponding JournalEntryLines
        JournalEntryLines.objects.filter(
            voucher_no=voucher.voucher_no,
            ledger_account_id=instance.ledger_account_id,
            customer_id=instance.customer_id,
            vendor_id=instance.vendor_id
        ).update(is_deleted=True)
        
        logger.info(f"Soft-deleted JournalEntryLine for voucher {voucher.voucher_no}")
        
    except Exception as e:
        logger.error(f"Error soft-deleting JournalEntryLine: {str(e)}")


@receiver(post_save, sender=JournalVoucher)
def handle_voucher_soft_delete(sender, instance, created, **kwargs):
    """
    Signal to handle JournalVoucher soft delete.
    When is_deleted is set to True, soft-delete all related JournalEntryLines.
    """
    if not created and instance.is_deleted:
        try:
            # Soft-delete all JournalEntryLines for this voucher
            deleted_count = JournalEntryLines.objects.filter(
                voucher_no=instance.voucher_no
            ).update(is_deleted=True)
            
            logger.info(f"Soft-deleted {deleted_count} JournalEntryLines for voucher {instance.voucher_no}")
            
        except Exception as e:
            logger.error(f"Error soft-deleting JournalEntryLines for voucher: {str(e)}")


def create_ledger_entries_for_voucher(voucher_id):
    """
    Utility function to create JournalEntryLines for all lines in a voucher.
    Can be called manually or from views after bulk operations.
    
    Args:
        voucher_id: UUID of the JournalVoucher
        
    Returns:
        Number of entries created
    """
    try:
        voucher = JournalVoucher.objects.get(pk=voucher_id)
        voucher_lines = JournalVoucherLine.objects.filter(journal_voucher_id=voucher_id)
        
        entries_created = 0
        
        for line in voucher_lines:
            debit_amount = line.amount if line.entry_type == 'Debit' else Decimal('0.00')
            credit_amount = line.amount if line.entry_type == 'Credit' else Decimal('0.00')
            
            # Get existing balance
            if line.customer_id:
                existing_balance = get_existing_balance(customer_id=line.customer_id)
            elif line.vendor_id:
                existing_balance = get_existing_balance(vendor_id=line.vendor_id)
            else:
                existing_balance = get_existing_balance(ledger_account_id=line.ledger_account_id)
            
            new_balance = calculate_new_balance(existing_balance, debit_amount, credit_amount)
            
            description = line.remark or voucher.narration or f"Journal Voucher {voucher.voucher_no}"
            
            # Check if entry already exists
            existing_entry = JournalEntryLines.objects.filter(
                voucher_no=voucher.voucher_no,
                ledger_account_id=line.ledger_account_id,
                customer_id=line.customer_id,
                vendor_id=line.vendor_id
            ).first()
            
            if not existing_entry:
                JournalEntryLines.objects.create(
                    ledger_account_id=line.ledger_account_id,
                    voucher_no=voucher.voucher_no,
                    debit=debit_amount,
                    credit=credit_amount,
                    description=description,
                    customer_id=line.customer_id,
                    vendor_id=line.vendor_id,
                    balance=new_balance,
                    is_deleted=False
                )
                entries_created += 1
        
        logger.info(f"Created {entries_created} JournalEntryLines for voucher {voucher.voucher_no}")
        return entries_created
        
    except JournalVoucher.DoesNotExist:
        logger.error(f"JournalVoucher {voucher_id} not found")
        return 0
    except Exception as e:
        logger.error(f"Error creating ledger entries for voucher: {str(e)}")
        return 0


def delete_ledger_entries_for_voucher(voucher_no):
    """
    Utility function to soft-delete all JournalEntryLines for a voucher.
    Called when deleting a JournalVoucher.
    
    Args:
        voucher_no: Voucher number string
        
    Returns:
        Number of entries soft-deleted
    """
    try:
        deleted_count = JournalEntryLines.objects.filter(
            voucher_no=voucher_no
        ).update(is_deleted=True)
        
        logger.info(f"Soft-deleted {deleted_count} JournalEntryLines for voucher {voucher_no}")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error deleting ledger entries for voucher: {str(e)}")
        return 0
