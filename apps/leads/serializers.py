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

# ------------ FOR LEADS ApiView---------------------------------
class ModLeadAssignmentsSerializer(serializers.ModelSerializer):
    sales_rep = ModEmployeesSerializer(source='sales_rep_id', read_only=True)
    class Meta:
        model = LeadAssignments
        fields = ['sales_rep']

class ModLeadInteractionsSerializer(serializers.ModelSerializer):
    interaction_type = ModInteractionTypesSerializer(source='interaction_type_id', read_only=True)
    class Meta:
        model = LeadInteractions
        fields = ['interaction_date','interaction_type','notes']

class ModLeadSerializer(serializers.ModelSerializer):
    lead_status = ModLeadStatusesSerializer(source='lead_status_id', read_only=True)
    asignment = ModLeadAssignmentsSerializer(many=True, read_only=True)
    interaction = ModLeadInteractionsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Leads
        fields = '__all__'

    def to_representation(self, instance):
                # Get the default serialized data
                representation = super().to_representation(instance)

                # Flatten the data according to your requirements
                flat_representation = {
                    'lead_id': representation.get('lead_id'),
                    'name': representation.get('name'),
                    'email': representation.get('email'),
                    'phone': representation.get('phone'),
                    'score': representation.get('score'),
                    'lead_status':None,
                    'sales_rep_name':None,                
                    'interaction_date': None,
                    'interaction_type': None,
                    'notes': None,
                    'created_at': representation.get('created_at'),
                    'updated_at': representation.get('updated_at'),
                }

                # Extract the nested fields and flatten them
                if representation.get('lead_status'):
                    first_status = representation['lead_status']
                    flat_representation['lead_status'] = first_status.get('status_name')

                if representation.get('asignment'):
                    first_assignment = representation['asignment'][0]
                    flat_representation['sales_rep_name'] = first_assignment['sales_rep'].get('name')

                if representation.get('interaction'):
                    first_interaction = representation['interaction'][0]
                    flat_representation['interaction_date'] = first_interaction.get('interaction_date')
                    flat_representation['interaction_type'] = first_interaction['interaction_type'].get('interaction_type')
                    flat_representation['notes'] = first_interaction.get('notes')

                return flat_representation