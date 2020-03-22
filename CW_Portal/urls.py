from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import studentportal

admin.autodiscover()

from studentportal.views import index, first_login
from studentportal import startup

startup.work()
handler404 = 'studentportal.views.handle404_LnF'
handler500 = 'studentportal.views.handle404_LnF'

urlpatterns = [
                  url(r'^$', index, name='index'),
                  url('', include('social_django.urls', namespace='social')),
                  url(r'^first_login/$', first_login),
                  url(r'^student/', include('studentportal.urls')),
                  url(r'^supervisor/', include('supervisor.urls')),
                  url(r'^admin/', admin.site.urls),
                  url(r'^accounts/', include('allauth.urls')),
                  url(r'^logout/$', studentportal.views._logout, name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
