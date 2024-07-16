from rest_framework import viewsets
from .models import *
from .serializers import *
from config.utils_methods import list_all_objects, create_instance, update_instance

class LeadStatusesView(viewsets.ModelViewSet):
    queryset = LeadStatuses.objects.all()
    serializer_class = LeadStatusesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class InteractionTypesView(viewsets.ModelViewSet):
    queryset = InteractionTypes.objects.all()
    serializer_class = InteractionTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

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

class LeadInteractionsView(viewsets.ModelViewSet):
    queryset = LeadInteractions.objects.all()
    serializer_class = LeadInteractionsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LeadAssignmentHistoryView(viewsets.ModelViewSet):
    queryset = LeadAssignmentHistory.objects.all()
    serializer_class = LeadAssignmentHistorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)