import copy
from .serializers import RoleSerializer, ActionsSerializer, ModulesSerializer, ModuleSectionsSerializer, GetUserDataSerializer, SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserTimeRestrictionsSerializer, UserAllowedWeekdaysSerializer, RolePermissionsSerializer, UserRoleSerializer
from .models import Roles, Actions, Modules, RolePermissions, ModuleSections, User, UserTimeRestrictions, UserAllowedWeekdays, UserRoles
from config.utils_methods import build_response, list_all_objects, create_instance, update_instance, remove_fields, validate_uuid, get_object_or_error
from rest_framework.decorators import permission_classes
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from .renderers import UserRenderer
from rest_framework import viewsets
from rest_framework import status
import json
import uuid
from django.db import transaction
from django.core.exceptions import ValidationError


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRoles.objects.all()
    serializer_class = UserRoleSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class GetUserDataViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = GetUserDataSerializer

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RoleSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class ActionsViewSet(viewsets.ModelViewSet):
    queryset = Actions.objects.all()
    serializer_class = ActionsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class ModulesViewSet(viewsets.ModelViewSet):
    queryset = Modules.objects.all()
    serializer_class = ModulesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class ModuleSectionsViewSet(viewsets.ModelViewSet):
    queryset = ModuleSections.objects.all()
    serializer_class = ModuleSectionsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class UserTimeRestrictionsViewSet(viewsets.ModelViewSet):
    queryset = UserTimeRestrictions.objects.all()
    serializer_class = UserTimeRestrictionsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class UserAllowedWeekdaysViewSet(viewsets.ModelViewSet):
    queryset = UserAllowedWeekdays.objects.all()
    serializer_class = UserAllowedWeekdaysSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class RolePermissionsViewSet(viewsets.ModelViewSet):
    queryset = RolePermissions.objects.all()
    serializer_class = RolePermissionsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

# ==================================================================================================
# Creating tokens manually


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    profile_picture_url = None
    if user.profile_picture_url:
        profile_picture_url = user.profile_picture_url.url

    roles_id = UserRoles.objects.filter(
        user_id=user.user_id).values_list('role_id', flat=True)
    role_permissions_id = RolePermissions.objects.filter(role_id__in=roles_id)
    role_permissions_json = RolePermissionsSerializer(
        role_permissions_id, many=True)
    Final_data = json.dumps(role_permissions_json.data,
                            default=str).replace("\\", "")
    role_permissions = json.loads(Final_data)
    role_permissions = role_permissions[0]
    remove_fields(role_permissions)

    return {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'mobile': user.mobile,
        'profile_picture_url': profile_picture_url,

        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
        'user_id': str(user.user_id),
        'role_permissions': role_permissions
        # 'type' : type(role_permissions)
    }

# login View


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        password = serializer.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'count': '1', 'msg': 'Login Success', 'data': [token]}, status=status.HTTP_200_OK)
        else:
            return Response({'count': '1', 'msg': 'Username or Password is not valid', 'data': []}, status=status.HTTP_404_NOT_FOUND)

# ==================================================================================================
# change known Password view


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'count': '1', 'msg': 'Password Changed Successfully', 'data': []}, status=status.HTTP_200_OK)

# =================================================================================================
# Forgot Password


@permission_classes([AllowAny])
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'count': '1', 'msg': 'Password Reset Link Send. Please Check Your Email', 'data': []}, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'count': '1', 'msg': 'Password Reset Successfully', 'data': []}, status=status.HTTP_200_OK)

# =================================================================================================


