from django.urls import path
from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwtview
from apps.users.views import UserManageView, RolePermissionsCreateView, CustomUserActivationViewSet, CustomUserCreateViewSet, RoleViewSet, ModulesViewSet, ActionsViewSet, ModuleSectionsViewSet, RolePermissionsViewSet, SendPasswordResetEmailView, UserChangePasswordView, UserPasswordResetView, UserTimeRestrictionsViewSet, UserAllowedWeekdaysViewSet, UserLoginView, UserRoleViewSet, UserAccessViewSet, UserAccessParamViewSet

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
router.register(r'user_access', UserAccessViewSet, basename='user_access')
# router.register(r'user_access_param/<uuid:user_id>/', UserAccessParamViewSet, basename='user_access')


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="User_Login_View"),
    path("jwt/verify/", jwtview.TokenVerifyView.as_view(), name="jwt_verify"),
    path('change_password/',UserChangePasswordView.as_view(), name='change_password'),
    path("jwt/refresh/", jwtview.TokenRefreshView.as_view(), name="get_access_token"),
    path('reset_password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset_password' ),
    path('reset_password_email/', SendPasswordResetEmailView.as_view(), name='reset_password_email'),
    path('activation/<uid>/<token>/', CustomUserActivationViewSet.as_view({'post': 'activation'}), name='activation'),
    path('role_permissions/', RolePermissionsCreateView.as_view(), name='load-role-permissions'),
    path('role_permissions/<uuid:role_id>/', RolePermissionsCreateView.as_view(), name='load-role-permissions'),
    path('user/<uuid:user_id>/', UserManageView.as_view(), name='load-role-permissions'),
    path('user/', UserManageView.as_view(), name='load-role-permissions'),
    path('user_access_param/<uuid:user_id>/', UserAccessParamViewSet.as_view(), name='user-access-param'),
]
urlpatterns  += router.urls

User = get_user_model()