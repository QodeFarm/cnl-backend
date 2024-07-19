from rest_framework import serializers
from .models import *
from apps.hrms.serializers import ModEmployeesSerializer
#--------------Mod Serializers------------------------------
class ModLeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = ['lead_id','name']

class ModLeadStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStatuses
        fields = ['lead_status_id','status_name']

class ModInteractionTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionTypes
        fields = ['interaction_type_id','interaction_type']
#-------------------------------------------------------------
        
class LeadStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStatuses
        fields = '__all__'

class InteractionTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionTypes
        fields = '__all__'

class LeadsSerializer(serializers.ModelSerializer):
    lead_status = ModLeadStatusesSerializer(source='lead_status_id', read_only=True)
    class Meta:
        model = Leads
        fields = '__all__'

class LeadAssignmentsSerializer(serializers.ModelSerializer):
    lead = ModLeadsSerializer(source='lead_id', read_only=True)
    sales_rep = ModEmployeesSerializer(source='sales_rep_id', read_only=True)
    class Meta:
        model = LeadAssignments
        fields = '__all__'

class LeadInteractionsSerializer(serializers.ModelSerializer):
    lead = ModLeadsSerializer(source='lead_id', read_only=True)
    interaction_type = ModInteractionTypesSerializer(source='interaction_type_id', read_only=True)
    class Meta:
        model = LeadInteractions
        fields = '__all__'

class LeadAssignmentHistorySerializer(serializers.ModelSerializer):
    lead = ModLeadsSerializer(source='lead_id', read_only=True)
    sales_rep = ModEmployeesSerializer(source='sales_rep_id', read_only=True)
    class Meta:
        model = LeadAssignmentHistory
        fields = '__all__'