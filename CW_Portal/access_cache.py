# def init():
#   #True noti_refresh indicates that notifications should be refreshed 
#   # add this using listener
#   global noti_refresh
#   noti_refresh = True

#   # listener
#   #experience feedback pie is the svg shown in statistics
#   global render_feedback_experience_piechart
#   render_feedback_experience_piechart = True

#   # listener
#   #compute leaderboard
#   global leaderboard
#   leaderboard = None
#   global leaderboard_refresh
#   leaderboard_refresh = True

from django.core.cache import cache

def get(key):
    return cache.get('-'.join(['custom', key]))
def set(key, value):
    cache.set('-'.join(['custom', key]), value)

def get_leaderboard():
    return cache.get('leaderboard')
def set_leaderboard(value):
    cache.set('leaderboard', value)

def get_TA():
    return cache.get('TA')
def set_TA(value):
    cache.set('TA', value)

def get_example_projects():
    return cache.get('example_projects')
def set_example_projects(value):
    cache.set('example_projects', value)

def get_news():
    return cache.get('news')
def set_news(value):
    cache.set('news', value)

def get_noti_count(key):
    return cache.get("_".join(["noti_count", key]))
def set_noti_count(key, value):
    cache.set("_".join(["noti_count", key]), value)