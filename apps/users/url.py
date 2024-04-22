from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from apps.users.views import RoleViewSet, ModulesViewSet, ActionsViewSet, GetUserDataViewSet, PermissionsViewSet, ModuleSectionsViewSet, RolePermissionsViewSet

router = DefaultRouter()

router.register(r'role', RoleViewSet, basename='role')
router.register(r'modules', ModulesViewSet, basename='modules')
router.register(r'actions', ActionsViewSet, basename='actions')
router.register(r'userdata', GetUserDataViewSet, basename='userdata')
router.register(r'permissions', PermissionsViewSet, basename='permissions')
router.register(r'module_sections', ModuleSectionsViewSet, basename='modulesections')
router.register(r'role_permissions', RolePermissionsViewSet, basename='role_permissions')

urlpatterns = [
    path("djoser/", include("djoser.urls")),
    path("token/", include("djoser.urls.jwt")),
]

urlpatterns += router.urls