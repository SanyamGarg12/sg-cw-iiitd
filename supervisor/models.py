from django.db import models

from studentportal.models import Project, NGO

from django.utils import timezone

class Notification(models.Model):
	noti_id = models.IntegerField(primary_key= True)
	noti_type 	= models.CharField(max_length=16, null=True, blank=True)
	#noti_type include -> new, edit, log, finish, suggest
	project 	= models.ForeignKey(Project, blank = True, unique= False)
	NGO_name 	= models.CharField(max_length=255)
	NGO_link 	= models.URLField(max_length=200)
	NGO_details	= models.TextField()
	NGO_sugg_by = models.CharField(max_length=255)

class Example(models.Model):
	project 	 = models.OneToOneField(Project, primary_key = True)
	date_created = models.DateTimeField(default = timezone.now)