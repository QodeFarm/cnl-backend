from rest_framework import serializers
from .models import *

class DesignationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designations
        fields = '__all__'

class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'

class EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = '__all__'