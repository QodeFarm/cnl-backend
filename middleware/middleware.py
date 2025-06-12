from django.db import connections
from django.utils.deprecation import MiddlewareMixin
from apps.users.models import License
import logging

logger = logging.getLogger('myapp')

def SubdomainFromMstcnl():
    # data = License.objects.using('mstcnl').values_list('domain', 'database_name')   
    # dict(data)

    DOMAIN_DATABASE_MAPPING = {
        'prod': 'cnl_cl002_prod',
        'rudhra': 'cnl_cl001_rudhra',
        '127': 'cnl2'
    }

    return DOMAIN_DATABASE_MAPPING 
 
    

class DatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get the client domain from the request header (sent by Nginx)
        # client_domain = request.headers.get("X-Client-Domain", "").replace("https://", "").replace("http://", "").split(":")[0]
        
        client_domain = request.get_host().split('.')[0]  # 'tp'
        
        DOMAIN_DATABASE_MAPPING = {
                        'prod' : 'cnl_cl002_prod', 
                        'rudhra': 'cnl_cl001_rudhra',
                        '127': 'cnl2'
                       }
         #SubdomainFromMstcnl()
        
        # Select the database based on the client domain
        db_name = DOMAIN_DATABASE_MAPPING.get(client_domain, "txt")  # Default to devcnl if not found

        # Set the correct database connection
        connections.databases["default"]["NAME"] = db_name

        # Print to logs for debugging
        logger.info("*" * 20)
        logger.info(f"Using database: {db_name} for client domain: {client_domain}")    
        logger.info("*" * 20)                                                                      