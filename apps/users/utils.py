from django.core.mail import EmailMessage
import os
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

#This file is used for sending Mail

class Utils:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get('EMAIL_FROM'),
            to=[data['to_email']]
      )
        email.send()

def send_activation_email(user, request):
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

    # Generate activation URL
    uid = urlsafe_base64_encode(force_bytes(user.user_id))
    token = default_token_generator.make_token(user)
    activation_url = f"{scheme}://{frontend_domain}/#/activation/{uid}/{token}"
    
    # Prepare email content
    subject = 'Activate Your Account'
    body = f"""You're receiving this email because you need to finish activation process on {frontend_domain}.

Please go to the following page to activate account:

{activation_url}
"""
    data = {
        'subject': subject,
        'body': body,
        'to_email': user.email
    }
    Utils.send_email(data)