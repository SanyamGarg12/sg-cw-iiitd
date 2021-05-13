import datetime
import logging
import mimetypes
import os
import sys

import xlwt
from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from CW_Portal import settings, access_cache
from studentportal.models import Project, NGO, Category, Document, project_stage, _project_stage_mapping, Semester
from supervisor.communication import send_email_to_all
from supervisor.decorators import supervisor_logged_in
from supervisor.forms import AdvanceSearchForm, NewsForm, NewCategoryForm, NewNGOForm, EmailProjectForm, TAForm, \
    ReportForm, SemesterForm, SemesterDeletionForm
from supervisor.methods import filtered_projects
from supervisor.models import Example, News, Notification, TA, diff_type, add_diff, add_notification, Flag
from supervisor.models import notification_type as nt
from supervisor.validators import is_int
from django.core.mail import send_mail

import credentials
from supervisor.async_helper import AsyncMethod


def Async(fnc=None, callback=None):
    if fnc is None:
        def AddAsyncCallback(fnc):
            return AsyncMethod(fnc, callback)

        return AddAsyncCallback
    else:
        return AsyncMethod(fnc, callback)


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
    projects = filtered_projects(request, stage=project_stage.TO_BE_VERIFIED)
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

    send_cw_sg_email(request, str(project.category.name) + ": " + str(project.title),
                     "Congratulations, your project has been verified. " +
                     "You have to present your work at the beginning of the subsequent semester " +
                     "failing which you will be awarded with X grade. " +
                     "Please reply to this mail for any assistance. \n" +
                     "Please follow the next steps as described in the guidelines. \n" +
                     "Please register the SG/CW credits on the ERP Portal too.",
                     recipients=[str(project.student.email)], project_id=project_id)

    return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project.id}))


@supervisor_logged_in
def unverify_project(request, project_id):
    project = Project.objects.get(pk=project_id)
    add_notification(noti_type=nt.NEW_PROJECT, project=project)
    project.stage = project_stage.TO_BE_VERIFIED
    project.save()
    add_diff(diff_type.PROJECT_UNVERIFIED, person=request.user, project=project)
    messages.warning(request, "You have unverified the project %s." % project.title)

    send_cw_sg_email(request, str(project.category.name) + ": " + str(project.title),
                     "It seems that the supervisor has unapproved your project. " +
                     "Reply to this email for assistance.", recipients=[str(project.student.email)],
                     project_id=project_id)

    return HttpResponseRedirect(reverse('super_viewproject', kwargs={'project_id': project.id}))


@supervisor_logged_in
def ongoing_projects(request):
    projects_filtered = filtered_projects(request)
    projects = projects_filtered.filter(stage=project_stage.ONGOING)
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

    send_cw_sg_email(request, str(project.category.name) + ": " + str(project.title),
                     "Congratulations, your project has has been selected by the supervisor as an example project. " +
                     "You must have done a mighty fine job. Keep it up.",
                     recipients=[str(project.student.email)], project_id=project_id)

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

    send_cw_sg_email(request, str(example_project.project.category.name) + ": " + str(example_project.project.title),
                     "Your project has has been removed by the admin from the example project. " +
                     "Thank you for contributing to the community. Keep it up.",
                     recipients=[str(Project.objects.get(pk=p_id).student.email)], project_id=p_id)

    example_project.delete()
    add_diff(diff_type.REMOVED_AS_EXAMPLE, person=request.user, project=get_object_or_404(Project, pk=p_id))
    messages.warning(request, "You have unmarked the project as an example project.")

    return HttpResponseRedirect(reverse('super_viewproject',
                                        kwargs={'project_id': p_id}))


@supervisor_logged_in
def submitted_projects(request):
    projects_filtered = filtered_projects(request)
    projects = projects_filtered.filter(stage=project_stage.SUBMITTED)
    return render(request, 'super_submittedprojects.html',
                  {'projects': projects})

@supervisor_logged_in
def deleted_projects(request):
    projects_filtered = filtered_projects(request)
    projects = projects_filtered.filter(deleted=True)
    return render(request, 'super_deletedprojects.html',
                  {'projects': projects})


@supervisor_logged_in
def allprojects(request):
    form = ReportForm()
    paginator = Paginator(filtered_projects(request).order_by('id').reverse(), 50, orphans=5)

    page = request.GET.get('page', None)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    stages = project_stage

    return render(request, 'super_allprojects.html',
                  {'projects': projects,
                   'form': form,
                   'stages': stages
                   })


@supervisor_logged_in
def basic_search(request):
    if request.method == "POST":
        query = request.POST.get('search_query', None)
        if query:
            if len(query) == 7 and is_int(query):
                # full roll number
                query = str(query)[2:]
            projects = filtered_projects(request).filter(student__email__icontains=query)
            # project_stage_mapping = _project_stage_mapping
            stage = project_stage
            return render(request, 'search_results.html',
                          {'projects': projects, 'query': query, 'stages': stage})
    return HttpResponseRedirect(reverse('index'))


