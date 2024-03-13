from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import studentportal

admin.autodiscover()

from studentportal.views import index, first_login
from studentportal import startup

import credentials


handler404 = 'studentportal.views.handle404_LnF'
handler500 = 'studentportal.views.handle404_LnF'

urlpatterns = [
                  path(r'^$', index, name='index'),
                  path('', include('social_django.urls', namespace='social')),
                  path(r'^first_login/$', first_login),
                  path(r'^student/', include('studentportal.urls')),
                  path(r'^supervisor/', include('supervisor.urls')),
                  path(r'^admin/', admin.site.urls),
                  path(r'^accounts/', include('allauth.urls')),
                  path(r'^logout/$', studentportal.views._logout, name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

startup.work()
credentials.init_firebase_keys()
