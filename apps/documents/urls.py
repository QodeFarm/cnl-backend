# apps/documents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, serve_public_document

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='documents')

urlpatterns = [
    path('', include(router.urls)),
    # Public endpoint for serving documents (no auth required for WhatsApp)
    path('public/documents/<path:file_path>', serve_public_document, name='serve_public_document'),
]