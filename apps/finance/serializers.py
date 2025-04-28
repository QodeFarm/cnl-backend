from rest_framework import serializers
from .models import *
from apps.hrms.serializers import ModEmployeesSerializer
from apps.customer.serializers import ModCustomersSerializer
from apps.vendor.serializers import ModVendorSerializer    

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
    class Meta:
        model = JournalEntry
        fields = '__all__'

class JournalEntryLinesSerializer(serializers.ModelSerializer):
    # journal_entry = ModJournalEntrySerializer(source='journal_entry_id', read_only=True)
    account = ModChartOfAccountsSerializer(source='account_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    vendor = ModVendorSerializer(source='vendor_id', read_only=True)

    class Meta:
        model = JournalEntryLines
        fields = '__all__'

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
    reference = serializers.CharField(source='journal_entry_id.reference')
    account = serializers.CharField(source='account_id.account_name', default='N/A')
    description = serializers.SerializerMethodField()

    def get_description(self, obj):
        return obj.description or obj.journal_entry_id.description

    class Meta:
        model = JournalEntryLines
        fields = ['date', 'reference', 'account', 'debit', 'credit', 'description']
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
                