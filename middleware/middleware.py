from django.db import connections
from django.utils.deprecation import MiddlewareMixin
from apps.users.models import License
import logging

logger = logging.getLogger(__name__)

# class DatabaseMiddleware(MiddlewareMixin):
#     def process_request(self, request):

#         data = License.objects.using('mstcnl').values_list('domain', 'database_name')   
#         DOMAIN_DATABASE_MAPPING =  dict(data)
#         print(DOMAIN_DATABASE_MAPPING)

#         # Get the client domain from the request header (sent by Nginx)
#         client_domain = request.headers.get("X-Client-Domain", "").replace("https://", "").replace("http://", "").split(":")[0]
#         subdomain =  client_domain.split('.')[0]
#         # Select the database based on the frontend domain
#         db_name = DOMAIN_DATABASE_MAPPING.get(subdomain, "cnl_loc")  # Default to devcnl if not found

#         # Set the correct database connection
#         connections.databases["default"]["NAME"] = db_name

#         # Print to logs for debugging
#         print(f"Using database: {db_name} for client domain: {client_domain}")                                                                          

class DatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # For portal requests - set database based on domain
        if request.path.startswith('/api/customers/portal/'):
            print(f"🟢 Portal request detected: {request.path}")
            
            # Get domain from header (same logic as admin)
            client_domain = request.headers.get("X-Client-Domain", "").replace("https://", "").replace("http://", "").split(":")[0]
            subdomain = client_domain.split('.')[0]
            
            # Get database name from License table
            try:
                data = License.objects.using('mstcnl').values_list('domain', 'database_name')
                DOMAIN_DATABASE_MAPPING = dict(data)
                db_name = DOMAIN_DATABASE_MAPPING.get(subdomain, "devcnl")
            except Exception as e:
                print(f"Error getting database: {e}")
                db_name = "devcnl"
            
            # Set the database connection
            connections.databases["default"]["NAME"] = db_name
            print(f"🟢 Portal using database: {db_name} for domain: {client_domain}")
            return None
            
        # Your existing database switching logic for non-portal requests
        try:
            data = License.objects.using('mstcnl').values_list('domain', 'database_name')   
            DOMAIN_DATABASE_MAPPING = dict(data)
            
            client_domain = request.headers.get("X-Client-Domain", "").replace("https://", "").replace("http://", "").split(":")[0]
            subdomain = client_domain.split('.')[0]
            db_name = DOMAIN_DATABASE_MAPPING.get(subdomain, "devcnl")
            
            connections.databases["default"]["NAME"] = db_name
            print(f"🟢 Using database: {db_name} for domain: {client_domain}")
            
        except Exception as e:
            print(f"❌ DatabaseMiddleware error: {e}")
            connections.databases["default"]["NAME"] = "devcnl"
        
        return None