#model for the Audit logs

import uuid
from django.db import models

from apps.users.models import User

class AuditLog(models.Model):
    audit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None, db_column='user_id')
    action_type = models.CharField(max_length=255)
    module_name = models.TextField(null=True, default=None)
    record_id = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.module_name}"
    
    class Meta:
        db_table = 'audit_log'


