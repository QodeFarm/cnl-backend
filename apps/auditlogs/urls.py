#creating urls for the audit log

from django.urls import include, path

from apps.alignbook import admin
from .views import AuditLogView

urlpatterns = [
    path('', AuditLogView.as_view(), name='audit-log-list'),
]
