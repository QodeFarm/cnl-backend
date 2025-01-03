from collections import OrderedDict
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

class ModLeadInteractionsSerializer(serializers.ModelSerializer):
    interaction_type = ModInteractionTypesSerializer(source='interaction_type_id', read_only=True)
    class Meta:
        model = LeadInteractions
        fields = ['interaction_date','interaction_type','notes']
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
    assignee = ModEmployeesSerializer(source='assignee_id', read_only=True)
    interaction = ModLeadInteractionsSerializer(many=True, read_only=True)
    class Meta:
        model = Leads
        fields = '__all__'

    # Not modifying the output data, but in order to find latest record in interaction, sorting the data to get latest record at 0 Index.
    def to_representation(self, instance):
        # Get the original representation
        representation = super().to_representation(instance)

        # Retrieve the list of interactions from the representation
        interaction_data = representation.get('interaction', [])

        # Check if interaction_data is list
        if isinstance(interaction_data, list):
            interaction_data = list(interaction_data)
            interaction_data = sorted(interaction_data, key=lambda x: x['interaction_date'], reverse=True)

        representation['interaction'] = interaction_data
        return representation

class LeadInteractionsSerializer(serializers.ModelSerializer):
    lead = ModLeadsSerializer(source='lead_id', read_only=True)
    interaction_type = ModInteractionTypesSerializer(source='interaction_type_id', read_only=True)
    class Meta:
        model = LeadInteractions
        fields = '__all__'

class LeadAssignmentHistorySerializer(serializers.ModelSerializer):
    lead = ModLeadsSerializer(source='lead_id', read_only=True)
    assignee = ModEmployeesSerializer(source='assignee_id', read_only=True)
    class Meta:
        model = LeadAssignmentHistory
        fields = '__all__'
