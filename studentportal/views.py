from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from PrivateData import *

from models import ProjectForm, Project

from django.db.models.signals import pre_save

def index(request):
	#if user is not admin
	return HttpResponseRedirect(reverse('studenthome'))

def home(request):
	popular_projects = Project.objects.all()[:10]
	if request.user.is_authenticated():
		return render(request, 'studenthome.html', 
		{'popular_projects': popular_projects})
	else:
		return render(request, 'core.html',
			{'popular_projects': popular_projects,})
	
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
			return HttpResponseRedirect(reverse('studenthome'))
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
		return render(request, 'editproject.html',
		 {'form': form, 'instance': instance})
	return HttpResponseRedirect(reverse('index'))


@login_required
def _logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('studenthome'))
