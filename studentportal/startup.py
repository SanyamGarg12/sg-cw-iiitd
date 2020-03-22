from django.core.cache import cache

from studentportal import receivers as r1
from studentportal.models import Project, Feedback
from supervisor import receivers as r2


def work():
    r1.refresh_leaderboard(Project)
    r1.refresh_example_projects(Project)
    r1.refresh_news(Project)

    r2.update_TAs(Project)
    r2.RenderProjectToMonthDistribution(Project)
    r2.RenderProjectCategoryPieChart(Project)
    r2.RenderFeedbackExperiencePieChart(Feedback)
    r2.refresh_notifications(Project)
    r2.refresh_projects_on_home_page(Project)

    cache.set('cache-valid', True)
