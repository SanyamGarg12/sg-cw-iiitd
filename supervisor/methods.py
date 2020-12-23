from studentportal.models import Project
from supervisor.decorators import supervisor_logged_in


@supervisor_logged_in
def filtered_projects(request, **kwargs):
    queryset = None
    if request.user.email == "sg@iiitd.ac.in":
        queryset = Project.objects.filter(**kwargs)
    elif request.user.email == "cw@iiitd.ac.in":
        queryset = Project.objects.filter(category__name='CW', **kwargs)
    elif request.user.email == "admin-btech@iiitd.ac.in":
        queryset = Project.objects.filter(category__name='SG', **kwargs)
    return queryset
