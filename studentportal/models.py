from django.contrib.auth.models import User
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from CW_Portal import settings
from studentportal.decorators import path_and_rename
from studentportal.validators import validate_credits, validate_feedback_hours

class project_stage(object):
    TO_BE_VERIFIED, ONGOING, SUBMITTED, COMPLETED = range(1,5)
    _all_stages_ = [TO_BE_VERIFIED, ONGOING, SUBMITTED, COMPLETED]

_project_stage_mapping = {
    project_stage.TO_BE_VERIFIED : "Yet to be verified",
    project_stage.ONGOING : "Ongoing",
    project_stage.SUBMITTED: "Submitted for final check",
    project_stage.COMPLETED: "Completed"
}

# Pretty bad idea to mix html with logic! :/
_project_stage_glyphicon_mapping = {
    project_stage.TO_BE_VERIFIED : "exclamation-sign",
    project_stage.ONGOING : "tree-conifer",
    project_stage.SUBMITTED: "list-alt",
    project_stage.COMPLETED: "ok"
}

# Type of the uploaded document
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

def _get_other_category():
    return Category.objects.get(name='Other')

class NGO(models.Model):
    name        = models.CharField(max_length=1000)
    link        = models.URLField(blank=True)
    details     = models.TextField(blank=True)
    category    = models.ForeignKey(Category, related_name='NGOs', null=True, on_delete=models.SET(_get_other_category))

    def __unicode__(self):
        return self.name

