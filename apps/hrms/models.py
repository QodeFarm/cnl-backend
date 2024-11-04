import uuid
from django.db import models
from config.utils_methods import *
from config.utils_variables import *
from phonenumber_field.modelfields import PhoneNumberField

class JobTypes(models.Model):
    job_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_type_name = models.CharField(max_length=55)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)	

    class Meta:
        db_table = jobtypes

    def __str__(self):
        return f"{self.job_type_name}"
		
class Designations(models.Model):
    designation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    designation_name = models.CharField(max_length=55)
    responsibilities = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = designations

    def __str__(self):
        return f"{self.designation_name}"
		
class JobCodes(models.Model):
    job_code_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_code = models.CharField(max_length=55)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = jobcodes

    def __str__(self):
        return f"{self.job_code}"
		
class Departments(models.Model):
    department_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department_name = models.CharField(max_length=55)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = departments

    def __str__(self):
        return f"{self.department_name}"
		
class Shifts(models.Model):
    shift_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shift_name = models.CharField(max_length=55)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = shifts

    def __str__(self):
        return f"{self.shift_name}"
		
class Employees(models.Model):
    employee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name =  models.CharField(max_length=55)
    last_name =  models.CharField(max_length=55)
    email = models.EmailField(max_length=255)
    phone = PhoneNumberField(blank=True, null=True, default=None, help_text="Enter the phone number with country code, e.g., +91 XXXXXXXXXX")
    address = models.CharField(max_length=255, null=True, default=None)
    hire_date = models.DateField(null=True, default=None)
    job_type_id = models.ForeignKey(JobTypes, on_delete=models.CASCADE, db_column='job_type_id')
    designation_id = models.ForeignKey(Designations, on_delete=models.CASCADE, db_column='designation_id')
    job_code_id = models.ForeignKey(JobCodes, on_delete=models.CASCADE, db_column='job_code_id')
    department_id = models.ForeignKey(Departments, on_delete=models.CASCADE, db_column='department_id')
    shift_id = models.ForeignKey(Shifts, on_delete=models.CASCADE, db_column='shift_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employees

    def __str__(self):
        return f"{self.first_name} {self.last_name}"  


class EmployeeDetails(models.Model):
    employee_detail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, null=True, default=None)
    nationality = models.CharField(max_length=20, null=True, default=None)
    emergency_contact = models.CharField(max_length=20, null=True, default=None)
    emergency_contact_relationship = models.CharField(max_length=55, null=True, default=None)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='employee_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeedetails
        
    def __str__(self):
        return f"{self.employee_detail_id}" 
                
class EmployeeSalary(models.Model):
    salary_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salary_amount = models.FloatField()
    salary_currency = models.CharField(max_length=45)
    salary_start_date = models.DateField()
    salary_end_date = models.DateField()
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default =None,db_column = 'employee_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeesalary
        
    def __str__(self):
        return f"Salary ID: {self.salary_id}, Amount: {self.salary_amount} {self.salary_currency}"
      
class SalaryComponents(models.Model):
    component_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = salarycomponents

    def __str__(self):
        return f"{self.component_name}"
        
class EmployeeSalaryComponents(models.Model):
    employee_component_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component_id = models.ForeignKey(SalaryComponents, on_delete=models.CASCADE, db_column = 'component_id')
    component_amount = models.FloatField(null=True, default =None)
    salary_id = models.ForeignKey(EmployeeSalary, on_delete=models.CASCADE, db_column ='salary_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeesalarycomponents

    def __str__(self):
        return f"Employee Component ID: {self.employee_component_id}, Component Amount: {self.component_amount}"

        
# =====================leaves====================================      
        
class LeaveTypes(models.Model):
    leave_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leave_type_name = models.CharField(max_length=55)
    description = models.CharField(max_length=255)
    max_days_allowed = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta :
        db_table = leavetypes

    def __str__(self):
        return f"{self.leave_type_name}"

class EmployeeLeaves(models.Model):
    leave_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_date = models.DateField()
    end_date = models.DateField()
    status_id = models.ForeignKey('masters.Statuses', on_delete=models.CASCADE, db_column='status_id')
    comments = models.CharField(max_length=255, null=True, blank=True)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='employee_id')
    leave_type_id = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE, db_column='leave_type_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeeleaves

    def __str__(self):
        return f"Leave ID: {self.leave_id}, Comments: {self.comments}"
        
class LeaveApprovals(models.Model):
    approval_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    approval_date = models.DateTimeField(null=True, default =None)
    comments = models.CharField(max_length=255, null=True, default=None)
    status_id = models.ForeignKey('masters.Statuses', on_delete=models.CASCADE, db_column='status_id')
    leave_id = models.ForeignKey(EmployeeLeaves, on_delete=models.CASCADE, db_column='leave_id')
    approver_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='approver_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = leaveapprovals
        
    def __str__(self):
        return f"Approval ID: {self.approval_id}, Comments: {self.comments}"
        
class EmployeeLeaveBalance(models.Model):
    balance_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='employee_id')
    leave_type_id = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE, db_column='leave_type_id')
    leave_balance = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table= employeeleavebalance
        
    def __str__(self):
        return f"Balance ID: {self.balance_id}, Leave Balance: {self.leave_balance}"


# =====================attendance====================================      

class Attendance(models.Model):
    attendance_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE,db_column = 'employee_id')
    attendance_date = models.DateField()
    clock_in_time = models.DateTimeField(null=True, default=None) 
    clock_out_time = models.DateTimeField(null=True, default=None) 
    status_id = models.ForeignKey('masters.Statuses', on_delete=models.CASCADE,default=None,null=True,db_column = 'status_id')
    department_id = models.ForeignKey(Departments, on_delete=models.CASCADE,default=None,null=True,db_column = 'department_id')
    shift_id = models.ForeignKey(Shifts, on_delete=models.CASCADE,default=None,null=True,db_column = 'shift_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = attendance

    def __str__(self):
        return f'Empoyee ID: {self.employee_id} IN: {self.clock_in_time} OUT: {self.clock_out_time}'
        
class Swipes(models.Model):
    swipe_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column = 'employee_id')
    swipe_time = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = swipes

    def __str__(self):
        return f"Swipe ID: {self.swipe_id}, Employee ID: {self.employee}, Swipe Time: {self.swipe_time}"
        
        
class Biometric(models.Model):
    biometric_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column = 'employee_id')
    biometric_entry_id = models.IntegerField(null=True, default=None)
    template_data = models.TextField()
    entry_stamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = biometric
 
    def __str__(self):
        return f"{self.biometric_id}"
