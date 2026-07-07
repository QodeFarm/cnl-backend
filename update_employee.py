# Save this in: C:\Users\Pramod Kumar\CNL_Backend\purchase_ledger\cnl-backend\update_employee.py

import os
import sys
import django

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set settings module - try different options
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # Try this first

try:
    django.setup()
    print("Django setup successful!")
except ImportError:
    # Try with cnl_backend.settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cnl_backend.settings')
    django.setup()
    print("Django setup with cnl_backend.settings successful!")

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