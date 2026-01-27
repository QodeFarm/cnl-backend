from django.urls import path
from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwtview
from apps.users.views import DebugDomainView, UserManageView, RolePermissionsCreateView, CustomUserActivationViewSet, CustomUserCreateViewSet, RoleViewSet, ModulesViewSet, ActionsViewSet, ModuleSectionsViewSet, RolePermissionsViewSet, SendPasswordResetEmailView, UserChangePasswordView, UserPasswordResetView, UserTimeRestrictionsViewSet, UserAllowedWeekdaysViewSet, UserLoginView, UserRoleViewSet, UserAccessAPIView, ForceChangePasswordView, ActivateAndSetPasswordView

router = DefaultRouter()

router.register(r'role', RoleViewSet, basename='role')
router.register(r'modules', ModulesViewSet, basename='modules')
router.register(r'actions', ActionsViewSet, basename='actions')
router.register(r'create_user', CustomUserCreateViewSet, basename='create_user')
router.register(r'module_sections', ModuleSectionsViewSet, basename='module_sections')

router.register(r'user_allowed_weekday', UserAllowedWeekdaysViewSet, basename='user_allowed_weekday')
router.register(r'user_time_restrictions', UserTimeRestrictionsViewSet, basename='user_time_restrictions')

router.register(r'user_roles', UserRoleViewSet, basename='user_roles')  
router.register(r'role_permissions_list', RolePermissionsViewSet, basename='role_permissions')


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="User_Login_View"),
    path("jwt/verify/", jwtview.TokenVerifyView.as_view(), name="jwt_verify"),
    path('change_password/',UserChangePasswordView.as_view(), name='change_password'),
    path('force_change_password/', ForceChangePasswordView.as_view(), name='force_change_password'),
    path("jwt/refresh/", jwtview.TokenRefreshView.as_view(), name="get_access_token"),
    path('reset_password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset_password' ),
    path('reset_password_email/', SendPasswordResetEmailView.as_view(), name='reset_password_email'),
    # Old activation endpoint (kept for backward compatibility)
    path('activation/<uid>/<token>/', CustomUserActivationViewSet.as_view({'post': 'activation'}), name='activation'),
    # New: Combined activation + set password endpoint (recommended)
    path('activate-set-password/', ActivateAndSetPasswordView.as_view(), name='activate_set_password'),
    path('activate-set-password/<uid>/<token>/', ActivateAndSetPasswordView.as_view(), name='activate_set_password_validate'),
    path('role_permissions/', RolePermissionsCreateView.as_view(), name='load-role-permissions'),
    path('role_permissions/<uuid:role_id>/', RolePermissionsCreateView.as_view(), name='load-role-permissions'),
    path('user/<uuid:user_id>/', UserManageView.as_view(), name='get-perticuler-user'),
    path('user/', UserManageView.as_view(), name='get-all-users'),
    path('user_access/<str:role_id>/', UserAccessAPIView.as_view(), name='user-access'),
    # path('users_update/<uuid:user_id>/', UserUpdateByAdminOnlyAPIView.as_view(), name='update-user-by-admin'),
    path('clienthost/', DebugDomainView.as_view(), name='user-host-info'),

]
urlpatterns  += router.urls

User = get_user_model()