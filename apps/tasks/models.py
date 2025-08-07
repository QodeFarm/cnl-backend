from django.db import models
import uuid
from config.utils_variables import *
from apps.masters.models import Statuses,TaskPriorities, UserGroups
from apps.users.models import User

# Create your models here.
class Tasks(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None, db_column='user_id')
    group_id = models.ForeignKey(UserGroups, on_delete=models.PROTECT, null=True, default=None, db_column='group_id')
    status_id = models.ForeignKey(Statuses, on_delete=models.PROTECT, db_column='status_id')
    priority_id = models.ForeignKey(TaskPriorities, on_delete=models.PROTECT, db_column='priority_id')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    due_date = models.DateField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.task_id}"
    
    class Meta:
        db_table = taskstable

class TaskComments(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_id = models.ForeignKey(Tasks, on_delete=models.PROTECT, db_column='task_id')
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, db_column='user_id')
    comment_text = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.comment_id}"
    
    class Meta:
        db_table = taskcommentstable

class TaskAttachments(models.Model):
    attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_id = models.ForeignKey(Tasks, on_delete=models.PROTECT, db_column='task_id')
    attachment_name = models.CharField(max_length=255)
    attachment_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.attachment_id}"
    
    class Meta:
        db_table = taskattachmentstable

class TaskHistory(models.Model):
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_id = models.ForeignKey(Tasks, on_delete=models.PROTECT, db_column='task_id')
    status_id = models.ForeignKey(Statuses, on_delete=models.PROTECT, db_column='status_id')
    changed_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None, db_column='user_id')
    group_id = models.ForeignKey(UserGroups, on_delete=models.PROTECT, null=True, default=None, db_column='group_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.history_id}"
    
    class Meta:
        db_table = taskhistorytable