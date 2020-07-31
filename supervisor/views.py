import datetime
import mimetypes
import os

import xlwt
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from CW_Portal import settings, access_cache
from studentportal.models import Project, NGO, Category, Document, project_stage
from supervisor.communication import send_email, send_email_to_all
from supervisor.decorators import supervisor_logged_in
from supervisor.forms import AdvanceSearchForm, NewsForm, NewCategoryForm, NewNGOForm, EmailProjectForm, TAForm, \
	ReportForm
from supervisor.models import Example, News, Notification, TA, diff_type, add_diff, add_notification
from supervisor.models import notification_type as nt
from supervisor.validators import is_int
from django.core.mail import send_mail


@supervisor_logged_in
def home(request):
    recent_projects = access_cache.get('projects_homepage')
    return render(request, 'supervisorhome.html', {'recent_projects': recent_projects,
                                                   'statistics_folder_name': getattr(settings,
                                                                                     "STATISTICS_FOLDER_NAME")})


@supervisor_logged_in
def _logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@supervisor_logged_in
def unverified_projects(request):
    projects = Project.objects.filter(stage=project_stage.TO_BE_VERIFIED)
    return render(request, 'unverified_projects.html',
                  {'projects': projects})


@supervisor_logged_in
def verify_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    Notification.objects.filter(project=project, noti_type=nt.NEW_PROJECT).delete()
    project.stage = project_stage.ONGOING
    project.save()
    add_diff(diff_type.PROJECT_VERIFIED, person=request.user, project=project)
    messages.success(request, "You have verified the project %s." % project.title)
    send_email("Congrats.. now get to work :)",
               "Congratulations, your project has has been verified. Now start working and making a difference",
               to=[str(project.student.email)])
    return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project.id}))


@supervisor_logged_in
def unverify_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    add_notification(noti_type=nt.NEW_PROJECT, project=project)
    project.stage = project_stage.TO_BE_VERIFIED
    project.save()
    add_diff(diff_type.PROJECT_UNVERIFIED, person=request.user, project=project)
    messages.warning(request, "You have unverified the project %s." % project.title)
    send_email("I got bad news :(",
               "It seems that the supervisor has un-approved your project. Contact him to find out the issue",
               to=[str(project.student.email)])
    return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project.id}))


@supervisor_logged_in
def ongoing_projects(request):
    projects = Project.objects.filter(stage=project_stage.ONGOING)
    return render(request, 'ongoing_projects.html',
                  {'projects': projects})


@supervisor_logged_in
def viewproject(request, project_id):
    # allow to see deleted projects.
    project = get_object_or_404(Project.all_projects, pk=project_id)
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
    return render(request, 'super_viewproject.html',
                  {'project': project, 'project_stage': project_stage,
                   'project_graph': project_graph})


@supervisor_logged_in
def example_projects(request):
    projects = Example.objects.all()
    return render(request, 'super_exampleprojects.html',
                  {
                      'projects': projects,
                  })


@supervisor_logged_in
def add_to_examples(request, project_id):
    project = Project.objects.get(pk=project_id)
    Example.objects.create(project=project)
    add_diff(diff_type.ADDED_AS_EXAMPLE, person=request.user, project=project)
    messages.success(request, "You have marked the project '%s' as an example project." % project.title)
    send_email("Congrats.. You deserve this :)",
               "Congratulations, your project has has been selected by the admin as an example project. You must have done a mighty fine job. Keep it up.",
               to=[str(project.student.email)])
    return HttpResponseRedirect(reverse('super_viewproject',
                                        kwargs={'project_id': project_id}))


@supervisor_logged_in
def toggle_presented_project(request, project_id):
    project = get_object_or_404(Project.all_projects, pk=project_id)
    project.presented = not project.presented
    project.save()
    add_diff(diff_type.PROJECT_PRESENTED, person=request.user,
             project=project, details="New value set to %s" % project.presented)
    messages.success(request,
                     "You have changed whether the student has presented his project to %s." % project.presented)
    return HttpResponseRedirect(reverse('super_viewproject',
                                        kwargs={'project_id': project_id}))


