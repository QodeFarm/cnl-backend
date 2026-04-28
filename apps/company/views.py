from django.forms import ValidationError
from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Companies, Branches, BranchBankDetails, CompanySettings
from .serializers import CompaniesSerializer, BranchesSerializer, BranchBankDetailsSerializer, CompanySettingsSerializer
from config.utils_methods import build_response, list_all_objects, create_instance, update_instance, soft_delete
from config.utils_filter_methods import list_filtered_objects
from config.utils_variables import *
from django_filters.rest_framework import DjangoFilterBackend
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
        # Check if 'logo' exists in request data and is a list
        if 'logo' in request.data and isinstance(request.data['logo'], list):
            attachment_data_list = request.data['logo']
            if attachment_data_list:
                # Ensure all items in the list have the required fields
                for attachment in attachment_data_list:
                    if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
                        return build_response(0, "Missing required fields in some logo data.", [], status.HTTP_400_BAD_REQUEST)
               
                # Set the logo field in request data as a list of objects
                request.data['logo'] = attachment_data_list
                print("Using logo data: ", request.data['logo'])
            else:
                # Handle case where 'logo' list is empty
                return build_response(0, "'logo' list is empty.", [], status.HTTP_400_BAD_REQUEST)
        else:
            # Handle the case where 'logo' is not provided or not a list
            return build_response(0, "'logo' field is required and should be a list.", [], status.HTTP_400_BAD_REQUEST)
 
        # Proceed with creating the instance
        try:
            response = super().create(request, *args, **kwargs)
           
            # Format the response to include the picture data
            if isinstance(response.data, dict):
                picture_data = response.data.get('logo')
                if picture_data:
                    response.data['logo'] = picture_data
            return response
       
        except ValidationError as e:
            return build_response(1, "Creation failed due to validation errors.", e.detail, status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


class CompanySettingsViewSet(viewsets.ViewSet):
    """
    Retrieve or update the settings record for a company.
    The record is created automatically on first GET (get_or_create).
    URL pk = company_id (UUID).

    GET  /api/v1/company/company-settings/{company_id}/
    PATCH /api/v1/company/company-settings/{company_id}/
    """

    def retrieve(self, request, pk=None):
        try:
            company = Companies.objects.get(pk=pk)
        except Companies.DoesNotExist:
            return build_response(0, "Company not found.", [], status.HTTP_404_NOT_FOUND)
        cfg, _ = CompanySettings.objects.get_or_create(company_id=company)
        return build_response(1, "Settings retrieved successfully.", CompanySettingsSerializer(cfg).data, status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        try:
            company = Companies.objects.get(pk=pk)
        except Companies.DoesNotExist:
            return build_response(0, "Company not found.", [], status.HTTP_404_NOT_FOUND)
        cfg, _ = CompanySettings.objects.get_or_create(company_id=company)
        serializer = CompanySettingsSerializer(cfg, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return build_response(1, "Settings updated successfully.", serializer.data, status.HTTP_200_OK)
        return build_response(0, "Validation error.", serializer.errors, status.HTTP_400_BAD_REQUEST)


class BranchesViewSet(viewsets.ModelViewSet):
    queryset = Branches.objects.all()
    serializer_class = BranchesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BranchesFilters
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Branches, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Check if 'picture' exists in request data and is a list
        if 'picture' in request.data and isinstance(request.data['picture'], list):
            attachment_data_list = request.data['picture']
            if attachment_data_list:
                # Ensure all items in the list have the required fields
                for attachment in attachment_data_list:
                    if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
                        return build_response(0, "Missing required fields in some picture data.", [], status.HTTP_400_BAD_REQUEST)
               
                # Set the picture field in request data as a list of objects
                request.data['picture'] = attachment_data_list
                print("Using picture data: ", request.data['picture'])
            else:
                # Handle case where 'picture' list is empty
                return build_response(0, "'picture' list is empty.", [], status.HTTP_400_BAD_REQUEST)
        else:
            # Handle the case where 'picture' is not provided or not a list
            return build_response(0, "'picture' field is required and should be a list.", [], status.HTTP_400_BAD_REQUEST)
 
        # Proceed with creating the instance
        try:
            response = super().create(request, *args, **kwargs)
           
            # Format the response to include the picture data
            if isinstance(response.data, dict):
                picture_data = response.data.get('picture')
                if picture_data:
                    response.data['picture'] = picture_data
            return response
       
        except ValidationError as e:
            return build_response(1, "Creation failed due to validation errors.", e.detail, status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class BranchBankDetailsViewSet(viewsets.ModelViewSet):
    queryset = BranchBankDetails.objects.all()
    serializer_class = BranchBankDetailsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BranchBankDetailsFilters
    ordering_fields = []
    
    #log actions
    log_actions = True
    log_module_name = "Branch Bank Details"
    log_pk_field = "bank_detail_id"
    log_display_field = "bank_name"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)