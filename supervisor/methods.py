from studentportal.models import Project
from supervisor.decorators import supervisor_logged_in


@supervisor_logged_in
def filtered_projects(request, **kwargs):
    queryset = None
    if request.user.email == "selfgrowth@iiitd.ac.in":
        queryset = Project.objects.filter(category__name='SG', **kwargs)
    elif request.user.email == "communitywork@iiitd.ac.in":
        queryset = Project.objects.filter(category__name='CW', **kwargs)
    else:
        queryset = Project.objects.filter(**kwargs)
    return queryset
