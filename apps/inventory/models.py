from django.db import models
# from apps.sales.models import SaleOrder
from config.utils_methods import *
from config.utils_variables import warehouselocations, warehousestable, config_block, inventory_blocked
# from apps.products.models import Products
import uuid


# Create your models here.
class Warehouses(models.Model):
    warehouse_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255,null=True,default=None)
    item_type_id = models.ForeignKey('masters.ProductItemType', on_delete=models.CASCADE, null=True, default=None, db_column='item_type_id')
    address = models.CharField(max_length=255, null=True, default=None)
    city_id = models.ForeignKey('masters.City', on_delete=models.CASCADE, db_column = 'city_id')
    state_id = models.ForeignKey('masters.State', on_delete=models.CASCADE, db_column = 'state_id')
    country_id = models.ForeignKey('masters.Country', on_delete=models.CASCADE, null=True, default=None, db_column = 'country_id')
    pin_code = models.CharField(max_length=50,null=True,default=None)
    phone = models.CharField(max_length=50,null=True,default=None)
    email = models.CharField(max_length=255,null=True,default=None)
    longitude = models.DecimalField(max_digits=10,decimal_places=6, null=True, default=None)
    latitude = models.DecimalField(max_digits=10,decimal_places=6, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = warehousestable

    def __str__(self):
        return f"{self.name}"
    
class WarehouseLocations(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location_name = models.CharField(max_length=255)
    warehouse_id = models.ForeignKey(Warehouses, on_delete=models.CASCADE, db_column='warehouse_id')
    description = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = warehouselocations

    def __str__(self):
        return f"{self.location_name}"
		
#---------------------------------------------------------------
#store the configuration hours

class InventoryBlockConfig(models.Model):
    config_id = models.AutoField(primary_key=True)
    block_duration_hours = models.IntegerField(default=24, help_text="Duration (in hours) to block inventory")
    product_id = models.ForeignKey('products.Products', on_delete=models.CASCADE, db_column='product_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = config_block

       
class BlockedInventory(models.Model):
    block_id = models.AutoField(primary_key=True)
    sale_order_id = models.ForeignKey('sales.SaleOrder', on_delete=models.CASCADE, db_column='sale_order_id')
    product_id = models.ForeignKey('products.Products', on_delete=models.CASCADE, db_column='product_id')
    blocked_qty = models.IntegerField(default=0)
    expiration_time = models.DateTimeField(help_text="Timestamp when the block expires")
    is_expired = models.BooleanField(default=False, help_text="True if block duration has passed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = inventory_blocked


