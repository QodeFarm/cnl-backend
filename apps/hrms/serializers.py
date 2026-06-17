from datetime import datetime, timedelta
from rest_framework import serializers
from apps.masters.models import Statuses
from .models import JobTypes, Designations, JobCodes, Departments, Shifts, Employees, EmployeeSalary, SalaryComponents, EmployeeSalaryComponents, LeaveTypes, EmployeeLeaves, LeaveApprovals, EmployeeLeaveBalance, EmployeeAttendance, Swipes, Biometric, Timesheets, TimesheetEntries, TimesheetApprovals
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

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
		
class PictureSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    attachment_name = serializers.CharField(max_length=255)
    file_size = serializers.IntegerField()
    attachment_path = serializers.CharField(max_length=255)
  
# class EmployeesSerializer(serializers.ModelSerializer):
#     job_type = ModJobTypesSerializer(source='job_type_id',read_only=True)
#     designation = ModDesignationsSerializer(source='designation_id',read_only=True)
#     job_code = ModJobCodesSerializer(source='job_code_id',read_only=True)
#     department = ModDepartmentsSerializer(source='department_id',read_only=True)
#     shift = ModShiftsSerializer(source = 'shift_id',read_only=True)
#     manager = ModEmployeesSerializer(source = 'manager_id',read_only=True)
#     full_name = serializers.CharField(read_only=True)
    
#     picture = PictureSerializer(required=True, allow_null=False, many=True)
#     class Meta:
#         model = Employees
#         fields = '__all__'

class EmployeesSerializer(serializers.ModelSerializer):
    job_type = ModJobTypesSerializer(source='job_type_id', read_only=True)
    designation = ModDesignationsSerializer(source='designation_id', read_only=True)
    job_code = ModJobCodesSerializer(source='job_code_id', read_only=True)
    department = ModDepartmentsSerializer(source='department_id', read_only=True)
    shift = ModShiftsSerializer(source='shift_id', read_only=True)
    manager = ModEmployeesSerializer(source='manager_id', read_only=True)
    full_name = serializers.CharField(read_only=True)
    picture = PictureSerializer(required=False, allow_null=True, many=True)
    
    class Meta:
        model = Employees
        fields = '__all__'
        
    def validate_username(self, value):
        """
        Validate that the username is unique, excluding the current instance
        """
        if self.instance and self.instance.username == value:
            return value
        if Employees.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        """
        Validate that the email is unique, excluding the current instance
        This allows employees to change their email as long as it's not used by someone else
        """
        # If we have an instance (update operation)
        if self.instance:
            # If the email hasn't changed, it's valid
            if self.instance.email == value:
                return value
            # If the email has changed, check if it's used by any OTHER employee
            if Employees.objects.filter(email=value).exclude(employee_id=self.instance.employee_id).exists():
                raise serializers.ValidationError("Email already exists")
        else:
            # For new employees, check if email already exists
            if Employees.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        return value
    
    def validate(self, data):
        """
        Additional cross-field validation
        """
        # Check if username is being updated and if it already exists (excluding current instance)
        username = data.get('username')
        if username and self.instance:
            if Employees.objects.filter(username=username).exclude(employee_id=self.instance.employee_id).exists():
                raise serializers.ValidationError({"username": "Username already exists"})
        
        # Check if email is being updated and if it already exists (excluding current instance)
        email = data.get('email')
        if email and self.instance:
            if Employees.objects.filter(email=email).exclude(employee_id=self.instance.employee_id).exists():
                raise serializers.ValidationError({"email": "Email already exists"})
        
        return data



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

# class EmployeeLeavesSerializer(serializers.ModelSerializer):
#     leave_type = ModLeaveTypesSerializer(source='leave_type_id', read_only=True)
#     employee = ModEmployeesSerializer(source='employee_id', read_only=True)
#     class Meta:
#         model = EmployeeLeaves
#         fields = '__all__'

#     def validate(self, data):
#         employee = data.get('employee_id')
#         leave_type = data.get('leave_type_id')
#         start_date = data.get('start_date')
#         end_date = data.get('end_date')

#         # Retrieve the employee's leave balance for the given leave type
#         leave_balance_record = EmployeeLeaveBalance.objects.filter(
#             employee_id=employee, leave_type_id=leave_type
#         ).first()

#         if leave_balance_record:
#             # Get the leave balance value
#             leave_balance = leave_balance_record.leave_balance

