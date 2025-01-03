import uuid
from django.db import models


class ReportDefinition(models.Model):
    query_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.TextField()
    query_name = models.CharField(max_length=255)
    visualization_type = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.query_name
    
    class Meta:
        db_table = 'report_definition' 