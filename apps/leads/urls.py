from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

#add your urls
router = DefaultRouter()

router.register(r'lead_statuses', LeadStatusesView)
router.register(r'interaction_types', InteractionTypesView)
router.register(r'leads_get', LeadsView)
router.register(r'lead_assignments', LeadAssignmentsView)
router.register(r'lead_interactions', LeadInteractionsView)
router.register(r'lead_assignment_history', LeadAssignmentHistoryView)
router.register(r'lead_group', ModLeadSerializerView)

urlpatterns = [
    path('',include(router.urls)),
    path('leads/', LeadsViewSet.as_view(), name='leads-list-create'),
    path('leads/<str:pk>/', LeadsViewSet.as_view(), name='leads-detail-update-delete'),
    ]