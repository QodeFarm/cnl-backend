import uuid
from django.db import models
from config.utils_variables import *
from apps.hrms.models import Employees

class LeadStatuses(models.Model):
	lead_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	status_name = models.CharField(max_length=50, null=True, default=None)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.status_name}"

	class Meta:
		db_table = leadstatuses

class InteractionTypes(models.Model):
	interaction_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	interaction_type = models.CharField(max_length=50, null=True, default=None)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.interaction_type}"

	class Meta:
		db_table = interactiontypes

class Leads(models.Model):
	lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=50, null=True, default=None)
	email = models.CharField(max_length=50, null=True, default=None)
	phone = models.CharField(max_length=50, null=True, default=None)
	lead_status_id = models.ForeignKey(LeadStatuses, on_delete=models.CASCADE, db_column='lead_status_id')
	score = models.IntegerField(null=True, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.name}"

	class Meta:
		db_table = leads

class LeadAssignments(models.Model):
	assignment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	lead_id = models.ForeignKey(LeadStatuses, on_delete=models.CASCADE, db_column='lead_id')
	sales_rep_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='sales_rep_id')
	assignment_date = models.DateTimeField(auto_now_add=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.assignment_id}"

	class Meta:
		db_table = leadassignments