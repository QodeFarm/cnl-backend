from rest_framework import serializers
from apps.masters.serializers import ModStatusesSerializer, ModTaskPrioritiesSerializer
from apps.users.serializers import ModUserSerializer
from apps.tasks.models import Tasks,TaskComments,TaskAttachments,TaskHistory
import os


class ModTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ['task_id','user_id','status_id','priority_id','title','due_date']

class TasksSerializer(serializers.ModelSerializer):
    user = ModUserSerializer(source='user_id', read_only=True)
    status = ModStatusesSerializer(source='status_id', read_only=True)
    priority = ModTaskPrioritiesSerializer(source='priority_id', read_only=True)
    class Meta:
        model = Tasks
        fields = '__all__'

class ModTaskCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComments
        fields = ['comment_id','task_id','user_id']

class TaskCommentsSerializer(serializers.ModelSerializer):
    task = ModTasksSerializer(source='task_id', read_only=True)
    user = ModUserSerializer(source='user_id', read_only=True)
    class Meta:
        model = TaskComments
        fields = '__all__'

class ModTaskAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachments
        fields = ['attachment_id','task_id','attachment_name','attachment_path']

class TaskAttachmentsSerializer(serializers.ModelSerializer):
    task = ModTasksSerializer(source='task_id', read_only=True)
    class Meta:
        model = TaskAttachments
        fields = '__all__'

class ModTaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = ['history_id','task_id','status_id','user_id']

class TaskHistorySerializer(serializers.ModelSerializer):
    task = ModTasksSerializer(source='task_id', read_only=True)
    user = ModUserSerializer(source='user_id', read_only=True)
    status = ModStatusesSerializer(source='status_id', read_only=True)
    class Meta:
        model = TaskHistory
        fields = '__all__'