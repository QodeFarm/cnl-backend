from rest_framework import serializers
from .models import *
from apps.hrms.serializers import ModEmployeesSerializer
from apps.customer.serializers import ModCustomersSerializer, ModLedgerAccountsSerializers
from apps.vendor.serializers import ModVendorSerializer    
from django.db.models import Sum

class ModBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['bank_account_id','bank_name']

class ModChartOfAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccounts
        fields = ['account_id','account_name']

class ModJournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ['journal_entry_id','entry_date']

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class ChartOfAccountsSerializer(serializers.ModelSerializer):
    parent_account = ModChartOfAccountsSerializer(source='parent_account_id', read_only=True)
    bank_account = ModBankAccountSerializer(source='bank_account_id', read_only=True)
    class Meta:
        model = ChartOfAccounts
        fields = '__all__'

class JournalEntrySerializer(serializers.ModelSerializer):
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)

    class Meta:
        model = JournalEntry
        fields = '__all__'

class JournalEntryLinesSerializer(serializers.ModelSerializer):
    # journal_entry = ModJournalEntrySerializer(source='journal_entry_id', read_only=True)
    # account = ModChartOfAccountsSerializer(source='account_id', read_only=True)
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    vendor = ModVendorSerializer(source='vendor_id', read_only=True)
    voucher_no = serializers.CharField(source='journal_entry_id.voucher_no', read_only=True)  # <-- FIXED LINE

    class Meta:
        model = JournalEntryLines
        fields = '__all__'
        
class GeneralAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerAccounts
        fields = ['ledger_account_id', 'name']        

class PaymentTransactionSerializer(serializers.ModelSerializer):
    invoice = serializers.SerializerMethodField()
    class Meta:
        model = PaymentTransaction
        fields = '__all__'

    def get_invoice(self, obj):
        return {
            "invoice_id": obj.invoice_id,
            "invoice_no": obj.invoice_id  # Using the same value for both
        }

class TaxConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxConfiguration
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    account = ModChartOfAccountsSerializer(source='account_id', read_only=True)
    class Meta:
        model = Budget
        fields = '__all__'

class ExpenseClaimSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = ExpenseClaim
        fields = '__all__'

class FinancialReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialReport
        fields = '__all__'

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['journal_id', 'date', 'description', 'total_debit', 'total_credit', 'created_at']

class JournalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalDetail
        fields = ['journal_detail_id', 'journal_id', 'ledger_account_id', 'debit', 'credit']
        
class GeneralLedgerReportSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='journal_entry_id.entry_date')
    voucher = serializers.CharField(source='journal_entry_id.voucher_no', read_only=True)
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    description = serializers.SerializerMethodField()
    # Use the balance field directly from the model
    # The balance is calculated and updated when ledger reports are generated

    def get_description(self, obj):
        return obj.description or obj.journal_entry_id.description

    class Meta:
        model = JournalEntryLines
        fields = ['date', 'voucher', 'ledger_account', 'debit', 'credit', 'balance', 'description']
        
        
class TrialBalanceReportSerializer(serializers.ModelSerializer):
    total_debit = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_credit = serializers.DecimalField(max_digits=15, decimal_places=2)
    # balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        model = ChartOfAccounts
        fields = ['account_id','account_code','account_name','account_type','total_debit','total_credit',]

class ProfitLossReportSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=15, decimal_places=2)

class BalanceSheetAccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = ChartOfAccounts
        fields = ['account_id','account_code','account_name','account_type','balance']   
        
class CashFlowStatementSerializer(serializers.ModelSerializer):
    cash_inflow = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    cash_outflow = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = ChartOfAccounts
        fields = ['account_id','account_code','account_name','account_type','cash_inflow','cash_outflow']  
        
class AgingReportSerializer(serializers.ModelSerializer):
    due_days = serializers.IntegerField(read_only=True)
    pending_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = ['invoice_id','order_type','payment_date','payment_status','due_days','pending_amount']                                       
        
class BankReconciliationReportSerializer(serializers.ModelSerializer):
    ledger_balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    difference = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = BankAccount
        fields = ['bank_account_id','account_name','account_number','bank_name','branch_name','ifsc_code','balance','ledger_balance', 'difference']
class JournalEntryReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ['journal_entry_id', 'entry_date', 'reference', 'description', 'created_at', 'updated_at']
                
                
# class ExpenseCategorySerializer(serializers.ModelSerializer):
#     account = ModChartOfAccountsSerializer(source='account_id', read_only=True)
    
#     class Meta:
#         model = ExpenseCategory
#         fields = '__all__'

# class ModExpenseCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ExpenseCategory
#         fields = ['category_id', 'category_name']


