from django.utils import timezone
from .serializers import RoleSerializer, ActionsSerializer, ModulesSerializer, ModuleSectionsSerializer, GetUserDataSerializer, SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserTimeRestrictionsSerializer, UserAllowedWeekdaysSerializer, RolePermissionsSerializer, UserRoleSerializer, ModulesOptionsSerializer, CustomUserUpdateSerializer
from .models import Roles, Actions, Modules, RolePermissions, ModuleSections, User, UserTimeRestrictions, UserAllowedWeekdays, UserRoles
from config.utils_methods import build_response, list_all_objects, create_instance, update_instance, remove_fields, validate_uuid
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
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import get_object_or_404

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRoles.objects.all()
    serializer_class = UserRoleSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


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
        sections = request.query_params.get('sections', 'false').lower() == 'true'
        if sections:
            modules = self.filter_queryset(self.get_queryset())
            data = ModulesOptionsSerializer.get_modules_sections(modules)
            result = Response(data, status=status.HTTP_200_OK)
        else:
            result = list_all_objects(self, request, *args, **kwargs)
        
        return result

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

#====================================USER-TOKEN-CREATE-FUNCTION=============================================================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    profile_picture_url = None
    if user.profile_picture_url:
        profile_picture_url = user.profile_picture_url.url

    try:
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

    except (ObjectDoesNotExist, IndexError, KeyError) as e:
            role_permissions = "Role not assigned yet"

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
    }

#====================================USER-LOGIN-VIEW=============================================================
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        password = serializer.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            user.last_login = timezone.now()
            user.save()
            token = get_tokens_for_user(user)
            return Response({'count': '1', 'msg': 'Login Success', 'data': [token]}, status=status.HTTP_200_OK)
        else:
            return Response({'count': '1', 'msg': 'Username or Password is not valid', 'data': []}, status=status.HTTP_404_NOT_FOUND)

#====================================USER-CHANGE-KNOW-PASSWD-VIEW=============================================================
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'count': '1', 'msg': 'Password Changed Successfully', 'data': []}, status=status.HTTP_200_OK)

#====================================USER-FORGET-PASSWD-VIEW=============================================================
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

