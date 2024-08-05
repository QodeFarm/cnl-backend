from django.shortcuts import render
from rest_framework import viewsets
from .models import Companies, Branches, BranchBankDetails
from .serializers import CompaniesSerializer, BranchesSerializer, BranchBankDetailsSerializer
from config.utils_methods import list_all_objects, create_instance, update_instance
from config.utils_variables import *
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from .filters import CompaniesFilters, BranchesFilters, BranchBankDetailsFilters
from rest_framework.filters import OrderingFilter

class CompaniesViewSet(viewsets.ModelViewSet):
    queryset = Companies.objects.all()
    serializer_class = CompaniesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CompaniesFilters
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class BranchesViewSet(viewsets.ModelViewSet):
    queryset = Branches.objects.all()
    serializer_class = BranchesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BranchesFilters
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class BranchBankDetailsViewSet(viewsets.ModelViewSet):
    queryset = BranchBankDetails.objects.all()
    serializer_class = BranchBankDetailsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BranchBankDetailsFilters
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)