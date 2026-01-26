from django.db import models
import uuid
from apps.hrms.models import Employees
from config.utils_methods import OrderNumberMixin, generate_order_number
from config.utils_variables import bankaccounts, chartofaccounts, journalentries, journalentrylines, paymenttransaction, taxconfigurations, budgets, expenseclaims, financialreports, journaldetail, journal, expenseitems, journalvouchers, journalvoucherlines, journalvoucherattachments
from apps.customer.models import Customer, LedgerAccounts
from apps.vendor.models import Vendor

# Create your models here.

class BankAccount(models.Model):
    bank_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_name = models.CharField(max_length=100, null=False)
    account_number = models.CharField(max_length=50, unique=True, null=False)
    bank_name = models.CharField(max_length=100, null=False)
    branch_name = models.CharField(max_length=100, default=None, null=True)
    ifsc_code = models.CharField(max_length=100, null=False)
    account_type = models.CharField(
        max_length=7,
        choices=[('Current', 'Current'), ('Savings', 'Savings')],
        default='Savings',
        null=False
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2, null=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = bankaccounts

    def __str__(self):
        return f"{self.bank_name}"

class ChartOfAccounts(models.Model):
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_code = models.CharField(max_length=20, unique=True, null=False)
    account_name = models.CharField(max_length=100, null=False)
    account_type = models.CharField(
        max_length=10,
        choices=[('Asset', 'Asset'), ('Equity', 'Equity'), ('Expense', 'Expense'), ('Liability', 'Liability'), ('Revenue', 'Revenue')],
        null=False
    )
    parent_account_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, default=None, related_name='sub_accounts', db_column='parent_account_id')
    is_active = models.BooleanField(default=True)
    bank_account_id = models.ForeignKey(BankAccount, on_delete=models.PROTECT, null=True, default=None, related_name='linked_accounts', db_column='bank_account_id')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = chartofaccounts

    def __str__(self):
        return f"{self.account_name}"  
class JournalEntry(OrderNumberMixin):
    journal_entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry_date = models.DateField(null=False)
    voucher_no = models.CharField(max_length=100, unique=True, default='')  
    order_no_prefix = 'JE'  # Journal Entry prefix
    order_no_field = 'voucher_no'  # Field to store the order number
    VOUCHER_TYPE_CHOICES = [
    ('CommonVoucher', 'CommonVoucher'),
    ('ExpenseVoucher', 'ExpenseVoucher'),
    ('IncomeVoucher', 'IncomeVoucher'),
    ('ReceiptVoucher', 'ReceiptVoucher'),
    ('AdvanceReceiptVoucher', 'AdvanceReceiptVoucher'),
    ('ReceiptRefundVoucher', 'ReceiptRefundVoucher'),
    ('PaymentVoucher', 'PaymentVoucher'),
    ('AdvancePaymentVendorVoucher', 'AdvancePaymentVendorVoucher'),
    ('PaymentRefundVoucher', 'PaymentRefundVoucher'),
        ]
    voucher_type = models.CharField(max_length=30, choices=VOUCHER_TYPE_CHOICES, default='CommonVoucher')
    cash_bank_posting = models.CharField(max_length=10, choices=[('Single', 'Single'), ('LineWise', 'LineWise')], default='Single')
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT, null=True, db_column='ledger_account_id')
    reference = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(default=None, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = journalentries

    def __str__(self):
        return f"{self.entry_date} - {self.voucher_no}"    
    
    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number
        
        # Determine if this is a new record
        is_new_record = self._state.adding
        
        # Only generate and set the voucher number if this is a new record AND voucher_no is not set
        if is_new_record and not self.voucher_no:
            order_number = generate_order_number(
                self.order_no_prefix,
                model_class=JournalEntry,
                field_name='voucher_no'
            )
            self.voucher_no = order_number
            
            # Save the record
            super().save(*args, **kwargs)
            
            # After saving, increment the order number sequence
            print(f"Creating new journal entry: {self.voucher_no}")
            increment_order_number(self.order_no_prefix)
        else:
            # For updates, just save without generating new voucher_no
            super().save(*args, **kwargs)
            if not is_new_record:
                print(f"Updating existing journal entry: {self.voucher_no}")
    

class JournalEntryLines(models.Model):
    journal_entry_line_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT, null=True, related_name='journal_entry_lines', db_column='ledger_account_id')
    voucher_no = models.CharField(max_length=20)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.CharField(max_length=1024, default=None, null=True)
    customer_id  = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, db_column='customer_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.PROTECT, null=True, db_column='vendor_id')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    journal_entry_id = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='entry_lines', db_column='journal_entry_id')
    
    class Meta:
        db_table = journalentrylines

    def __str__(self):
        return f"Line {self.journal_entry_line_id} for Entry {self.description}"