#             # Calculate the number of days excluding weekends
#             days_count = self.get_days_excluding_weekends(start_date, end_date)

#             # Check if the requested leave duration exceeds the available balance
#             if days_count > leave_balance:
#                 error_message = (
#                     f"Your leave balance is {leave_balance} days. "
#                     f"You cannot apply for more than {leave_balance} days."
#                 )
#                 raise serializers.ValidationError(error_message)
            
#         else:
#             raise serializers.ValidationError(f"No leave balance record found for Employee {employee} and Leave Type {leave_type}.")

#         return data

#     def get_days_excluding_weekends(self, start_date, end_date):
#         """
#         This method calculates the number of days between start_date and end_date
#         excluding weekends (Saturday and Sunday).
#         """
#         total_days = (end_date - start_date).days + 1  # Include the start date
#         weekend_days = 0

#         # Loop through each day and count weekends
#         current_day = start_date
#         while current_day <= end_date:
#             if current_day.weekday() in [5, 6]:  # Saturday and Sunday
#                 weekend_days += 1
#             current_day += timedelta(days=1)

#         # Exclude weekend days
#         return total_days - weekend_days

class EmployeeLeavesSerializer(serializers.ModelSerializer):
    leave_type = ModLeaveTypesSerializer(source='leave_type_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    
    class Meta:
        model = EmployeeLeaves
        fields = '__all__'

    def validate(self, data):
        """
        Comprehensive validation for employee leave requests
        """
        employee = data.get('employee_id')
        leave_type = data.get('leave_type_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Get current year
        current_year = datetime.now().year
        
        # Get employee name for error messages
        employee_name = f"{employee.first_name} {employee.last_name}" if hasattr(employee, 'first_name') and employee.first_name else str(employee.employee_code)
        
        # Validate dates
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'date_validation': "End date must be later than or equal to the start date."
                })
        
        # Calculate requested days (only for validation, not stored)
        requested_days = self.get_days_excluding_weekends(start_date, end_date)
        
        if requested_days <= 0:
            raise serializers.ValidationError({
                'days_validation': "Leave duration must be at least 1 day."
            })
        
        # Check for overlapping leave requests (not deleted)
        overlapping_leaves = EmployeeLeaves.objects.filter(
            employee_id=employee,
            is_deleted=False,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exclude(leave_id=data.get('leave_id') if data.get('leave_id') else None)
        
        if overlapping_leaves.exists():
            raise serializers.ValidationError({
                'overlap_validation': f"You already have a leave request for these dates. Please check your existing leaves."
            })
        
        # Get or create leave balance record
        leave_balance_record = EmployeeLeaveBalance.objects.filter(
            employee_id=employee, 
            leave_type_id=leave_type,
            year=str(current_year)
        ).first()
        
        # If no balance record exists, create one with default values
        if not leave_balance_record:
            # Get max days allowed from leave type (add this field to your LeaveTypes model)
            max_days_allowed = getattr(leave_type, 'max_days_allowed', 12)  # Default 12 days
            
            # Create new leave balance record
            leave_balance_record = EmployeeLeaveBalance.objects.create(
                employee_id=employee,
                leave_type_id=leave_type,
                year=str(current_year),
                leave_balance=max_days_allowed
            )
            
            logger.info(f"Auto-created leave balance for {employee_name} - {leave_type.leave_type_name} with {max_days_allowed} days for year {current_year}")
        
        # Calculate used leaves for this employee and leave type in current year
        used_leaves = self.calculate_used_leaves(employee, leave_type, current_year)
        
        # Calculate available balance
        total_balance = float(leave_balance_record.leave_balance)
        available_balance = total_balance - used_leaves
        
        # Check if sufficient balance is available
        if requested_days > available_balance:
            error_message = (
                f"Insufficient leave balance.\n"
                f"Requested: {requested_days} days\n"
                f"Available: {available_balance} days\n"
                f"Total Balance: {total_balance} days\n"
                f"Used this year: {used_leaves} days\n"
                f"Leave Type: {leave_type.leave_type_name}"
            )
            raise serializers.ValidationError(error_message)
        
        # Check if requesting more than allowed per request (optional)
        max_days_per_request = getattr(leave_type, 'max_days_per_request', 30)
        if requested_days > max_days_per_request:
            raise serializers.ValidationError({
                'days_validation': f"You cannot apply for more than {max_days_per_request} days in a single leave request for {leave_type.leave_type_name}."
            })
        
        # DO NOT add total_days to data - your model doesn't have this field
        # Just store it in validated_data if needed for post-processing
        self.context['requested_days'] = requested_days
        
        # Log successful validation
        logger.info(f"Leave validation passed for {employee_name} - {leave_type.leave_type_name}: Requested {requested_days} days, Available {available_balance} days")
        
        return data
    
    def calculate_used_leaves(self, employee, leave_type, year):
        """
        Calculate total used leaves for an employee for a specific leave type in a given year
        Counts approved leaves only
        """
        # First get all employee leaves for this year
        employee_leaves = EmployeeLeaves.objects.filter(
            employee_id=employee,
            leave_type_id=leave_type,
            start_date__year=year,
            is_deleted=False
        )
        
        # If leaves exist, check which are approved via LeaveApprovals
        total_used_days = 0
        for leave in employee_leaves:
            # Check if this leave is approved
            is_approved = LeaveApprovals.objects.filter(
                leave_id=leave,
                status_id__status_name='Approved'  # Adjust based on your Statuses model
            ).exists()
            
            if is_approved:
                total_used_days += self.get_days_excluding_weekends(
                    leave.start_date, 
                    leave.end_date
                )
        
        return total_used_days
    
    def get_days_excluding_weekends(self, start_date, end_date):
        """
        Calculate number of days between start_date and end_date excluding weekends (Saturday and Sunday)
        """
        if not start_date or not end_date:
            return 0
        
        # Ensure start_date <= end_date
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        total_days = (end_date - start_date).days + 1
        weekend_days = 0
        
        current_day = start_date
        while current_day <= end_date:
            if current_day.weekday() in [5, 6]:  # Saturday (5) or Sunday (6)
                weekend_days += 1
            current_day += timedelta(days=1)
        
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


# ===================== timesheets ====================================

class ModTimesheetsSerializer(serializers.ModelSerializer):
    """Minimal representation used when a timesheet is embedded inside another
    serializer (e.g. inside TimesheetApprovalsSerializer)."""
    class Meta:
        model = Timesheets
        fields = ['timesheet_id', 'start_date', 'end_date', 'total_hours', 'notes']


class TimesheetsSerializer(serializers.ModelSerializer):
    """
    Full timesheet serializer.

    Read-only nested fields:
      - employee  : expanded employee object for display purposes.
      - customer  : expanded client object (id + name) for billing display.

    Write fields (flat IDs):
      - employee_id : FK — send the UUID directly when creating/updating.
      - customer_id : FK — send the client UUID when the work is billable.

    Validation rules enforced here:
      1. end_date must be >= start_date.
      2. No duplicate active timesheet for the same employee + period.
         (The DB constraint is the final guard; this gives a friendly message.)
    """
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    # Lightweight nested client (id + name). Implemented as a method field so we
    # do not import a Customer serializer across apps (keeps imports clean and
    # avoids any circular-import risk).
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Timesheets
        fields = '__all__'
        # Disable DRF's auto-generated UniqueTogetherValidator (built from the
        # model's UniqueConstraint). That validator cannot exclude the record
        # being edited, so it wrongly blocks every UPDATE. We perform our own
        # duplicate-period check in validate() below, which correctly excludes
        # the current record on update.
        validators = []

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        employee = data.get('employee_id')

        # --- date order check ---
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'date_validation': "end_date must be on or after start_date."
                })

        # --- duplicate period check (excludes the current record on update) ---
        if start_date and end_date and employee:
            existing_qs = Timesheets.objects.filter(
                employee_id=employee,
                start_date=start_date,
                end_date=end_date,
                is_deleted=False,
            )

            # Determine the current record's PK so we never flag it against itself.
            # - On a normal update the instance is set.
            # - In this project's update flow the PK arrives inside the payload
            #   as 'timesheet_id', so fall back to that.
            current_pk = None
            if self.instance is not None:
                current_pk = self.instance.pk
            elif getattr(self, 'initial_data', None):
                current_pk = self.initial_data.get('timesheet_id')

            if current_pk:
                existing_qs = existing_qs.exclude(pk=current_pk)

            if existing_qs.exists():
                raise serializers.ValidationError({
                    'duplicate_validation': (
                        "An active timesheet already exists for this employee "
                        "covering the same period."
                    )
                })

        return data

    def get_customer(self, obj):
        """Return a minimal client object {customer_id, name} for display, or None."""
        client = obj.customer_id  # FK attribute returns the related Customer instance
        if client:
            return {'customer_id': str(client.customer_id), 'name': client.name}
        return None


