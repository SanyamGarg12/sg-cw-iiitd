from django import forms

from studentportal.models import Project, Feedback, Bug, Category
from studentportal.models import document_type, Document

class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

    NGO_super         = forms.CharField(label="Supervisor at NGO")
    NGO_super_contact = forms.CharField(
                          label="Supervisor contact information",
                          help_text="Complete and submit the rest of the form in the next tab")
    category          = forms.ModelChoiceField(
                          queryset=Category.objects.all())
    schedule_text     = forms.CharField(widget=forms.Textarea,
                          label="Schedule")
    credits           = forms.ChoiceField(choices=((1,1),(2,2)))
    class Meta:
        model = Project
        fields = ['title', 'credits', 'NGO_name', 'NGO_details',
                'NGO_super', 'NGO_super_contact', 'goals',
                'schedule_text','category']

    # injecting student in the save method itself.
    def save(self, force_insert=False, force_update=False, commit=True, student=None):
        _project = super(ProjectForm, self).save(commit=False)
        _project.student = student
        if commit:
            _project.save()
        return _project


class UploadDocumentForm(forms.Form):
    document = forms.FileField( label='Select a file',
                help_text='max. 10 Mb.')
    CHOICES  = tuple([(i, Document.get_document_type(i)) for i in [
                document_type.PROPOSAL, document_type.LOG,
                document_type.FINAL_REPORT]])
    category = forms.ChoiceField(choices=CHOICES,
        help_text = 'Type of Document')

class suggest_NGOForm(forms.Form):
    name    = forms.CharField()
    link    = forms.URLField(required = False)
    details = forms.CharField(max_length = 2000, required = False)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['hours', 'achievements', 'experience']

class BugsForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=(
        ((x,x) for x in range(1,11))
        ), initial =5)
    class Meta:
        model = Bug
        fields = ['suggestions', 'rating']
