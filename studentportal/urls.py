from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^home$', views.home, name='studenthome'),
	url(r'^add$', views.add, name='addproject'),
)
