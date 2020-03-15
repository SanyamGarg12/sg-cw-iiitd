from django.contrib import admin

from supervisor.models import TA, Notification, Example, Comment, News

admin.site.register(TA)
admin.site.register(Notification)
admin.site.register(Example)
admin.site.register(Comment)
admin.site.register(News)