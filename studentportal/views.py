from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from PrivateData import SUPERVISOR_EMAIL

from supervisor.models import Notification, Example

from models import ProjectForm, Project, Document, UploadDocumentForm

from django.db.models.signals import pre_save

def add_notification(noti_type, project):
	Notification.objects.create(noti_type=noti_type, project=project)

def index(request):
	if request.user.is_authenticated():
		if request.user.email == SUPERVISOR_EMAIL:
			return HttpResponseRedirect(reverse('supervisor_home'))
	return HttpResponseRedirect(reverse('studenthome'))

def home(request):
	example_projects = Example.objects.all()[:10]
	if request.user.is_authenticated():
		return render(request, 'studenthome.html', 
		{'example_projects': example_projects})
	else:
		return render(request, 'core.html',
			{'example_projects': example_projects,})
	
@login_required
def addproject(request):
	def add_user(sender, **kwargs):
		if sender == Project:
			obj = kwargs['instance']
			obj.student = request.user

	if request.method == 'POST':
		form = ProjectForm(request.user, request.POST)
		if form.is_valid():
			pre_save.connect(add_user)
			form.save()
			pre_save.disconnect(add_user)
			add_notification("new", Project.objects.last())
			return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': Project.objects.last().id}))
	else:
		form = ProjectForm(request.user)
	return render(request, 'newproject.html',
				{'form': form})

@login_required
def viewproject(request, project_id):
	project = get_object_or_404(Project, pk = project_id)
	if request.user == project.student:
		return render(request, 'viewproject.html',
			{'project': project})
	return HttpResponseRedirect(reverse('studenthome'))

@login_required
def editproject(request, project_id):
	instance = get_object_or_404(Project, pk = project_id)
	if instance.student == request.user:
		form = ProjectForm(request.user, None, instance = instance)
		if request.method == 'POST':
			form = ProjectForm(request.user, request.POST, instance = instance)
			if form.is_valid():
				form.save()
				add_notification("edit", instance)
			return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
		return render(request, 'editproject.html',
		 {'form': form, 'instance': instance})
	return HttpResponseRedirect(reverse('index'))

@login_required
def _upload(request, project_id):
	project = get_object_or_404(Project, pk = project_id)
	if project.student == request.user:
		form = UploadDocumentForm()
		if request.method == "POST":
			form = UploadDocumentForm(request.POST, request.FILES)
			if form.is_valid():
				Document.objects.create(document=request.FILES['document'],
				 project=project, category="submission")
				add_notification("log", project)
				return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
		return render(request, 'upload_document.html', {'form': form, 'id': project_id})
	return HttpResponseRedirect(reverse('index'))

@login_required
def profile(request):
	projects = request.user.projects.all()
	return render(request, 'studentprofile.html', {'projects': projects})

@login_required
def download(request, document_id):
	doc = get_object_or_404(Document, pk=document_id)
	if doc.project.student == request.user:
		return HttpResponseRedirect(doc.document.url)
	return HttpResponseRedirect(reverse('index'))


@login_required
def _logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('studenthome'))