from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout

from supervisor.decorators import supervisor_logged_in

@supervisor_logged_in
def home(request):
	return HttpResponse('<h1><center>THIS IS SUPERVISOR HOME</center></h1>')

@supervisor_logged_in
def _logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