@supervisor_logged_in
def remove_from_examples(request, example_project_id):
    example_project = Example.objects.get(pk=example_project_id)
    p_id = example_project.project.id
    example_project.delete()
    add_diff(diff_type.REMOVED_AS_EXAMPLE, person=request.user, project=get_object_or_404(Project, pk=p_id))
    messages.warning(request, "You have unmarked the project as an example project.")
    send_email("Thank you :)",
               "Your project has has been removed by the admin from the example project. Thank you for contributing to the community. Keep it up.",
               to=[str(Project.objects.get(pk=p_id).student.email)])
    return HttpResponseRedirect(reverse('super_viewproject',
                                        kwargs={'project_id': p_id}))


@supervisor_logged_in
def submitted_projects(request):
    projects = Project.objects.filter(stage=project_stage.SUBMITTED)
    return render(request, 'super_submittedprojects.html',
                  {'projects': projects})


@supervisor_logged_in
def allprojects(request):
    form = ReportForm()
    paginator = Paginator(Project.all_projects.all(), 10, orphans=5)

    page = request.GET.get('page', None)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    return render(request, 'super_allprojects.html',
                  {'projects': projects,
                   'form': form,
                   })


@supervisor_logged_in
def basic_search(request):
    if request.method == "POST":
        query = request.POST.get('search_query', None)
        if query:
            if len(query) == 7 and is_int(query):
                # full roll number
                query = str(query)[2:]
            projects = Project.all_projects.filter(student__email__icontains=query)
            return render(request, 'search_results.html',
                          {'projects': projects, 'query': query})
    return HttpResponseRedirect(reverse('index'))


@supervisor_logged_in
def complete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    Notification.objects.filter(project=project).delete()
    project.stage = project_stage.COMPLETED
    project.finish_date = timezone.now()
    project.save()
    add_diff(diff_type.PROJECT_COMPLETED, person=request.user, project=project)
    messages.success(request, "You have marked the Community Work project as completed and finished.")
    send_email("Congrats.. you did it :)",
               "Congratulations, your completed project has has been accepted by the admin.Please fill the feedback at %(feedback_link)s. \n\nThanks for giving back to the community. Keep it up." % {
                   'feedback_link': request.build_absolute_uri(reverse('feedback', kwargs={'project_id': project.pk}))
               },
               to=[str(project.student.email)])
    # send link for feedback form
    return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project_id}))


@supervisor_logged_in
def advance_search(request):
    if not (request.method == "POST" or request.is_ajax()):
        messages.warning(request, "There's something wrong with the request you sent.")
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        form = AdvanceSearchForm(request.POST)
        if form.is_valid():
            # this will speed up querying a lot
            if form.cleaned_data['category']:
                projects = form.cleaned_data['category'].projects.all()
            else:
                projects = Project.all_projects.all()
            if form.cleaned_data['stage'] != '0':
                projects = projects.filter(stage=form.cleaned_data['stage'])
            if form.cleaned_data['project_title']:
                projects = projects.filter(title__icontains=form.cleaned_data['project_title'])
            if form.cleaned_data['NGO_name']:
                projects = projects.filter(NGO_name__icontains=form.cleaned_data['NGO_name'])
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
                #   Q(student__last_name__icontains=name))
                # projects = projects.filter(student__get_full_name__icontains=name)
                # LC is the way to go
                projects = [project for project in projects if ''.join(name.split()).lower() in \
                            ''.join([project.student.first_name, project.student.last_name]).lower()]
            return render(request, 'advance_search_results.html',
                          {'projects': projects})
        messages.warning(request, "The data provided was wrong somehow.")
        return HttpResponseRedirect(reverse('index'))
    form = AdvanceSearchForm()
    return render(request, 'advance_search.html',
                  {'form': form})


@supervisor_logged_in
def add_news(request):
    if not (request.method == "POST" or request.is_ajax()):
        messages.warning(request, "There was something funny about the request the server received.")
        return HttpResponseRedirect(reverse('all_news'))
    if (request.method == "POST"):
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            if form.cleaned_data['priority'] == 'False':
                send_email_to_all(str(form.cleaned_data['content']))
            messages.success(request, 'News has been posted.')
            return HttpResponseRedirect(reverse('all_news'))
        messages.warning(request, "The new post data was incomplete or incorrect.")
        return HttpResponseRedirect(reverse('all_news'))
    form = NewsForm()
    return render(request, 'add_news.html',
                  {'form': form})


