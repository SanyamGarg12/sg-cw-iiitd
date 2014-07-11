from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from PrivateData import SUPERVISOR_EMAIL

from supervisor.models import Notification, Example, News

from supervisor.decorators import RenderFeedbackExperiencePieChart, RenderProjectToMonthDistribution, RenderProjectCategoryPieChart

from models import ProjectForm, Project, Document, UploadDocumentForm, NGO, suggest_NGOForm
from models import Feedback, FeedbackForm, Category, BugsForm, Bugs

from django.db.models.signals import pre_save

from django.contrib import messages

from django.conf import settings

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter

def add_notification(noti_type, project):
	Notification.objects.create(noti_type=noti_type, project=project)

def index(request):
	if request.user.is_authenticated():
		if request.user.email in SUPERVISOR_EMAIL:
			return HttpResponseRedirect(reverse('supervisor_home'))
	return HttpResponseRedirect(reverse('studenthome'))

def home(request):
	news = News.objects.all().order_by('-date_created')[:5]
	if request.user.is_authenticated():
		example_projects = Example.objects.all()[:6]
		return render(request, 'studenthome.html', 
		{'example_projects': example_projects, 'news': news})
	else:
		return render(request, 'studenthome.html',
			{'news': news,})

class DomainLoginAdapter(DefaultSocialAccountAdapter):
	def pre_social_login(self, request, sociallogin):
		u = sociallogin.account.user
		if u.email.split('@')[1] not in settings.ALLOWED_DOMAINS:
			logout(request)
			messages.error(request, "Sorry. You must login through a IIIT-D account only.")
			raise ImmediateHttpResponse(home(request))

class NoMessagesLoginAdapter(DefaultAccountAdapter):
	def add_message(self, request, level, message_template,
                    message_context={}, extra_tags=''):
		pass

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
			RenderProjectToMonthDistribution().start()
			RenderProjectCategoryPieChart().start()
			messages.success(request, 'Your project was added successfully.')
			return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': Project.objects.last().id}))
		else:
			messages.warning(request, 'There was something wrong in the provided details.')
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
def view_project_NGO(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	NGOs = NGO.objects.all()
	if request.user == project.student:
		return render(request, 'view_project_NGO.html',{'project': project, 'NGOs': NGOs})
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
				RenderProjectCategoryPieChart().start()
				messages.success(request, "Your project details have been succesfully updated.")
				return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
			else:
				messages.warning(request, "There was something wrong in the provided details.")
		return render(request, 'editproject.html',
		 {'form': form, 'instance': instance})
	return HttpResponseRedirect(reverse('index'))

@login_required
def _upload(request, project_id):
	project = get_object_or_404(Project, pk = project_id)
	if project.student == request.user:
		form = UploadDocumentForm()
		if request.method == "POST":
			name = request.FILES['document'].name
			form = UploadDocumentForm(request.POST, request.FILES)
			if form.is_valid():
				if form.cleaned_data['category'] == 'submission' and project.stage == 'to_be_verified':
					messages.warning(request, "You can't submit the final submission until the supervisor has verified your project.")
					return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id})) 
				Document.objects.create(document=request.FILES['document'],
				 project=project, category=form.cleaned_data['category'], name=name)
				if form.cleaned_data['category'] == 'submission':
					add_notification("finish", project)
				messages.success(request, "Your document was uploaded successfully")
				return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
			else:
				messages.warning(request, "There was an error in uploading your file.")
		return render(request, 'upload_document.html', {'form': form, 'id': project_id})
	return HttpResponseRedirect(reverse('index'))

@login_required
def link_NGO_project(request, NGO_id, project_id):
	ngo = get_object_or_404(NGO, pk = NGO_id)
	project = get_object_or_404(Project, pk = project_id)
	if project.student == request.user:
		project.NGO = ngo
		project.save()
		messages.success(request, "You have linked your project with %s"%ngo.name)
		return HttpResponseRedirect(reverse('view_project_NGO', 
			kwargs = {'project_id': project_id}))
	return HttpResponseRedirect(reverse('index'))

