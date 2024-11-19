from rest_framework import serializers
from apps.masters.models import Statuses
from .models import *

class ModJobTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTypes
        fields = ['job_type_id','job_type_name']

class JobTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTypes
        fields = '__all__'

class ModDesignationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designations
        fields = ['designation_id','designation_name','responsibilities']

class DesignationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designations
        fields = '__all__'

		
class ModJobCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCodes
        fields = ['job_code_id','job_code']
		
class JobCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCodes
        fields = '__all__' 

		
class ModDepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = ['department_id','department_name']
		
class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'


class ModShiftsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shifts
        fields = ['shift_id','shift_name','start_time','end_time']
		
class ShiftsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shifts
        fields = '__all__'
 
 
class ModEmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = ['employee_id','first_name','last_name','email','phone','address','hire_date']
		
class EmployeesSerializer(serializers.ModelSerializer):
    job_type = ModJobTypesSerializer(source='job_type_id',read_only=True)
    designation = ModDesignationsSerializer(source='designation_id',read_only=True)
    job_code = ModJobCodesSerializer(source='job_code_id',read_only=True)
    department = ModDepartmentsSerializer(source='department_id',read_only=True)
    shift = ModShiftsSerializer(source = 'shift_id',read_only=True)
    class Meta:
        model = Employees
        fields = '__all__'
	
	
class ModEmployeeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDetails
        fields = ['employee_detail_id','date_of_birth','gender','nationality','emergency_contact']
		
class EmployeeDetailsSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id', read_only = True)
    class Meta:
        model = EmployeeDetails
        fields = '__all__'


class ModEmployeeSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalary
        fields = ['salary_id','salary_amount','salary_currency','salary_start_date','salary_end_date']
		
class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = EmployeeSalary
        fields = '__all__'


class ModSalaryComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponents
        fields = ['component_id','component_name']
		
class SalaryComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponents
        fields = '__all__'
	
	
class ModEmployeeSalaryComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSalaryComponents
        fields = ['employee_component_id','component_amount']
		
class EmployeeSalaryComponentsSerializer(serializers.ModelSerializer):
    component = ModSalaryComponentsSerializer(source='component_id', read_only = True)
    salary = ModEmployeeSalarySerializer(source='salary_id', read_only = True)
    class Meta:
        model = EmployeeSalaryComponents
        fields = '__all__'      

# =====================leaves====================================      

class ModLeaveTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypes
        fields = ['leave_type_id','leave_type_name','description','max_days_allowed']
		
class LeavesTypesSerializer(serializers.ModelSerializer):
    class Meta :
        model = LeaveTypes
        fields = '__all__'

class ModStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statuses
        fields = ['status_id','status_name']

		
class ModEmployeeLeavesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLeaves
        fields = ['leave_id','start_date','end_date', 'comments']
		
class EmployeeLeavesSerializer(serializers.ModelSerializer):
    status = ModStatusSerializer(source='status_id', read_only=True)
    leave_type = ModLeaveTypesSerializer(source='leave_type_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta :
        model = EmployeeLeaves
        fields = '__all__'
		

class ModLeaveApprovalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApprovals
        fields = ['approval_id','approval_date','comments']
		
class LeaveApprovalsSerializer(serializers.ModelSerializer):
    status = ModStatusSerializer(source='status_id', read_only=True)
    leave = ModEmployeeLeavesSerializer(source='leave_id', read_only=True)
    approver = ModEmployeesSerializer(source='approver_id', read_only=True)
    class Meta:
        model   = LeaveApprovals
        fields  = '__all__'
		

class ModEmployeeLeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLeaveBalance
        fields = ['balance_id','leave_balance','year']
		
class EmployeeLeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type = ModLeaveTypesSerializer(source='leave_type_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = EmployeeLeaveBalance
        fields = '__all__'
		

# ====================attendance====================================      

class ModAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['attendance_id','attendance_date','clock_in_time','clock_out_time']
		
class AttendanceSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id',read_only=True)
    status = ModStatusSerializer(source='status_id',read_only=True)
    department = ModDepartmentsSerializer(source='department_id',read_only=True)
    shift = ModShiftsSerializer(source='shift_id',read_only=True)
    class Meta:
        model = Attendance
        fields = '__all__'


class ModSwipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Swipes
        fields = ['swipe_id','swipe_time']
		
class SwipesSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id', read_only = True)
    class Meta:
        model = Swipes
        fields = '__all__'


class ModBiometricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biometric
        fields = ['biometric_id','biometric_entry_id','template_data','entry_stamp']
		
class BiometricSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source = 'employee_id',read_only =  True)
    class Meta:
        model = Biometric
        fields = '__all__'