class ExpenseItemSerializer(serializers.ModelSerializer):
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    bank_account = ModBankAccountSerializer(source='bank_account_id', read_only=True)
    vendor = ModVendorSerializer(source='vendor_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    expense_claim = ExpenseClaimSerializer(source='expense_claim_id', read_only=True)
    budget = BudgetSerializer(source='budget_id', read_only=True)
    tax_configuration = TaxConfigurationSerializer(source='tax_id', read_only=True)
    
    class Meta:
        model = ExpenseItem
        fields = '__all__'


# ======================================
# JOURNAL VOUCHER SERIALIZERS
# ======================================

class ModJournalVoucherSerializer(serializers.ModelSerializer):
    """Minimal serializer for nested references"""
    class Meta:
        model = JournalVoucher
        fields = ['journal_voucher_id', 'voucher_no', 'voucher_date']


class JournalVoucherSerializer(serializers.ModelSerializer):
    """Main Journal Voucher Serializer with nested read-only data"""
    expense_claim = ExpenseClaimSerializer(source='expense_claim_id', read_only=True)
    
    # Allow blank/null for optional fields
    narration = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reference_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = JournalVoucher
        fields = '__all__'
    
    def validate_voucher_no(self, value):
        """Validate unique voucher number on update"""
        journal_voucher_id = None
        if self.instance and hasattr(self.instance, 'journal_voucher_id'):
            journal_voucher_id = self.instance.journal_voucher_id
        elif 'journal_voucher_id' in self.initial_data:
            journal_voucher_id = self.initial_data['journal_voucher_id']
        
        qs = JournalVoucher.objects.filter(voucher_no=value)
        if journal_voucher_id:
            qs = qs.exclude(journal_voucher_id=journal_voucher_id)
        if qs.exists():
            raise serializers.ValidationError("Journal voucher with this voucher number already exists.")
        return value


class JournalVoucherLineSerializer(serializers.ModelSerializer):
    """Journal Voucher Line Serializer"""
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    vendor = ModVendorSerializer(source='vendor_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    
    # Allow blank/null for optional fields
    remark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bill_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = JournalVoucherLine
        fields = '__all__'


class JournalVoucherAttachmentSerializer(serializers.ModelSerializer):
    """Journal Voucher Attachment Serializer"""
    class Meta:
        model = JournalVoucherAttachment
        fields = '__all__'


# ======================================
# JOURNAL BOOK REPORT SERIALIZERS
# ======================================

class JournalBookLineSerializer(serializers.Serializer):
    """
    Serializer for individual journal book line items (debit/credit entries).
    Used within JournalBookReportSerializer for nested line data.
    """
    ledger_account_name = serializers.CharField()
    ledger_group = serializers.CharField(allow_null=True)
    party_name = serializers.CharField(allow_null=True)
    entry_type = serializers.CharField()  # 'Debit' or 'Credit'
    debit = serializers.DecimalField(max_digits=18, decimal_places=2)
    credit = serializers.DecimalField(max_digits=18, decimal_places=2)


class JournalBookReportSerializer(serializers.Serializer):
    """
    Groups journal entries by voucher with all line details.
    
    - Voucher No
    - Date
    - Particulars (ledger account name, party details, narration)
    - Debit Amount
    - Credit Amount
    """
    voucher_no = serializers.CharField()
    voucher_date = serializers.DateField()
    voucher_type = serializers.CharField()
    narration = serializers.CharField(allow_null=True, allow_blank=True)
    particulars = serializers.SerializerMethodField()
    lines = JournalBookLineSerializer(many=True)
    total_debit = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_credit = serializers.DecimalField(max_digits=18, decimal_places=2)
    journal_voucher_id = serializers.UUIDField()
    is_posted = serializers.BooleanField()

    def get_particulars(self, obj):
        """
        'Ledger Group\nParty Name\n(Being Journal Entry narration with details)'
        """
        lines = obj.get('lines', [])
        narration = obj.get('narration', '')
        
        particulars_list = []
        for line in lines:
            ledger_group = line.get('ledger_group', '')
            ledger_name = line.get('ledger_account_name', '')
            party_name = line.get('party_name', '')
            entry_type = line.get('entry_type', '')
            amount = line.get('debit', 0) if entry_type == 'Debit' else line.get('credit', 0)
            
            # Build line text
            line_text = f"{ledger_group}"
            if party_name:
                line_text += f"\n{ledger_name} [ {party_name}]"
            else:
                line_text += f"\n{ledger_name}"
            
            particulars_list.append({
                'text': line_text,
                'entry_type': entry_type,
                'amount': amount
            })
        
        # Add narration
        if narration:
            # Format narration with all line details
            narration_parts = []
            for line in lines:
                ledger_name = line.get('ledger_account_name', '')
                party_name = line.get('party_name', '')
                entry_type = line.get('entry_type', '')
                amount = line.get('debit', 0) if entry_type == 'Debit' else line.get('credit', 0)
                
                if party_name:
                    narration_parts.append(f"{ledger_name} [ {party_name}]## {entry_type} ₹{amount}")
                else:
                    narration_parts.append(f"{ledger_name}## {entry_type} ₹{amount}")
            
            full_narration = f"(Being Journal Entry {' '.join(narration_parts)})"
            particulars_list.append({
                'text': full_narration,
                'entry_type': 'narration',
                'amount': 0
            })
        
        return particulars_list


class JournalBookSummarySerializer(serializers.Serializer):
    """
    Summary serializer for Journal Book Report totals.
    Shows grand total of all debits and credits.
    """
    total_debit = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_credit = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_vouchers = serializers.IntegerField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
