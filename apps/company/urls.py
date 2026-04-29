from django.urls import path, include
from rest_framework import routers
from .views import CompaniesViewSet, BranchesViewSet, BranchBankDetailsViewSet, CompanySettingsViewSet

router = routers.DefaultRouter()
router.register(r'companies', CompaniesViewSet)
router.register(r'branches', BranchesViewSet)
router.register(r'branch_bank_details', BranchBankDetailsViewSet)
router.register(r'company-settings', CompanySettingsViewSet, basename='company-settings')

urlpatterns = [
    path('', include(router.urls)),
]