@login_required
def unlink_NGO_project(request, project_id):
	project = get_object_or_404(Project, pk = project_id)
	if project.student == request.user:
		project.NGO = None
		project.save()
		messages.success(request, "You have unlinked your project")
		return HttpResponseRedirect(reverse('view_project_NGO', 
			kwargs = {'project_id': project_id}))
	return HttpResponseRedirect(reverse('index'))

@login_required
def profile(request):
	projects = request.user.projects.all()
	return render(request, 'studentprofile.html', {'projects': projects})

@login_required
def download(request, document_id):
	doc = get_object_or_404(Document, pk=document_id)
	if doc.project.student == request.user:
		response = HttpResponse(doc.document)
		response['Content-Disposition'] = 'attachment; filename=%s' %doc.name
		return response
	return HttpResponseRedirect(reverse('index'))


@login_required
def _logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('studenthome'))

# @login_required
def view_news(request, news_id='0'):
	single = True
	if news_id == '0':
		news = News.objects.all()
		single = False
	else:
		news = get_list_or_404(News, pk=news_id)
	return render(request, 'view_news.html', {
		'news': news, 'single': single
		})

#I am not checking for login on purpose.
# Anyone should view this acccording to requirements pur forward
def all_NGOs(request):
	NGOs = NGO.objects.all()
	return render(request, 'all_ngos.html', 
		{'NGOs': NGOs})

@login_required
def suggest_NGO(request):
	if request.method == "POST":
		form = suggest_NGOForm(request.POST)
		if form.is_valid():
			Notification.objects.create(noti_type='suggest',
				NGO_name=form.cleaned_data['name'],
				NGO_link=form.cleaned_data['link'],
				NGO_details=form.cleaned_data['details'],
				NGO_sugg_by=str(request.user.email))
			messages.success(request, "Thank you for your suggestion. We'll get back to you as soon as possible.")
			return HttpResponseRedirect(reverse('all_NGO'))
		else:
			messages.warning(request, "There was something wrong in the provided details.")
	else:
		form = suggest_NGOForm()
	return render(request, 'suggest_ngo.html', 
	{'form': form})

@login_required
def feedback(request, project_id):
	project = get_object_or_404(Project, pk = project_id)
	if not project.student == request.user:
		return HttpResponseRedirect(reverse('index'))
	if request.method == 'POST':
		form = FeedbackForm(request.POST)
		if form.is_valid():
			form.instance.project = project
			form.save()
			RenderFeedbackExperiencePieChart().start()
			messages.success(request, "Thank you for your feedback.")
			return HttpResponseRedirect(reverse('index'))
		else:
			messages.warning(request, "There was something wrong in the provided details.")
	else:
		form = FeedbackForm()
	return render(request, 'feedback.html', {'form': form, 'id': project_id})

def all_projects_open_to_public_year_select(request):
	from datetime import date
	years = range(2014, date.today().year + 1)
	return render(request, 'all_projects_open_to_public_year_select.html',
		{'years': years})

def all_projects_open_to_public(request, year):
	projects = Project.objects.filter(date_created__year=year, stage='completed')
	return render(request, 'all_projects_open_to_public.html',
		{'projects': projects})

@login_required
def all_examples(request):
	projects = Example.objects.all()
	return render(request, 'all_examples.html',
		{'projects': projects})

@login_required
def view_example(request, example_id):
	project = get_object_or_404(Example, pk=example_id)
	return render(request, 'view_example.html',
		{'project': project})
def guidlines(request):
	return render(request, 'guidlines.html')

@login_required
def bugs(request):
	if request.method == "POST":
		form = BugsForm(request.POST)
		if form.is_valid():
			form.save()
			a = Bugs.objects.last()
			a.user = request.user
			a.save()
			messages.success(request, "Thank you for your suggestions")
		return HttpResponseRedirect(reverse('index'))
	else:
		form = BugsForm()
	return render(request, "bugs.html", {'form': form})