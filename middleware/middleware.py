from django.utils.deprecation import MiddlewareMixin
from apps.users.models import License
from urllib.parse import urlparse
from django.db import connections
import logging

logger = logging.getLogger('myapp')


def get_db_name(request):
    # First try to get custom header
    domain_header = request.headers.get("X-Client-Domain")
    
    if not domain_header:
        # Fall back to actual host
        domain_header = request.get_host().split(':')[0]  # strips port like 8000

    # Ensure urlparse works
    parsed_url = urlparse(f"http://{domain_header}")
    full_domain = parsed_url.hostname

    if not full_domain:
        return "txt"

    if full_domain.replace('.', '').isdigit() or full_domain.startswith('127'):
        subdomain = full_domain.split('.')[0]
    else:
        subdomain = full_domain.split('.')[0]

    print("===>>", subdomain)

    DOMAIN_DATABASE_MAPPING = {
        'prod': 'cnl_cl002_prod',
        'rudhra': 'rudhra_DB',
        '127': 'cnl2'
    }
   
    return DOMAIN_DATABASE_MAPPING.get(subdomain, "txt")


class DatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):
     
        # Select the database based on the client domain
        db_name = get_db_name(request)  

        # Set the correct database connection
        connections.databases["default"]["NAME"] = db_name

        # Print to logs for debugging
        logger.info("*" * 20)
        logger.info(f"Using database: {db_name}")    
        logger.info("*" * 20)                                                                      