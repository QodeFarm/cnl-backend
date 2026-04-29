from rest_framework import serializers
from .models import Companies, Branches, BranchBankDetails, CompanySettings
from apps.masters.serializers import ModCitySerializer, ModStateSerializer, ModCountrySerializer, ModStatusesSerializer 
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from passlib.hash import bcrypt
from apps.products.serializers import PictureSerializer

class ModCompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = ['company_id','name']

class ModBranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branches
        fields = ['branch_id','name']
    
class CompaniesSerializer(serializers.ModelSerializer):
    city = ModCitySerializer(source='city_id', read_only = True)
    state = ModStateSerializer(source='state_id', read_only = True)
    country = ModCountrySerializer(source='country_id', read_only = True)
    logo = PictureSerializer(many=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Companies
        fields = '__all__'
        
    def get_logo_url(self, obj):
        if obj.logo and isinstance(obj.logo, list) and len(obj.logo) > 0:
            logo_path = obj.logo[0].get("attachment_path", "")
            if logo_path:
                return f"{settings.MEDIA_URL}{logo_path}"
        return None  # Or return a default logo

class BranchesSerializer(serializers.ModelSerializer): 
    company = ModCompaniesSerializer(source='company_id', read_only = True)
    status = ModStatusesSerializer(source='status_id', read_only = True)
    city = ModCitySerializer(source='city_id', read_only = True)
    state = ModStateSerializer(source='state_id', read_only = True)
    country = ModCountrySerializer(source='country_id', read_only = True)
    picture = PictureSerializer(many=True)
    class Meta:
        model = Branches
        fields='__all__'

class BranchBankDetailsSerializer(serializers.ModelSerializer):
    branch = ModBranchesSerializer(source='branch_id', read_only = True)
    class Meta:
        model = BranchBankDetails
        fields = '__all__'


class CompanySettingsSerializer(serializers.ModelSerializer):
    # Read-only display names — used by the frontend to show the selected account name
    sales_account_name         = serializers.CharField(source='sales_ledger_account.name',    read_only=True, default=None)
    purchase_account_name      = serializers.CharField(source='purchase_ledger_account.name', read_only=True, default=None)
    receivables_account_name   = serializers.CharField(source='receivables_account.name',     read_only=True, default=None)
    payables_account_name      = serializers.CharField(source='payables_account.name',        read_only=True, default=None)
    cash_account_name          = serializers.CharField(source='cash_account.name',            read_only=True, default=None)
    bank_account_name          = serializers.CharField(source='bank_account.name',            read_only=True, default=None)
    discount_account_name      = serializers.CharField(source='discount_account.name',        read_only=True, default=None)
    round_off_account_name     = serializers.CharField(source='round_off_account.name',       read_only=True, default=None)

    class Meta:
        model  = CompanySettings
        fields = '__all__'