@supervisor_logged_in
def complete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    Notification.objects.filter(project=project).delete()
    project.stage = project_stage.COMPLETED
    project.finish_date = timezone.now()
    project.save()
    add_diff(diff_type.PROJECT_COMPLETED, person=request.user, project=project)
    messages.success(request, "You have marked the Project as completed and finished.")

    send_cw_sg_email(request, str(project.category.name) + ": " + str(project.title),
                     "Congratulations, your project has been accepted " +
                     "and marked completed by the admin. ",
                     recipients=[str(project.student.email)], project_id=project_id)

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
                projects = filtered_projects(request, category=form.cleaned_data['category'])
                # projects = form.cleaned_data['category'].projects.all()
            else:
                projects = filtered_projects(request)
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
    if request.method == "POST":
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

    send_cw_sg_email(request, "Organization: " + str(noti.NGO_name),
                     "We have added the Organization suggested by you as a trusted Organization \n" +
                     "Org Name: " + str(noti.NGO_name) + "\n" +
                     "Org Details: " + str(noti.NGO_details) + "\n" +
                     "Org Link: " + str(noti.NGO_link) + "\n"
                                                         "Suggested By: " + str(noti.NGO_sugg_by) + "\n",
                     recipients=[str(noti.NGO_sugg_by.email)], notif_id=noti_id)

    messages.success(request, "%s is now a trusted Organization." % noti.NGO_name)
    noti.delete()
    return HttpResponseRedirect(reverse('super_suggested_ngos'))


@supervisor_logged_in
def reject_NGO(request, noti_id):
    noti = get_object_or_404(Notification, pk=noti_id)
    messages.info(request, "You have rejected the suggestion of adding %s as a trusted NGO." % noti.NGO_name)

    send_cw_sg_email(request, "Organization: " + str(noti.NGO_name),
                     "We have reviewed your suggestion for the Organization but as of now have to reject it. " +
                     "But thank you for your suggestion", recipients=[str(noti.NGO_sugg_by.email)], notif_id=noti_id)

    noti.delete()

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
    student = get_object_or_404(get_user_model(), pk=user_id)
    return render(request, 'super_viewuser.html',
                  {'student': student, 'projects': filtered_projects(request, student=student)})


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
                                "Please Note: This mail is generated via the SG/CW-portal. " +
                                "For any further communication regarding the above mentioned issue(s), " +
                                "please reply to this mail, unless explicitly asked to create a new email thread, " +
                                "for proper redressal."])

            send_cw_sg_email(request, str(project.category.name) + ": " + str(project.title), text,
                             recipients=[form.cleaned_data['to']], project_id=project_id)

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


@supervisor_logged_in
def generateReport(request):
    BASE_DIR = getattr(settings, "BASE_DIR")
    logger = logging.getLogger("generate-report")
    logger.warning(f"{request.POST}")

    # months = int(request.POST['date'])
    semester = int(request.POST['semester'])
    batch = int(request.POST['batch'])

    projects = filtered_projects(request).all()
    # projects = projects.filter(
    #     Q(finish_date__gte=datetime.datetime.now() - datetime.timedelta(months * 31)) |
    #     Q(finish_date=None))  # for incomplete projects

    # if semester != 0:
    projects = projects.filter(Q(semester_id=semester))

    if batch != 0:
        new_projects = []

        for project in projects:
            if project.student.batch_number == batch:
                new_projects.append(project)

        projects = new_projects

    report = xlwt.Workbook(encoding="utf-8")

    unverified_sheet = report.add_sheet("Unverified Projects")
    ongoing_sheet = report.add_sheet("Ongoing Projects")
    submitted_sheet = report.add_sheet("Submitted Projects")
    completed_sheet = report.add_sheet("Completed Projects")

    headings = [
        "Name",
        "Batch",
        "Roll number",
        "Email",
        "Category",
        "Organization",
        "Title",
        "Goals",
        "Schedule",
        "Started on",
        "Presented",
        "Semester"
    ]
    for (index, h) in enumerate(headings):
        ongoing_sheet.write(0, index, h)
        completed_sheet.write(0, index, h)
        unverified_sheet.write(0, index, h)
        submitted_sheet.write(0, index, h)

    completed_projects_row = 0
    ongoing_projects_row = 0
    submitted_projects_row = 0
    unverified_projects_row = 0

    for project in projects:
        if project.stage == project_stage.COMPLETED:
            sheet = completed_sheet
            completed_projects_row += 1
            row = completed_projects_row
        elif project.stage == project_stage.ONGOING:
            sheet = ongoing_sheet
            ongoing_projects_row += 1
            row = ongoing_projects_row
        elif project.stage == project_stage.SUBMITTED:
            sheet = submitted_sheet
            submitted_projects_row += 1
            row = submitted_projects_row
        elif project.stage == project_stage.TO_BE_VERIFIED:
            sheet = unverified_sheet
            unverified_projects_row += 1
            row = unverified_projects_row

        for col, x in enumerate([
            ' '.join([project.student.first_name, project.student.last_name]),
            project.get_batch(),
            project.get_rollno(),
            project.student.email,
            project.get_category(),
            project.get_NGO(),
            project.title,
            project.goals,
            project.schedule_text,
            project.date_created.strftime('%d-%m-%Y'),
            "%s" % project.presented,
            project.semester.label
        ]):
            sheet.write(row, col, x)

    report.save(os.path.join(BASE_DIR, 'report.xls'))

    encoding = ""
    if sys.platform == "linux":
        encoding = "utf8"
    else:
        encoding = "ISO-8859-1"

    # report = open(os.path.join(BASE_DIR, 'report.xls'), 'r', encoding=encoding)
    # response = StreamingHttpResponse(report)
    # response['Content-Disposition'] = 'download; filename=report.xls'
    # response['Content-Disposition'] = 'inline; filename=' + os.path.basename('Report.xls')

    report_path = os.path.join(BASE_DIR, 'report.xls')
    with open(report_path, 'rb') as file:
        response = HttpResponse(file.read())
        response['Content-Disposition'] = 'download; filename=' + os.path.basename(report_path)
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
    ta = get_user_model().objects.filter(email=email)
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


