from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^home/', views.home, name='supervisor_home'),
	url(r'^logout/$', views._logout, name='supervisor_logout'),
	url(r'^ongoing/(?P<skip>[0-9]+)/$', views.ongoing_projects, name='ongoing_projects'),
	url(r'^unverified/$', views.unverified_projects, name='unverified_projects'),
	url(r'^verify/(?P<project_id>[0-9]+)/$', views.verify_project, name='verify_project'),
	url(r'^unverify/(?P<project_id>[0-9]+)/$', views.unverify_project, name='unverify_project'),
	url(r'^project/(?P<project_id>[0-9]+)/$', views.viewproject, name = 'super_viewproject'),
	url(r'^example/$', views.example_projects, name = 'example_projects'),
	url(r'^addtoexamples/(?P<project_id>[0-9]+)/$', views.add_to_examples, name='addtoexamples'),
	url(r'^removefromexamples/(?P<example_project_id>[0-9]+)/$', views.remove_from_examples, name='removefromexamples'),
	url(r'^submittedprojects/$', views.submitted_projects, name='submitted_projects'),
	url(r'^allprojects/$', views.allprojects, name = 'super_allprojects'),
	url(r'^allprojects/(?P<skip>[0-9]+)/$', views.allprojects, name = 'super_allprojects'),
)