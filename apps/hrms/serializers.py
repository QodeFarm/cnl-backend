from rest_framework import serializers
from .models import *
# from apps.masters.serializers import StatusesSerializer

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


class ModOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['org_id','org_name','org_address','description','org_email']
		
class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = '__all__'


class ModEmployeeCompensationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeCompensationHistory
        fields = ['compensation_id','start_date','compensation_name','amount','currency']
		
class EmployeeCompensationHistorySerializer(serializers.ModelSerializer):
    org = ModOrganisationSerializer(source = 'org_id',read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = EmployeeCompensationHistory
        fields = '__all__'
		
class ModOrganisationBranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationBranches
        fields = ['org_branch_id','branch_name','branch_address','branch_contact_person']
		
class OrganisationBranchesSerializer(serializers.ModelSerializer):
    org = ModOrganisationSerializer(source='org_id',read_only=True)
    class Meta:
        model = OrganisationBranches
        fields = '__all__'

class ModEmployeeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeHistory
        fields = ['history_id','start_date','action_name']
		
class EmployeeHistorySerializer(serializers.ModelSerializer):
    job_type = ModJobTypesSerializer(source='job_type_id',read_only=True)
    designation = ModDesignationsSerializer(source='designation_id',read_only=True)
    manager = ModEmployeesSerializer(source='manager_id', read_only=True)
    branch = ModOrganisationBranchesSerializer(source='branch_id',read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)

    class Meta:
        model = EmployeeHistory
        fields = '__all__'

		
class ModPreviousCompanyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PreviousCompanyHistory
        fields = ['history_id','company_name','position','start_date','end_date']
		
class PreviousCompanyHistorySerializer(serializers.ModelSerializer):
    employee= ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = PreviousCompanyHistory
        fields = '__all__'
	
	
class ModEmployeesalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employeesalary
        fields = ['salary_id','salary_amount','salary_currency','salary_start_date','salary_end_date']
		
class EmployeesalarySerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = Employeesalary
        fields = '__all__'
	
	
class ModHardwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hardware
        fields = ['hardware_id','hardware_name']
		
class HardwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hardware
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
    salary = ModEmployeesalarySerializer(source='salary_id', read_only = True)
    class Meta:
        model = EmployeeSalaryComponents
        fields = '__all__'      


class ModBenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefits
        fields = ['benefit_id','benefit_name']
		
class BenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefits
        fields = '__all__'
	

class ModBenefitProvidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitProviders
        fields = ['provider_id','provider_name']
		
class BenefitProvidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitProviders
        fields = '__all__'  


class ModEmployeeBenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBenefits
        fields = ['employee_benefit_id','enrollment_date','coverage_amount']
		
class EmployeeBenefitsSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id',read_only=True)
    benefit = ModBenefitsSerializer(source='benefit_id',read_only=True)
    class Meta:
        model = EmployeeBenefits
        fields = '__all__'


class ModEmployeeBenefitProvidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBenefitProviders
        fields = ['employee_benefit_provider_id','policy_number']
		
class EmployeeBenefitProvidersSerializer(serializers.ModelSerializer):
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    benefit = ModBenefitsSerializer(source='benefit_id', read_only=True)
    provider = ModBenefitProvidersSerializer(source='provider_id', read_only=True)
    class Meta:
        model = EmployeeBenefitProviders
        fields = '__all__'


class ModEmployeeOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeOnboarding
        fields = ['onboarding_id','onboarding_date','orientation_completed']

class EmployeeOnbordingSerializer(serializers.ModelSerializer):
    # status = StatusesSerializer(source='status_id', read_only=True)
    department_training = ModDepartmentsSerializer(source='department_training_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    mentor = ModEmployeesSerializer(source='mentor_id', read_only=True)
    class Meta :
        model = EmployeeOnboarding
        fields = '__all__'
		
		
class ModEmployeeHardwareAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeHardwareAssignment
        fields = ['assignment_id','onboarding_id','hardware_id']
		
class EmployeeHardwareAssignmentSerializer(serializers.ModelSerializer):
    onboarding = ModEmployeeOnboardingSerializer(source='onboarding_id',read_only=True)
    hardware = ModHardwareSerializer(source='hardware_id',read_only=True)
    class Meta:
        model = EmployeeHardwareAssignment
        fields = '__all__'        


# =====================leaves====================================      

# class ModStatusesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Statuses
#         fields = ['status_id','status_name']
		
# class StatusesSerializer(serializers.ModelSerializer):
#     class Meta :
#         model = Statuses
#         fields = '__all__'
		

class ModLeaveTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypes
        fields = ['leave_type_id','leave_type_name','description','max_days_allowed']
		
class LeavesTypesSerializer(serializers.ModelSerializer):
    class Meta :
        model = LeaveTypes
        fields = '__all__'

		
class ModEmployeeLeavesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLeaves
        fields = ['leave_id','start_date','end_date']
		
class EmployeeLeavesSerializer(serializers.ModelSerializer):
    # status = StatusesSerializer(source='status_id', read_only=True)
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
    # status = StatusesSerializer(source='status_id', read_only=True)
    leave = ModLeaveTypesSerializer(source='leave_id', read_only=True)
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
    # status = StatusesSerializer(source='status_id',read_only=True)
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

# class ModEmployeesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employees
#         fields = ['employee_id','name','email']

# class ModDesignationsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Designations
#         fields = ['designation_id','designation_name']

# class ModDepartmentsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Departments
#         fields = ['department_id','department_name']

# class DesignationsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Designations
#         fields = '__all__'

# class DepartmentsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Departments
#         fields = '__all__'

# class EmployeesSerializer(serializers.ModelSerializer):
#     designation = ModDesignationsSerializer(source='designation_id', read_only=True)
#     department = ModDepartmentsSerializer(source='department_id', read_only=True)

#     class Meta:
#         model = Employees
#         fields = '__all__'