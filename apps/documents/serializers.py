#serializers

from rest_framework import serializers

from apps.documents.models import DocumentsGeneration

class DocumentSerializersSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)

    class Meta:
        model = DocumentsGeneration
        fields = [
            'customer_document_id', 'document_type', 'document_type_display', 'document_id',
            'customer', 'vendor', 'file_name', 'file_url', 'file_size',
            'generated_at', 'last_accessed', 'access_count',
            'is_active'
        ]
        read_only_fields = ['generated_at', 'last_accessed', 'access_count']
