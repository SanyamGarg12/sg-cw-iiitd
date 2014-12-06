from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from CW_Portal import settings
from decorators import path_and_rename
from validators import validate_credits, validate_feedback_hours

class project_stage(object):
    TO_BE_VERIFIED, ONGOING, SUBMITTED, COMPLETED = range(1,5)
_project_stage_mapping = {
    project_stage.TO_BE_VERIFIED : "Yet to be verified",
    project_stage.ONGOING : "Ongoing",
    project_stage.SUBMITTED: "Submitted for final check",
    project_stage.COMPLETED: "Completed"
}

class document_type(object):
    PROPOSAL, LOG, FINAL_REPORT = range(1,4)
    mapping = {
        PROPOSAL: "Proposal",
        LOG: "Log",
        FINAL_REPORT: "Final Submission",
    }

class Category(models.Model):
    name        = models.CharField(max_length=300)
    description = models.CharField(max_length=1000, blank=True)
    
    def __unicode__(self):
        return self.name

    @staticmethod
    def get_other_category():
        return Category.objects.get(name='Other')

class NGO(models.Model):
    name        = models.CharField(max_length=1000)
    link        = models.URLField(blank=True)
    details     = models.TextField(blank=True)
    category    = models.ForeignKey(Category, related_name='NGOs', null=True,
                    on_delete=models.SET(Category.get_other_category))

    def __unicode__(self):
        return self.name

class UndeletedProjects(models.Manager):
    def get_query_set(self):
        return super(UndeletedProjects, self).get_query_set().filter(deleted=False)

class AllProjects(models.Manager):
    def get_query_set(self):
        return super(AllProjects, self).get_query_set()

class Project(models.Model):
    student             = models.ForeignKey(User, related_name='projects')
    title               = models.CharField(max_length=1000)
    date_created        = models.DateTimeField(default=timezone.now)
    credits             = models.IntegerField(default=2, 
                            validators=[validate_credits])
    NGO                 = models.ForeignKey(NGO, blank=True,
                            null = True,related_name='projects',
                            on_delete=models.SET_NULL)
    NGO_name            = models.CharField(max_length=1000)
    NGO_details         = models.CharField(max_length=1000)
    NGO_super           = models.CharField(max_length=1000)
    NGO_super_contact   = models.CharField(max_length=100)
    goals               = models.TextField()
    schedule_text       = models.TextField()
    finish_date         = models.DateTimeField(blank = True, null = True)
    stage               = models.IntegerField(max_length = 5, 
                            default = project_stage.TO_BE_VERIFIED)
    category            = models.ForeignKey(Category, 
                            related_name='projects', null=False, blank=False,
                            on_delete=models.SET(Category.get_other_category))
    deleted             = models.BooleanField(default = False)

    objects             = UndeletedProjects()
    all_projects        = AllProjects()

    def __unicode__(self):
        return self.title

    def get_rollno(self):
        first = self.student.email.split('@')[0][-5:]
        return ''.join(['20',first])

    def get_batch(self):
        return "".join(["BTech 20", self.student.email.split('@')[0][-5:-3]])

    def get_NGO(self):
        if self.NGO:
            return ''.join(["<strong>", self.NGO.name, " |","</strong>", " ", self.NGO_name])
        return self.NGO_name

    def is_submittable(self):
        return all([self.stage in [project_stage.ONGOING],
            document_type.FINAL_REPORT in ( x.category for x in self.documents.all()),
            ])

    def get_project_status(self):
        return _project_stage_mapping[self.stage]

    def delete(self, *args, **kwargs):
        for doc in self.documents.all(): doc.delete()
        for noti in self.notification_set.all(): noti.delete()
        super(Project, self).delete(*args, **kwargs)


class Document(models.Model):
    document     = models.FileField(upload_to=path_and_rename('uploads/%Y/'))
    name         = models.CharField(max_length=100)
    date_added   = models.DateTimeField(default=timezone.now)
    category     = models.IntegerField(max_length=5)
    project      = models.ForeignKey(Project, related_name = 'documents')

    def __unicode__(self):
        return ': '.join([self.project.title, self.document.name])

    def delete(self, *args, **kwargs):
        import os
        os.remove(os.path.join(settings.MEDIA_ROOT, self.document.name))
        super(Document, self).delete(*args, **kwargs)

    @staticmethod
    def get_document_type(a):
        return document_type.mapping.get(a, None)

    def get_current_document_type(self):
        return self.get_document_type(self.category)

class Feedback(models.Model):
    project       = models.ForeignKey(Project, primary_key = True,
                      related_name='feedback')
    hours         = models.IntegerField(validators=[validate_feedback_hours])
    achievements  = models.TextField(max_length = 2000)
    experience    = models.IntegerField(choices=(
                      (1,"Very Poor"), (2,"Poor"), (3,"Neutral"),
                      (4,"Good"), (5,"Very Good")), default=1)

    def __unicode__(self):
        return ': '.join([self.project.title, self.experience])

class Bug(models.Model):
    user        = models.ForeignKey(User, related_name='bugs', null = True)
    suggestions = models.TextField(max_length=2000, blank=True)
    rating      = models.IntegerField()