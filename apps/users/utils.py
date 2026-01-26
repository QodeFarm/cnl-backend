from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import os
import secrets
import string
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

#This file is used for sending Mail

# Default branding constants
DEFAULT_COMPANY_NAME = "CNL ERP"
DEFAULT_DOMAIN = "cnlerp.com"


def generate_temp_password(length=10):
    """
    Generate a secure, unique temporary password.
    
    Password format: Mix of uppercase, lowercase, digits, and special chars
    Example: "Xk9mP2nL3Q"
    
    Args:
        length: Password length (default 10)
    
    Returns:
        str: Secure random password
    """
    # Using only safe special characters that won't cause encoding issues
    safe_special = "@#$"
    
    # Ensure at least one of each type
    uppercase = secrets.choice(string.ascii_uppercase)
    lowercase = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice(safe_special)
    
    # Fill remaining with mixed characters (mostly alphanumeric for simplicity)
    remaining_length = length - 4
    all_chars = string.ascii_letters + string.digits + safe_special
    remaining = ''.join(secrets.choice(all_chars) for _ in range(remaining_length))
    
    # Combine and shuffle
    password_list = list(uppercase + lowercase + digit + special + remaining)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)


def get_tenant_context(request, user=None):
    """
    Build tenant-aware context for email templates.
    
    Extracts frontend domain from X-Client-Domain header and fetches
    company information for branding. Never returns API domain.
    
    Args:
        request: Django HTTP request object
        user: Optional user model instance
    
    Returns:
        dict: Context dictionary with branding variables
    """
    from apps.company.models import Companies
    
    # Get frontend domain from X-Client-Domain header (set by Nginx)
    client_domain = ""
    backend_host = request.get_host() if request else ""
    
    if request:
        client_domain = request.headers.get("X-Client-Domain", "")
        client_domain = client_domain.replace("https://", "").replace("http://", "").split(":")[0]
    
    # Determine scheme and domain
    if '127.0.0.1' in backend_host or 'localhost' in backend_host:
        frontend_domain = 'localhost:4200'
        scheme = 'http'
    else:
        # IMPORTANT: Never use apicore.cnlerp.com - always use frontend domain
        frontend_domain = client_domain if client_domain else DEFAULT_DOMAIN
        scheme = 'https'
    
    # Try to get company info from database
    company_name = DEFAULT_COMPANY_NAME
    support_email = None
    
    try:
        company = Companies.objects.first()
        if company:
            company_name = company.name or DEFAULT_COMPANY_NAME
            support_email = company.email
    except Exception:
        pass  # Use defaults if company lookup fails
    
    # Build site URL
    site_url = f"{scheme}://{frontend_domain}"
    
    context = {
        'company_name': company_name,
        'site_domain': frontend_domain,
        'site_url': site_url,
        'login_url': f"{site_url}/#/login",
        'support_email': support_email,
        'scheme': scheme,
        'frontend_domain': frontend_domain,
    }
    
    # Add user info if provided
    if user:
        context['username'] = user.username if hasattr(user, 'username') else user.email
        context['user_email'] = user.email
    
    return context


class Utils:
    @staticmethod
    def send_email(data):
        """
        Send plain text email (legacy method for backward compatibility).
        """
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=os.environ.get('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.send()
    
    @staticmethod
    def send_branded_email(subject, to_email, html_template, text_template, context, company_name=None):
        """
        Send branded HTML email with plain text fallback.
        
        Args:
            subject: Email subject line
            to_email: Recipient email address
            html_template: Path to HTML template
            text_template: Path to plain text template
            context: Template context dictionary
            company_name: Company name for FROM address (optional)
        """
        company = company_name or context.get('company_name', DEFAULT_COMPANY_NAME)
        
        # Render templates
        html_content = render_to_string(html_template, context)
        text_content = render_to_string(text_template, context)
        
        # Build FROM address with company name
        from_email = os.environ.get('EMAIL_FROM', settings.DEFAULT_FROM_EMAIL)
        from_name = f"{company} Team"
        from_address = f"{from_name} <{from_email}>"
        
        # Create email with HTML and plain text alternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_address,
            to=[to_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


def send_activation_email(user, request):
    """
    Send branded activation email to newly created user.
    
    This function generates the activation URL using the frontend domain
    (never the API domain) and sends a professional HTML email.
    
    NEW FLOW: Link goes to /set-password/ page where user sets their own password
    and activates their account in one step.
    """
    # Get tenant context with branding info
    context = get_tenant_context(request, user)
    
    # Generate activation URL using frontend domain
    # IMPORTANT: Points to /set-password/ route (user sets own password during activation)
    uid = urlsafe_base64_encode(force_bytes(user.user_id))
    token = default_token_generator.make_token(user)
    activation_url = f"{context['site_url']}/#/set-password/{uid}/{token}"
    
    # Add activation-specific context
    context['activation_link'] = activation_url
    
    # Build branded subject
    subject = f"Welcome to {context['company_name']} - Set Up Your Account"
    
    # Send branded HTML email
    Utils.send_branded_email(
        subject=subject,
        to_email=user.email,
        html_template='emails/activation_email.html',
        text_template='emails/activation_email.txt',
        context=context
    )