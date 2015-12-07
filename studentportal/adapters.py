from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from CW_Portal import settings, access_cache
from django.contrib.auth import logout
from django.contrib import messages
from allauth.exceptions import ImmediateHttpResponse
from allauth.account.adapter import DefaultAccountAdapter
from studentportal import views
import supervisor.communication

class DomainLoginAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        # allow TAs be outside ALLOWED DOMAINS
        email = user.email
        if all([email.split('@')[1] not in \
                 getattr(settings,"ALLOWED_DOMAINS", []),
                email in access_cache.get_TA()]):
            logout(request)
            messages.warning(request,
                    "Sorry. You must login through a IIIT-D account only.")
            raise ImmediateHttpResponse(views.home(request))

class NoMessagesLoginAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template,
                    message_context={}, extra_tags=''):
        pass

def send_report_to_admins():
    proposals   = access_cache.get_noti_count('proposal')
    submissions = access_cache.get_noti_count('submissions')
    ngos        = access_cache.get_noti_count('NGO')

    if any([proposals, submissions, ngos]):
        body = """Hi,
        There are notifications pending in the community work portal. Please check them out whenever you have the chance.\n"""
        body = "".join([body, "     New projects waiting to be approved: ", str(proposals), "\n"])
        body = "".join([body, "     Projects with new submissions: ", str(submissions), "\n"])
        body = "".join([body, "     New suggested NGOs: ", str(ngos), "\n"])

        supervisor.communication.send_email("[CW-portal] - Notifications", body, access_cache.get_TA())

        print "Sent report to admins: ", body
    else:
        print "No report sending required."