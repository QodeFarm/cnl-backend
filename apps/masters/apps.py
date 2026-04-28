from django.apps import AppConfig


class MastersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.masters'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_seed_ledger_groups, sender=self)


def _seed_ledger_groups(sender, **kwargs):
    try:
        from apps.masters.models import LedgerGroups
        # Only seed when the table is completely empty (fresh server / new client).
        # Skips on every subsequent deploy so production data is never touched.
        if LedgerGroups.objects.exists():
            return
        from django.core.management import call_command
        call_command('seed_ledger_groups', verbosity=0)
    except Exception:
        pass  # Never crash startup — DB may not be ready yet on first run
