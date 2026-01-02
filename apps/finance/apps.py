from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance'

    def ready(self):
        """
        Import signals when the app is ready.
        This registers the Journal Voucher signals for auto-creating
        JournalEntryLines (Account Ledger entries) on CRUD operations.
        """
        import apps.finance.signals  # noqa: F401
