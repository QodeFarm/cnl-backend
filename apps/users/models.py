from config.utils_variables import rolestable, rolepermissionstable, actionstable, modulestable, modulesections, userstable, usertimerestrictions, userallowedweekdays, userroles
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import pre_delete
from apps.masters.models import Statuses
from apps.company.models import Branches
from django.dispatch import receiver
from django.db import models
import uuid, os


class Roles(models.Model):
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField( max_length=255,  unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()

    class Meta:
        db_table = rolestable

    def __str__(self):
        return f"{self.role_id}.{self.role_name}"


class Actions(models.Model):
    action_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_name = models.CharField(max_length=255,  unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()


    class Meta:
        db_table = actionstable

    def __str__(self):
        return f"{self.action_id}.{self.action_name}"


class Modules(models.Model):
    module_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_name = models.CharField(max_length=255,  unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()

    class Meta:
        db_table = modulestable

    def __str__(self):
        return f"{self.module_id}.{self.module_name}"


class ModuleSections(models.Model):
    module_id = models.ForeignKey(Modules, on_delete=models.CASCADE, default=None, db_column = 'module_id')
    section_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    section_name = models.CharField( max_length=255,)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = modulesections

    def __str__(self):
        return f"{self.section_id}.{self.section_name}"

class UserManager(BaseUserManager):
    '''Creating User'''
    def create_user(self, email, username, password = None, **extra_fields):
        if not email:
            raise ValueError("The Email Field Must be set")        
        email = self.normalize_email(email)
        user = self.model(
        email = email,
        username = username,
        **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        # Set any required flags for superusers here if needed
        user = self.create_user(username, email, password, **extra_fields)
        # You can set specific flags or permissions for superusers here
        return user

#====
class User(AbstractBaseUser):
    GENDER_CHOICES = [('Male', 'Male'),('Female', 'Female'),('Other', 'Other'),('Prefer Not to Say', 'Prefer Not to Say')]
    TITLE_CHOICES = [('Mr.', 'Mr.'),('Ms.', 'Ms.')]
    profile_picture_url = models.JSONField(null = True, default=None) 
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Prefer Not to Say')
    title = models.CharField(max_length=20, choices=TITLE_CHOICES, default=None)
    username = models.CharField(verbose_name="Username",max_length=255,unique=True) 
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, null= True, default=None)
    timezone = models.CharField(max_length=100, null= True, default=None)
    language = models.CharField(max_length=10, null= True, default=None)
    date_of_birth = models.DateField(null= True, default=None)
    email = models.EmailField(max_length=255, unique=True)
    otp_required = models.BooleanField(default=False)
    mobile= models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bio = models.TextField(null= True, default=None)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, default=None)
    branch_id  = models.ForeignKey(Branches, on_delete=models.CASCADE, db_column='branch_id', null= True)
    status_id  = models.ForeignKey(Statuses, on_delete=models.CASCADE, db_column='status_id')
    role_id    = models.ForeignKey(Roles, on_delete=models.CASCADE,  db_column = 'role_id')

    objects = UserManager()
    
    class Meta:
        db_table = userstable

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'mobile', 'profile_picture_url', 'bio', 'language', 'date_of_birth', 'gender', 'title', 'otp_required', 'timezone', 'status_id', 'branch_id', 'role_id'] 

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name} "

    def has_perm(self, perm, obj=None):
        # Define your custom permission logic here
        return True

    def has_module_perms(self, app_label):
        # Define your custom module permission logic here
        return True

    # Optionally remove or customize the is_staff property
    # If it's not needed, you can safely remove it
    @property
    def is_staff(self):
        return False  # or customize based on your own logic
    
class UserTimeRestrictions(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,  db_column = 'user_id')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.TimeField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = usertimerestrictions

    def __str__(self):
        return f"{self.id}"
    

class UserAllowedWeekdays(models.Model):
    WEEKDAYS = [('Monday', 'Monday'),('Tuesday', 'Tuesday'),('Wednesday', 'Wednesday'),('Thursday', 'Thursday'),('Friday', 'Friday'),('Saturday', 'Saturday'),('Sunday', 'Sunday'),]
    weekday = models.CharField(max_length=9, choices=WEEKDAYS, null=False, blank=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,  db_column = 'user_id')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = userallowedweekdays

    def __str__(self):
        return f"{self.id}"
    

class RolePermissions(models.Model):
    section_id = models.ForeignKey(ModuleSections, on_delete=models.CASCADE,  db_column = 'section_id')
    module_id  = models.ForeignKey(Modules, on_delete=models.CASCADE,  db_column = 'module_id')
    action_id  = models.ForeignKey(Actions, on_delete=models.CASCADE,  db_column = 'action_id')
    role_permission_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_id    = models.ForeignKey(Roles, on_delete=models.CASCADE,  db_column = 'role_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = rolepermissionstable

    def __str__(self):
        return f"{self.role_permission_id}"
    
class UserRoles(models.Model):
    user_role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,  db_column = 'user_id')
    role_id = models.ForeignKey(Roles, on_delete=models.CASCADE, db_column = 'role_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = userroles
    
    def __str__(self):
        return f"{self.user_role_id}"