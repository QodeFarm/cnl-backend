# apps/documents/utils.py
import os
import random
import string
from django.conf import settings
from datetime import datetime

def get_customer_folder(customer_id, customer_name):
    """
    Generate customer folder path
    Format: customers/{customer_id}_{customer_name_slug}/
    """
    customer_slug = customer_name.lower().replace(' ', '_').replace('/', '_')
    customer_slug = ''.join(c for c in customer_slug if c.isalnum() or c == '_')
    return f"customers/{customer_id}_{customer_slug}"

def generate_document_path(document_type, customer_id, customer_name, document_id):
    """
    Generate organized file path for document
    Returns: (doc_name, full_file_path, relative_file_path, folder_path)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    doc_name = f"{document_type}_{document_id}_{timestamp}_{unique_code}.pdf"

    if customer_id and customer_name:
        folder = get_customer_folder(customer_id, customer_name)
    else:
        folder = f"documents/{document_type}"

    relative_folder = folder
    relative_file_path = os.path.join(relative_folder, doc_name)
    full_file_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)

    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

    latest_doc_name = f"{document_type}_{document_id}_latest.pdf"
    latest_relative_path = os.path.join(relative_folder, latest_doc_name)
    latest_full_path = os.path.join(settings.MEDIA_ROOT, latest_relative_path)

    return {
        'doc_name': doc_name,
        'full_file_path': full_file_path,
        'relative_file_path': relative_file_path,
        'folder': folder,
        'latest_full_path': latest_full_path,
        'latest_relative_path': latest_relative_path
    }

def get_document_url(relative_file_path, request=None):
    """
    Get public URL for document
    """
    from django.conf import settings

    relative_url = relative_file_path.replace('\\', '/')

    if settings.DEBUG:
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            base_url = "http://localhost:8000"
        return f"{base_url}/public/documents/{relative_url}"
    else:
        return f"https://apicore.cnlerp.com/public/documents/{relative_url}"
