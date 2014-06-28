from functools import wraps
from django.http import Http404
from PrivateData import SUPERVISOR_EMAIL

def supervisor_logged_in(view):
    def _wrapped_view(request, *args, **kwargs):
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