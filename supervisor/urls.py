from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^home/', views.home, name='supervisor_home'),
	url(r'^logout/', views._logout, name='supervisor_logout'),
	url(r'^ongoing/(?P<skip>[0-9]+)/', views.ongoing_projects, name='ongoing_projects'),
	url(r'^unverified/', views.unverified_projects, name='unverified_projects'),
	url(r'^verify/(?P<project_id>[0-9])/', views.verify_project, name='verify_project'),
	url(r'^unverify/(?P<project_id>[0-9])/', views.unverify_project, name='unverify_project'),
	url(r'^project/(?P<project_id>[0-9])/', views.viewproject, name = 'super_viewproject'),
)