class CustomUserCreateViewSet(DjoserUserViewSet):
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            custom_response_data = {
                'count': '1',
                'msg': 'Success! Your user account has been created. Please check your mailbox',
                'data': [response.data]
            }
            return Response(custom_response_data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_response_data = {
                'count': '1',
                'msg': 'User creation failed due to validation errors.',
                'data': [e.detail]
            }
            return Response(error_response_data, status=status.HTTP_400_BAD_REQUEST)

# =================================================================================================


class CustomUserActivationViewSet(DjoserUserViewSet):
    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        try:
            response = super().activation(request, *args, **kwargs)
            custom_response_data = {
                'count': '1',
                'msg': 'Successfully activated the user!',
                'data': []
            }
            return Response(custom_response_data, status=status.HTTP_200_OK)
        except ValidationError as e:
            error_response_data = {
                'count': '1',
                'msg': 'User activation failed due to validation errors.',
                'data': [e.detail],
            }
            return Response(error_response_data, status=status.HTTP_400_BAD_REQUEST)
# ================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=======================================
# ================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=======================================
# ++==================================CODE with POST and DELETE Method:========+++++++++++++++++++++++++++++++++++++++

class RolePermissionsAPIView(APIView):
    def post(self, request):
        roles_data = request.data.get('roles', [])
        role_permissions_data = []

        # Check if roles data is present
        if not roles_data:
            return build_response(0, "ValidationError: roles data is missing" , [], status.HTTP_400_BAD_REQUEST)
           
        with transaction.atomic():
            for role_data in roles_data:
                # Validate role_id
                role_id = role_data.get('role_id')
                if not role_id:
                    return build_response(0, "ValidationError: role_id is missing" , [], status.HTTP_400_BAD_REQUEST)
               
                try:
                    validate_uuid(role_id)
                except ValidationError as e:
                    return build_response(0, "role_id " + str(e) , [], status.HTTP_400_BAD_REQUEST)
                
                role = get_object_or_error(Roles, role_id=role_id)
                if not role:
                    return build_response(0, f"ValidationError: Role with id {role_id} does not exist." , [], status.HTTP_400_BAD_REQUEST)
                   
                for module_data in role_data.get('modules', []):
                    # Validate module_id
                    module_id = module_data.get('module_id')
                    if not module_id:
                        return build_response(0, "ValidationError: module_id is missing" , [], status.HTTP_400_BAD_REQUEST)
                    
                    try:
                        validate_uuid(module_id)
                    except ValidationError as e:
                        return build_response(0, "module_id" + str(e) , [], status.HTTP_400_BAD_REQUEST)
                  
                    module = get_object_or_error(Modules, module_id=module_id)
                    if not module:
                        return build_response(0, f"ValidationError: Module with id {module_id} does not exist." , [], status.HTTP_400_BAD_REQUEST)
                    
                    for section_data in module_data.get('sections', []):
                        # Validate section_id
                        section_id = section_data.get('section_id')
                        if not section_id:
                            return build_response(0, "ValidationError: section_id is missing" , [], status.HTTP_400_BAD_REQUEST)
                       
                        try:
                            validate_uuid(section_id)
                        except ValidationError as e:
                            return build_response(0, "section_id " + str(e) , [], status.HTTP_400_BAD_REQUEST)
                        
                        section = get_object_or_error(
                            ModuleSections, section_id=section_id, module_id=module)
                        if not section:
                            return  build_response(0, f"ValidationError: Section with id {section_id} does not exist in module {module.module_name}." , [], status.HTTP_400_BAD_REQUEST)
                      
                        # Validate actions field presence
                        actions_data = section_data.get('actions')
                        if actions_data is None:
                            return build_response(0, f"ValidationError: Actions field is missing in section {section_id}.", [], status.HTTP_400_BAD_REQUEST)
                        
                        for action_data in actions_data:
                            # Validate action_id
                            action_id = action_data.get('action_id')
                            if not action_id:
                                return build_response(0, "ValidationError: action_id is missing", [], status.HTTP_400_BAD_REQUEST)
                         
                            try:
                                validate_uuid(action_id)
                            except ValidationError as e:
                                return build_response(0, "action_id " + str(e), [], status.HTTP_400_BAD_REQUEST)
                            
                            action = get_object_or_error(
                                Actions, action_id=action_id)
                            if not action:
                                return build_response(0, f"ValidationError: Action with id {action_id} does not exist." , [], status.HTTP_400_BAD_REQUEST)
                            
                            # Create role permission and serialize
                            role_permission_data = RolePermissions.objects.create(
                                role_id=role,
                                module_id=module,
                                section_id=section,
                                action_id=action
                            )
                            serializer = RolePermissionsSerializer(
                                role_permission_data)
                            role_permissions_data.append(serializer.data)

        return build_response(len(role_permissions_data), "Record created successfully", role_permissions_data, status.HTTP_201_CREATED)      
# ================================================================================================================================================
# ===========================================DELETE METHOD============================================================================
# ================================================================================================================================================
    def delete(self, request, role_permission_id):
        """Deletes all role permissions by role_id if it exists."""

        # Validate role_permission_id
        try:
            validate_uuid(role_permission_id)
        except ValidationError as e:
            return build_response(0, "role_permission_id " + str(e), [], status.HTTP_400_BAD_REQUEST)
       
        # Fetch all RolePermission objects with the given role_id
        role_permissions = RolePermissions.objects.filter(role_id=role_permission_id)
        if not role_permissions.exists():
            return build_response(0, "ValidationError: No RolePermissions found with role_id" + str(role_permission_id), [], status.HTTP_400_BAD_REQUEST)
           
        # Delete the RolePermission objects
        count, _ = role_permissions.delete()

        return build_response(count, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

# ================================================================================================================================================
# ===========================================PUT METHOD============================================================================
# ================================================================================================================================================
    def put(self, request, role_permission_id):
        """Updates a role permission by its ID if it exists."""
        # Validate role_permission_id
        try:
            validate_uuid(role_permission_id)
        except ValidationError as e:
            return Response({
                "count": 0,
                "message": "role_permission_id " + str(e),
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the RolePermission object
        role_permission = get_object_or_error(
            RolePermissions, role_permission_id=role_permission_id)
        if not role_permission:
            return Response({
                "count": 0,
                "message": f"ValidationError: RolePermission with id {role_permission_id} does not exist.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate the request data
        role_id = request.data.get('role_id')
        module_id = request.data.get('module_id')
        section_id = request.data.get('section_id')
        action_id = request.data.get('action_id')

        if not all([role_id, module_id, section_id, action_id]):
            return Response({
                "count": 0,
                "message": "ValidationError: All fields (role_id, module_id, section_id, action_id) must be provided.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_uuid(role_id)
            validate_uuid(module_id)
            validate_uuid(section_id)
            validate_uuid(action_id)
        except ValidationError as e:
            return Response({
                "count": 0,
                "message": str(e),
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        role = get_object_or_error(Roles, role_id=role_id)
        module = get_object_or_error(Modules, module_id=module_id)
        section = get_object_or_error(
            ModuleSections, section_id=section_id, module_id=module)
        action = get_object_or_error(Actions, action_id=action_id)

        if not all([role, module, section, action]):
            return Response({
                "count": 0,
                "message": "ValidationError: One or more provided IDs do not correspond to existing records.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update the RolePermission object
        role_permission.role_id = role
        role_permission.module_id = module
        role_permission.section_id = section
        role_permission.action_id = action
        role_permission.save()

        serializer = RolePermissionsSerializer(role_permission)
        return Response({
            "message": "Role permission updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
