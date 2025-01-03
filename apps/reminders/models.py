from django.db import models
import uuid
from apps.hrms.models import Employees
from config.utils_variables import notificationfrequenciestable, notificationmethodstable, remindertypestable, reminderstable, reminderrecipientstable, remindersettingstable, reminderlogstable

# Create your models here.
class NotificationFrequencies(models.Model):
    frequency_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    frequency_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.frequency_name
    
    class Meta:
        db_table = notificationfrequenciestable
		
		
class NotificationMethods(models.Model):
    method_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    method_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.method_name
    
    class Meta:
        db_table = notificationmethodstable
		
		
class ReminderTypes(models.Model):
    reminder_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type_name
    
    class Meta:
        db_table = remindertypestable
		

class Reminders(models.Model):
    reminder_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reminder_type_id = models.ForeignKey('ReminderTypes', on_delete=models.CASCADE, db_column='reminder_type_id')
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    reminder_date = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    RECURRING_FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Monthly', 'Monthly'),
        ('Weekly', 'Weekly'),
        ('Yearly', 'Yearly'),
    ]
    recurring_frequency = models.CharField(max_length=7,choices=RECURRING_FREQUENCY_CHOICES,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reminder_id} {self.subject}"
    
    class Meta:
        db_table = reminderstable


class ReminderRecipients(models.Model):
    recipient_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reminder_id = models.ForeignKey('Reminders', on_delete=models.CASCADE, db_column='reminder_id')
    recipient_user_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='recipient_user_id')
    recipient_email = models.CharField(max_length=255, null=True, default=None)
    notification_method_id = models.ForeignKey('NotificationMethods', on_delete=models.CASCADE, db_column='notification_method_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.recipient_id
    
    class Meta:
        db_table = reminderrecipientstable


class ReminderSettings(models.Model):
    setting_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='user_id')
    notification_frequency_id = models.ForeignKey('NotificationFrequencies', on_delete=models.CASCADE, db_column='notification_frequency_id')
    notification_method_id = models.ForeignKey('NotificationMethods', on_delete=models.CASCADE, db_column='notification_method_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.setting_id
    
    class Meta:
        db_table = remindersettingstable


class ReminderLogs(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reminder_id = models.ForeignKey('Reminders', on_delete=models.CASCADE, db_column='reminder_id')
    log_date = models.DateTimeField(auto_now_add=True)
    LOG_ACTION_CHOICES = [
        ('Cancelled', 'Cancelled'),
        ('Created', 'Created'),
        ('Dismissed', 'Dismissed'),
        ('Rescheduled', 'Rescheduled'),
        ('Viewed', 'Viewed'),
    ]
    log_action = models.CharField(max_length=11, choices=LOG_ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.log_id
    
    class Meta:
        db_table = reminderlogstable
