from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.core.urlresolvers import reverse

from supervisor.decorators import supervisor_logged_in, is_int

from studentportal.models import Project

from models import Example

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

@supervisor_logged_in
def example_projects(request):
	projects = Example.objects.all()
	return render(request, 'super_exampleprojects.html', 
		{
			'projects': projects,
		})

@supervisor_logged_in
def add_to_examples(request, project_id):
	project = Project.objects.get(pk = project_id)
	Example.objects.create(project = project)
	return HttpResponseRedirect(reverse('super_viewproject', 
		kwargs={'project_id': project_id}))

@supervisor_logged_in
def remove_from_examples(request, example_project_id):
	example_project = Example.objects.get(pk = example_project_id)
	p_id = example_project.project.id
	example_project.delete()
	return HttpResponseRedirect(reverse('super_viewproject',
		kwargs = {'project_id':p_id}))

@supervisor_logged_in
def submitted_projects(request):
	projects = Project.objects.filter(documents__category__exact='submission',
		stage='ongoing').distinct()
	return render(request, 'super_submittedprojects.html',
		{'projects': projects})

@supervisor_logged_in
def allprojects(request, skip='0'):
	skip = int(skip)
	step = 9999
	# next_temp = skip + step if skip+step < Project.objects.count() else None
	# back_temp = skip - step if skip-step >= 0 else None
	# print skip, step, back_temp
	projects = Project.objects.all()[skip: skip + step]
	return render(request, 'super_allprojects.html',
		{'projects': projects,
		 #'next': next_temp, 'back': back_temp
		 })

@supervisor_logged_in
def basic_search(request):
	if request.method == "POST":
		query = request.POST.get('search_query', None)
		if query:
			if len(query)==7 and is_int(query):
				#full roll number
				query = str(query)[2:]
			projects = Project.objects.filter(student__email__icontains = query)
			return render(request, 'search_results.html',
				{'projects': projects, 'query': query})
	return HttpResponseRedirect(reverse('index'))

@supervisor_logged_in
def complete(request,project_id):
	project = get_object_or_404(Project, pk = project_id)
	project.stage = 'completed'
	project.save()
	#send link for feedback form
	return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project_id}))