from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from studentportal.models import Category, NGO, Project, Document, Feedback, Bug, CustomUser

admin.site.register(Category)
admin.site.register(NGO)
admin.site.register(Project)
admin.site.register(Document)
admin.site.register(Feedback)
admin.site.register(Bug)
admin.site.register(CustomUser, UserAdmin)