@supervisor_logged_in
def view_news(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    return render(request, 'super_view_news.html', {'news': news})


@supervisor_logged_in
def all_NGO(request):
    NGOs = NGO.objects.all()
    form = NewNGOForm()
    return render(request, 'super_all_ngo.html',
                  {'NGOs': NGOs, 'form': form})


@supervisor_logged_in
def view_NGO(request, NGO_id):
    ngo = get_object_or_404(NGO, pk=NGO_id)
    form = NewNGOForm(initial={'name': ngo.name, 'link': ngo.link, 'details': ngo.details})
    return render(request, 'super_view_ngo.html', {'NGO': ngo, 'form': form})


@supervisor_logged_in
def all_news(request):
    news = News.objects.all()
    return render(request, 'all_news.html', {'news': news})


@supervisor_logged_in
def suggested_NGOs(request):
    notifications = Notification.objects.filter(noti_type=nt.NGO_SUGGESTION).distinct()
    return render(request, 'suggested_NGOs.html', {'notifications': notifications})


@supervisor_logged_in
def accept_NGO(request, noti_id):
    noti = get_object_or_404(Notification, pk=noti_id)
    NGO.objects.create(name=noti.NGO_name,
                       link=noti.NGO_link,
                       details=noti.NGO_details,
                       category=Category.objects.last())
    send_email("Thank you :)", "We have added the NGO you suggested as a trusted NGO..",
               to=[str(noti.NGO_sugg_by)])
    messages.success(request, "%s is now a trusted NGO." % noti.NGO_name)
    noti.delete()
    return HttpResponseRedirect(reverse('super_suggested_ngos'))


@supervisor_logged_in
def reject_NGO(request, noti_id):
    noti = get_object_or_404(Notification, pk=noti_id)
    messages.info(request, "You have rejected the suggestion of adding %s as a trusted NGO." % noti.NGO_name)
    noti.delete()
    send_email("Thank you but sorry :|",
               "We have reviewed your suggestion for the NGO but as of now have to reject it. But thank you for your suggestion",
               to=[str(noti.NGO_sugg_by)])
    return HttpResponseRedirect(reverse('super_suggested_ngos'))


@supervisor_logged_in
def remove_NGO(request, ngo_id):
    ngo = get_object_or_404(NGO, pk=ngo_id)
    messages.info(request, "%s has been deleted." % ngo.name)
    ngo.delete()
    return HttpResponseRedirect(reverse('super_all_NGO'))


@supervisor_logged_in
def download(request, doc_id):
    doc = get_object_or_404(Document, pk=doc_id)
    content_type = mimetypes.guess_type(doc.name)[0]
    if content_type is not None:
        response = HttpResponse(doc.document,
                                content_type=content_type)
        response['Content-Disposition'] = 'inline; filename=%s' % doc.name
    else:
        response = HttpResponse(doc.document)
        response['Content-Disposition'] = 'download; filename=%s' % doc.name
    return response


@supervisor_logged_in
def view_student(request, user_id):
    student = get_object_or_404(User, pk=user_id)
    return render(request, 'super_viewuser.html',
                  {'student': student, 'projects': Project.all_projects.filter(student=student)})


@supervisor_logged_in
def all_categories(request):
    categories = Category.objects.all()
    form = NewCategoryForm()
    return render(request, 'super_allcategories.html',
                  {'categories': categories, 'form': form})


@supervisor_logged_in
def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    form = NewCategoryForm(initial={'name': category.name, 'description': category.description})
    return render(request, 'super_category.html',
                  {'category': category, 'form': form})


@supervisor_logged_in
def add_category(request):
    if request.method == "POST":
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            Category.objects.create(name=form.cleaned_data['name'],
                                    description=form.cleaned_data['description'])
            messages.success(request, "%s has been added as a new category." % form.cleaned_data['name'])
            return HttpResponseRedirect(reverse('super_allcategories'))
        else:
            messages.warning(request, "There was something wrong in the data you entered.")
            categories = Category.objects.all()
            return render(request, 'super_allcategories.html',
                          {'form': form, "categories": categories})
    else:
        return HttpResponseRedirect(reverse('super_allcategories'))


@supervisor_logged_in
def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    name = category.name
    if str(name).lower() == 'other':
        messages.warning(request, "'Other' is the defaiult category. It cannot be deleted.")
        return HttpResponseRedirect(reverse('super_allcategories'))
    category.delete()
    messages.success(request, "%s was deleted" % name)
    return HttpResponseRedirect(reverse('super_allcategories'))


@supervisor_logged_in
def add_NGO(request):
    if request.method == "POST":
        form = NewNGOForm(request.POST)
        if form.is_valid():
            NGO.objects.create(name=form.cleaned_data['name'],
                               link=form.cleaned_data['link'],
                               details=form.cleaned_data['details'])
            messages.success(request, "NGO has been created successfully.")
        else:
            NGOs = NGO.objects.all()
            messages.warning(request, "The data entered was incorrect.")
            return render(request, 'super_all_ngo.html',
                          {'NGOs': NGOs, 'form': form})
    return HttpResponseRedirect(reverse('super_all_NGO'))


@supervisor_logged_in
def delete_news(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    news.delete()
    messages.success(request, "The news post has been deleted successfully.")
    return HttpResponseRedirect(reverse('all_news'))


@supervisor_logged_in
def email_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = EmailProjectForm(request.POST)
        if form.is_valid():
            text = '\n\n'.join([form.cleaned_data['body'],
                                "Please Note: This mail is generated via the SG-CW-portal. For any further communication regarding the above mentioned issue(s), please reply to this mail, unless explicitly asked to create a new email thread, for proper redressal."])
            send_mail("CW Project '%s' " % project.title, text, "sgcw@iiitd.ac.in", [form.cleaned_data['to']])
            # send_email("CW Project '%s' " % project.title, text, to=[form.cleaned_data['to']])
            messages.success(request, "E-mail sent.")
            add_diff(diff_type.EMAIL_SENT, person=request.user, project=project, details=form.cleaned_data['body'])
            return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project.id}))
    else:
        form = EmailProjectForm(
            {'to': str(project.student.email), 'body': "This is regarding your project '%s'." % project.title
             })
    return render(request, 'email.html', {'form': form, 'project_id': project_id})