class PaymentTransaction(models.Model): # Enhance Later
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_id = models.CharField(max_length=36, null=False)  # Foreign key will depend on specific implementation
    order_type = models.CharField(   # order_type
        max_length=10,
        choices=[('Purchase', 'Purchase'),('Sale', 'Sale')],
        null=False
    )
    payment_date = models.DateField(null=False)
    payment_method = models.CharField(
    max_length=20,
    choices=[
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash', 'Cash'),        
        ('Cheque', 'Cheque'),
        ('Credit Card', 'Credit Card'),
    ],
    null=False
    )
    payment_status = models.CharField(
        max_length=10,
        choices=[
            ('Completed', 'Completed'),
            ('Failed', 'Failed'),
            ('Pending', 'Pending'),            
        ],
        default='Pending',
        null=False
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=False)
    reference_number = models.CharField(max_length=100, default=None, null=True)
    notes = models.CharField(max_length=512, default=None, null=True)
    currency = models.CharField(max_length=10, default=None, null=True)
    transaction_type = models.CharField(max_length=10, choices=[('Credit', 'Credit'), ('Debit', 'Debit')], default='Credit',null=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = paymenttransaction

    def __str__(self):
        return f"Payment {self.payment_id} for Invoice {self.invoice_id}"

class TaxConfiguration(models.Model):
    tax_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tax_name = models.CharField(max_length=100, null=False)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    PERCENTAGE = 'Percentage'
    FIXED = 'Fixed'
    TAX_TYPE_CHOICES = [
        (FIXED, 'Fixed'),
        (PERCENTAGE, 'Percentage'),
    ]
    tax_type = models.CharField(max_length=10, choices=TAX_TYPE_CHOICES, null=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = taxconfigurations

    def __str__(self):
        return f"{self.tax_name} ({self.tax_rate}{'%' if self.tax_type == 'Percentage' else ''})"

class Budget(models.Model):
    budget_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='budgets', db_column='account_id')
    fiscal_year = models.PositiveIntegerField(null=False)
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2, null=False)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = budgets

    def __str__(self):
        # return f"Budget for {self.account.account_name} - Fiscal Year {self.fiscal_year}"
        return f"Budget for {self.account_id.account_name if self.account_id else 'Unknown'} - Fiscal Year {self.fiscal_year}"



class ExpenseClaim(models.Model):
    expense_claim_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.PROTECT, related_name='expense_claims', db_column='employee_id')
    claim_date = models.DateField(null=False)
    description = models.CharField(max_length=1024, default=None, null=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=False)
    APPROVED = 'Approved'
    PENDING = 'Pending'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
        (REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = expenseclaims

    def __str__(self):
        return f"Expense Claim {self.expense_claim_id} by Employee {self.employee_id}"

class FinancialReport(models.Model):
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_name = models.CharField(max_length=100, null=False)
    BALANCE_SHEET = 'Balance Sheet'
    CASH_FLOW = 'Cash Flow'
    PROFIT_LOSS = 'Profit & Loss'
    TRIAL_BALANCE = 'Trial Balance'
    REPORT_TYPE_CHOICES = [
        (BALANCE_SHEET, 'Balance Sheet'),
        (CASH_FLOW, 'Cash Flow'),
        (PROFIT_LOSS, 'Profit & Loss'),
        (TRIAL_BALANCE, 'Trial Balance'),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, null=False)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = financialreports

    def __str__(self):
        return f"Report: {self.report_name} ({self.report_type})"

class Journal(models.Model):
    journal_id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True, null=True)
    total_debit = models.DecimalField(max_digits=18, decimal_places=2)
    total_credit = models.DecimalField(max_digits=18, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = journal

    def __str__(self):
        return f"Journal {self.journal_id}"
    
class JournalDetail(models.Model):
    journal_detail_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    journal_id = models.ForeignKey(Journal, related_name="journal_details", on_delete=models.PROTECT, db_column='journal_id')
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT,  db_column='ledger_account_id')

    class Meta:
        db_table = journaldetail

    def __str__(self):
        return f"Journal Detail {self.journal_detail_id}"
    
    