@Async
@supervisor_logged_in
def send_cw_sg_email(request, subject, text, recipients, project_id=None, notif_id=None):
    ta_email = None
    ta_pass = None

    project = None

    if project_id is not None:
        project = get_object_or_404(Project, pk=project_id)

    elif notif_id is not None:
        notification = get_object_or_404(Notification, pk=notif_id)
        project = notification.project

    if project is not None:
        if project.get_category() == "SG":
            ta_email = credentials.EMAIL_SG_USER
            ta_pass = credentials.EMAIL_SG_PASSWORD
        else:
            ta_email = credentials.EMAIL_CW_USER
            ta_pass = credentials.EMAIL_CW_PASSWORD

        send_mail(subject, text, ta_email, recipients, auth_user=ta_email, auth_password=ta_pass)


@supervisor_logged_in
def toggle_allow_project(request):
    allow_project_flag = Flag.objects.get(key='add_project')
    allow_project_flag.value = not allow_project_flag.value
    allow_project_flag.save()
    context = {'value': allow_project_flag.value}
    popup_message = "Projects allowed." if allow_project_flag.value else "Projects disallowed."
    messages.success(request, popup_message)
    return render(request, 'allow_project.html', context=context)


@supervisor_logged_in
def allow_project(request):
    allow_project_flag = Flag.objects.get(key='add_project')
    context = {'value': allow_project_flag.value}
    print(allow_project_flag)
    return render(request, 'allow_project.html', context=context)


@supervisor_logged_in
def update_batch(request):
    user_id = int(request.POST['user_id'])
    new_batch = int(request.POST['new_batch'])
    student = get_object_or_404(get_user_model(), pk=user_id)
    student.batch_number = new_batch
    student.save()

    messages.info(request, "Batch updated!")
    return render(request, 'super_viewuser.html',
                  {'student': student, 'projects': Project.all_projects.filter(student=student)})


@supervisor_logged_in
def new_sem_page(request):
    form = SemesterForm()
    semesters = Semester.objects.all()
    return render(request, 'create_new_semester.html', context={'form': form,
                                                                'semesters': semesters})


@supervisor_logged_in
def all_semesters(request):
    form = SemesterForm()
    if request.method == "POST":
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New semester created")
        else:
            messages.warning(request, "There was some error in the data submitted.")
        return HttpResponseRedirect(reverse('index'))
    semesters = Semester.objects.all()
    return render(request, 'create_new_semester.html', context={'form': form,
                                                                'semesters': semesters})


@supervisor_logged_in
def update_semester(request, id):
    if request.method == 'POST':
        semester = get_object_or_404(Semester, pk=id)
        updation_form = SemesterForm(request.POST, instance=semester)
        if updation_form.is_valid():
            updation_form.save()
            messages.success(request, 'Update successful!')
        else:
            messages.error(request, 'Update failed.')
    return redirect('create_new_semester')


@supervisor_logged_in
def delete_semester(request):
    if request.method == 'POST':
        deletion_form = SemesterDeletionForm(request.POST)
        if deletion_form.is_valid():
            id = deletion_form.cleaned_data.get("id")
            semester = get_object_or_404(Semester, pk=id)
            semester.delete()
            messages.success(request, "Semester has been successfully deleted.")
        else:
            messages.error(request, "Cannot delete the semester.")
    return redirect('create_new_semester')
