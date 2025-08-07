from datetime import datetime
import uuid
from django.db import models
from config.utils_variables import *
from apps.hrms.models import Employees


class LeadStatuses(models.Model):
	lead_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	status_name = models.CharField(max_length=50, null=False)
	is_deleted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.status_name}"

	class Meta:
		db_table = leadstatuses

class InteractionTypes(models.Model):
	interaction_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	interaction_type = models.CharField(max_length=50, null=False)
	is_deleted = models.BooleanField(default=False)
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
	phone = models.CharField(max_length=50, null=True, default=None)
	assignee_id = models.ForeignKey(Employees, on_delete=models.PROTECT, null=False, db_column='assignee_id')
	lead_status_id = models.ForeignKey(LeadStatuses, on_delete=models.PROTECT, null=False, db_column='lead_status_id')
	score = models.IntegerField(null=True, default=0)
	is_deleted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.name}"

	class Meta:
		db_table = leads

class LeadInteractions(models.Model):
	interaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	lead_id = models.ForeignKey(Leads, on_delete=models.PROTECT, db_column='lead_id', related_name='interaction')
	interaction_type_id = models.ForeignKey(InteractionTypes, on_delete=models.PROTECT, db_column='interaction_type_id')
	interaction_date = models.DateTimeField(null=False, default=datetime.today)
	notes = models.TextField(null=True, default=None)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.interaction_id}"

	class Meta:
		db_table = leadinteractions

class LeadAssignmentHistory(models.Model):
	history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	lead_id = models.ForeignKey(Leads, on_delete=models.PROTECT, db_column='lead_id', related_name='history')
	assignee_id = models.ForeignKey(Employees, on_delete=models.PROTECT, db_column='assignee_id')
	assignment_date = models.DateTimeField(null=False, default=datetime.today)
	end_date = models.DateTimeField(null=True, default=None)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.history_id}"

	class Meta:
		db_table = leadassignmenthistory
