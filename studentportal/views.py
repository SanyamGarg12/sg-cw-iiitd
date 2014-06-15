from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse

from models import ProjectForm, Project

def index(request):
	#if user is not admin
	return HttpResponseRedirect(reverse('studenthome'))

def home(request):
	a = Project.objects.all()[:5]
	return render(request, 'studenthome.html', 
		{'recent_projects': a})

def add(request):
	if request.method == 'POST':
		form = ProjectForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('studenthome'))
	else:
		form = ProjectForm()
	return render(request, 'newproject.html',
				{'form': form})
