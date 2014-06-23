from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^home/', views.home, name='supervisor_home'),
	url(r'^logout', views._logout, name='supervisor_logout'),
	
)