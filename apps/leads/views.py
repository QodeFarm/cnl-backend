from rest_framework import viewsets
from .models import *
from .serializers import *
from config.utils_methods import list_all_objects, create_instance, update_instance
from config.utils_variables import *

class LeadsView(viewsets.ModelViewSet):
    queryset = Leads.objects.all()
    serializer_class = LeadsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LeadAssignmentsView(viewsets.ModelViewSet):
    queryset = LeadAssignments.objects.all()
    serializer_class = LeadAssignmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)