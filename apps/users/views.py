from .serializers import RoleSerializer, ActionsSerializer, ModulesSerializer, ModuleSectionsSerializer, GetUserDataSerializer, SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserTimeRestrictionsSerializer, UserAllowedWeekdaysSerializer, RolePermissionsSerializer, UserRoleSerializer, ModulesOptionsSerializer, CustomUserUpdateSerializer, UserAccessModuleSerializer
from .models import Roles, Actions, Modules, RolePermissions, ModuleSections, User, UserTimeRestrictions, UserAllowedWeekdays, UserRoles
from config.utils_methods import build_response, list_all_objects, create_instance, update_instance, remove_fields, validate_uuid
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework.decorators import permission_classes
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from .renderers import UserRenderer
from rest_framework import viewsets
from rest_framework import status
from django.utils import timezone
import json
from collections import defaultdict

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
    
class UserAccessViewSet(viewsets.ModelViewSet):
    queryset = RolePermissions.objects.all()
    serializer_class = UserAccessModuleSerializer

    def list(self, request, *args, **kwargs):
        # Get all role permissions, ordering by module's `created_at` field
        role_permissions = RolePermissions.objects.select_related('module_id').order_by('module_id__created_at')

        # Create a defaultdict to group sections by module
        module_dict = defaultdict(list)

        for permission in role_permissions:
            module_name = permission.module_id.module_name
            mod_icon = permission.module_id.mod_icon

            section_data = {
                'sec_link': permission.section_id.sec_link,
                'section_name': permission.section_id.section_name,
                'sec_icon': permission.section_id.sec_icon
            }

            # Append section data under the respective module
            module_dict[(module_name, mod_icon)].append(section_data)

        # Create a list for the response
        data = []
        for (module_name, mod_icon), sections in module_dict.items():
            data.append({
                "module_name": module_name,
                "mod_icon": mod_icon,
                "module_sections": sections
            })

        return Response({"count": len(data), "message": None, "data": data}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User

class UserAccessParamViewSet(APIView):
    def get(self, request, user_id, *args, **kwargs):
        # Fetch the User object based on the user_id (UUID)
        user = get_object_or_404(User, user_id=user_id)
        
        # Access the role_id from the ForeignKey relationship
        role_id = user.role.id  # Access the ForeignKey role's ID
        
        # Return the role_id in the response
        return Response({"role_id": role_id}, status=status.HTTP_200_OK)
#====================================USER-TOKEN-CREATE-FUNCTION=============================================================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    profile_picture_url = None
    if user.profile_picture_url:
        profile_picture_url = user.profile_picture_url

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
        if 'profile_picture_url' in request.data and isinstance(request.data['profile_picture_url'], list):
            attachment_data_list = request.data['profile_picture_url']
            if attachment_data_list:
                # Ensure all items in the list have the required fields
                for attachment in attachment_data_list:
                    if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
                        return build_response(0, "Missing required fields in some profile_picture_url data.", [], status.HTTP_400_BAD_REQUEST)
               
                # Set the profile_picture_url field in request data as a list of objects
                request.data['profile_picture_url'] = attachment_data_list
                print("Using profile_picture_url data: ", request.data['profile_picture_url'])
            else:
                # Handle case where 'profile_picture_url' list is empty
                return build_response(0, "'profile_picture_url' list is empty.", [], status.HTTP_400_BAD_REQUEST)
        else:
            # Handle the case where 'profile_picture_url' is not provided or not a list
            return build_response(0, "'profile_picture_url' field is required and should be a list.", [], status.HTTP_400_BAD_REQUEST)
 
        # Proceed with creating the instance
        try:
            response = super().create(request, *args, **kwargs)
           
            # Format the response to include the profile_picture_url data
            if isinstance(response.data, dict):
                picture_data = response.data.get('profile_picture_url')
                if picture_data:
                    response.data['profile_picture_url'] = picture_data
            return response
       
        except ValidationError as e:
            return build_response(1, "Creation failed due to validation errors.", e.detail, status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
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
        user_id_str = str(user_id).replace("-", "")
        # user = get_object_or_404(User, user_id=user_id)
        try:
        # Start a database transaction
            with transaction.atomic():
                # Get the cursor object to execute raw SQL queries
                with connection.cursor() as cursor:
                    # Check if the user exists in the database
                    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = %s", [user_id_str])
                    user_exists = cursor.fetchone()[0]

                    if not user_exists:
                        # If the user does not exist, return a 404 response
                        return build_response(0, "User not found!", {}, status.HTTP_404_NOT_FOUND)

                    # Execute the deletion query
                    cursor.execute("DELETE FROM users WHERE user_id = %s", [user_id_str])

                    # Check if the deletion was successful
                    if cursor.rowcount == 0:
                        # If no rows were deleted, return an error response
                        return build_response(0, "Failed to delete the user!", {}, status.HTTP_500_INTERNAL_SERVER_ERROR)

                    # If successful, return a success response
                    return build_response(1, "User Deleted Successfully!", {}, status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return build_response(0, "An error occurred while deleting the user.", {}, status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        role_id = data[0].get('role_id')
        deleted_count, _ = RolePermissions.objects.filter(role_id=role_id).delete()
        #Check if deletion was successful
        if deleted_count == 0:
            return build_response(0, "No records found for the given role_id",  [], status.HTTP_404_NOT_FOUND)
        
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
    
    # This is redundant code will needed in future.
    # def put(self, request, role_id, *args, **kwargs):
    #     # Delete existing records for the given role_id
    #     deleted_count, _ = RolePermissions.objects.filter(role_id=role_id).delete()
        
    #     # Check if deletion was successful
    #     if deleted_count == 0:
    #         return build_response(0, "No records found for the given role_id",  [], status.HTTP_404_NOT_FOUND)

    #     # Create new records
    #     result = self.create_list_data(request.data)
    #     if isinstance(result, Response):
    #         return result
        
    #     serializer = RolePermissionsSerializer(result, many=True)
    #     return build_response(len(result), "Record created successfully", serializer.data, status.HTTP_201_CREATED)

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