class ModTimesheetEntriesSerializer(serializers.ModelSerializer):
    """Minimal representation used for embedding entries in responses."""
    class Meta:
        model = TimesheetEntries
        fields = ['entry_id', 'work_date', 'hours_worked', 'description']


class TimesheetEntriesSerializer(serializers.ModelSerializer):
    """
    Full timesheet entry serializer.

    Read-only nested fields:
      - timesheet : expanded timesheet header for context.

    Validation rules enforced here:
      1. hours_worked must be between 0.01 and 24.00.
      2. work_date must fall within the parent timesheet's start_date / end_date.
         (work_date vs period check only runs when timesheet_id is available.)
    """
    timesheet = ModTimesheetsSerializer(source='timesheet_id', read_only=True)

    class Meta:
        model = TimesheetEntries
        fields = '__all__'

    def validate(self, data):
        hours_worked = data.get('hours_worked')
        work_date = data.get('work_date')
        timesheet = data.get('timesheet_id')

        # --- hours range check ---
        if hours_worked is not None:
            if hours_worked <= 0 or hours_worked > 24:
                raise serializers.ValidationError({
                    'hours_validation': "hours_worked must be between 0.01 and 24.00."
                })

        # --- work_date within timesheet period check ---
        if work_date and timesheet:
            if work_date < timesheet.start_date or work_date > timesheet.end_date:
                raise serializers.ValidationError({
                    'date_range_validation': (
                        f"work_date {work_date} must fall within the timesheet period "
                        f"({timesheet.start_date} to {timesheet.end_date})."
                    )
                })

        return data


