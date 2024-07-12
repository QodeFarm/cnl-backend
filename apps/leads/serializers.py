from rest_framework import serializers
from .models import *

class LeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = '__all__'

class LeadAssignmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadAssignments
        fields = '__all__'