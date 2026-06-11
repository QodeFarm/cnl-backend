import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cnl_backend.settings')
django.setup()

from apps.hrms.models import Employees
from django.contrib.auth.hashers import make_password

try:
    emp = Employees.objects.get(employee_id='6f864d4674c441b28882f4c52263fbd3')
    emp.username = 'pramod.kumar'
    emp.password = make_password('Welcome@123')
    emp.is_portal_user = True
    emp.save()
    print(f"✅ Success! Username: {emp.username}, Password: Welcome@123")
except Exception as e:
    print(f"Error: {e}")