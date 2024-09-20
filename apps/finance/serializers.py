from rest_framework import serializers
from .models import *
from apps.hrms.serializers import ModEmployeesSerializer

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
    journal_entry = ModJournalEntrySerializer(source='journal_entry_id', read_only=True)
    account = ModChartOfAccountsSerializer(source='account_id', read_only=True)
    class Meta:
        model = JournalEntryLines
        fields = '__all__'

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'

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