# class ExpenseCategory(models.Model):
#     category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     category_name = models.CharField(max_length=100, null=False)
#     description = models.CharField(max_length=255, default=None, null=True)
#     account_id = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='expense_categories', db_column='account_id', null=True)
#     is_active = models.BooleanField(default=True)
#     is_deleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = expensecategories

#     def __str__(self):
#         return f"{self.category_name}"

class ExpenseItem(models.Model):
    expense_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense_date = models.DateField(null=False)
    description = models.CharField(max_length=255, default=None, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=False)
    receipt_image = models.ImageField(upload_to='expenses/receipts/', null=True, blank=True)
    
    # Link to category
    # category_id = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expense_items', db_column='category_id', null=True)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT, related_name='expense_items', db_column='ledger_account_id', null=True)

    
    # If expense is linked to a bank account
    bank_account_id = models.ForeignKey(BankAccount, on_delete=models.PROTECT, null=True, related_name='expenses', db_column='bank_account_id')
    
    # If expense is linked to a vendor
    vendor_id = models.ForeignKey(Vendor, on_delete=models.PROTECT, null=True, db_column='vendor_id')
    
    # If expense is made by an employee
    employee_id = models.ForeignKey(Employees, on_delete=models.PROTECT, null=True, db_column='employee_id')
    
    # If expense is part of a claim
    expense_claim_id = models.ForeignKey(ExpenseClaim, on_delete=models.PROTECT, null=True, related_name='expense_items', db_column='expense_claim_id')
    
    # Expense status
    PAID = 'Paid'
    PENDING = 'Pending'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (PAID, 'Paid'),
        (PENDING, 'Pending'),
        (REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    
    # Payment details
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('Bank Transfer', 'Bank Transfer'),
            ('Cash', 'Cash'),        
            ('Cheque', 'Cheque'),
            ('Credit Card', 'Credit Card'),
        ],
        null=True
    )
    
    reference_number = models.CharField(max_length=100, default=None, null=True)
    
    # Budget tracking
    budget_id = models.ForeignKey(Budget, on_delete=models.PROTECT, null=True, db_column='budget_id')
    
    # For tax calculations
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_taxable = models.BooleanField(default=True)
    tax_id = models.ForeignKey(TaxConfiguration, on_delete=models.PROTECT, null=True, db_column='tax_id')
    
    # Recurring expense
    is_recurring = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=10,
        choices=[
            ('Daily', 'Daily'),
            ('Weekly', 'Weekly'),
            ('Monthly', 'Monthly'),
            ('Quarterly', 'Quarterly'),
            ('Yearly', 'Yearly'),
        ],
        null=True, blank=True
    )
    next_recurrence_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = expenseitems

    def __str__(self):
        return f"Expense {self.expense_item_id} - {self.amount} on {self.expense_date}"


# ======================================
# JOURNAL VOUCHER MODELS
# ======================================
"""
Journal Voucher - Used for recording accounting entries in the general ledger.
Real-time scenarios:
1. Expense Recording - Recording business expenses (rent, utilities, salaries)
2. Adjusting Entries - Month-end/year-end adjustments
3. Inter-Account Transfers - Transfer between ledger accounts
4. Depreciation Entries - Record asset depreciation
5. Reversing Entries - Correct previous accounting entries
6. Contra Entries - Cash to bank or bank to cash transfers
7. Opening Balance Entries - Record opening balances for new financial year
8. Advance Receipts/Payments - Recording advances from customers or to vendors
9. TDS/Tax Adjustments - Recording tax deductions and adjustments
10. Provisions - Creating provisions for expenses or bad debts
"""

