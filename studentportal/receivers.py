from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from CW_Portal import access_cache
from supervisor.models import Like, Example, News

@receiver([post_save, post_delete], sender=Like)
def refresh_leaderboard(sender, **kwargs):
    # improve the algorithm
    temp = Example.objects.all().order_by('-likes_count')[:5]
    access_cache.set_leaderboard(temp)

@receiver([post_save, post_delete], sender=Example)
def refresh_example_projects(sender, **kwargs):
    example_projects = Example.objects.all()[:6]
    access_cache.set_example_projects(example_projects)

@receiver([post_save, post_delete], sender=News)
def refresh_news(sender, **kwargs):
    news = News.objects.all().order_by('-date_created')[:5]
    access_cache.set_news(news)