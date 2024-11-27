from rest_framework import serializers
from .models import ReportDefinition

class ReportDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDefinition
        fields = ['query_name', 'query', 'query_id', 'visualization_type']
