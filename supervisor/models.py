from django.db import models
from django.contrib.auth.models import User
from studentportal.models import Project, NGO, Category
from django import forms
from django.utils import timezone
from CW_Portal import global_constants

class Notification(models.Model):
    noti_id = models.IntegerField(primary_key= True)
    noti_type   = models.CharField(max_length=16, null=True, blank=True)
    #noti_type include -> new, finish, suggest
    project     = models.ForeignKey(Project, null= True, unique= False)
    NGO_name    = models.CharField(max_length=255, blank=True)
    NGO_link    = models.URLField(max_length=200, blank=True)
    NGO_details = models.TextField(blank=True)
    NGO_sugg_by = models.CharField(max_length=255) 

class Example(models.Model):
    project      = models.OneToOneField(Project, primary_key = True)
    date_created = models.DateTimeField(default = timezone.now)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    def delete(self, *args, **kwargs):
        for l in self.likes.all():
            l.delete()
        for c in self.comments.all():
            c.delete()
        super(Example, self).delete(*args, **kwargs)

class Like(models.Model):
    project = models.ForeignKey(Example, related_name='likes')
    liked_by = models.ForeignKey(User, related_name='liked_projects')
    def save(self, *args, **kwargs):
        self.project.likes_count += 1
        self.project.save()
        global_constants.leaderboard_refresh = True
        super(Like, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        self.project.likes_count -= 1
        self.project.save()
        global_constants.leaderboard_refresh = True
        super(Like, self).delete(*args, **kwargs)

class Comment(models.Model):
    text = models.CharField(max_length=200) 
    project = models.ForeignKey(Example, related_name='comments')
    commentor = models.ForeignKey(User, related_name='comments')
    def save(self, *args, **kwargs):
        self.project.comments_count += 1
        self.project.save()
        super(Comment, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        self.project.comments_count -= 1
        self.project.save()
        super(Comment, self).delete(*args, **kwargs)


class News(models.Model):
    content = models.TextField(max_length=1000)
    date_created = models.DateTimeField(default = timezone.now)
    priority = models.IntegerField()
    #from 1,2
    def get_priority(self):
        if self.priority == 1: return "Low"
        else: return "High"

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
    priority = forms.ChoiceField( choices=(
        (1, "Low"), (2, "High"),),
        help_text = "High priority will also send a mail to all the students who are still doing their projects."
        )
    class Meta:
        model = News
        fields = ['content', 'priority']

class NewCategoryForm(forms.Form):
    name = forms.CharField(label="Name of the category", required=True)
    description = forms.CharField(label="Describe the category", required=False)

class NewNGOForm(forms.Form):
    name = forms.CharField(label="Name of the NGO")
    link = forms.CharField(label="Link for the NGO", required = False)
    details = forms.CharField(label="Something about the NGO", required=False)

class EmailProjectForm(forms.Form):
    to = forms.CharField(label="Student Email", required = True)
    body = forms.CharField(label="Body", widget=forms.Textarea, required=True)

class NewCommentForm(forms.ModelForm):
    text = forms.CharField(label="Comment: ", required=True)
    class Meta:
        model = Comment
        fields = ['text']