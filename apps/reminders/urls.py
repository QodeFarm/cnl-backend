from django.urls import path, include
from apps.reminders.views import ReminderView, NotificationFrequenciesViewSet, NotificationMethodsViewSet, ReminderTypesViewSet, RemindersViewSet, ReminderRecipientsViewSet, ReminderSettingsViewSet, ReminderLogsViewSet 
from rest_framework.routers import DefaultRouter

#add your urls
router = DefaultRouter()
router.register(r'notification_frequencies', NotificationFrequenciesViewSet)
router.register(r'notification_methods', NotificationMethodsViewSet)
router.register(r'reminder_types', ReminderTypesViewSet)
router.register(r'reminders_get', RemindersViewSet)
router.register(r'reminder_recipients', ReminderRecipientsViewSet)
router.register(r'reminder_settings', ReminderSettingsViewSet)
router.register(r'reminder_logs', ReminderLogsViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('reminders/', ReminderView.as_view(), name='reminders-list-create'),
    path('reminders/<str:pk>/', ReminderView.as_view(), name='reminders-detail-update-delete'),
]