class ModTimesheetApprovalsSerializer(serializers.ModelSerializer):
    """Minimal representation used when embedding an approval inside another
    serializer (e.g. inside the timesheet detail response)."""
    class Meta:
        model = TimesheetApprovals
        fields = ['timesheet_approval_id', 'approval_date', 'rejection_reason', 'status_id']


class TimesheetApprovalsSerializer(serializers.ModelSerializer):
    """
    Full timesheet approval serializer.

    Read-only nested fields:
      - status    : expanded status object (status_id, status_name).
      - timesheet : expanded timesheet header.
      - approver  : expanded approver employee object.

    Also exposes total_hours directly from the related timesheet so the
    approvals list does not need a separate API call to show hours worked.
    """
    status = ModStatusSerializer(source='status_id', read_only=True)
    timesheet = ModTimesheetsSerializer(source='timesheet_id', read_only=True)
    approver = ModEmployeesSerializer(source='approver_id', read_only=True)
    # Convenience field: surface the employee who owns the timesheet.
    employee = serializers.SerializerMethodField()
    total_hours = serializers.SerializerMethodField()

    class Meta:
        model = TimesheetApprovals
        fields = '__all__'

    def get_employee(self, obj):
        """Return the employee who owns the related timesheet."""
        try:
            emp = obj.timesheet_id.employee_id
            return ModEmployeesSerializer(emp).data
        except Exception:
            return {}

    def get_total_hours(self, obj):
        """Return total_hours from the related timesheet for quick display."""
        try:
            return obj.timesheet_id.total_hours
        except Exception:
            return None
        
        
 #employee portal login
# Add to your existing serializers.py
from django.contrib.auth.hashers import check_password

# serializers.py
from django.contrib.auth.hashers import check_password

class EmployeePortalLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        print(f"🔍 Validating username: {username}")
        
        try:
            # Use the model name correctly (Employees or Employee based on your model)
            # from apps.hrms.models import Employees  # or Employees
            
            employee = Employees.objects.get(
                username=username, 
                is_portal_user=True, 
                is_deleted=False
            )
            print(f"✅ Employee found: {employee.full_name}")
            print(f"📝 Stored password hash: {employee.password[:50]}...")
            
            # Check password
            if not employee.password:
                print("❌ Password is None in database")
                raise serializers.ValidationError("Password not set. Please generate credentials first.")
            
            if not check_password(password, employee.password):
                print("❌ Password check failed")
                raise serializers.ValidationError("Invalid credentials")
            
            print("✅ Password verified successfully")
            data['employee'] = employee
            return data
            
        except Employees.DoesNotExist:
            print(f"❌ Employee not found with username: {username}")
            raise serializers.ValidationError("Invalid credentials or account not activated")