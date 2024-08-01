from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

#add your urls

router = DefaultRouter()

router.register(r'tasks_get', TasksViewSet)
router.register(r'task_comments', TaskCommentsViewSet)
router.register(r'task_attachments', TaskAttachmentsViewSet)
router.register(r'task_history', TaskHistoryViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('task/', TaskView.as_view(), name='task_list_create'),
    path('task/<str:pk>/', TaskView.as_view(), name='task_detail_update_delete'),
]