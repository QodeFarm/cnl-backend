from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.purchase'

    def ready(self):
        import apps.purchase.signals