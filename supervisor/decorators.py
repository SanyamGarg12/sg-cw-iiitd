from functools import wraps
from django.http import Http404
from PrivateData import SUPERVISOR_EMAIL, EMAIL_HOST_USER

from supervisor.models import Notification
from studentportal.models import Project

import threading
from django.core.mail import EmailMultiAlternatives

from CW_Portal import globals

from studentportal.models import Feedback, Category
from pygal import Pie, StackedLine
from pygal.style import CleanStyle as pygal_CleanStyle
import os
from CW_Portal.settings import BASE_DIR
import datetime

class RenderFeedbackExperiencePieChart(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		frequency = [0, 0, 0, 0, 0]
		for feedback in Feedback.objects.all():
			frequency[int(feedback.experience) - 1] += 1
		pie_chart = Pie(title_font_size = 48)
		pie_chart.title = "Student experience"
		for x in range(5):
			pie_chart.add(str(x+1), frequency[x])
		pie_chart.render_to_file(os.path.join(BASE_DIR, 'studentportal/static/statistics/feedback_experience_piechart.svg'))

class RenderProjectToMonthDistribution(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
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
		chart.render_to_file(os.path.join(BASE_DIR, 'studentportal/static/statistics/project_to_month_distribution.svg'))

class RenderProjectCategoryPieChart(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		pie_chart = Pie(title_font_size=48)
		category_dict = {c: 0 for c in Category.objects.all()}
		for project in Project.objects.all():
			category_dict[project.category] += 1
		for k,v in category_dict.iteritems():
			pie_chart.add(k.name, v)
		pie_chart.render_to_file(os.path.join(BASE_DIR, 'studentportal/static/statistics/project_category_piechart.svg'))		

def supervisor_logged_in(view):
	def _wrapped_view(request, *args, **kwargs):
		if (globals.noti_refresh == True \
		or request.session.get('noti_count_submissions', None) == None \
		or request.session.get('noti_count_NGO', None) == None \
		or request.session.get('noti_count_proposal', None) == None ):
			request.session['noti_count_proposal'] = Notification.objects.filter(noti_type='new').distinct().count()
			request.session['noti_count_submissions'] = Notification.objects.filter(noti_type='finish').distinct().count()
			request.session['noti_count_NGO'] = Notification.objects.filter(noti_type='suggest').distinct().count()
			globals.noti_refresh = False

		if request.user.is_authenticated() and request.user.email == SUPERVISOR_EMAIL:
			return view(request, *args, **kwargs)
		raise Http404()
	return _wrapped_view

def is_int(x):
	try:
		x = int(x)
		return True
	except:
		return False

class EmailThread(threading.Thread):
	def __init__(self, subject, text_content, recipient_list):
		self.subject = subject
		self.recipient_list = recipient_list
		self.text_content = text_content
		threading.Thread.__init__(self)

	def run(self):
		msg = EmailMultiAlternatives(self.subject, self.text_content, EMAIL_HOST_USER, self.recipient_list)
		# msg.attach_alternative(True, "text/html")
		msg.send()

def EmailMessage(subject, text_content, to=[]):
	pass
	# EmailThread(subject, text_content, to).start()

def chunks(full, size):
	for i in xrange(0, len(full), size):
		yield full[i:i+size]

def EmailMessageAll(text_content,subject="New Announcement"):
	projects = Project.objects.filter(stage='ongoing')
	projects = list(chunks(projects, 10))
	for p in projects:
		EmailMessage(subject, text_content, to=[str(x.student.email) for x in p])