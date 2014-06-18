from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.forms import ModelForm

from django import forms

class NGO(models.Model):
	name 	= models.CharField(max_length=255)
	link 	= models.URLField()
	details = models.TextField()

class Project(models.Model):
	credits 				= models.IntegerField(default=2)
	title 					= models.CharField(max_length=1024)
	date_created 			= models.DateTimeField(default=timezone.now)
	NGO_name 				= models.CharField(max_length=1024)
	NGO 					= models.ForeignKey(NGO, blank=True, null = True)
	NGO_details 			= models.CharField(max_length=2048)
	NGO_super 				= models.CharField(max_length=127)
	goals 					= models.TextField()
	expected_finish_date 	= models.DateTimeField(blank = True, null = True)
	schedule_text 			= models.TextField()
	student 				= models.ForeignKey(User, related_name='projects')

	def __unicode__(self):
		return self.title

class Document(models.Model):
	document = models.FileField(upload_to='uploads/%Y/')
	date_added 	= models.DateTimeField(default=timezone.now)
	#category has the following options -> proposal, log, submission
	category	= models.CharField(max_length=16)
	project = models.ForeignKey(Project, related_name = 'documents')

class Notification(models.Model):
	noti_type 	= models.CharField(max_length=16)
	#noti_type include -> new, edit, log, finish, suggest
	project 	= models.OneToOneField(Project, blank = True)
	NGO_name 	= models.CharField(max_length=255)
	NGO_link 	= models.URLField(max_length=200)
	NGO_details	= models.TextField()
	NGO_sugg_by = models.CharField(max_length=255)

class Example(models.Model):
	project 	 = models.OneToOneField(Project, primary_key = True)
	date_created = models.DateTimeField(timezone.now)


class ProjectForm(ModelForm):
	def __init__(self, user, *args, **kwargs):
		super(ProjectForm, self).__init__(*args, **kwargs)
	class Meta:
		model = Project
		fields = ['title', 'credits', 'NGO_name', 'NGO_details',
				'NGO_super', 'goals',
				'schedule_text']

class UploadDocumentForm(forms.Form):
	document = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )