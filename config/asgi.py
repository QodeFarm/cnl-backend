"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from config.settings import DATABASE_MAPPING

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

#application = get_asgi_application()

def application(environ, start_response):
    from django.conf import settings
    from django.core.asgi import get_asgi_application

    host = environ.get("HTTP_HOST", "master.cnlerp.com").split(":")[0]
    os.environ["DB_NAME"] = DATABASE_MAPPING.get(host, "cnl")

    try:
        _application = get_asgi_application()
    except Exception as e:
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [b"Internal Server Error"]

    return _application(environ, start_response)