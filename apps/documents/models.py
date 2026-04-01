# apps/documents/models.py
from time import timezone
import uuid

from django.db import models
from django.conf import settings
import os

from apps.customer.models import Customer
from apps.vendor.models import Vendor

class DocumentsGeneration(models.Model):
    DOCUMENT_TYPES = [
        ('sale_order', 'Sale Order'),
        ('sales_invoice', 'Sales Invoice'),
        ('purchase_order', 'Purchase Order'),
        ('quotation', 'Quotation'),
        ('delivery_challan', 'Delivery Challan'),
    ]
    customer_document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_id = models.CharField(max_length=36)  # ID of the original document (sale_order_id, etc.)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, db_column='customer_id')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True, db_column='vendor_id')

    # File information
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)  # Relative path from MEDIA_ROOT
    file_url = models.CharField(max_length=500)   # Full URL for access
    file_size = models.IntegerField(null=True, blank=True)  # Size in bytes
    
    # Metadata
    # generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['document_type', 'document_id']),
            models.Index(fields=['customer']),
            models.Index(fields=['generated_at']),
        ]
        ordering = ['-generated_at']
        db_table = 'documents_generation'
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.file_name}"
    
    def increment_access(self):
        """Increment access count and update last accessed time"""
        self.access_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['access_count', 'last_accessed'])