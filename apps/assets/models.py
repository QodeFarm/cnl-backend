from django.db import models
import uuid
from config.utils_variables import assetstatusestable,assetcategoriestable,assetstable,locationstable, assetmaintenancetable


# Create your models here.
class AssetStatuses(models.Model):
    asset_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = assetstatusestable

    def __str__(self):
        return f"{self.asset_status_id} {self.status_name}"
		
class AssetCategories(models.Model):
    asset_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = assetcategoriestable

    def __str__(self):
        return f"{self.asset_category_id} {self.category_name}"		
		
class Locations(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location_name = models.CharField(max_length=50)
    address = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = locationstable

    def __str__(self):
        return f"{self.location_id} {self.location_name}"

class Assets(models.Model):
    asset_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    asset_category_id = models.ForeignKey(AssetCategories, on_delete=models.CASCADE, db_column='asset_category_id')
    asset_status_id = models.ForeignKey(AssetStatuses, on_delete=models.CASCADE, db_column='asset_status_id')
    location_id = models.ForeignKey(Locations, on_delete=models.CASCADE, db_column='location_id')
    purchase_date = models.DateField(null=True, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = assetstable

    def __str__(self):
        return f"{self.asset_id} {self.name}"

class AssetMaintenance(models.Model):
    asset_maintenance_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_id = models.ForeignKey(Assets, on_delete=models.CASCADE, db_column='asset_id')
    maintenance_date = models.DateField(null=True, default=None)
    maintenance_description = models.CharField(max_length=1024, null=True, default=None)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = assetmaintenancetable

    def __str__(self):
        return f"{self.asset_maintenance_id}"	
