from studentportal.models import Project
from supervisor.decorators import supervisor_logged_in
from credentials import SG_USERS, CW_USERS, FULL_USERS


@supervisor_logged_in
def filtered_projects(request, **kwargs):
    queryset = None
    if request.user.email in FULL_USERS:
        queryset = Project.objects.filter(**kwargs)
    elif request.user.email in SG_USERS:
        queryset = Project.objects.filter(category__name='SG', **kwargs)
    elif request.user.email in CW_USERS:
        queryset = Project.objects.filter(category__name='CW', **kwargs)
    else:
        queryset = Project.objects.filter(**kwargs)
    return queryset
