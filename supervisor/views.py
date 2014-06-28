from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.core.urlresolvers import reverse

from supervisor.decorators import supervisor_logged_in

from studentportal.models import Project

@supervisor_logged_in
def home(request):
	recent_projects = Project.objects.extra(order_by=['-date_created'])[:10]
	return render(request, 'supervisorhome.html', {'recent_projects': recent_projects})

@supervisor_logged_in
def _logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

@supervisor_logged_in
def unverified_projects(request):
	projects = Project.objects.filter(stage="to_be_verified")
	print projects
	return render(request, 'unverified_projects.html',
		{'projects': projects})

@supervisor_logged_in
def verify_project(request, project_id):
	project = Project.objects.get(pk = project_id)
	project.stage = "ongoing"
	project.save()
	return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id':project.id}))

@supervisor_logged_in
def unverify_project(request, project_id):
	project = Project.objects.get(pk = project_id)
	project.stage = "to_be_verified"
	project.save()
	return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id':project.id}))

@supervisor_logged_in
def ongoing_projects(request, skip='0'):
	skip = int(skip)
	projects = Project.objects.filter(stage='ongoing')[skip:skip+20]
	return render(request, 'ongoing_projects.html', 
		{'projects': projects})

@supervisor_logged_in
def viewproject(request, project_id):
	project = Project.objects.get(pk = project_id)
	return render(request, 'super_viewproject.html', 
		{'project': project})