from django.db import models
import uuid
from apps.hrms.models import Employees
from config.utils_variables import bankaccounts, chartofaccounts, journalentries, journalentrylines, paymenttransaction, taxconfigurations, budgets, expenseclaims, financialreports, journaldetail, journal
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
    bank_account_id = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, default=None, related_name='linked_accounts', db_column='bank_account_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = chartofaccounts

    def __str__(self):
        return f"{self.account_name}"

class JournalEntry(models.Model):
    journal_entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry_date = models.DateField(null=False)
    reference = models.CharField(max_length=100, default=None, null=True)
    description = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = journalentries

    def __str__(self):
        return f"{self.entry_date} - {self.reference}"

class JournalEntryLines(models.Model):
    journal_entry_line_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, null=True, related_name='journal_entry_lines', db_column='account_id')
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.CharField(max_length=1024, default=None, null=True)
    customer_id  = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, db_column='customer_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, db_column='vendor_id')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = taxconfigurations

    def __str__(self):
        return f"{self.tax_name} ({self.tax_rate}{'%' if self.tax_type == 'Percentage' else ''})"

class Budget(models.Model):
    budget_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, related_name='budgets', db_column='account_id')
    fiscal_year = models.PositiveIntegerField(null=False)
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2, null=False)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = budgets

    def __str__(self):
        return f"Budget for {self.account.account_name} - Fiscal Year {self.fiscal_year}"


class ExpenseClaim(models.Model):
    expense_claim_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='expense_claims', db_column='employee_id')
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = journal

    def __str__(self):
        return f"Journal {self.journal_id}"
    
class JournalDetail(models.Model):
    journal_detail_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    journal_id = models.ForeignKey(Journal, related_name="journal_details", on_delete=models.CASCADE, db_column='journal_id')
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.CASCADE,  db_column='ledger_account_id')

    class Meta:
        db_table = journaldetail

    def __str__(self):
        return f"Journal Detail {self.journal_detail_id}"