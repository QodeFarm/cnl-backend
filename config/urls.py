"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from config import settings
from config.views import api_links
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.users.custom_schema_generator import CustomOpenAPISchemaGenerator  

schema_view = get_schema_view(
    openapi.Info(
        title="NTHRAS",
        default_version='v1',
        #description="API for NTHRAS",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('apps.users.url')),
    path('api/v1/company/', include('apps.company.urls')),
    path('api/v1/customers/', include('apps.customer.urls')),
    path('api/v1/vendors/', include('apps.vendor.urls')),
    path('api/v1/company/', include('apps.company.urls')),
    path('api/v1/masters/', include('apps.masters.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/purchase/', include('apps.purchase.urls')),
    path('api/v1/per_val/', include('apps.per_val.url')),
    path('api/v1/alignbooks/', include('apps.alignbook.url')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/assets/', include('apps.asset.urls')),
    path('', api_links, name='api_links'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

#below will handle media files uploaded when instance is created.

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

