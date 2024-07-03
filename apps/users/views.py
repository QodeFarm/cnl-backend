import copy
from .serializers import RoleSerializer, ActionsSerializer, ModulesSerializer, ModuleSectionsSerializer, GetUserDataSerializer, SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserTimeRestrictionsSerializer, UserAllowedWeekdaysSerializer, RolePermissionsSerializer, UserRoleSerializer
from .models import Roles, Actions, Modules, RolePermissions, ModuleSections, User, UserTimeRestrictions, UserAllowedWeekdays, UserRoles
from config.utils_methods import list_all_objects, create_instance, update_instance, remove_fields
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
    
#==================================================================================================
# Creating tokens manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    profile_picture_url = None
    if user.profile_picture_url:
        profile_picture_url = user.profile_picture_url.url 
            
    roles_id = UserRoles.objects.filter(user_id=user.user_id).values_list('role_id', flat=True)
    role_permissions_id = RolePermissions.objects.filter(role_id__in=roles_id)
    role_permissions_json = RolePermissionsSerializer(role_permissions_id, many=True)
    Final_data = json.dumps(role_permissions_json.data, default=str).replace("\\", "")
    role_permissions = json.loads(Final_data)
    role_permissions = role_permissions[0]
    remove_fields(role_permissions)
    
    return {
        'username': user.username,
        'first_name' : user.first_name,
        'last_name' : user.last_name,
        'email' : user.email,
        'mobile' : user.mobile,
        'profile_picture_url': profile_picture_url,

        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
        'user_id' : str(user.user_id),
        'role_permissions' : role_permissions
        #'type' : type(role_permissions)
    }

#login View
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
            return Response({'count':'1', 'msg':'Login Success', 'data':[token]}, status=status.HTTP_200_OK)
        else:
            return Response({'count':'1', 'msg':'Username or Password is not valid', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

#==================================================================================================
#change known Password view
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'count':'1', 'msg':'Password Changed Successfully', 'data':[]}, status=status.HTTP_200_OK)

#=================================================================================================
#Forgot Password
@permission_classes([AllowAny])
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'count':'1', 'msg':'Password Reset Link Send. Please Check Your Email', 'data':[]}, status=status.HTTP_200_OK)
        

@permission_classes([AllowAny])
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'count':'1', 'msg':'Password Reset Successfully', 'data':[]}, status=status.HTTP_200_OK)

#=================================================================================================
class CustomUserCreateViewSet(DjoserUserViewSet):
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            custom_response_data = {
            'count':'1',
            'msg':'Success! Your user account has been created. Please check your mailbox',
            'data':[response.data]
            }
            return Response(custom_response_data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_response_data = {
                'count':'1',
                'msg':'User creation failed due to validation errors.',
                'data':[e.detail]
            }
            return Response(error_response_data, status=status.HTTP_400_BAD_REQUEST)

#=================================================================================================
class CustomUserActivationViewSet(DjoserUserViewSet):
    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        try:
            response = super().activation(request, *args, **kwargs)
            custom_response_data = {
                'count':'1',
                'msg':'Successfully activated the user!',
                'data':[]
            }
            return Response(custom_response_data, status=status.HTTP_200_OK)
        except ValidationError as e:
            error_response_data = {
                'count':'1',
                'msg':'User activation failed due to validation errors.',
                'data':[e.detail],
            }
            return Response(error_response_data, status=status.HTTP_400_BAD_REQUEST)
