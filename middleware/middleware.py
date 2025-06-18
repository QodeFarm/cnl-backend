from django.db import connections
from django.utils.deprecation import MiddlewareMixin
from apps.users.models import License

class DatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):

        data = License.objects.using('mstcnl').values_list('domain', 'database_name')   
        DOMAIN_DATABASE_MAPPING =  dict(data)
        print(DOMAIN_DATABASE_MAPPING)

        # Get the client domain from the request header (sent by Nginx)
        client_domain = request.headers.get("X-Client-Domain", "").replace("https://", "").replace("http://", "").split(":")[0]
        subdomain =  client_domain.split('.')[0]
        # Select the database based on the frontend domain
        db_name = DOMAIN_DATABASE_MAPPING.get(subdomain, "rudhra_rd001_prod")  # Default to devcnl if not found

        # Set the correct database connection
        connections.databases["default"]["NAME"] = 'rudhra_rd001_prod' #db_name

        # Print to logs for debugging
        print(f"Using database: {db_name} for client domain: {client_domain}")                                                                          