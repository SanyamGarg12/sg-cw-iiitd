from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^home/', views.home, name='studenthome'),
	url(r'^add/$', views.addproject, name='addproject'),
	url(r'^project/(?P<project_id>[0-9])/edit/$', views.editproject, name='editproject'),	
	url(r'^project/(?P<project_id>[0-9])/$', views.viewproject, name='viewproject'),
	url(r'^project/(?P<project_id>[0-9])/upload/$', views._upload, name='upload_document'),
)