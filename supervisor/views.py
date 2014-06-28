from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.core.urlresolvers import reverse

from django.db.models import Q
from supervisor.decorators import supervisor_logged_in, is_int, EmailMessage

from studentportal.models import Project, NGO, Category
from models import Example, AdvanceSearchForm, NewsForm, News, Notification

from CW_Portal import globals

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
	Notification.objects.get(project=project, project__stage='to_be_verified').delete()
	project.stage = "ongoing"
	project.save()
	EmailMessage("Congrats.. now get to work :)","Congratulations, your project has has been verified. Now start working and making a difference", to=[str(project.student.email)])
	globals.noti_refresh = True
	return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id':project.id}))

@supervisor_logged_in
def unverify_project(request, project_id):
	project = Project.objects.get(pk = project_id)
	Notification.objects.create(project=project, noti_type='new')
	project.stage = "to_be_verified"
	project.save()
	EmailMessage("I got bad news :(","It seems that the supervisor has un-approved your project. Contact him to find out the issue", to=[str(project.student.email)])
	globals.noti_refresh = True
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
	EmailMessage("Congrats.. You deserve this :)","Congratulations, your project has has been selected by the admin as an example project. You must have done a mighty fine job. Keep it up.",
	 to=[str(project.student.email)])
	return HttpResponseRedirect(reverse('super_viewproject', 
		kwargs={'project_id': project_id}))

@supervisor_logged_in
def remove_from_examples(request, example_project_id):
	example_project = Example.objects.get(pk = example_project_id)
	p_id = example_project.project.id
	example_project.delete()
	EmailMessage("Thank you :)","Your project has has been removed by the admin from the example project. Thank you for contributing to the community. Keep it up.",
	 to=[str(Project.objects.get(pk=p_id).student.email)])
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
	EmailMessage("Congrats.. you did it :)","Congratulations, your completed project has has been accepted by the admin. Thanks for giving back to the community. Keep it up.",
	 to=[str(project.student.email)])
	#send link for feedback form
	return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project_id}))

@supervisor_logged_in
def advance_search(request):
	if request.method == "POST":
		form = AdvanceSearchForm(request.POST)
		if form.is_valid():
			projects = Project.objects.all()
			if form.cleaned_data['stage'] != 'all':
				projects = projects.filter(stage=form.cleaned_data['stage'])
			if form.cleaned_data['project_title']:
				projects = projects.filter(title__icontains=form.cleaned_data['project_title'])
			if form.cleaned_data['NGO_name']:
				projects = projects.filter(title__icontains=form.cleaned_data['NGO_name'])
			if form.cleaned_data['proposal_year']:
				date = int(form.cleaned_data['proposal_year'])
				projects = projects.filter(date_created__year=date)
			if form.cleaned_data['email']:
				projects = projects.filter(student__email__icontains=form.cleaned_data['email'])
			if form.cleaned_data['roll_no']:
				roll_no = str(form.cleaned_data['roll_no'])
				if len(roll_no) > 5:
					roll_no = roll_no[-5:]
				projects = projects.filter(student__email__icontains=roll_no)
			if form.cleaned_data['name']:
				name = form.cleaned_data['name']
				# projects = projects.filter(Q(student__first_name__icontains=name) | 
				# 	Q(student__last_name__icontains=name))
				# projects = projects.filter(student__get_full_name__icontains=name)
				#LC is the way to go
				projects = [project for project in projects if ''.join(name.split()).lower() in \
				''.join([project.student.first_name, project.student.last_name]).lower()]
			return render(request, 'advance_search_results.html',
				{'projects': projects})
	else:
		form = AdvanceSearchForm()
	return render(request, 'advance_search.html',
		{'form': form})

@supervisor_logged_in
def add_news(request):
	if request.method == "POST":
		form = NewsForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('all_news'))
	else:
		form = NewsForm
	return render(request, 'add_news.html',
		{'form': form})

#should i add or not..??
def view_news(request, news_id):
	news = get_object_or_404(News, pk=news_id)
	return render(request, 'view_news.html', {'news': news})

@supervisor_logged_in
def all_NGO(request):
	NGOs = NGO.objects.all()
	return render(request, 'super_all_ngo.html', {'NGOs': NGOs})

@supervisor_logged_in
def view_NGO(request, NGO_id):
	ngo = get_object_or_404(NGO, pk = NGO_id)
	return render(request, 'super_view_ngo.html', {'NGO': ngo})

@supervisor_logged_in
def all_news(request):
	news = News.objects.all()
	return render(request, 'all_news.html', {'news': news})

@supervisor_logged_in
def newlogs(request):
	notifications = Notification.objects.filter(noti_type='log').distinct()
	return render(request, 'newlogs.html', {'notifications': notifications})

@supervisor_logged_in
def suggested_NGOs(request):
	notifications = Notification.objects.filter(noti_type='suggest').distinct()
	return render(request, 'suggested_NGOs.html', {'notifications': notifications})	

@supervisor_logged_in
def accept_NGO(request, noti_id):
	noti = get_object_or_404(Notification, pk = noti_id)
	NGO.objects.create(name=noti.NGO_name,
		link=noti.NGO_link,
		details=noti.NGO_details,
		category=Category.objects.last())
	noti.delete()
	globals.noti_refresh = True
	EmailMessage("Thank you :)","We have added the NGO you suggested as a trusted NGO..",
	 to=[str(noti.NGO_sugg_by)])
	return HttpResponseRedirect(reverse('super_suggested_ngos'))

@supervisor_logged_in
def reject_NGO(request, noti_id):
	noti = get_object_or_404(Notification, pk=noti_id)
	noti.delete()
	globals.noti_refresh = True
	EmailMessage("Thank you but sorry :|","We have reviewed your suggestion for the NGO but as of now have to reject it. But thank you for your suggestion",
	 to=[str(noti.NGO_sugg_by)])
	return HttpResponseRedirect(reverse('super_suggested_ngos'))