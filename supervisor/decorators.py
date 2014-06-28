from functools import wraps
from django.http import Http404
from PrivateData import SUPERVISOR_EMAIL, EMAIL_HOST_USER

from supervisor.models import Notification

import threading
from django.core.mail import EmailMultiAlternatives

def supervisor_logged_in(view):
    def _wrapped_view(request, *args, **kwargs):

    	if (request.session.get('noti_count_proposal', None) == None \
    	or request.session.get('noti_count_log', None) == None \
    	or request.session.get('noti_count_NGO', None) == None ):
    		request.session['noti_count_proposal'] = Notification.objects.filter(noti_type='new').distinct().count()
    		request.session['noti_count_log'] = Notification.objects.filter(noti_type='log').distinct().count()
    		request.session['noti_count_NGO'] = Notification.objects.filter(noti_type='suggest').distinct().count()
        print request.user.email, SUPERVISOR_EMAIL
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
    EmailThread(subject, text_content, to).start()