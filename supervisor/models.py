from django.db import models
from django.contrib.auth.models import User
from studentportal.models import Project, NGO, Category
from django import forms
from django.utils import timezone
from CW_Portal import global_constants
from django.contrib.admin import widgets
from notifications import notification_type

class Notification(models.Model):
    noti_id     = models.IntegerField(primary_key= True)
    noti_type   = models.IntegerField(max_length=5, null=True, blank=True)
    project     = models.ForeignKey(Project, null= True, unique= False)
    NGO_name    = models.CharField(max_length=200, blank=True)
    NGO_link    = models.URLField(max_length=200, blank=True)
    NGO_details = models.TextField(blank=True)
    NGO_sugg_by = models.ForeignKey(User, null=True)

class Example(models.Model):
    project         = models.OneToOneField(Project, primary_key = True)
    date_created    = models.DateTimeField(default = timezone.now)
    likes_count     = models.IntegerField(default=0)
    comments_count  = models.IntegerField(default=0)
    
    def delete(self, *args, **kwargs):
        for l in self.likes.all():
            l.delete()
        for c in self.comments.all():
            c.delete()
        super(Example, self).delete(*args, **kwargs)

class Like(models.Model):
    project     = models.ForeignKey(Example, related_name='likes')
    liked_by    = models.ForeignKey(User, related_name='liked_projects')
    def save(self, *args, **kwargs):
        self.project.likes_count += 1
        self.project.save()
        super(Like, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        self.project.likes_count -= 1
        self.project.save()
        super(Like, self).delete(*args, **kwargs)

class Comment(models.Model):
    text        = models.CharField(max_length=200) 
    project     = models.ForeignKey(Example, related_name='comments')
    commentor   = models.ForeignKey(User, related_name='comments')
    def save(self, *args, **kwargs):
        self.project.comments_count += 1
        self.project.save()
        super(Comment, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        self.project.comments_count -= 1
        self.project.save()
        super(Comment, self).delete(*args, **kwargs)

class News(models.Model):
    content         = models.TextField(max_length=1000)
    date_created    = models.DateTimeField(default = timezone.now)
    priority        = models.BooleanField(default=False)
    def get_priority(self):
        return "High" if self.priority else "Low"

class TA(models.Model):
    email       = models.CharField(max_length = 100)
    instructor  = models.BooleanField(default=False)