@supervisor_logged_in
def deleteproject(request, project_id):
    project = get_object_or_404(Project.all_projects, pk=project_id)
    project.deleted = True
    is_example = Example.objects.filter(project=project)
    if is_example: is_example.delete()
    project.save()
    for noti in project.notification_set.all(): noti.delete()
    add_diff(diff_type.PROJECT_DELETED, person=request.user, project=project)
    messages.info(request, "Project has been marked as deleted")
    return HttpResponseRedirect(reverse('index'))


@supervisor_logged_in
def force_delete_project(request, project_id):
    project = get_object_or_404(Project.all_projects, pk=project_id)
    title = project.title
    project.delete()
    add_diff(diff_type.PROJECT_DELETED, person=request.user, details="Force deleted %s." % title)
    messages.info(request, "Project has been irrevocably deleted")
    return HttpResponseRedirect(reverse('index'))


@supervisor_logged_in
def revert_delete_project(request, project_id):
    project = get_object_or_404(Project.all_projects, pk=project_id)
    project.deleted = False
    project.save()
    add_diff(diff_type.PROJECT_DELETED, person=request.user, project=project, details="Undeleted.")
    messages.info(request, "Project has been brought back from the dead")
    return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project.pk}))


@supervisor_logged_in
def update_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method != "POST":
        messages.info(request, "Wrong html request method.")
        return HttpResponseRedirect(reverse('super_allcategories'))
    form = NewCategoryForm(request.POST)
    if form.is_valid():
        category.name = form.cleaned_data['name']
        category.description = form.cleaned_data['description']
        category.save()
        messages.success(request, "Category: %s updated successfuly" % category.name)
        return HttpResponseRedirect(reverse('super_viewcategory', kwargs={'category_id': category_id}))
    else:
        messages.error(request, "There was an error in the updated data.")
        return HttpResponseRedirect(reverse('super_viewcategory', kwargs={'category_id': category_id}))


@supervisor_logged_in
def update_ngo(request, NGO_id):
    ngo = get_object_or_404(NGO, pk=NGO_id)
    if request.method != "POST":
        messages.info(request, "Wrong html request method.")
        return HttpResponseRedirect(reverse('super_all_ngo'))
    form = NewNGOForm(request.POST)
    if form.is_valid():
        ngo.name = form.cleaned_data['name']
        ngo.link = form.cleaned_data['link']
        ngo.details = form.cleaned_data['details']
        ngo.save()
        messages.success(request, "NGO: %s updated successfuly" % ngo.name)
        return HttpResponseRedirect(reverse('super_view_ngo', kwargs={'NGO_id': NGO_id}))
    else:
        messages.error(request, "There was an error in the updated data.")
        return HttpResponseRedirect(reverse('super_view_ngo', kwargs={'NGO_id': NGO_id}))


