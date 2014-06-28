from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.core.urlresolvers import reverse

from supervisor.decorators import supervisor_logged_in

@supervisor_logged_in
def home(request):
	return render(request, 'supervisorhome.html')

@supervisor_logged_in
def _logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

