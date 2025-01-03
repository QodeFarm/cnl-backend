from rest_framework import serializers
from apps.hrms.serializers import ModEmployeesSerializer
from apps.reminders.models import NotificationFrequencies, NotificationMethods, ReminderTypes, Reminders, ReminderRecipients, ReminderSettings, ReminderLogs

class ModNotificationFrequenciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationFrequencies
        fields = ['frequency_id','frequency_name']

class NotificationFrequenciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationFrequencies
        fields = '__all__'
		
class ModNotificationMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationMethods
        fields = ['method_id','method_name']

class NotificationMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationMethods
        fields = '__all__'
		
class ModReminderTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderTypes
        fields = ['reminder_type_id','type_name']

class ReminderTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderTypes
        fields = '__all__'
		
class ModRemindersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminders
        fields = ['reminder_id','subject','description','reminder_date','is_recurring','recurring_frequency']

class RemindersSerializer(serializers.ModelSerializer):
    reminder_type = ModReminderTypesSerializer(source='reminder_type_id', read_only=True)
    class Meta:
        model = Reminders
        fields = '__all__'
		

class ModReminderRecipientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderRecipients
        fields = ['recipient_id','recipient_user_id','recipient_email','notification_method_id']

class ReminderRecipientsSerializer(serializers.ModelSerializer):
    reminder = ModRemindersSerializer(source='reminder_id', read_only=True)
    recipient_user = ModEmployeesSerializer(source='recipient_user_id', read_only=True)
    notification_method = ModNotificationMethodsSerializer(source='notification_method_id', read_only=True)
    class Meta:
        model = ReminderRecipients
        fields = '__all__'
		
		
class ModReminderSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderSettings
        fields = ['setting_id','user_id']

class ReminderSettingsSerializer(serializers.ModelSerializer):
    user = ModEmployeesSerializer(source='user_id', read_only=True)
    notification_frequency = ModNotificationFrequenciesSerializer(source='notification_frequency_id', read_only=True)
    notification_method = ModNotificationMethodsSerializer(source='notification_method_id', read_only=True)
    class Meta:
        model = ReminderSettings
        fields = '__all__'
		
		
class ModReminderLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderLogs
        fields = ['log_id','log_date','log_action']

class ReminderLogsSerializer(serializers.ModelSerializer):
    reminder = ModRemindersSerializer(source='reminder_id', read_only=True)
    class Meta:
        model = ReminderLogs
        fields = '__all__'