@supervisor_logged_in
def change_TA(request, TA_id='-1'):
    if eval(TA_id) != -1:
        ta = get_object_or_404(TA, pk=TA_id)
        if ta.instructor and not TA.objects.get(email=request.user.email).instructor:
            messages.info(request, ''.join(
                [ta.email, " can't be removed as the person is an instructor. Contact the admin to remove this."]))
        else:
            ta.delete()
            add_diff(diff_type.REMOVE_TA, person=request.user, details=ta.email)
            messages.success(request, "TA deleted successfully.")
            if request.user.email == ta.email:
                return HttpResponseRedirect(reverse('logout'))
        return HttpResponseRedirect(reverse('TA'))
    tas = TA.objects.all()
    form = TAForm()
    if request.method == "POST":
        form = TAForm(request.POST)
        if form.is_valid():
            ta = form.save()
            messages.success(request, "TA added successfully.")
            add_diff(diff_type.ADD_TA, person=request.user, details=ta.email)
            return HttpResponseRedirect(reverse('TA'))
        messages.error(request, "There was something wrong in the email provided.")
    return render(request, 'TA.html', {'form': form, 'tas': tas})

# TODO fix this
@supervisor_logged_in
def generateReport(request):
    BASE_DIR = getattr(settings, "BASE_DIR")

    months = int(request.POST['date'])

    projects = Project.objects.filter(~Q(stage=project_stage.TO_BE_VERIFIED))
    projects = projects.filter(
        Q(finish_date__gte=datetime.datetime.now() - datetime.timedelta(months * 31)) |
        Q(finish_date=None))  # for incomplete projects

    report = xlwt.Workbook(encoding="utf-8")

    completed_sheet = report.add_sheet("Completed CW Projects")
    ongoing_sheet = report.add_sheet("Ongoing CW Projects")

    headings = [
        "Name",
        "Batch",
        "Roll number",
        "Email",
        "NGO",
        "Title",
        "Started on",
        "Presented"
    ]
    for (index, h) in enumerate(headings):
        ongoing_sheet.write(0, index, h)
        completed_sheet.write(0, index, h)

    completed_projects_row = 0
    ongoing_projects_row = 0
    for project in projects:
        if project.stage == project_stage.COMPLETED:
            sheet = completed_sheet
            completed_projects_row += 1
            row = completed_projects_row
        else:  # for both SUBMITTED as well as ONGOING
            sheet = ongoing_sheet
            ongoing_projects_row += 1
            row = ongoing_projects_row

        for col, x in enumerate([
            ' '.join([project.student.first_name, project.student.last_name]),
            project.get_batch(),
            project.get_rollno(),
            project.student.email,
            project.get_NGO(),
            project.title,
            project.date_created.strftime('%d-%m-%Y'),
            "%s" % project.presented
        ]):
            sheet.write(row, col, x)

    report.save(os.path.join(BASE_DIR, 'report.csv'))
    report = open(os.path.join(BASE_DIR, 'report.csv'), 'r')
    response = StreamingHttpResponse(report)
    response['Content-Disposition'] = 'download; filename=Report.csv'
    return response


@supervisor_logged_in
def get_project_logs(request, project_id):
    project = get_object_or_404(Project.all_projects, pk=project_id)
    diffs = project.diff.all()
    return render(request, 'super_project_log.html', {
        'project': project, 'diffs': diffs})


@supervisor_logged_in
def get_TA_logs(request, ta_id):
    email = get_object_or_404(TA, pk=ta_id).email
    ta = User.objects.filter(email=email)
    if ta:
        ta = ta[0]
    else:
        messages.warning(request, "This TA has never logged in till now.")
        return HttpResponseRedirect(reverse('TA'))
    if not request.user.email == email:
        if not TA.objects.get(email=request.user.email).instructor:
            messages.warning(request, "You don't have permission to view these logs.")
            return HttpResponseRedirect(reverse('index'))
    diffs = ta.diff.all()
    return render(request, 'super_ta_log.html', {
        'ta': ta, 'diffs': diffs})
