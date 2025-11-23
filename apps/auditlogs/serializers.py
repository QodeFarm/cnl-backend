from rest_framework import serializers

from apps.users.serializers import ModUserSerializer
from .models import AuditLog  # or ActivityLog

class AuditLogSerializer(serializers.ModelSerializer):
    user = ModUserSerializer(source='user_id', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
