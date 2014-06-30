from django.db import models

from studentportal.models import Project, NGO, Category
from django import forms
from django.utils import timezone

class Notification(models.Model):
	noti_id = models.IntegerField(primary_key= True)
	noti_type 	= models.CharField(max_length=16, null=True, blank=True)
	#noti_type include -> new, finish, suggest
	project 	= models.ForeignKey(Project, null= True, unique= False)
	NGO_name 	= models.CharField(max_length=255, blank=True)
	NGO_link 	= models.URLField(max_length=200, blank=True)
	NGO_details	= models.TextField(blank=True)
	NGO_sugg_by = models.CharField(max_length=255)


class Example(models.Model):
	project 	 = models.OneToOneField(Project, primary_key = True)
	date_created = models.DateTimeField(default = timezone.now)

class News(models.Model):
    content = models.TextField()
    date_created = models.DateTimeField(default = timezone.now)
    priority = models.IntegerField()
    #from 1,2,3
    def get_priority(self):
        if self.priority == 1: return "LOW"
        elif self.priority == 2: return "MEDIUM"
        else: return "HIGH"

class AdvanceSearchForm(forms.Form):
    stage = forms.ChoiceField(choices=(
    	('all', 'all'),('ongoing', 'ongoing'),('to_be_verified', 'unverified'), ('completed', 'completed')
    	),
    label="Stage of project"
    )
    name = forms.CharField(label="Name of student", required = False) 
    email = forms.EmailField(label="Email", required = False)
    roll_no = forms.IntegerField(required = False, label="Roll number")
    project_title = forms.CharField(required = False, label = "Words in project title")
    NGO_name = forms.CharField(required = False, label = "Name of the NGO")
    year_choices = ((x,str(x)) for x in range(2014, timezone.now().year + 1))
    proposal_year = forms.ChoiceField(choices = year_choices, label="Year of proposal of CW project")
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
         empty_label='All', required=False, label="Category of the project")
    # time_completed_before
    # time_completed_after

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['content', 'priority']

class NewCategoryForm(forms.Form):
    name = forms.CharField(label="Name of the category")
    description = forms.CharField(label="Describe the category")

class NewNGOForm(forms.Form):
    name = forms.CharField(label="Name of the NGO")
    link = forms.CharField(label="Link for the NGO", required = False)
    details = forms.CharField(label="Something about the NGO", required=False)