from datetime import date
import json
from urllib import urlencode
from urllib2 import urlopen

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404

from CW_Portal import access_cache, settings, diff_match_patch
from models import Feedback, Project, Document, Category, Bug, NGO, document_type, project_stage, Edit
from forms import ProjectForm, FeedbackForm, UploadDocumentForm, BugsForm, suggest_NGOForm
from supervisor.forms import NewCommentForm
from supervisor.models import Notification, Example, News, Like, Comment, TA, add_notification, notification_type, diff_type, add_diff, Diff

diff_worker = diff_match_patch.diff_match_patch()

def index(request):
    if request.user.is_authenticated():
        if request.user.email in access_cache.get_TA():
            return HttpResponseRedirect(reverse('supervisor_home'))
    return HttpResponseRedirect(reverse('studenthome'))

def first_login(request):
    if request.user.email in access_cache.get_TA():
        return HttpResponseRedirect(reverse('supervisor_home'))
    return HttpResponseRedirect(reverse('studentprofile'))

def home(request):
    if request.user.is_authenticated():
        return render(request, 'studenthome.html',{
            'example_projects': access_cache.get_example_projects(),
            'news': access_cache.get_news(),
            'leaderboard': access_cache.get_leaderboard(),
            'stages': project_stage})
    else:
        return render(request, 'studenthome.html',
            {'news': access_cache.get_news(), 'stages': project_stage})

@login_required
def addproject(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)      
        if form.is_valid():
            project = form.save(student=request.user)
            add_notification(notification_type.NEW_PROJECT, project=project)
            add_diff(diff_type.PROJECT_ADDED, person=request.user, project=project)
            messages.success(request, 'Your project was added successfully.')
            return HttpResponseRedirect(reverse('view_project_NGO', kwargs = {
                                                    'project_id': project.pk}))
        else:
            messages.warning(request, 'There was something wrong in the provided details.')
    else:
        form = ProjectForm()
    return render(request, 'newproject.html',
                {'form': form})

@login_required
def viewproject(request, project_id):
    # don't allow deleted_projects
    project = Project.get_student_viewable_project(project_id)
    project_graph = project.get_project_status_graph()
    project.viewable_edits = [
        {'when': edit.when.strftime("%T [%d-%m-%Y]"),
        'diff_html': [
            {
                'label': x.split("<LABEL_AND_EDIT_SEPARATOR>")[0],
                'content': x.split("<LABEL_AND_EDIT_SEPARATOR>")[1].replace('&para;', '').replace('\r', ''),
            } for x in edit.diff_text.split('<MULTIPLE_FIELDS_SEPARATOR>') if x
        ]} for edit in project.edits.all()
    ]
    if request.user != project.student: raise Http404
    return render(request, 'viewproject.html',
        {'project': project, 'stages': project_stage,
        'project_graph': project_graph})

###################
#Ajaxify
###################
@login_required
def view_project_NGO(request, project_id):
    project = Project.get_student_viewable_project(project_id)
    NGOs = NGO.objects.all()
    if request.user == project.student:
        return render(request, 'view_project_NGO.html',{'project': project, 'NGOs': NGOs})
    return HttpResponseRedirect(reverse('studenthome'))

