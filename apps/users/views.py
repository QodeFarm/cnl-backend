from config.utils_filter_methods import filter_response, list_filtered_objects
from .serializers import UserUpdateByAdminOnlySerializer, RoleSerializer, ActionsSerializer, ModulesSerializer, ModuleSectionsSerializer, GetUserDataSerializer, SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserTimeRestrictionsSerializer, UserAllowedWeekdaysSerializer, RolePermissionsSerializer, UserRoleSerializer, ModulesOptionsSerializer, CustomUserUpdateSerializer, UserAccessModuleSerializer
from .models import Roles, Actions, Modules, RolePermissions, ModuleSections, User, UserTimeRestrictions, UserAllowedWeekdays, UserRoles
from config.utils_methods import IsAdminRoles, build_response, list_all_objects, create_instance, update_instance, validate_uuid
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .filters import RolePermissionsFilter, RolesFilter, UserFilter
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.decorators import permission_classes
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.company.models import Companies
from rest_framework.views import APIView
from .renderers import UserRenderer
from rest_framework import viewsets
from collections import defaultdict
from rest_framework import status
from django.utils import timezone
import uuid

import logging
# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

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
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = RolesFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Roles,*args, **kwargs)

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
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = RolePermissionsFilter
    # ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    

class UserAccessAPIView(APIView):
    def get(self, request, role_id):
        try:
            # Check if the user has a role assigned
            if role_id:

                # Fetch all permissions related to the user's role
                permissions = RolePermissions.objects.filter(role_id=role_id).select_related('module_id','section_id','action_id').order_by('module_id__created_at','section_id__created_at','action_id__created_at')
                if permissions.exists():
                    # Use defaultdict to group permissions by module
                    module_dict = defaultdict(list)

                    for permission in permissions:
                        module_name = permission.module_id.module_name
                        mod_icon = permission.module_id.mod_icon

                        # Action data to be grouped under each section
                        action_data = {
                            'action_id': permission.action_id.action_id,
                            'action_name': permission.action_id.action_name
                        }
                        
                        # Section data with an added list of actions
                        section_data = {
                            'sec_link': permission.section_id.sec_link,
                            'section_name': permission.section_id.section_name,
                            'sec_icon': permission.section_id.sec_icon or None,
                            'actions': []  # Placeholder for actions
                        }

                        # Check if the section already exists for this module
                        section_exists = False
                        for existing_section in module_dict[(module_name, mod_icon)]:
                            if existing_section['section_name'] == section_data['section_name']:
                                # Append the action to the existing section
                                existing_section['actions'].append(action_data)
                                section_exists = True
                                break

                        # If the section doesn't exist, add the section and the action
                        if not section_exists:
                            section_data['actions'].append(action_data)
                            module_dict[(module_name, mod_icon)].append(section_data)

                    # Prepare the response data in the desired format
                    data = []
                    for (module_name, mod_icon), sections in module_dict.items():
                        data.append({
                            "module_name": module_name,
                            "mod_icon": mod_icon,
                            "module_sections": sections
                        })

                    # Return the structured response
                    return Response({
                        'count': len(data),       
                        'message': None,                 
                        'role_id': str(role_id),
                        'data': data
                    }, status=status.HTTP_200_OK)
                else:
                    # If no permissions exist for the role
                    return Response({
                        'role_id': str(role_id),
                        'message': 'No permissions found for this role',
                        'data': [],
                    }, status=status.HTTP_200_OK)
            else:
                # If the user has no role assigned
                return Response({
                    'message': 'Role not assigned to user'
                }, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            # If the user is not found in the database
            return Response({
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Roles.DoesNotExist:
            # If the role is not found in the database
            return Response({
                'message': 'Role not found'
            }, status=status.HTTP_404_NOT_FOUND)

#====================================USER-TOKEN-CREATE-FUNCTION=============================================================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    company = Companies.objects.first()  # Get the first company
    company_name = company.name if company else "N/A"
    company_code = company.code if company else "N/A"

    profile_picture_url = None
    if user.profile_picture_url:
        profile_picture_url = user.profile_picture_url

    try:
        role_id = user.role_id.role_id
        role_name = user.role_id.role_name

    except (ObjectDoesNotExist, IndexError, KeyError) as e:
            role_id = "Role not assigned yet"
            role_name = "Role not assigned yet"

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
        'role_id': str(role_id),
        'role_name' : role_name,
        'company_name' : company_name,
        'company_code' : company_code
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
          return Response({'count': '1', 'msg': 'Username or Password is not valid', 'data': []}, status=status.HTTP_401_UNAUTHORIZED)

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
            return build_response(1, "User Created Successfully.", response.data, status.HTTP_201_CREATED)
       
        except ValidationError as e:
            return build_response(1, "Creation failed due to validation errors.", e.detail, status.HTTP_400_BAD_REQUEST)

 #=============================================================UPDATE USER BY ADMIN ONLY &&& UPDATE PROFILE=====================================================   
    ''' In the code below, we update the user's data using two methods:
        1.If the payload contains a flag admin_update, the update will only be allowed if the user has 
            admin privileges.
        2.If the admin_update flag is not present, the code will execute a normal update process, 
            allowing the user to update their own data.
    '''
    def check_admin_permission(self, user):
        return user.role_id.role_name == 'Admin'
    
    def get_target_user(self, user_id):
        return get_object_or_404(User, pk=user_id)

    def update(self, request, *args, **kwargs):
        flag = request.data.get("flag", None)

        # If 'admin_update' flag is passed, execute admin update logic
        if flag == "admin_update":
            user_id = kwargs.get("user_id")  # Get user ID from URL

            if not self.check_admin_permission(request.user):
                return build_response(0, "You do not have permission to perform this action.", [], status.HTTP_403_FORBIDDEN)

            target_user = self.get_target_user(user_id)
            if not target_user:
                return build_response(0, "Invalid Request.", [], status.HTTP_404_NOT_FOUND)

            serializer = UserUpdateByAdminOnlySerializer(target_user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return build_response(1, "User Updated Successfully!", serializer.data, status.HTTP_200_OK)

            return build_response(0, "User Not Updated!", serializer.errors, status.HTTP_400_BAD_REQUEST)

        # Else, execute the regular user update logic
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = CustomUserUpdateSerializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response({
                'count': '1',
                'msg': 'Success! Your user account has been updated.',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return build_response(0,'Form validation failed', [], status.HTTP_400_BAD_REQUEST, e.detail)
            # return Response({
            #     'count': '1',
            #     'msg': 'User update failed due to validation errors.',
            #     'data': [e.detail]
            # }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'msg': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

#=============================================================USER DELETE=====================================================   
    # Add the destroy method for user deletion (Admin only)
    def destroy(self, request, *args, **kwargs):
        """
        Delete a user and related data (Admin only).
        """
        # Check if the requesting user is an Admin
        if not self.check_admin_permission(request.user):
            print("NOT admin")
            return build_response(0, "Permission denied: Only Admins can delete users.", [], status.HTTP_403_FORBIDDEN)

        user_id = kwargs.get("user_id")  # Get user ID from URL
        target_user = self.get_target_user(user_id)
        if not target_user:
            return build_response(0, "Invalid Request.", [], status.HTTP_404_NOT_FOUND)
        
        user_id_str = str(target_user.user_id).replace("-", "")  # Format if needed
        
        try:
            # Start a database transaction
            with transaction.atomic():
                # Get the cursor for raw SQL execution
                with connection.cursor() as cursor:
                    # 1. Delete user's TaskHistory
                    cursor.execute("DELETE FROM task_history WHERE user_id = %s", [user_id_str])

                    # 2. Fetch all tasks associated with the user
                    cursor.execute("SELECT task_id FROM tasks WHERE user_id = %s", [user_id_str])
                    task_ids = [row[0] for row in cursor.fetchall()]

                    if task_ids:
                        # 3. Delete TaskComments
                        cursor.execute("DELETE FROM task_comments WHERE task_id IN %s", [tuple(task_ids)])

                        # 4. Delete TaskAttachments
                        cursor.execute("DELETE FROM task_attachments WHERE task_id IN %s", [tuple(task_ids)])

                        # 5. Delete TaskHistory for tasks
                        cursor.execute("DELETE FROM task_history WHERE task_id IN %s", [tuple(task_ids)])

                        # 6. Delete the tasks themselves
                        cursor.execute("DELETE FROM tasks WHERE user_id = %s", [user_id_str])

                    # 7. Finally, delete the user
                    cursor.execute("DELETE FROM users WHERE user_id = %s", [user_id_str])
                    
                    # Check if deletion was successful
                    if cursor.rowcount == 0:
                        return build_response(0, "User not found or already deleted.", {}, status.HTTP_404_NOT_FOUND)

                    return build_response(1, "User Deleted Successfully!", {}, status.HTTP_204_NO_CONTENT)

        except Exception as e:
            print(f"Error during user deletion: {str(e)}")
            return build_response(0, "Deletion failed due to an internal error.", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================USER GET ,  USER GET-All ===================================================
class UserManageView(APIView):    
    # def get(self, request, user_id=None):
    #     """
    #     Retrieve a specific user if user_id is provided, otherwise retrieve all users.
    #     """
    #     if user_id:
    #         user = get_object_or_404(User, user_id=user_id)
    #         serializer = GetUserDataSerializer(user)
    #         return build_response(1, "User Data Retrieved Successfully!", serializer.data, status.HTTP_200_OK)
    #     else:
    #         users = User.objects.all()
    #         serializer = GetUserDataSerializer(users, many=True)
    #         return build_response(len(serializer.data), "All User Data Retrieved Successfully!", serializer.data, status.HTTP_200_OK)
        
    def get(self, request, user_id=None):
        """
        Retrieve a specific user if user_id is provided, otherwise retrieve all users with pagination and filtering.
        """
        try:
            if user_id:
                user = get_object_or_404(User, user_id=user_id)
                serializer = GetUserDataSerializer(user)
                return build_response(1, "User Data Retrieved Successfully!", serializer.data, status.HTTP_200_OK)
            else:
                logger.info("Retrieving all users")

                # Get pagination parameters
                page = int(request.query_params.get('page', 1))  # Default to page 1
                limit = int(request.query_params.get('limit', 10))  # Default limit 10

                # Initial queryset
                queryset = User.objects.all().order_by('-created_at')

                # Add exclusion filter for current user
                exclude_id = request.query_params.get('exclude_id')
                if exclude_id:
                    # Remove any trailing slashes from the parameter
                    exclude_id = exclude_id.rstrip('/')
                    try:
                        # Validate UUID format
                        valid_uuid = uuid.UUID(exclude_id, version=4)
                        queryset = queryset.exclude(user_id=valid_uuid)
                    except (ValueError, AttributeError, ValidationError):
                        logger.warning(f"Ignoring invalid exclude_id: {exclude_id}")     

                # Apply filters manually
                if request.query_params:
                    filterset = UserFilter(request.GET, queryset=queryset)
                    if filterset.is_valid():
                        queryset = filterset.qs

                total_count = User.objects.count()


                serializer = GetUserDataSerializer(queryset, many=True)
                logger.info("User data retrieved successfully.")

                return filter_response(
                    queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK
                )

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    permission_classes = [IsAdminRoles]
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

#Let it be as it is in future will remove this code

# class UserUpdateByAdminOnlyAPIView(APIView):
#     '''This API is designed for updating user information, and it is admin-only. To use it, you need to pass the Target User ID in the URL.
#         I have provided two methods for this: PUT and PATCH.
#         The PUT method requires the following mandatory fields: username, email, mobile, first_name, status_id, and role_id. These fields are necessary for updating the user information.
#         The PATCH method allows for partial updates, where you can send any of the fields (including optional ones) except for the password. Additionally, you can update the signals field in the PATCH method.
#     '''
#     permission_classes = [IsAuthenticated]
#     def check_admin_permission(self, user):
#         return user.role_id.role_name == 'Admin'

#     def get_target_user(self, user_id):
#         return get_object_or_404(User, pk=user_id)

#     # Apply ratelimit to all HTTP methods or only 'PUT','PATCH
#     @method_decorator(ratelimit(key='ip', rate='5/m', method=['PUT','PATCH'], block=True))
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def put(self, request, user_id):
#         # Check if request user is admin
#         if not self.check_admin_permission(request.user):
#             return build_response(0, "You do not have permission to perform this action.",  [], status.HTTP_403_FORBIDDEN)

#         # Get target user
#         target_user = self.get_target_user(user_id)
#         if not target_user:
#             return build_response(0, "Invalid Request.",  [], status.HTTP_404_NOT_FOUND)
    
#         # Full update
#         serializer = UserUpdateByAdminOnlySerializer(target_user, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             final_PUT_data = serializer.data
#             return build_response(len(final_PUT_data), "User Updated Successfully!",  final_PUT_data, status.HTTP_200_OK)
#         return build_response(0, "User Not Updated!",  serializer.errors, status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, user_id):
#         # Check if request user is admin
#         if not self.check_admin_permission(request.user):
#             return build_response(0, "You do not have permission to perform this action.",  [], status.HTTP_403_FORBIDDEN)

#         # Get target user
#         target_user = self.get_target_user(user_id)
#         if not target_user:
#             return build_response(0, "Invalid Request.",  [], status.HTTP_404_NOT_FOUND)

#         # Partial update
#         serializer = UserUpdateByAdminOnlySerializer(target_user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             final_PATCH_data = serializer.data
#             return build_response(len(final_PATCH_data), "User Updated Successfully!",  final_PATCH_data, status.HTTP_200_OK)
#         return build_response(0, "User Not Updated!",  serializer.errors, status.HTTP_400_BAD_REQUEST)
