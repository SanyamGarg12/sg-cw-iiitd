from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.forms import ModelForm

from django import forms

from decorators import path_and_rename, validate_credits


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)
    def __unicode__(self):
        return self.name

class NGO(models.Model):
    name    = models.CharField(max_length=1023)
    link    = models.URLField(blank = True)
    details = models.TextField(blank=True)
    category = models.ForeignKey(Category, related_name='NGOs', null=True)

    def __unicode__(self):
        return self.name

class Project(models.Model):
    credits                 = models.IntegerField(default=2, validators=[validate_credits])
    title                   = models.CharField(max_length=1024)
    date_created            = models.DateTimeField(default=timezone.now)
    NGO_name                = models.CharField(max_length=1024)
    NGO                     = models.ForeignKey(NGO, blank=True, null = True, related_name='projects')
    NGO_details             = models.CharField(max_length=2048)
    NGO_super               = models.CharField(max_length=127)
    NGO_super_contact       = models.CharField(max_length=127)
    goals                   = models.TextField()
    expected_finish_date    = models.DateTimeField(blank = True, null = True)
    schedule_text           = models.TextField()
    student                 = models.ForeignKey(User, related_name='projects')
    stage                   = models.CharField(max_length = 15, default = 'to_be_verified')
    #stage includes -> 'to_be_verified','ongoing', 'completed' 
    category                = models.ForeignKey(Category, null=True, related_name='projects')

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

    def get_NGO(self):
        if self.NGO:
            return self.NGO.name
        else: 
            return self.NGO_name     

class Document(models.Model):
    document = models.FileField(upload_to=path_and_rename('uploads/%Y/'))
    date_added  = models.DateTimeField(default=timezone.now)
    #category has the following options -> proposal, log, submission
    category    = models.CharField(max_length=16)
    project = models.ForeignKey(Project, related_name = 'documents')

    def __unicode__(self):
        return ': '.join([self.project.title, self.document.name])

class Feedback(models.Model):
    project         = models.ForeignKey(Project, primary_key = True, related_name='feedback')
    hours           = models.IntegerField()
    achievements    = models.CharField(max_length = 1024)
    experience      = models.IntegerField(choices=(
        (1,"Very Poor"), (2,"Poor"), (3,"Neutral"), (4,"Good"), (5,"Very Good") ), default=1)

    def get_name(self):
        return ' '.join([self.project.student.first_name, self.project.student.last_name])
    
    def get_rollno(self):
        return self.project.get_rollno

    def get_name_of_NGO(self):
        return self.project.NGO.name if self.project.NGO else self.project.NGO_name

    def get_name_of_supervisor(self):
        return self.project.NGO_super

    def get_contact_of_supervisor(self):
        return self.project.NGO_super_contact

    def get_nature(self):
        return ','.join((str(x) for x in self.project.category))

class ProjectForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Project
        fields = ['title', 'credits', 'NGO_name', 'NGO_details',
                'NGO_super', 'NGO_super_contact', 'goals',
                'schedule_text']

class UploadDocumentForm(forms.Form):
    document = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )
    CHOICES = (('proposal','proposal'),('log', 'log'),('submission', 'submission'),)
    category = forms.ChoiceField(choices=CHOICES,
        help_text = 'Type of Document')

class suggest_NGOForm(forms.Form):
    name = forms.CharField()
    link = forms.URLField(required = False)
    details = forms.CharField(max_length = 2000, required = False)
    # category

class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ['hours', 'achievements', 'experience']