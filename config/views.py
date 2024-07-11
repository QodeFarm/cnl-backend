from django.http import HttpResponse
from django.urls import reverse
 
 


def api_links(request):
    #Here we need to define the list of API endpoints and their names
    api_endpoints = [
        ('api/v1/hrms/', 'HRMS API'),
        ('api/v1/leads/', 'Leads API'),
        ('api/v1/users/', 'Users API'),
        ('api/v1/masters/', 'Masters API'),
        ('api/v1/company/', 'Company API'),
        ('api/v1/customers/', 'Customers API'),
        ('api/v1/vendors/', 'Vendor API'),
        ('api/v1/products/', 'Products API'),
        ('api/v1/sales/', 'Sales API'),
        ('api/v1/inventory/', 'Inventory API'),
        ('api/v1/purchase/', 'Purchase API'),
        ('api/v1/tasks/', 'Tasks API'),
        ('swagger/','Swagger')
    ]

    # Generate HTML markup for the links
    html = "<h1>API Endpoints</h1>"
    html += "<ul>"
    for endpoint, name in api_endpoints:
        link = reverse('api_links') + endpoint  
        html += f"<li><a href='{link}'>{name}</a></li>"
    html += "</ul>"

    return HttpResponse(html)
