from rest_framework import serializers
from apps.masters.models import Statuses
from .models import JobTypes, Designations, JobCodes, Departments, Shifts, Employees, EmployeeSalary, SalaryComponents, EmployeeSalaryComponents, LeaveTypes, EmployeeLeaves, LeaveApprovals, EmployeeLeaveBalance, EmployeeAttendance, Swipes, Biometric
from datetime import timedelta

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
        fields = ['employee_id','first_name','last_name','email','phone','gender','manager_id']
		
class EmployeesSerializer(serializers.ModelSerializer):
    job_type = ModJobTypesSerializer(source='job_type_id',read_only=True)
    designation = ModDesignationsSerializer(source='designation_id',read_only=True)
    job_code = ModJobCodesSerializer(source='job_code_id',read_only=True)
    department = ModDepartmentsSerializer(source='department_id',read_only=True)
    shift = ModShiftsSerializer(source = 'shift_id',read_only=True)
    manager = ModEmployeesSerializer(source = 'manager_id',read_only=True)
    class Meta:
        model = Employees
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
    leave_type = ModLeaveTypesSerializer(source='leave_type_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = EmployeeLeaves
        fields = ['leave_id','start_date','end_date', 'comments','employee','leave_type']

class EmployeeLeavesSerializer(serializers.ModelSerializer):
    leave_type = ModLeaveTypesSerializer(source='leave_type_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = EmployeeLeaves
        fields = '__all__'

    def validate(self, data):
        employee = data.get('employee_id')
        leave_type = data.get('leave_type_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Retrieve the employee's leave balance for the given leave type
        leave_balance_record = EmployeeLeaveBalance.objects.filter(
            employee_id=employee, leave_type_id=leave_type
        ).first()

        if leave_balance_record:
            # Get the leave balance value
            leave_balance = leave_balance_record.leave_balance

            # Calculate the number of days excluding weekends
            days_count = self.get_days_excluding_weekends(start_date, end_date)

            # Check if the requested leave duration exceeds the available balance
            if days_count > leave_balance:
                error_message = (
                    f"Your leave balance is {leave_balance} days. "
                    f"You cannot apply for more than {leave_balance} days."
                )
                raise serializers.ValidationError(error_message)
            
        else:
            raise serializers.ValidationError(f"No leave balance record found for Employee {employee} and Leave Type {leave_type}.")

        return data

    def get_days_excluding_weekends(self, start_date, end_date):
        """
        This method calculates the number of days between start_date and end_date
        excluding weekends (Saturday and Sunday).
        """
        total_days = (end_date - start_date).days + 1  # Include the start date
        weekend_days = 0

        # Loop through each day and count weekends
        current_day = start_date
        while current_day <= end_date:
            if current_day.weekday() in [5, 6]:  # Saturday and Sunday
                weekend_days += 1
            current_day += timedelta(days=1)

        # Exclude weekend days
        return total_days - weekend_days


class ModLeaveApprovalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApprovals
        fields = ['approval_id','approval_date','status_id']
		
class LeaveApprovalsSerializer(serializers.ModelSerializer):
    status = ModStatusSerializer(source='status_id', read_only=True)
    leave = ModEmployeeLeavesSerializer(source='leave_id', read_only=True)
    approver = ModEmployeesSerializer(source='approver_id', read_only=True)
    leave_days = serializers.SerializerMethodField()  # Add leave_days field
    class Meta:
        model = LeaveApprovals
        fields = '__all__'  # Include all fields, including the leave_days field

    def get_leave_days(self, obj):
        # Ensure both start_date and end_date are present in the leave object
        leave = obj.leave_id  # Access the related leave object
        if leave and leave.start_date and leave.end_date:
            leave_days = self.calculate_leave_days(leave.start_date, leave.end_date)
            return leave_days
        return 0

    @staticmethod
    def calculate_leave_days(start_date, end_date):
        """Calculate the leave days excluding weekends."""
        total_days = (end_date - start_date).days + 1
        leave_days = 0

        for i in range(total_days):
            current_date = start_date + timedelta(days=i)
            if current_date.weekday() < 5:  # Exclude Saturdays (5) and Sundays (6)
                leave_days += 1

        return leave_days


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

class ModEmployeeAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAttendance
        fields = ['employee_attendance_id','attendance_date','absent','leave_duration']
		
class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id',read_only=True)
    class Meta:
        model = EmployeeAttendance
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
