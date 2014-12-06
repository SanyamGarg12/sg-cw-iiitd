from django.core.cache import cache
from decorators import validate_cache

@validate_cache
def get(key):
    return cache.get('-'.join(['custom', key]))
@validate_cache
def set(key, value):
    cache.set('-'.join(['custom', key]), value)

@validate_cache
def get_leaderboard():
    return cache.get('leaderboard')
@validate_cache
def set_leaderboard(value):
    cache.set('leaderboard', value)

@validate_cache
def get_TA():
    return cache.get('TA')
@validate_cache
def set_TA(value):
    cache.set('TA', value)

@validate_cache
def get_example_projects():
    return cache.get('example_projects')
@validate_cache
def set_example_projects(value):
    cache.set('example_projects', value)

@validate_cache
def get_news():
    return cache.get('news')
@validate_cache
def set_news(value):
    cache.set('news', value)

@validate_cache
def get_noti_count(key):
    return cache.get("_".join(["noti_count", key]))
@validate_cache
def set_noti_count(key, value):
    cache.set("_".join(["noti_count", key]), value)