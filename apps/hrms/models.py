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
    employee_detail_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, null=True, default=None)
    nationality = models.CharField(max_length=20, null=True, default=None)
    emergency_contact = models.CharField(max_length=20, null=True, default=None)
    emergency_contact_relationship = models.CharField(max_length=55, null=True, default=None)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='employee_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_details'
        
    def __str__(self):
        return f"{self.employee_detail_id}" 
        
class Organisation(models.Model):
    org_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    org_name = models.CharField(max_length=128)
    org_address = models.CharField(max_length=255, null=True, default=None)
    description = models.CharField(max_length=255, null=True, default=None)
    org_email = models.CharField(max_length=55, null=True, default=None)
    org_phone = models.CharField(max_length=20, null=True, default=None)
    org_contact_person = models.CharField(max_length=55, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        db_table = organisation
 
    def __str__(self):
        return f"{self.org_name}" 
        
class EmployeeCompensationHistory(models.Model):
    compensation_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    start_date = models.DateField(null=True, default=None)
    compensation_name = models.CharField(max_length=55, null=True, default=None)
    amount = models.FloatField(null=True, default=None)
    currency = models.CharField(max_length=20, null=True, default=None)
    org_id = models.ForeignKey(Organisation, on_delete=models.CASCADE, db_column='org_id')
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='employee_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
   
    class Meta:
        db_table = employeecompensationhistory
 
    def __str__(self):
        return f"{self.compensation_name}"

class OrganisationBranches(models.Model):
    org_branch_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.ForeignKey(Organisation, on_delete=models.CASCADE, db_column='org_id')
    branch_name = models.CharField(max_length=128)
    branch_address = models.CharField(max_length=255, null=True, default=None)
    branch_contact_person = models.CharField(max_length=45, null=True, default=None)
    branch_email = models.CharField(max_length=55, null=True, default=None)
    branch_phone = models.CharField(max_length=20, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = organisationbranches

    def __str__(self):
        return self.branch_name
     
class EmployeeHistory(models.Model):
    history_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    start_date = models.DateField(null=True, default=None)
    action_name = models.CharField(max_length=100, null=True, default=None)
    designation_id = models.ForeignKey(Designations, on_delete=models.CASCADE, null=True, default=None, db_column='designation_id')
    job_type_id = models.ForeignKey(JobTypes, on_delete=models.CASCADE, null=True, default=None, db_column='job_type_id')
    manager_id = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True, default=None, db_column='manager_id', related_name='employee_manager')
    branch_id = models.ForeignKey(OrganisationBranches, on_delete=models.CASCADE, null=True, default=None, db_column='branch_id')
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default=None, db_column='employee_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = employeehistory

    def __str__(self):
        return self.history_id
        
class PreviousCompanyHistory(models.Model):
    history_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255, null=True, default=None)
    position = models.CharField(max_length=55, null=True, default=None)
    start_date = models.DateField(null=True, default=None)
    end_date = models.DateField(null=True, default=None)
    responsibilities = models.TextField()
    manager_name = models.CharField(max_length=55, null=True, default=None)
    manager_email = models.EmailField(max_length=55, null=True, default=None)
    manager_contact = PhoneNumberField(max_length=20,null=True, default=None)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default=None, db_column='employee_id', related_name='previous_company_history')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = previouscompanyhistory
        
    def __str__(self):
        return self.company_name
        
class Employeesalary(models.Model):
    salary_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
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

class Hardware(models.Model):
    hardware_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    hardware_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = hardware
        
    def __str__(self):
        return self.hardware_name
        
class SalaryComponents(models.Model):
    component_id = models.AutoField(primary_key=True)
    component_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = salarycomponents

    def __str__(self):
        return f"{self.component_name}"
        
class EmployeeSalaryComponents(models.Model):
    employee_component_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    component_id = models.ForeignKey(SalaryComponents, on_delete=models.CASCADE, null=True, default =None, db_column = 'component_id')
    component_amount = models.FloatField(null=True, default =None)
    salary_id = models.ForeignKey(Employeesalary, on_delete=models.CASCADE, null=True, default =None, db_column ='salary_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeesalarycomponents

    def __str__(self):
        return f"{self.employee_component_id}"
        
class Benefits(models.Model):
    benefit_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    benefit_name = models.CharField(max_length=55)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = benefits

    def __str__(self):
        return '{}'.format(self.benefit_name)

class BenefitProviders(models.Model):
    provider_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_name = models.CharField(max_length=55)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = benefitproviders
		
    def __str__(self):
        return self.provider_name
        
        
class EmployeeBenefits(models.Model):
    employee_benefit_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment_date = models.DateField(null=True, default=None) 
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True, default=None,db_column = 'employee_id')
    benefit_id = models.ForeignKey(Benefits, on_delete=models.CASCADE,null=True, default=None,db_column = 'benefit_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeebenefits
       
    def __str__(self):
        return self.employee_benefit_id
        

class EmployeeBenefitProviders (models.Model):
    employee_benefit_provider_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_number = models.DecimalField(max_digits=10, decimal_places=2)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default =None, db_column= 'employee_id')
    benefit_id= models.ForeignKey(Benefits, on_delete=models.CASCADE, null=True, default =None, db_column= 'benefit_id')
    provider_id = models.ForeignKey(BenefitProviders, on_delete=models.CASCADE, null=True, default =None, db_column= 'provider_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeebenefitproviders

    def __str__(self):
        return self.employee_benefit_provider_id
        

class EmployeeOnboarding(models.Model):
    STATUS_CHOICE =(
        (1, 'Completed'),
        (2, 'Pending')
    )
    onboarding_id =  models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    onboarding_date = models.DateField(null=True, default =None)
    orientation_completed = models.IntegerField(choices=STATUS_CHOICE, null=True, default =None)
    team_building_completed = models.IntegerField(choices=STATUS_CHOICE, null=True, default =None)
    training_completed = models.IntegerField(choices=STATUS_CHOICE, null=True, default =None)
    access_card_issued = models.IntegerField(choices=STATUS_CHOICE, null=True, default =None)
    access_card_expiry_date = models.DateField(null=True, default =None)
    welcome_kit_provided = models.IntegerField(choices=STATUS_CHOICE, null=True, default =None)
    it_hardware_provided = models.IntegerField(choices=STATUS_CHOICE, null=True, default =None)
    additional_notes = models.TextField()
    status_id = models.ForeignKey('masters.Statuses', on_delete=models.CASCADE, null=True, default =None, db_column='status_id')
    department_training_id = models.ForeignKey(Departments,on_delete=models.CASCADE, null=True, default =None, db_column='department_training_id')
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True, default =None, db_column='employee_id', related_name='employee_onboarding')
    mentor_id = models.ForeignKey(Employees, on_delete=models.CASCADE,null=True, default =None, related_name='mentor_onboarding', db_column='mentor_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        db_table = employeeonboarding

    def __str__(self) :
        return f"Employee_id: {self.employee_id}, Mentor_id: {self.mentor_id}"

class EmployeeHardwareAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    onboarding_id = models.ForeignKey(EmployeeOnboarding, on_delete=models.CASCADE, null=True, default =None, db_column='onboarding_id')
    hardware_id = models.ForeignKey(Hardware, on_delete=models.CASCADE, null=True, default =None, db_column='hardware_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeehardwareassignment

    def __str__(self):
        return f"{self.assignment_id}"	
        
        
# =====================leaves====================================      

# class Statuses(models.Model):
#     status_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
#     status_name = models.CharField(max_length=55)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta :
#         db_table = statuses

#     def __str__(self):   
#         return f"{self.status_name}"
        
class LeaveTypes(models.Model):
    leave_type_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
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
    leave_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    start_date = models.DateField()
    end_date = models.DateField()
    status_id = models.ForeignKey('masters.Statuses', on_delete=models.CASCADE, null=True, default =None, db_column='status_id')
    comments = models.CharField(max_length=255)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default =None, db_column='employee_id')
    leave_type_id = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE, null=True, default =None, db_column='leave_type_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = employeeleaves

    def __str__(self):
        return f"{self.leave_id}"
        
class LeaveApprovals(models.Model):
    approval_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    approval_date = models.DateTimeField(null=True, default =None)
    comments = models.CharField(max_length=255, null=True, default=None)
    status_id = models.ForeignKey('masters.Statuses', on_delete=models.CASCADE, null=True, default=None, db_column='status_id')
    leave_id = models.ForeignKey(EmployeeLeaves, on_delete=models.CASCADE, null=True, default=None, db_column='leave_id')
    approver_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default=None, db_column='approver_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = leaveapprovals
        
    def __str__(self):
        return f"{self.approval_id}"
        
class EmployeeLeaveBalance(models.Model):
    balance_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default=None, db_column='employee_id')
    leave_type_id = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE, null=True, default=None, db_column='leave_type_id')
    leave_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    year = models.CharField(max_length=45, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table= employeeleavebalance
        
    def __str__(self):
        return f"{self.balance_id}"

# =====================attendance====================================      

class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE,default=None,null=True,db_column = 'employee_id')
    attendance_date = models.DateTimeField(null=True, default=None)
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
    swipe_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE,default=None,null=True,db_column = 'employee_id')
    swipe_time = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = swipes

    def __str__(self):
        return f"Swipe ID: {self.swipe_id}, Employee ID: {self.employee}, Swipe Time: {self.swipe_time}"
        
        
class Biometric(models.Model):
    biometric_id = models.AutoField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=True, default=None,db_column = 'employee_id')
    biometric_entry_id = models.IntegerField(null=True, default=None)
    template_data = models.TextField()
    entry_stamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = biometric
 
    def __str__(self):
        return f"{self.biometric_id}"


# class Designations(models.Model):
#     designation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     designation_name = models.CharField(max_length=50, null=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = designations

#     def __str__(self):
#         return f"{self.designation_name}"

# class Departments(models.Model):
#     department_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     department_name = models.CharField(max_length=50, null=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = departments

#     def __str__(self):
#         return f"{self.department_name}"
    
# class Employees(models.Model):
#     employee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name =  models.CharField(max_length=255, null=False)
#     email = models.EmailField(max_length=255, null=False)
#     phone = PhoneNumberField(blank=True, null=True, default=None, help_text="Enter the phone number with country code, e.g., +91 XXXXXXXXXX")
#     designation_id = models.ForeignKey(Designations, on_delete=models.CASCADE, db_column='designation_id', null=False)
#     department_id = models.ForeignKey(Departments, on_delete=models.CASCADE, db_column='department_id', null=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = employees

#     def __str__(self):
#         return f"{self.name}"