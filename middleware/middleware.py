from django.db import connections
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Default mapping for system domains that don't require License lookup
DEFAULT_DOMAIN_DATABASE_MAPPING = {
    "master.cnlerp.com": "cnl",
    "dev.cnlerp.com": "devcnl",
    "demo.cnlerp.com": "democnl",  
}

def get_domain_database_mapping():
    """
    Get domain-to-database mapping from cache or build it from License table.
    Returns a dictionary mapping domains to database names.
    """
    # Try to get the mapping from cache
    mapping = cache.get('domain_database_mapping')
    
    # If not in cache, build it from the License table
    if mapping is None:
        mapping = DEFAULT_DOMAIN_DATABASE_MAPPING.copy()
        
        try:
            # Import here to avoid circular import issues
            from apps.users.models import License
            
            # Query all License records with domain and database_name
            license_mappings = License.objects.using('mstcnl').values('domain', 'database_name', 'domain_url')
            
            # Add all License domain-database mappings
            for license_map in license_mappings:
                domain = license_map.get('domain')
                domain_url = license_map.get('domain_url', '')
                db_name = license_map.get('database_name')
                
                if not domain or not db_name:
                    logger.warning(f"Skipping incomplete license entry: {license_map}")
                    continue
                
                if domain and db_name:
                    # Map the domain directly
                    mapping[domain] = db_name
                    
                    # Also map domain.cnlerp.com format
                    mapping[f"{domain}.cnlerp.com"] = db_name
                    
                    # If domain_url provided, clean it and add to mapping
                    if domain_url:
                        # Remove http:// or https:// and port
                        clean_domain_url = domain_url.replace('https://', '').replace('http://', '').split(':')[0]
                        mapping[clean_domain_url] = db_name
            
            # Cache the mapping (cache invalidation is handled by License model signals)
            cache.set('domain_database_mapping', mapping, timeout=3600)  # Cache for 1 hour
            logger.info(f"Domain-database mapping built from License table with {len(license_mappings)} entries")
            logger.debug(f"Mapping details: {mapping}")
            
        except Exception as e:
            logger.error(f"Error building domain-database mapping: {str(e)}")
    
    return mapping

class DatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get the client domain from the request header (sent by Nginx)
        client_domain = request.headers.get("X-Client-Domain", "").replace("https://", "").replace("http://", "").split(":")[0]
        
        # Get domain-database mapping (from cache or build it)
        domain_db_mapping = get_domain_database_mapping()
        
        # Select the database based on the client domain
        db_name = domain_db_mapping.get(client_domain, "devcnl")  

        # Set the correct database connection
        connections.databases["default"]["NAME"] = db_name

        # Log for debugging
        logger.info(f"Using database: {db_name} for client domain: {client_domain}")

                                                                      