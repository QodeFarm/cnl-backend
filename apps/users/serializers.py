from .models import Roles, Actions, Modules, RolePermissions, ModuleSections, User, UserTimeRestrictions, UserAllowedWeekdays, UserRoles
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from apps.company.serializers import ModBranchesSerializer
from apps.masters.serializers import ModStatusesSerializer
from apps.masters.models import Statuses
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
    """
    Custom user creation serializer.
    
    Password is OPTIONAL because:
    - Users WITH email: Will set password during activation (activate-set-password flow)
    - Users WITHOUT email: Backend auto-generates temp password
    
    This supports the new secure onboarding flow where users set their own passwords.
    """
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    status_id = serializers.PrimaryKeyRelatedField(queryset=Statuses.objects.all(), required=False, allow_null=True)
    # Make password fields optional - will be auto-generated if not provided
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    re_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta(BaseUserCreateSerializer.Meta):
        profile_picture_url = PictureSerializer(many=True)
        model = User
        fields = '__all__'
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
            'status_id': {'required': False, 'allow_null': True},
            'password': {'required': False, 'allow_blank': True},
        }
    
    def validate(self, attrs):
        """
        Custom validation to handle password logic:
        - If password provided: validate it matches re_password
        - If password not provided: auto-generate a secure temp password
        
        NOTE: We skip Djoser's parent validate to avoid re_password handling issues.
        """
        from apps.users.utils import generate_temp_password
        
        password = attrs.get('password', None)
        re_password = attrs.pop('re_password', None)  # Remove immediately
        email = attrs.get('email', None)
        
        # If no password provided, generate a temp password
        if not password or password.strip() == '':
            temp_password = generate_temp_password()
            attrs['password'] = temp_password
            # Store flag to indicate this was auto-generated (for response)
            self.context['temp_password_generated'] = temp_password
        else:
            # Password was provided - validate it matches
            if re_password and password != re_password:
                raise serializers.ValidationError({"re_password": "Password fields didn't match."})
        
        # Skip Djoser's validate - we handle password ourselves
        # Just call the base ModelSerializer validate
        return attrs
    
    def create(self, validated_data):
        """
        Create user with proper password handling.
        
        Auto-sets:
        - status_id: Default to "Active" status if not provided (for create mode without status field)
        - is_active: False if email provided (requires activation), True if no email
        - force_password_change: True if no email (temp password flow)
        """
        from apps.masters.models import Statuses
        
        # Remove re_password if it somehow got through
        validated_data.pop('re_password', None)
        
        # Set default status_id if not provided (since Status field is hidden in Create mode)
        if 'status_id' not in validated_data or validated_data.get('status_id') is None:
            # Try to get "Active" status, fallback to first available status
            default_status = Statuses.objects.filter(status_name__iexact='Active').first()
            if not default_status:
                default_status = Statuses.objects.first()
            if default_status:
                validated_data['status_id'] = default_status
            else:
                raise serializers.ValidationError({"status_id": "No status found in database. Please create at least one status."})
        
        # Get email to determine activation flow
        email = validated_data.get('email', None)
        
        # Set is_active based on email presence
        if email and email.strip() != '':
            # User with email - requires activation
            validated_data['is_active'] = False
            validated_data['force_password_change'] = False  # Will set own password during activation
        else:
            # User without email - active immediately, must change temp password
            validated_data['is_active'] = True
            validated_data['force_password_change'] = True
        
        # Get password before creating user (need to hash it)
        password = validated_data.pop('password', None)
        
        # Create user directly (bypass Djoser's create to avoid re_password issues)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

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
        # Reset force_password_change flag after user changes password
        user.force_password_change = False
        user.save()
        return attrs


#====================================FIRST-LOGIN-FORCE-CHANGE-PASSWORD-SERIALIZER=============================================================
class ForceChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for first-time login password change.
    Used when user logs in with temporary password and must set their own password.
    Does NOT require old password (since it's a temp password given by admin).
    """
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password']
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')

        # Check if user actually needs to change password
        if not user.force_password_change:
            raise serializers.ValidationError("Password change is not required for this account.")

        if password != confirm_password:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        
        # Validate password strength (optional - add your rules)
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        user.set_password(password)
        user.force_password_change = False  # Reset the flag
        user.save()
        return attrs


#====================================ACTIVATE-AND-SET-PASSWORD-SERIALIZER=============================================================
class ActivateAndSetPasswordSerializer(serializers.Serializer):
    """
    Serializer for combined activation + password setup flow.
    User clicks activation link → Sets their own password → Account activated.
    
    This is the most secure approach as:
    - No password is sent via email
    - User creates their own memorable password
    - Password meets your security requirements
    """
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['uid', 'token', 'password', 'confirm_password']
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Password and confirm password don't match"})
        
        # Validate password strength
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})
        
        # Check for at least one uppercase, one lowercase, one digit
        import re
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter"})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter"})
        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one digit"})
        
        return attrs


#====================================USER-FORGET-PASSWD-SERIALIZER=============================================================
# class SendPasswordResetEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=255)
#     class Meta:
#         fields = ['email']
#     def validate(self, attrs):
#         email = attrs.get('email')
#         if User.objects.filter(email=email).exists():
#             #if exists get user object from DB
#             user = User.objects.get(email=email)
#             uid = urlsafe_base64_encode(force_bytes(user.user_id))
#             token = CustomPasswordResetTokenGenerator().make_token(user)
#             link = baseurl +'api/v1/users/reset_password/'+uid+'/'+token+'/'
#             #Send Mail Code
#             body='Click Following Link To Reset Your Password: ' + link
#             data={
#                 'subject':'Reset Your Password',
#                 'body' : body,
#                 'to_email': user.email
#             }
#             Utils.send_email(data)
#             return attrs
#         else:
#             raise serializers.ValidationError('You are not a Registered User')
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        request = self.context.get('request')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.user_id))
            token = CustomPasswordResetTokenGenerator().make_token(user)

            # Get current domain from request
            backend_host = request.get_host()
            
            # Handle development environment
            if '127.0.0.1' in backend_host or 'localhost' in backend_host:
                frontend_domain = 'localhost:4200'
                scheme = 'http'
            else:
                # Get client domain from header, fallback to host if not present
                client_domain = request.headers.get("X-Client-Domain")
                if client_domain:
                    # Remove protocol and port if present
                    frontend_domain = client_domain.replace("https://", "").replace("http://", "").split(":")[0]
                else:
                    # Fallback to backend host if X-Client-Domain not present
                    frontend_domain = backend_host
                scheme = 'https'

            # Build reset URL for frontend
            frontend_reset_url = f"{scheme}://{frontend_domain}/#/reset-password/{uid}/{token}"
            
            # Send email
            body = f'Click Following Link To Reset Your Password: {frontend_reset_url}'
            data = {
                'subject': 'Reset Your Password',
                'body': body,
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