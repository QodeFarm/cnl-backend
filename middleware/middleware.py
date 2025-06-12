from django.db import connections
from django.utils.deprecation import MiddlewareMixin

DOMAIN_DATABASE_MAPPING = {
    "master.cnlerp.com": "cnl",
    "dev.cnlerp.com": "devcnl",
    "demo.cnlerp.com": "democnl",
    "qa.cnlerp.com": "qacnl"
}

class DatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get the client domain from the request header (sent by Nginx)
        client_domain = request.headers.get("X-Client-Domain", "").replace("https://", "").replace("http://", "").split(":")[0]

        # Select the database based on the frontend domain
        db_name = DOMAIN_DATABASE_MAPPING.get(client_domain, "devcnl")  # Default to devcnl if not found

        # Set the correct database connection
        connections.databases["default"]["NAME"] = db_name

        # Print to logs for debugging
        print(f"Using database: {db_name} for client domain: {client_domain}")                                                                          