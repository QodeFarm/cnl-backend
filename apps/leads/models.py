from datetime import datetime
import uuid
from django.db import models
from config.utils_variables import *
from apps.hrms.models import Employees
from phonenumber_field.modelfields import PhoneNumberField


class LeadStatuses(models.Model):
	lead_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	status_name = models.CharField(max_length=50, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.status_name}"

	class Meta:
		db_table = leadstatuses

class InteractionTypes(models.Model):
	interaction_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	interaction_type = models.CharField(max_length=50, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.interaction_type}"

	class Meta:
		db_table = interactiontypes

class Leads(models.Model):
	lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=50, null=False)
	email = models.CharField(max_length=50, null=False)
	phone = PhoneNumberField(blank=True, null=True, default=None, help_text="Enter the phone number with country code, e.g., +91 XXXXXXXXXX")
	lead_status_id = models.ForeignKey(LeadStatuses, on_delete=models.CASCADE, null=False, db_column='lead_status_id')
	score = models.IntegerField(null=True, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.name}"

	class Meta:
		db_table = leads

class LeadAssignments(models.Model):
	assignment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	lead_id = models.ForeignKey(Leads, on_delete=models.CASCADE, null=False, db_column='lead_id')
	sales_rep_id = models.ForeignKey(Employees, on_delete=models.CASCADE, null=False, db_column='sales_rep_id')
	assignment_date = models.DateTimeField(null=False, default=datetime.today)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.assignment_id}"

	class Meta:
		db_table = leadassignments