@login_required
def editproject(request, project_id):
    instance = Project.get_student_viewable_project(project_id)
    if instance.student == request.user:
        form = ProjectForm(None, instance = instance)
        if request.method == 'POST':
            form = ProjectForm(request.POST, instance = instance)

            # get edits
            # fields = instance._meta.get_all_field_names()
            fields = ['title', 'credits', 'schedule_text', 'goals', 'NGO_name', 'NGO_super', 'NGO_super_contact', 'NGO_details']
            differences = [(field, diff_worker.diff_main(str(getattr(instance, field)), str(form.data[field]))) for field in fields]
            differences = [x for x in differences if not (len(x[1]) == 1 and x[1][0][0] == 0)] #keeping only those with diff

            if form.is_valid():
                new_instance = form.save(student=request.user)
                messages.success(request, "Your project details have been succesfully updated.")
                add_diff(diff_type.PROJECT_EDITED, person=request.user, project=new_instance)

                # save edit information
                edit_history = ""
                if differences:
                    for diff in differences:
                        diff_worker.diff_cleanupSemantic(diff[1])
                        _ = '<LABEL_AND_EDIT_SEPARATOR>'.join([str(diff[0]), diff_worker.diff_prettyHtml(diff[1])])
                        edit_history = '<MULTIPLE_FIELDS_SEPARATOR>'.join([_, edit_history])
                    Edit.objects.create(project=new_instance, diff_text=edit_history)

                # add_notification(notification_type.PROJECT_EDITED, project=instance)
                return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
            else:
                messages.warning(request, "There was something wrong in the provided details.")
        return render(request, 'editproject.html',
         {'form': form, 'instance': instance})
    return HttpResponseRedirect(reverse('index'))

@login_required
def _upload(request, project_id):
    max_size = getattr(settings, 'MAXIMUM_UPLOAD_SIZE_ALLOWED', 10)*1024*1024
    project = Project.get_student_viewable_project(project_id)
    if not (request.is_ajax() or request.method == "POST"):
        messages.warning(request, "There was something wrong in the request made")
        return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
    if project.student == request.user:
        form = UploadDocumentForm()
        if request.method == "POST":
            if not request.FILES.get('document', None):
                messages.warning(request, "No file selected for upload")
                return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
            name = request.FILES['document'].name
            form = UploadDocumentForm(request.POST, request.FILES)
            if form.is_valid():
                if int(form.cleaned_data['category']) == document_type.FINAL_REPORT and project.stage == project_stage.TO_BE_VERIFIED:
                    messages.warning(request, "You can't submit the final submission until the supervisor has verified your project.")
                    return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id})) 
                if request.FILES['document']._size > max_size:
                    messages.warning(request, "File size limit exceeded.")
                    return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
                Document.objects.create(document=request.FILES['document'],
                 project=project, category=form.cleaned_data['category'], name=name)
                add_diff(diff_type.DOCUMENT_UPLOADED, person=request.user, project=project, details=name)
                messages.success(request, "Your document was uploaded successfully")
                return HttpResponseRedirect(reverse('viewproject', kwargs = {'project_id': project_id}))
            else:
                messages.warning(request, "There was an error in uploading your file.")
        return render(request, 'upload_document.html', {'form': form, 'id': project_id, 'max_size': max_size})
    return HttpResponseRedirect(reverse('index'))

@login_required
def submitproject(request, project_id):
    project = Project.get_student_viewable_project(project_id)
    if project.student != request.user:
        messages.error(request, "Seriously ?? -_-")
        return HttpResponseRedirect(reverse('index'))
    if not project.is_submittable():
        if project.stage == project_stage.TO_BE_VERIFIED:
            messages.warning(request, "The TA hasn't approved your project yet.")
        elif project.stage == project_stage.SUBMITTED:
            messages.warning(request, "Your request is already under consideration.")
        elif project.stage == project_stage.COMPLETED:
            messages.warning(request, "You've already completed your project.")
        else:
            messages.warning(request, "Please submit a final report before submitting your project.")
        return HttpResponseRedirect(reverse('viewproject', kwargs={'project_id': project_id}))
    project.stage = project_stage.SUBMITTED
    project.save()
    add_diff(diff_type.PROJECT_SUBMITTED, person=request.user, project=project)
    add_notification(noti_type=notification_type.PROJECT_FINISHED, project=project)
    messages.success(request, "Your request has been completed successfully. You'll know the results soon.")
    return HttpResponseRedirect(reverse('viewproject', kwargs={'project_id': project_id}))

