from rest_framework import serializers
from .models import *

class ModEmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = ['employee_id','name']

class ModDesignationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designations
        fields = ['designation_id','designation_name']

class ModDepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = ['department_id','department_name']

class DesignationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designations
        fields = '__all__'

class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'

class EmployeesSerializer(serializers.ModelSerializer):
    designation = ModDesignationsSerializer(source='designation_id', read_only=True)
    department = ModDepartmentsSerializer(source='department_id', read_only=True)

    class Meta:
        model = Employees
        fields = '__all__'