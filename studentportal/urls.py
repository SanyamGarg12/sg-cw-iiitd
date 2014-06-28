from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	# url(r'^$', views.index, name='index'),
	url(r'^home/', views.home, name='studenthome'),
	url(r'^add/$', views.addproject, name='addproject'),
	url(r'^project/(?P<project_id>[0-9]+)/edit/$', views.editproject, name='editproject'),	
	url(r'^project/(?P<project_id>[0-9]+)/upload/$', views._upload, name='upload_document'),
	url(r'^project/(?P<project_id>[0-9]+)/$', views.viewproject, name='viewproject'),
	url(r'^download/(?P<document_id>[0-9]+)/$', views.download, name='download_document'),
	url(r'^profile/$', views.profile, name='studentprofile'),
	url(r'^news/(?P<news_id>[0-9]*)/$', views.view_news, name='student_view_news'),
	url(r'^project/(?P<project_id>[0-9]+)/NGO/$', views.view_project_NGO, name='view_project_NGO'),
	url(r'^link_ngo_project/(?P<NGO_id>[0-9]+)/(?P<project_id>[0-9]+)/$', 
		views.link_NGO_project, name='link_NGO_project'),
	url(r'^unlink_ngo_project/(?P<project_id>[0-9]+)/$', views.unlink_NGO_project,
		name = 'unlink_ngo_project'),
	url(r'^all_ngo/$', views.all_NGOs, name='all_NGO'),
	
)
