from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', include('studentportal.urls')),
    url(r'^student/', include('studentportal.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^logout/$', 'studentportal.views._logout', name='logout'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)