class JournalVoucher(OrderNumberMixin):
    """
    Main Journal Voucher model - Header information
    Similar to MaterialIssue / SaleOrder pattern
    """
    journal_voucher_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voucher_no = models.CharField(max_length=20, unique=True, default='')
    order_no_prefix = 'JV'
    order_no_field = 'voucher_no'
    voucher_date = models.DateField()
    
    # Voucher Type for categorization
    VOUCHER_TYPE_CHOICES = [
        ('Journal', 'Journal'),
        ('Contra', 'Contra'),
        ('Receipt', 'Receipt'),
        ('Payment', 'Payment'),
        ('DebitNote', 'Debit Note'),
        ('CreditNote', 'Credit Note'),
    ]
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES, default='Journal')
    
    # Reference fields
    reference_no = models.CharField(max_length=50, null=True, default=None)
    reference_date = models.DateField(null=True, default=None)
    
    # Pull from Expense Claim (as shown in screenshot)
    expense_claim_id = models.ForeignKey(ExpenseClaim, on_delete=models.PROTECT, null=True, default=None, db_column='expense_claim_id')
    
    # Narration/Description
    narration = models.TextField(null=True, default=None)
    
    # Total amounts
    total_debit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total_credit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    # Status tracking
    is_posted = models.BooleanField(default=False)  # Whether posted to ledger
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = journalvouchers

    def __str__(self):
        return f"{self.voucher_no} - {self.voucher_date}"
    
    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number
        
        # Determine if this is a new record
        is_new_record = self._state.adding
        
        # Only generate voucher number for new records
        if is_new_record and not self.voucher_no:
            order_number = generate_order_number(
                self.order_no_prefix,
                model_class=JournalVoucher,
                field_name='voucher_no'
            )
            self.voucher_no = order_number
            
            # Save the record
            super().save(*args, **kwargs)
            
            # After saving, increment the order number sequence
            increment_order_number(self.order_no_prefix)
        else:
            super().save(*args, **kwargs)


class JournalVoucherLine(models.Model):
    """
    Journal Voucher Line Items - Individual debit/credit entries
    Similar to MaterialIssueItem / SaleOrderItems pattern
    """
    journal_voucher_line_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_voucher_id = models.ForeignKey(JournalVoucher, on_delete=models.CASCADE, related_name='voucher_lines', db_column='journal_voucher_id')
    
    # Ledger Account (main account for the entry)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT, db_column='ledger_account_id')
    
    # Party details (Customer/Vendor for sub-ledger entries)
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, default=None, db_column='customer_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.PROTECT, null=True, default=None, db_column='vendor_id')
    employee_id = models.ForeignKey(Employees, on_delete=models.PROTECT, null=True, default=None, db_column='employee_id')
    
    # Debit/Credit Type and Amount
    ENTRY_TYPE_CHOICES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES, default='Debit')
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    
    # Bill Adjustment fields
    bill_no = models.CharField(max_length=50, null=True, default=None)
    bill_date = models.DateField(null=True, default=None)
    bill_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    
    # TDS fields
    tds_applicable = models.BooleanField(default=False)
    tds_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)
    tds_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    
    # Investment/Panel flags (as shown in screenshot)
    is_panel = models.BooleanField(default=False)
    is_investment = models.BooleanField(default=False)
    
    # Remark for line item
    remark = models.CharField(max_length=255, null=True, default=None)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = journalvoucherlines

    def __str__(self):
        return f"{self.entry_type} - {self.amount} - {self.ledger_account_id}"


class JournalVoucherAttachment(models.Model):
    """
    Attachments for Journal Voucher
    Similar to MaterialIssueAttachment pattern
    """
    attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_voucher_id = models.ForeignKey(JournalVoucher, on_delete=models.CASCADE, related_name='attachments', db_column='journal_voucher_id')
    attachment_name = models.CharField(max_length=255)
    attachment_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = journalvoucherattachments

    def __str__(self):
        return self.attachment_name