# ============================= #USER-CREATE   &    USER-UPDATE#==========================================================
class CustomUserCreateViewSet(DjoserUserViewSet):
    def create(self, request, *args, **kwargs):
        # if 'profile_picture_url' in request.data and isinstance(request.data['profile_picture_url'], list):
        # # Assuming the first item in the list contains the attachment data
        #     attachment_data_list = request.data['profile_picture_url']
        #     if attachment_data_list:
        #         first_attachment = attachment_data_list[0]
        #         request.data['profile_picture_url'] = first_attachment.get('attachment_path', None)
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
            return Response(error_response_data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        # if 'profile_picture_url' in request.data and isinstance(request.data['profile_picture_url'], list):
        #     attachment_data_list = request.data['profile_picture_url']
        #     if attachment_data_list:
        #         first_attachment = attachment_data_list[0]
        #         request.data['profile_picture_url'] = first_attachment.get('attachment_path', None)
        
        try:
            # Retrieve the user instance
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            # Use the custom serializer for updates
            serializer = CustomUserUpdateSerializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            custom_response_data = {
                'count': '1',
                'msg': 'Success! Your user account has been updated.',
                'data': [serializer.data]
            }
            return Response(custom_response_data, status=status.HTTP_200_OK)
        except ValidationError as e:
            error_response_data = {
                'count': '1',
                'msg': 'User update failed due to validation errors.',
                'data': [e.detail]
            }
            return Response(error_response_data, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'msg': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

# =============================USER GET ,  USER GET-All  ,  USER DELETE===================================================
class UserManageView(APIView):    
    def get(self, request, user_id=None):
        """
        Retrieve a specific user if user_id is provided, otherwise retrieve all users.
        """
        if user_id:
            user = get_object_or_404(User, user_id=user_id)
            serializer = GetUserDataSerializer(user)
            return build_response(1, "User Data Retrieved Successfully!", serializer.data, status.HTTP_200_OK)
        else:
            users = User.objects.all()
            serializer = GetUserDataSerializer(users, many=True)
            return build_response(len(serializer.data), "All User Data Retrieved Successfully!", serializer.data, status.HTTP_200_OK)

    def delete(self, request, user_id):
        """
        Delete a specific user identified by user_id.
        """
        user = get_object_or_404(User, user_id=user_id)
        user.delete()
        return build_response(1, "User Deleted Successfully!", {}, status.HTTP_204_NO_CONTENT)

#====================================USER-ACTIVATION-VIEW=============================================================
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
        
#====================================CODE with GET, POST, UPDATE, DELETE Methods:========+++++++++++++++++++++++++++++++++++++++
class RolePermissionsCreateView(APIView):
    def post(self, request, *args, **kwargs):
        result = self.create_list_data(request.data)
        if isinstance(result, Response):
            return result
        
        serializer = RolePermissionsSerializer(result, many=True)
        return build_response(len(result), "Record created successfully", serializer.data, status.HTTP_201_CREATED)
  

    def create_list_data(self, data):
        created_records = []
        for item in data:
            module_id = item.get('module_id')
            section_id = item.get('section_id')
            action_id = item.get('action_id')
            role_id = item.get('role_id')

            try:
                validate_uuid(role_id)
            except ValidationError as e:
                return build_response(0, "role_id " + str(e), [], status.HTTP_400_BAD_REQUEST)
              
            role = get_object_or_404(Roles, pk=role_id)
            if not role:
                return build_response(0, f"Role with id {role_id} does not exist.", [], status.HTTP_400_BAD_REQUEST)

            try:
                validate_uuid(module_id)
            except ValidationError as e:
                return build_response(0, "module_id " + str(e),  [], status.HTTP_400_BAD_REQUEST)

            module = get_object_or_404(Modules, pk=module_id)
            if not module:
                return build_response(0, f"Module with id {module_id} does not exist.",  [], status.HTTP_400_BAD_REQUEST)

            try:
                validate_uuid(section_id)
            except ValidationError as e:
                return build_response(0, "section_id " + str(e),  [], status.HTTP_400_BAD_REQUEST)

            section = get_object_or_404(ModuleSections, pk=section_id, module_id=module)
            if not section:
                return build_response(0, f"Section with id {section_id} does not exist in module {module.module_name}.",  [], status.HTTP_400_BAD_REQUEST)

            try:
                validate_uuid(action_id)
            except ValidationError as e:
                return build_response(0, "action_id " + str(e),  [], status.HTTP_400_BAD_REQUEST)


            action = get_object_or_404(Actions, pk=action_id)
            if not action:
                return build_response(0, f"Action with id {action_id} does not exist.",  [], status.HTTP_400_BAD_REQUEST)

            role_permission = RolePermissions.objects.create(
                module_id=module,
                section_id=section,
                action_id=action,
                role_id=role,
            )
            created_records.append(role_permission)
        return created_records
    
    def delete(self, request, role_id, *args, **kwargs):
        # Delete records with the provided role_id
        deleted_count, _ = RolePermissions.objects.filter(role_id=role_id).delete()
        
        if deleted_count == 0:
            return build_response(0, "No records found for the given role_id",  [], status.HTTP_404_NOT_FOUND)
        
        return build_response(deleted_count, f"{deleted_count} records deleted",  [], status.HTTP_204_NO_CONTENT)
    

    def put(self, request, role_id, *args, **kwargs):
        # Delete existing records for the given role_id
        deleted_count, _ = RolePermissions.objects.filter(role_id=role_id).delete()
        
        # Check if deletion was successful
        if deleted_count == 0:
            return build_response(0, "No records found for the given role_id",  [], status.HTTP_404_NOT_FOUND)

        # Create new records
        result = self.create_list_data(request.data)
        if isinstance(result, Response):
            return result
        
        serializer = RolePermissionsSerializer(result, many=True)
        return build_response(len(result), "Record created successfully", serializer.data, status.HTTP_201_CREATED)

     # Query the RolePermissions table for the given role_id
    def get(self, request, role_id, *args, **kwargs):
        permissions = RolePermissions.objects.filter(role_id=role_id).values(
            'role_id', 'module_id', 'section_id', 'action_id'
        )

        # Check if permissions exist for the given role_id
        if not permissions:
            return build_response(0, "No permissions found for the specified role_id.",  [], status.HTTP_404_NOT_FOUND)

         # Convert QuerySet to a list of dictionaries
        permissions_list = list(permissions)
        return build_response(len(permissions_list), "Records", permissions_list, status.HTTP_200_OK)
