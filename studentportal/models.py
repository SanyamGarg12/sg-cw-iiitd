from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.forms import ModelForm

from django import forms

from decorators import path_and_rename

class NGO(models.Model):
    name    = models.CharField(max_length=255)
    link    = models.URLField()
    details = models.TextField()

class Project(models.Model):
    credits                 = models.IntegerField(default=2)
    title                   = models.CharField(max_length=1024)
    date_created            = models.DateTimeField(default=timezone.now)
    NGO_name                = models.CharField(max_length=1024)
    NGO                     = models.ForeignKey(NGO, blank=True, null = True)
    NGO_details             = models.CharField(max_length=2048)
    NGO_super               = models.CharField(max_length=127)
    goals                   = models.TextField()
    expected_finish_date    = models.DateTimeField(blank = True, null = True)
    schedule_text           = models.TextField()
    student                 = models.ForeignKey(User, related_name='projects')
    stage                   = models.CharField(max_length = 15, default = 'to_be_verified')
    #stage includes -> 'to_be_verified','ongoing', 'completed' 

    def __unicode__(self):
        return self.title

    def get_rollno(self):
        first = self.student.email.split('@')[0][-5:]
        return ''.join(['20',first])

    def submitted_and_awaiting_completion(self):
        if self.stage != 'ongoing': return False
        for document in self.documents.all():
            if document.category == 'submission':
                return True
        return False

class Document(models.Model):
    document = models.FileField(upload_to=path_and_rename('uploads/%Y/'))
    date_added  = models.DateTimeField(default=timezone.now)
    #category has the following options -> proposal, log, submission
    category    = models.CharField(max_length=16)
    project = models.ForeignKey(Project, related_name = 'documents')

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
    CHOICES = (('proposal','proposal'),('log', 'log'),('submission', 'submission'),)
    category = forms.ChoiceField(choices=CHOICES,
        help_text = 'Type of Document')