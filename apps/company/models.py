from django.db import models
from django.core.validators import RegexValidator
import uuid,os # type: ignore
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from config.utils_methods import EncryptedTextField
from config.utils_variables import companytable, branchestable, branchbankdetails

def company_logos(instance, filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]
    # Construct the filename
    original_filename = os.path.splitext(filename)[0]  # Get the filename without extension
    return f"company/{original_filename}_{unique_id}{file_extension}"

class Companies(models.Model):
    company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    print_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100, null=True, default =None)
    code = models.CharField(max_length=100, null=True, default=None)
    num_branches = models.IntegerField(default=0)
    num_employees = models.IntegerField(null=True, default =None)
    logo = models.ImageField(null=True, upload_to=company_logos, default=None)
    address = models.CharField(max_length=255, default=None, null=True)
    city_id = models.ForeignKey('masters.City', on_delete=models.CASCADE, db_column = 'city_id')
    state_id = models.ForeignKey('masters.State', on_delete=models.CASCADE, db_column = 'state_id')
    country_id = models.ForeignKey('masters.Country', on_delete=models.CASCADE, null=True, default=None, db_column = 'country_id')
    pin_code = models.CharField(max_length=20, null=True, default=None)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=20, null=True, default=None)
    email = models.EmailField(max_length=255, null=True, default=None)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, default=None)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, default=None)
    print_address = models.TextField(null=True, default=None)
    website = models.URLField(max_length=255, default=None, null=True)
    facebook_url = models.URLField(max_length=255, default=None, null=True)
    skype_id = models.CharField(max_length=50, default=None, null=True)
    twitter_handle = models.CharField(max_length=50, default=None, null=True)
    linkedin_url = models.URLField(max_length=255, default=None, null=True)
    pan = models.CharField(max_length=50, default=None, null=True)
    tan = models.CharField(max_length=50, default=None, null=True)
    cin = models.CharField(max_length=50, default=None, null=True)
    gst_tin = models.CharField(max_length=50, default=None, null=True)
    establishment_code = models.CharField(max_length=50, default=None, null=True)
    esi_no = models.CharField(max_length=50, default=None, null=True)
    pf_no = models.CharField(max_length=50, default=None, null=True)
    authorized_person = models.CharField(max_length=255, default=None, null=True)
    iec_code = models.CharField(max_length=50, default=None, null=True)
    eway_username = models.CharField(max_length=100, default=None, null=True)
    eway_password = EncryptedTextField(max_length=100, default=None, null=True)
    gstn_username = models.CharField(max_length=100, default=None, null=True)
    gstn_password = EncryptedTextField(max_length=100, default=None, null=True)
    VAT_GST_STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
    )
    vat_gst_status = models.CharField(max_length=10, choices=VAT_GST_STATUS_CHOICES, default=None, null=True)
    GST_TYPE_CHOICES = (
        ('Goods', 'Goods'),
        ('Service', 'Service'),
        ('Both', 'Both')
    )
    gst_type = models.CharField(max_length=10, choices=GST_TYPE_CHOICES, default=None, null=True)
    einvoice_approved_only = models.BooleanField(default=False)
    marketplace_url = models.URLField(max_length=255, default=None, null=True)
    drug_license_no = models.CharField(max_length=50, default=None, null=True)
    other_license_1 = models.CharField(max_length=50, default=None, null=True)
    other_license_2 = models.CharField(max_length=50, default=None, null=True)
    turnover_less_than_5cr = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company_id}.{self.name}"

    class Meta:
        db_table = companytable

    @receiver(pre_delete, sender='company.Companies')
    def delete_company_logo(sender, instance, **kwargs):
        if instance.logo and instance.logo.name:
            file_path = instance.logo.path
            if os.path.exists(file_path):
                os.remove(file_path)
                logo_dir = os.path.dirname(file_path)
                if not os.listdir(logo_dir):
                    os.rmdir(logo_dir)

def branches_picture(instance, filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]

    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]

    # Construct the filename
    branch_name = instance.name.replace(' ', '_')
    original_filename = os.path.splitext(filename)[0]  # Get the filename without extension
    return f"company/branch/{branch_name}/{original_filename}_{unique_id}{file_extension}"


class Branches(models.Model):
    branch_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE, db_column = 'company_id')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, default=None, null=True)
    party = models.CharField(max_length=255, default=None, null=True)  
    gst_no = models.CharField(max_length=50, default=None, null=True)
    status_id = models.ForeignKey('masters.Statuses', on_delete=models.CASCADE, db_column = 'status_id')
    allowed_warehouse = models.CharField(max_length=255, default=None, null=True)
    e_way_username = models.CharField(max_length=255, default=None, null=True)
    e_way_password = EncryptedTextField(max_length=255, default=None, null=True) 
    gstn_username = models.CharField(max_length=255, default=None, null=True)
    gstn_password = EncryptedTextField(max_length=255, default=None, null=True)
    other_license_1 = models.CharField(max_length=255, default=None, null=True)
    other_license_2 = models.CharField(max_length=255, default=None, null=True)
    picture = models.ImageField(max_length=255, default=None, null=True, upload_to=branches_picture) 
    address = models.CharField(max_length=255, default=None, null=True)
    city_id = models.ForeignKey('masters.City', on_delete=models.CASCADE, db_column = 'city_id')
    state_id = models.ForeignKey('masters.State', on_delete=models.CASCADE, db_column = 'state_id')
    country_id = models.ForeignKey('masters.Country', on_delete=models.CASCADE, null=True, default=None, db_column = 'country_id')
    pin_code = models.CharField(max_length=20, default=None, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=20, default=None, null=True)  # validators should be a list
    email = models.EmailField(max_length=255, default=None, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, default=None, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.branch_id}.{self.name}"
    
    class Meta:
        db_table = branchestable

    @receiver(pre_delete, sender='company.Branches')
    def delete_branches_picture(sender, instance, **kwargs):
        if instance.picture and instance.picture.name:
            file_path = instance.picture.path
            if os.path.exists(file_path):
                os.remove(file_path)
                picture_dir = os.path.dirname(file_path)
                if not os.listdir(picture_dir):
                    os.rmdir(picture_dir)
    
class BranchBankDetails(models.Model):
    bank_detail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch_id = models.ForeignKey(Branches, on_delete=models.CASCADE, db_column = 'branch_id')
    bank_name = models.CharField(max_length=255,default=None, null=True)
    account_number = EncryptedTextField(max_length=255, default=None, null=True)  # Using custom encrypted field
    branch_name = models.CharField(max_length=255, default=None, null=True)
    ifsc_code = models.CharField(max_length=100, default=None, null=True)
    swift_code = models.CharField(max_length=100, default=None, null=True)
    address = models.CharField(max_length=255, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank_name}"

    class Meta:
        db_table = branchbankdetails





