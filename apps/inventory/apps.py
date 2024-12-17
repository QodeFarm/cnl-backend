from django.apps import AppConfig
from apps.inventory.scheduler import start_scheduler


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'
    
    def ready(self):
        start_scheduler()

