from config.utils_variables import rolestable, rolepermissionstable, actionstable, modulestable, modulesections, userstable, usertimerestrictions, userallowedweekdays, userroles
from django.db.models.signals import pre_delete
from apps.masters.models import Statuses
from apps.company.models import Branches
from django.dispatch import receiver
from django.db import models
import uuid
import os


class Roles(models.Model):
    role_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=255,  unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()

    class Meta:
        db_table = rolestable

    def __str__(self):
        return f"{self.role_id}.{self.role_name}"


class Actions(models.Model):
    action_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    action_name = models.CharField(max_length=255,  unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()

    class Meta:
        db_table = actionstable

    def __str__(self):
        return f"{self.action_id}.{self.action_name}"


class Modules(models.Model):
    module_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    module_name = models.CharField(max_length=255,  unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()

    class Meta:
        db_table = modulestable

    def __str__(self):
        return f"{self.module_id}.{self.module_name}"


class ModuleSections(models.Model):
    module_id = models.ForeignKey(
        Modules, on_delete=models.CASCADE, default=None, db_column='module_id')
    section_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    section_name = models.CharField(max_length=255,)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = modulesections

    def __str__(self):
        return f"{self.section_id}.{self.section_name}"


def profile_picture(instance, filename):
    '''Uploading Profile Picture'''
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]
    # Construct the filename
    # Get the filename without extension
    original_filename = os.path.splitext(filename)[0]
    return f"users/{original_filename}_{unique_id}{file_extension}"

# ====


class User(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'),
                      ('Other', 'Other'), ('Prefer Not to Say', 'Prefer Not to Say')]
    TITLE_CHOICES = [('Mr.', 'Mr.'), ('Ms.', 'Ms.')]
    profile_picture_url = models.ImageField(
        max_length=255, null=True, default=None,  upload_to=profile_picture)
    gender = models.CharField(
        max_length=20, choices=GENDER_CHOICES, default='Prefer Not to Say')
    title = models.CharField(
        max_length=20, choices=TITLE_CHOICES, default=None)
    username = models.CharField(
        verbose_name="Username", max_length=255, unique=True)
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    last_name = models.CharField(max_length=255, null=True, default=None)
    timezone = models.CharField(max_length=100, null=True, default=None)
    language = models.CharField(max_length=10, null=True, default=None)
    date_of_birth = models.DateField(null=True, default=None)
    email = models.EmailField(max_length=255, unique=True)
    otp_required = models.BooleanField(default=False)
    mobile = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bio = models.TextField(null=True, default=None)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=255)
    last_login = models.DateTimeField()
    password = models.CharField(max_length=20)

    branch_id = models.ForeignKey(
        Branches, on_delete=models.CASCADE, db_column='branch_id')
    status_id = models.ForeignKey(
        Statuses, on_delete=models.CASCADE, db_column='status_id')

    class Meta:
        db_table = userstable

    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'mobile', 'profile_picture_url', 'bio', 'language', 'date_of_birth', 'gender', 'title', 'otp_required', 'timezone', 'status_id', 'branch_id', 'password']

    @receiver(pre_delete, sender='users.User')
    def delete_user_picture(sender, instance, **kwargs):
        if instance.profile_picture_url and instance.profile_picture_url.name:
            file_path = instance.profile_picture_url.path
            if os.path.exists(file_path):
                os.remove(file_path)
                picture_dir = os.path.dirname(file_path)
                if not os.listdir(picture_dir):
                    os.rmdir(picture_dir)


class UserTimeRestrictions(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE,  db_column='user_id')
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
    WEEKDAYS = [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday'),]
    weekday = models.CharField(
        max_length=9, choices=WEEKDAYS, null=False, blank=False)
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE,  db_column='user_id')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = userallowedweekdays

    def __str__(self):
        return f"{self.id}"


class RolePermissions(models.Model):
    section_id = models.ForeignKey(
        ModuleSections, on_delete=models.CASCADE,  db_column='section_id')
    module_id = models.ForeignKey(
        Modules, on_delete=models.CASCADE,  db_column='module_id')
    action_id = models.ForeignKey(
        Actions, on_delete=models.CASCADE,  db_column='action_id')
    role_permission_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    role_id = models.ForeignKey(
        Roles, on_delete=models.CASCADE,  db_column='role_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = rolepermissionstable

    def __str__(self):
        return f"{self.role_permission_id}"


class UserRoles(models.Model):
    user_role_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE,  db_column='user_id')
    role_id = models.ForeignKey(
        Roles, on_delete=models.CASCADE, db_column='role_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = userroles

    def __str__(self):
        return f"{self.user_role_id}"