@login_required
def link_NGO_project(request, NGO_id, project_id):
    ngo = get_object_or_404(NGO, pk = NGO_id)
    project = Project.get_student_viewable_project(project_id)
    if project.student == request.user:
        project.NGO = ngo
        project.save()
        messages.success(request, "You have linked your project with %s"%ngo.name)
        add_diff(diff_type.PROJECT_EDITED, person=request.user, project=project, details="Link ngo to " + ngo.name)
        return HttpResponseRedirect(reverse('view_project_NGO', 
            kwargs = {'project_id': project_id}))
    return HttpResponseRedirect(reverse('index'))

@login_required
def unlink_NGO_project(request, project_id):
    project = Project.get_student_viewable_project(project_id)
    if project.student == request.user:
        project.NGO = None
        project.save()
        add_diff(diff_type.PROJECT_EDITED, person=request.user, project=project, details="Unliked NGO.")
        messages.success(request, "You have unlinked your project")
        return HttpResponseRedirect(reverse('view_project_NGO', 
            kwargs = {'project_id': project_id}))
    return HttpResponseRedirect(reverse('index'))

@login_required
def profile(request):
    projects = request.user.projects.filter(deleted=False)
    return render(request, 'studentprofile.html', {
        'projects': projects, 'stages': project_stage})

@login_required
def download(request, document_id):
    doc = get_object_or_404(Document, pk=document_id)
    if doc.project.deleted: raise Http404
    if doc.project.student == request.user:
        response = HttpResponse(doc.document)
        response['Content-Disposition'] = 'download; filename=%s' %doc.name
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
# Anyone should view this acccording to requirements put forward
def all_NGOs(request):
    NGOs = NGO.objects.all()
    return render(request, 'all_ngos.html', 
        {'NGOs': NGOs})

@login_required
def suggest_NGO(request):
    if not (request.method == "POST" or request.is_ajax()):
        messages.error(request, "There was an error in the request received.")
        return HttpResponseRedirect(reverse('all_NGO'))
    if request.method == "POST":
        form = suggest_NGOForm(request.POST)
        if form.is_valid():
            add_notification(noti_type=notification_type.NGO_SUGGESTION,
                NGO_name=form.cleaned_data['name'],
                NGO_link=form.cleaned_data['link'],
                NGO_details=form.cleaned_data['details'],
                NGO_sugg_by=request.user)
            messages.success(request, "Thank you for your suggestion. We'll get back to you as soon as possible.")
        else:
            messages.warning(request, "There was something wrong in the provided details.")
        return HttpResponseRedirect(reverse('all_NGO'))

    form = suggest_NGOForm()
    return render(request, 'suggest_ngo.html', {'form': form})

@login_required
def feedback(request, project_id):
    project = Project.get_student_viewable_project(project_id)
    if not project.student == request.user:
        return HttpResponseRedirect(reverse('index'))
    if project.feedback.all():
        messages.info(request, "You've already filled in your feedback.")
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.instance.project = project
            form.save()
            add_diff(diff_type.FEEDBACK_GIVEN, person=request.user, project=project)
            messages.success(request, "Thank you for your feedback.")
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.warning(request, "There was something wrong in the provided details.")
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form, 'id': project_id})

def all_projects_open_to_public_year_select(request):
    years = range(2014, date.today().year + 1)
    return render(request, 'all_projects_open_to_public_year_select.html',
        {'years': years})

def all_projects_open_to_public(request, year):
    projects = Project.objects.filter(date_created__year=year, stage=project_stage.COMPLETED)
    return render(request, 'all_projects_open_to_public.html',
        {'projects': projects})

@login_required
def all_examples(request):
    projects = Example.objects.all()
    return render(request, 'all_examples.html',
        {'projects': projects, 'project_stage': project_stage})

