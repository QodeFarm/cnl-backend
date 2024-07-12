from rest_framework import serializers
from .models import *

class LeadStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStatuses
        fields = '__all__'

class InteractionTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionTypes
        fields = '__all__'

class LeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = '__all__'

class LeadAssignmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadAssignments
        fields = '__all__'