class UndeletedProjects(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        return super(UndeletedProjects, self).get_queryset().filter(deleted=False)

class AllProjects(models.Manager):
    def get_queryset(self):
        return super(AllProjects, self).get_queryset()

class Project(models.Model):
    student             = models.ForeignKey(User, related_name='projects', on_delete=models.SET_DEFAULT)
    title               = models.CharField(max_length=1000)
    date_created        = models.DateTimeField(default=timezone.now)
    credits             = models.IntegerField(default=2,
                            validators=[validate_credits])
    NGO                 = models.ForeignKey(NGO, blank=True, null = True,related_name='projects', on_delete=models.SET_NULL)
    NGO_name            = models.CharField(max_length=1000)
    NGO_details         = models.CharField(max_length=1000)
    NGO_super           = models.CharField(max_length=1000)
    NGO_super_contact   = models.CharField(max_length=100)
    goals               = models.TextField()
    schedule_text       = models.TextField()
    finish_date         = models.DateTimeField(blank = True, null = True)
    stage               = models.IntegerField(max_length = 5, default = project_stage.TO_BE_VERIFIED)
    category            = models.ForeignKey(Category, related_name='projects', null=False, blank=False, on_delete=models.SET(_get_other_category))
    deleted             = models.BooleanField(default = False)
    presented           = models.BooleanField(default = False)

    all_projects        = AllProjects()
    objects             = UndeletedProjects()
    # override `objects` with custom manager to prevent showing deleted objects.

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
        # It should be in the `ONGOING` stage and
        # a final report should have been submitted.
        return all([self.stage in [project_stage.ONGOING],
            document_type.FINAL_REPORT in ( x.category for x in self.documents.all()),
            ])

    @classmethod
    def get_student_viewable_project(kls, pk):
        # allow exceptions to be raised up
        project = get_object_or_404(kls, pk=pk)
        if not project.is_viewable_by_student(): raise Http404
        return project

    def final_submission_document(self):
        final_report = self.documents.filter(category=document_type.FINAL_REPORT)
        if len(final_report) == 0:
            return None
        return final_report[0]

    def is_viewable_by_student(self):
        return not self.deleted

    def get_project_status(self):
        return _project_stage_mapping[self.stage]

    def get_project_status_graph(self):
        # Returns a list of dictionaries.
        # Each dictionary is the state of what should be shown
        # in the corresponding project state entry in the graph.
        return [{
                    'stage_cleared':x <= self.stage,
                    'stage_glyphicon': _project_stage_glyphicon_mapping[x],
                    'info': ProgressAnalyser.next_steps[x](self),
                    'stage_name': _project_stage_mapping[x]
                }
                 for x in project_stage._all_stages_]

    def delete(self, *args, **kwargs):
        for doc in self.documents.all(): doc.delete()
        for noti in self.notification_set.all(): noti.delete()
        super(Project, self).delete(*args, **kwargs)


class Document(models.Model):
    document     = models.FileField(upload_to=path_and_rename)
    name         = models.CharField(max_length=100)
    date_added   = models.DateTimeField(default=timezone.now)
    category     = models.IntegerField(max_length=5)
    project      = models.ForeignKey(Project, related_name='documents', on_delete=models.SET_DEFAULT)

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
    # The feedback that has to filled by the students at the end of
    # their project.
    project       = models.ForeignKey(Project, primary_key = True, related_name='feedback', on_delete=models.SET_DEFAULT)
    hours         = models.IntegerField(validators=[validate_feedback_hours])
    achievements  = models.TextField(max_length = 2000)
    experience    = models.IntegerField(choices=(
                      (1,"Very Poor"), (2,"Poor"), (3,"Neutral"),
                      (4,"Good"), (5,"Very Good")), default=1)

    def __unicode__(self):
        return ': '.join([self.project.title, str(self.experience)])

class Bug(models.Model):
    user        = models.ForeignKey(User, related_name='bugs', null = True, on_delete=models.SET_DEFAULT)
    suggestions = models.TextField(max_length=2000, blank=True)
    rating      = models.IntegerField()

class Edit(models.Model):
    # store the prettified diff of the changes made to the project details.
    project     = models.ForeignKey(Project, related_name='edits', on_delete=models.SET_DEFAULT)
    diff_text   = models.TextField(max_length=2000, blank=True)
    when        = models.DateTimeField(default=timezone.now)

class ProgressAnalyser(object):

    _unverified = "Your proposal has been sent to the TA for approval. You may receive a mail asking for clarifications about your proposal before accepting. If this takes more than a couple of days, please drop a mail at communitywork <magic> iiitd.ac.in."
    _ongoing = "Continue working on your project. Also keep uploading regular log reports for faster review. Click on 'Submit Project' on completion of the project."
    _submit_final_report = "Also, it seems you haven't submitted the final report as of now."
    _submitted = "Your project details has been sent to the TA for final acceptance. You may receive a mail asking for your project details or logs. If this takes more than a couple of days, please drop a mail at communitywork <magic> iiitd.ac.in."

    _all_unverified = "Your project has not been verified until now."
    _all_completed = "You have completed your CW project! :)"

    _ongoing_submitted = "You submitted your project for final approval on %s."

    _submitted_ongoing = "Please submit the project for final consideration by clicking on 'Submit Project'."
    _submitted_submitted = _ongoing_submitted

    _completed_ongoing = _submitted_ongoing
    _completed_submitted = _ongoing_submitted

    @staticmethod
    def _base_analyse_stage(project):
        if project.stage == project_stage.TO_BE_VERIFIED: return ProgressAnalyser._all_unverified
        if project.stage == project_stage.COMPLETED: return ProgressAnalyser._all_completed
        return None # could not give a generic return statement

    def _analyse_to_be_verified_stage(project):
        from supervisor.models import diff_type
        if project.stage == project_stage.TO_BE_VERIFIED:
            return ProgressAnalyser._unverified
        time = [d for d in project.diff.all() if d.diff_type == diff_type().PROJECT_VERIFIED][0].when
        return "Your proposal was accepted on %(accept_time)s." % {'accept_time': time.strftime('%d-%m-%Y')}

    def _analyse_ongoing_stage(project):
        from supervisor.models import diff_type
        base_try = ProgressAnalyser._base_analyse_stage(project)
        if base_try: return base_try

        if project.stage == project_stage.ONGOING:
            if not project.is_submittable():
                return ' '.join([ProgressAnalyser._ongoing, ProgressAnalyser._submit_final_report])
            return ProgressAnalyser._ongoing

        if project.stage == project_stage.SUBMITTED:
            date = [d for d in project.diff.all() if d.diff_type == diff_type.PROJECT_SUBMITTED][0].when
            return ProgressAnalyser._ongoing_submitted % (date.strftime('%d-%m-%Y'))

    def _analyse_submitted_stage(project):
        from supervisor.models import diff_type
        base_try = ProgressAnalyser._base_analyse_stage(project)
        if base_try: return base_try

        if project.stage == project_stage.ONGOING:
            return ProgressAnalyser._submitted_ongoing

        if project.stage == project_stage.SUBMITTED:
            date = [d for d in project.diff.all() if d.diff_type == diff_type.PROJECT_SUBMITTED][0].when
            return ProgressAnalyser._submitted_submitted % (date.strftime('%d-%m-%Y'))

    def _analyse_completed_stage(project):
        from supervisor.models import diff_type
        base_try = ProgressAnalyser._base_analyse_stage(project)
        if base_try: return base_try

        if project.stage == project_stage.ONGOING: return ProgressAnalyser._completed_ongoing
        if project.stage == project_stage.SUBMITTED:
            date = [d for d in project.diff.all() if d.diff_type == diff_type.PROJECT_SUBMITTED][0].when
            return ProgressAnalyser._completed_submitted % (date.strftime('%d-%m-%Y'))
        return ProgressAnalyser._all_completed

    # next steps returns a mapping of stage to a function that needs a project as an argument
    # The function returns the string to be displayed according to the stage of the project in the popup
    next_steps = {
        project_stage.TO_BE_VERIFIED: _analyse_to_be_verified_stage,
        project_stage.ONGOING: _analyse_ongoing_stage,
        project_stage.SUBMITTED: _analyse_submitted_stage,
        project_stage.COMPLETED: _analyse_completed_stage
    }