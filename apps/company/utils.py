import logging

logger = logging.getLogger(__name__)


def get_finance_setting(field_name: str, fallback_name: str = None):
    """
    Return a LedgerAccounts instance for the requested setting field.

    Lookup order:
      1. company_settings table  (admin-configured, proper ERP way)
      2. Name-based fallback     (backward compatibility for existing data)
      3. None                    (caller must handle the missing account case)

    Args:
        field_name:    CompanySettings FK field name, e.g. 'sales_ledger_account'
        fallback_name: Legacy ledger account name to search when not configured,
                       e.g. 'Sale Account'

    Usage:
        from apps.company.utils import get_finance_setting
        sale_account = get_finance_setting('sales_ledger_account', fallback_name='Sale Account')
    """
    try:
        from apps.company.models import CompanySettings
        cfg = CompanySettings.objects.select_related(field_name).first()
        if cfg:
            account = getattr(cfg, field_name, None)
            if account:
                return account
    except Exception as exc:
        logger.warning("CompanySettings lookup failed for '%s': %s", field_name, exc)

    if fallback_name:
        try:
            from apps.customer.models import LedgerAccounts
            return LedgerAccounts.objects.filter(
                name__iexact=fallback_name, is_deleted=False
            ).first()
        except Exception as exc:
            logger.warning("Fallback ledger account lookup failed for '%s': %s", fallback_name, exc)

    return None


def is_notification_enabled(field_name: str, default: bool = False) -> bool:
    """
    Return the value of a boolean preference/notification toggle on CompanySettings.

    Fails SAFE: if settings are missing, the field is unset, or anything errors, it
    returns `default` (False) — so a customer-facing message is NEVER sent unless the
    toggle is explicitly turned on by an admin.

    Usage:
        from apps.company.utils import is_notification_enabled
        if is_notification_enabled('notify_sale_order_whatsapp'):
            ...send...
    """
    try:
        from apps.company.models import CompanySettings
        cfg = CompanySettings.objects.first()
        if cfg is not None:
            val = getattr(cfg, field_name, None)
            if val is not None:
                return bool(val)
    except Exception as exc:
        logger.warning("CompanySettings toggle lookup failed for '%s': %s", field_name, exc)

    return default
