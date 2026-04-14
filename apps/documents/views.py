# apps/documents/views.py
import os
import mimetypes
from urllib.parse import quote
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse, HttpResponseNotFound, HttpResponseForbidden
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import DocumentsGeneration
from .serializers import DocumentSerializersSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customer documents"""
    serializer_class = DocumentSerializersSerializer

    def get_queryset(self):
        queryset = DocumentsGeneration.objects.all()

        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer__id=customer_id)

        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            queryset = queryset.filter(vendor__id=vendor_id)

        document_type = self.request.query_params.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)

        doc_id = self.request.query_params.get('document_id')
        if doc_id:
            queryset = queryset.filter(document_id=doc_id)

        return queryset

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the actual file"""
        document = self.get_object()
        document.increment_access()

        file_path = os.path.join(settings.MEDIA_ROOT, document.file_path)

        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=document.file_name
            )
            return response
        else:
            return HttpResponseNotFound("File not found")

    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """Get all documents for a customer"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({"error": "customer_id required"}, status=status.HTTP_400_BAD_REQUEST)

        documents = self.get_queryset().filter(customer__id=customer_id)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest document for a specific document type and ID"""
        document_type = request.query_params.get('document_type')
        document_id = request.query_params.get('document_id')

        if not document_type or not document_id:
            return Response(
                {"error": "document_type and document_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = DocumentsGeneration.objects.filter(
                document_type=document_type,
                document_id=document_id,
                is_active=True
            ).latest('generated_at')

            serializer = self.get_serializer(document)
            return Response(serializer.data)
        except DocumentsGeneration.DoesNotExist:
            return Response({"error": "No document found"}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@cache_control(max_age=3600, public=True)
def serve_public_document(request, file_path):
    """
    Serve documents publicly for WhatsApp and app access
    """
    try:
        print("=" * 50)
        print(f"Serving file: {file_path}")

        safe_path = os.path.normpath(file_path)
        if safe_path.startswith('..') or os.path.isabs(safe_path):
            return HttpResponseForbidden("Invalid file path")

        full_file_path = os.path.join(settings.MEDIA_ROOT, safe_path)
        print(f"Full path: {full_file_path}")

        if not os.path.exists(full_file_path):
            return HttpResponseNotFound("File not found")

        filename = os.path.basename(full_file_path)
        file_size = os.path.getsize(full_file_path)

        content_type, _ = mimetypes.guess_type(full_file_path)
        if not content_type:
            content_type = 'application/pdf'

        file_handle = open(full_file_path, 'rb')
        response = FileResponse(
            file_handle,
            content_type=content_type,
            as_attachment=False
        )

        response['Content-Disposition'] = f"inline; filename=\"{filename}\"; filename*=UTF-8''{quote(filename)}"
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        response['Cache-Control'] = 'public, max-age=3600'
        response['Content-Length'] = file_size
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Filename'] = filename

        print(f"SUCCESS: Serving file: {filename}")
        print("=" * 50)

        return response

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponseNotFound(f"Error serving file: {str(e)}")
