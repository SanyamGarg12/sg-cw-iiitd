import datetime
from multiprocessing import Process
import os

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Q
from pygal import Pie, StackedLine
from pygal.style import CleanStyle as pygal_CleanStyle

from CW_Portal import access_cache, settings
from supervisor.models import TA, Notification
from supervisor.models import notification_type as nt
from studentportal.models import Project, Category, project_stage,  Feedback

media_root = getattr(settings, "MEDIA_ROOT")
folder = getattr(settings, "STATISTICS_FOLDER_NAME")

@receiver([post_save, post_delete], sender = TA)
def update_TAs(sender, **kwargs):
    new_TAs = [x.email for x in TA.objects.all()]
    access_cache.set_TA(list(set(new_TAs)))

def _RenderFeedbackExperiencePieChart():
    frequency = [0, 0, 0, 0, 0]
    for feedback in Feedback.objects.all():
        frequency[int(feedback.experience) - 1] += 1
    pie_chart = Pie(title_font_size = 48)
    pie_chart.title = "Student experience"
    for x in range(5):
        pie_chart.add(str(x+1), frequency[x])
    pie_chart.render_to_file(os.path.join(media_root,
                        '%s/feedback_experience_piechart.svg'%folder))

def _RenderProjectToMonthDistribution():
    chart = StackedLine(fill=True, title_font_size=48,
     y_title = 'Projects', style=pygal_CleanStyle )#\
     # interpolate='quadratic',,)
    years = {x: 0 for x in range(2014, datetime.date.today().year+1)[-5:]}
    #db reading is very fast / caching
    for year in years:
        month = {x: 0 for x in range(1,13)}
        for project in Project.objects.all():
            month[project.date_created.month] += 1
        chart.add(str(year),[month[x] for x in sorted(month)] )
    chart.render_to_file(os.path.join(media_root,
                        '%s/project_to_month_distribution.svg'%folder))

def _RenderProjectCategoryPieChart():
    pie_chart = Pie(title_font_size=48)
    category_dict = {c: 0 for c in Category.objects.all()}
    for project in Project.objects.all():
        category_dict[project.category] += 1
    for k,v in category_dict.items():
        pie_chart.add(k.name, v)
    pie_chart.render_to_file(os.path.join(media_root,
                     '%s/project_category_piechart.svg'%folder))

@receiver([post_save, post_delete], sender=Feedback)
def RenderFeedbackExperiencePieChart(sender, **kwargs):
    # Process(target=_RenderFeedbackExperiencePieChart).start()
    _RenderFeedbackExperiencePieChart()

@receiver([post_save, post_delete], sender=Project)
def RenderProjectToMonthDistribution(sender, **kwargs):
    # Process(target=_RenderProjectToMonthDistribution).start()
    _RenderProjectToMonthDistribution()

@receiver([post_save, post_delete], sender=Project)
def RenderProjectCategoryPieChart(sender, **kwargs):
    # Process(target=_RenderProjectCategoryPieChart).start()
    _RenderProjectCategoryPieChart()

#listen for changes in notifications.
@receiver([post_save, post_delete], sender=Notification)
def refresh_notifications(sender, **kwargs):
    # improve this
    # import pdb
    # pdb.set_trace()
    access_cache.set_noti_count('proposal',Notification.objects.filter(noti_type=nt.NEW_PROJECT).distinct().count())
    access_cache.set_noti_count('submissions', Notification.objects.filter(noti_type=nt.PROJECT_FINISHED).distinct().count())
    access_cache.set_noti_count('NGO', Notification.objects.filter(noti_type=nt.NGO_SUGGESTION).distinct().count())

@receiver([post_save, post_delete], sender=Project)
def refresh_projects_on_home_page(sender, **kwargs):
     access_cache.set('projects_homepage', Project.objects.filter(
                            ~Q(stage=project_stage.COMPLETED)).order_by(
                            '-date_created')[:10])