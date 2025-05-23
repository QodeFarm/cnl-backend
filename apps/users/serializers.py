from .models import Roles, Actions, Modules, RolePermissions, ModuleSections, User, UserTimeRestrictions, UserAllowedWeekdays, UserRoles
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from apps.company.serializers import ModBranchesSerializer
from apps.masters.serializers import ModStatusesSerializer
from rest_framework import serializers
from .utils import Utils
from .passwdgen import *
import os
from apps.products.serializers import PictureSerializer
from config.utils_variables import baseurl
#=========================MOD_SERIALIZATION=========================
class ModRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ['role_id','role_name']

class ModModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = ['module_id', 'module_name', 'mod_link', 'mod_icon']

class ModUserAccessModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = ['module_name', 'mod_link', 'mod_icon']

class ModUserAccessSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleSections
        fields = ['section_name', 'sec_link', 'sec_icon']

class ModuleSectionChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleSections
        fields = ['sec_link', 'section_name', 'sec_icon']
        
class ModActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actions
        fields = ['action_id','action_name']

class ModModuleSectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleSections
        fields = ['section_id','section_name', 'sec_link', 'sec_icon']

class ModUserTimeRestrictionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTimeRestrictions
        fields = ['user_time_restrictions_id']

class ModUserAllowedWeekdaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAllowedWeekdays
        fields = ['user_allowed_weekdays_id']

class ModRolePermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermissions
        fields = ['role_permission_id']

class ModUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id','first_name','last_name','username']
        
class ModUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoles
        fields = ['user_role_id']
#=========================SERIALIZATIONS=========================
class UserRoleSerializer(serializers.ModelSerializer):
    role = ModRoleSerializer(source='role_id', read_only = True)
    user = ModUserSerializer(source='user_id', read_only = True)
    class Meta:
        model = UserRoles
        fields = '__all__'

class UserTimeRestrictionsSerializer(serializers.ModelSerializer):
    user = ModUserSerializer(source='user_id', read_only = True)
    class Meta:
        model = UserTimeRestrictions
        fields = '__all__'

class UserAllowedWeekdaysSerializer(serializers.ModelSerializer):
    user = ModUserSerializer(source='user_id', read_only = True)
    class Meta:
        model = UserAllowedWeekdays
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class ActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actions
        fields = '__all__'

class ModuleSectionsSerializer(serializers.ModelSerializer):
    module = ModModulesSerializer(source='module_id', read_only = True)
    class Meta:
        model = ModuleSections
        fields = '__all__'

class ModulesSerializer(serializers.ModelSerializer):
    # module_sections = ModuleSectionsSerializer(many=True, read_only=True, source='modulesections_set') //commented for future references

    class Meta:
        model = Modules
        fields = '__all__'

# class UserAccessSerializer(serializers.ModelSerializer):
#     # role = ModRoleSerializer(source='role_id', read_only = True)
#     module = ModUserAccessModuleSerializer(source='module_id', read_only = True)
#     # action =  ModActionsSerializer(source='action_id', read_only = True)
#     section = ModUserAccessSectionSerializer(source='section_id', read_only = True)

#     class Meta:
#         model = RolePermissions
#         fields = ['module', 'section']


class UserAccessModuleSerializer(serializers.ModelSerializer):
    child = serializers.SerializerMethodField()

    class Meta:
        model = Modules
        fields = ['module_name', 'mod_icon', 'child']

    def get_child(self, obj):
        # Get the sections related to this module
        sections = ModuleSections.objects.filter(module_id=obj.module_id)
        return ModuleSectionChildSerializer(sections, many=True).data

class UserAccessSerializer(serializers.ModelSerializer):
    module = UserAccessModuleSerializer(source='module_id', read_only=True)

    class Meta:
        model = RolePermissions
        fields = ['module']

class RolePermissionsSerializer(serializers.ModelSerializer):
    role = ModRoleSerializer(source='role_id', read_only = True)
    module = ModModulesSerializer(source='module_id', read_only = True)
    action =  ModActionsSerializer(source='action_id', read_only = True)
    section = ModuleSectionsSerializer(source='section_id', read_only = True)

    class Meta:
        model = RolePermissions
        fields = '__all__'

class GetUserDataSerializer(serializers.ModelSerializer):
    branch = ModBranchesSerializer(source='branch_id', read_only = True)
    status = ModStatusesSerializer(source='status_id', read_only = True)
    role = ModRoleSerializer(source='role_id', read_only = True)
    class Meta:
        model = User
        fields = ['email', 'user_id', 'username', 'title', 'first_name', 'last_name', 'mobile', 'otp_required', 'profile_picture_url', 'bio', 'timezone', 'language', 'created_at', 'updated_at', 'last_login', 'date_of_birth', 'gender', 'is_active', 'branch', 'status', 'role']   #if we use here '__all__' then it shows password field also.

#====================================USER-CREATE-SERIALIZER=============================================================
class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        profile_picture_url = PictureSerializer(many=True)
        model = User
        fields = '__all__'

#====================================USER-UPDATE-SERIALIZER=============================================================
class CustomUserUpdateSerializer(DjoserUserSerializer):
    class Meta:
        model = User
        fields = DjoserUserSerializer.Meta.fields 

    def update(self, instance, validated_data):
        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
    
#====================================USER-LOGIN-SERIALIZER=============================================================
class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    class Meta:
        model = User
        fields =['username', 'password']

#====================================USER-CHANGE-KNOWN-PASSWD-SERIALIZER=============================================================
class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)

    class Meta:
        fields=['old_password', 'password', 'confirm_password']    
    def validate(self, attrs):
        old_password = attrs.get('old_password')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')

        # Validate old password
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})

        if password != confirm_password:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        
        user.set_password(password)
        user.save()
        return attrs

#====================================USER-FORGET-PASSWD-SERIALIZER=============================================================
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']
    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            #if exists get user object from DB
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.user_id))
            token = CustomPasswordResetTokenGenerator().make_token(user)
            link = baseurl +'api/v1/users/reset_password/'+uid+'/'+token+'/'
            #Send Mail Code
            body='Click Following Link To Reset Your Password: ' + link
            data={
                'subject':'Reset Your Password',
                'body' : body,
                'to_email': user.email
            }
            Utils.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')
            

class UserPasswordResetSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  confirm_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'confirm_password']

  def validate(self, attrs):
    try:
      password = attrs.get('password')
      confirm_password = attrs.get('confirm_password')
      uid = self.context.get('uid')
      token = self.context.get('token')
      if password != confirm_password:
        raise serializers.ValidationError("Password and Confirm Password doesn't match")
      id = smart_str(urlsafe_base64_decode(uid))
      user = User.objects.get(user_id=id)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError('Token is not Valid or Expired')
      user.set_password(password)
      user.save()
      return attrs
    except DjangoUnicodeDecodeError as identifier:
      PasswordResetTokenGenerator().check_token(user, token)
      raise serializers.ValidationError('Token is not Valid or Expired')
  
        
class ModulesOptionsSerializer(serializers.ModelSerializer):
    module_sections = ModModuleSectionsSerializer(many=True, read_only=True, source='modulesections_set')

    class Meta:
        model = Modules
        fields = ['module_id', 'module_name', 'description', 'module_sections']

    def get_modules_sections(modules):
        serializer = ModulesOptionsSerializer(modules, many=True)
        return {
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }

class UserUpdateByAdminOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = (
            'user_id', 
            'created_at', 
            'updated_at', 
            'last_login', 
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False  # Makes password optional in requests
            }
        }