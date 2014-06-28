from functools import wraps
from django.http import Http404
from PrivateData import SUPERVISOR_EMAIL

from supervisor.models import Notification

def supervisor_logged_in(view):
    def _wrapped_view(request, *args, **kwargs):
    	
    	if (request.session.get('noti_count_proposal', None) == None \
    	or request.session.get('noti_count_log', None) == None \
    	or request.session.get('noti_count_NGO', None) == None ):
    		request.session['noti_count_proposal'] = Notification.objects.filter(noti_type='new').distinct().count()
    		request.session['noti_count_log'] = Notification.objects.filter(noti_type='log').distinct().count()
    		request.session['noti_count_NGO'] = Notification.objects.filter(noti_type='suggest').distinct().count()

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