@login_required
def view_example(request, example_id):
    project = get_object_or_404(Example, pk=example_id)
    liked = True if request.user.liked_projects.filter(Q(project=project)) else False
    form = NewCommentForm
    return render(request, 'view_example.html',
        {'project': project, 'liked': liked, 'form': form, 'stages': project_stage})
    
def guidelines(request):
    return render(request, 'guidelines.html')

@login_required
def bugs(request):
    if not (request.method == "POST" or request.is_ajax()):
        messages.warning(request, "There was an error in the request received.")
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        form = BugsForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.user = request.user
            temp.save()
            messages.success(request, "Thank you for your suggestions.")
        else:
            messages.warning("There was some error in the data submitted.")
        return HttpResponseRedirect(reverse('index'))
    form = BugsForm()
    return render(request, "bugs.html", {'form': form})

#handle notifications on deletion

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk = project_id)
    if not project.student == request.user:
        return HttpResponseRedirect(reverse('studenthome'))
    project.deleted = True
    is_example = Example.objects.filter(project=project) 
    if is_example: is_example.delete()
    project.save()
    add_diff(diff_type.PROJECT_DELETED, person=request.user, project=project)
    for noti in project.notification_set.all(): noti.delete()
    messages.info(request, "Project has been deleted")
    return HttpResponseRedirect(reverse('studentprofile'))

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    project = document.project
    doc_name = document.name
    if not project.student == request.user:
        return HttpResponseRedirect(reverse('studenthome'))
    document.delete()
    messages.success(request, "Document has been removed.")
    return HttpResponseRedirect(reverse('viewproject', kwargs={'project_id': project.pk}))

@login_required
def like_project(request, example_id):
    example = get_object_or_404(Example, pk=example_id)
    if request.user.liked_projects.filter(project=example):
        messages.error(request, "You have already liked the project.")
    else:
        Like.objects.create(project=example, liked_by=request.user)
    return HttpResponseRedirect(reverse('view_example', kwargs={'example_id': example_id}))

@login_required
def unlike_project(request, example_id):
    example = get_object_or_404(Example, pk=example_id)
    if not request.user.liked_projects.filter(project=example):
        messages.error(request, "You had not liked the project previously.")
    else:
        like = request.user.liked_projects.get(Q(project=example))
        like.delete()
    return HttpResponseRedirect(reverse('view_example', kwargs={'example_id': example_id}))

@login_required
def add_comment(request, example_id):
    if request.method=="POST":
        project = get_object_or_404(Example, pk=example_id)
        form = NewCommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(commentor=request.user,
                text=form.cleaned_data['text'],
                project=project)
        else:
            liked = True if request.user.liked_projects.filter(Q(project=project)) else False
            return render(request, 'view_example.html',
        {'project': project, 'liked': liked, 'form': form})
    return HttpResponseRedirect(reverse('view_example', kwargs={'example_id': example_id}))

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    example_id = comment.project.pk 
    if comment.commentor != request.user:
        messages.info(request, "It seems to me that it ain't your comment, mistah..")
    else:
        comment.delete()
        messages.info(request, "Comment deleted.")
    return HttpResponseRedirect(reverse('view_example', kwargs={'example_id': example_id}))

def handle404_LnF(request):

    class Item(object):
        def __init__(self, name, location, info):
            self.name = name
            self.location = location
            self.info = info

    url = settings.LnF404_url
    site_id = settings.LnF404_SiteID
    token = settings.LnF404_token
    q = 6

    data = urlencode({
        'id': site_id, 'token': token, 'quantity': q
        })
    request = urlopen(url, data)
    resp = json.loads(request.read())

    items = []
    if resp['success'] == 'true' and resp['quantity'] != 0:
        for i in range(int(resp['quantity'])):
            items.append(Item(
            resp[str(i)]['item-name'],
            resp[str(i)]['location'],
            resp[str(i)]['info'],
            ))
    return render(request, 'LnF404.html',{
                    'items': items})
    # render LnF404.html. Also check if items is empty
