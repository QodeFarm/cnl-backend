from rest_framework import serializers
from .models import Companies, Branches, BranchBankDetails 
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

    class Meta:
        model = Companies
        fields = '__all__'

    def create(self, validated_data):
        logo = validated_data.pop('logo', None)
        instance = super().create(validated_data)
        if logo:
            instance.logo = logo
            instance.save()
        return instance

    def update(self, instance, validated_data):
        logo = validated_data.pop('logo', None)
        if logo:
            # Delete the previous logo file and its directory if they exist
            if instance.logo:
                logo_path = instance.logo.path
                if os.path.exists(logo_path):
                    os.remove(logo_path)
                    logo_dir = os.path.dirname(logo_path)
                    if not os.listdir(logo_dir):
                        os.rmdir(logo_dir)
            instance.logo = logo
            instance.save()
        return super().update(instance, validated_data)


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