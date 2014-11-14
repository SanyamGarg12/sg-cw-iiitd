from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from CW_Portal import settings
from django.contrib.auth import logout
from django.contrib import messages
from allauth.exceptions import ImmediateHttpResponse
from allauth.account.adapter import DefaultAccountAdapter
from studentportal import views

class DomainLoginAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.account.user
        if user.email.split('@')[1] not in \
                            getattr(settings,"ALLOWED_DOMAINS", []):
            logout(request)
            messages.error(request,
                    "Sorry. You must login through a IIIT-D account only.")
            raise ImmediateHttpResponse(views.home(request))

class NoMessagesLoginAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template,
                    message_context={}, extra_tags=''):
        pass