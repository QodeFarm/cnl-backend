"""
Custom email classes for Djoser to override default email behavior.
This module provides branded, tenant-aware email templates.

ROOT CAUSE FIX:
The issue where "apicore.cnlerp.com" appears in confirmation emails is because
Djoser's default ConfirmationEmail class uses `request.get_host()` which returns
the API backend domain. This module overrides that behavior to use the frontend
tenant domain passed via X-Client-Domain header.
"""

from djoser.email import ConfirmationEmail as DjoserConfirmationEmail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from apps.company.models import Companies
import os


def get_tenant_email_context(request, user=None):
    """
    Build tenant-aware context for email templates.
    
    This function extracts the frontend domain from request headers
    and fetches company information for branding.
    
    Args:
        request: Django HTTP request object
        user: User model instance (optional)
    
    Returns:
        dict: Context dictionary with branding variables
    """
    # Default branding
    default_company_name = "CNL ERP"
    default_domain = "cnlerp.com"
    
    # Get frontend domain from X-Client-Domain header (set by Nginx)
    client_domain = ""
    if request:
        client_domain = request.headers.get("X-Client-Domain", "")
        client_domain = client_domain.replace("https://", "").replace("http://", "").split(":")[0]
    
    # Determine scheme and domain
    if request and ('127.0.0.1' in request.get_host() or 'localhost' in request.get_host()):
        frontend_domain = 'localhost:4200'
        scheme = 'http'
    else:
        frontend_domain = client_domain if client_domain else default_domain
        scheme = 'https'
    
    # Try to get company info from database
    company_name = default_company_name
    support_email = None
    
    try:
        company = Companies.objects.first()
        if company:
            company_name = company.name or default_company_name
            support_email = company.email
    except Exception:
        pass  # Use defaults if company lookup fails
    
    # Build site URL (never use apicore.cnlerp.com)
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


class CustomConfirmationEmail(DjoserConfirmationEmail):
    """
    Custom confirmation email sent after user successfully activates their account.
    
    This overrides Djoser's default ConfirmationEmail to:
    1. Use branded HTML template instead of plain text
    2. Use frontend domain (prod.cnlerp.com) instead of API domain (apicore.cnlerp.com)
    3. Include company name in subject and signature
    """
    
    template_name = "emails/activation_success_email.html"
    
    def get_context_data(self):
        """Build context with tenant-aware branding."""
        context = super().get_context_data()
        
        # Get user from context (Djoser passes user in context, not as self.user)
        user = context.get('user')
        
        # Get tenant context
        tenant_context = get_tenant_email_context(self.request, user)
        context.update(tenant_context)
        
        return context
    
    def send(self, to, *args, **kwargs):
        """
        Send branded confirmation email.
        
        Overrides default send to:
        - Use custom subject with company name
        - Send HTML email with plain text fallback
        - Set proper FROM name
        """
        context = self.get_context_data()
        company_name = context.get('company_name', 'CNL ERP')
        
        # Build subject (NO apicore.cnlerp.com!)
        subject = f"Your {company_name} Account Is Ready to Use"
        
        # Render HTML template
        html_content = render_to_string(
            'emails/activation_success_email.html',
            context
        )
        
        # Render plain text fallback
        text_content = render_to_string(
            'emails/activation_success_email.txt',
            context
        )
        
        # Get FROM email settings
        from_email = os.environ.get('EMAIL_FROM', settings.DEFAULT_FROM_EMAIL)
        from_name = f"{company_name} Team"
        from_address = f"{from_name} <{from_email}>"
        
        # Create email with HTML and plain text
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_address,
            to=to,
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
