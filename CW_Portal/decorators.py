from django.core.cache import cache

def validate_cache(view):
    def _wrapped_view(*args, **kwargs):
        if not cache.get('cache-valid'):
            import studentportal.startup
            studentportal.startup.work()
        return view(*args, **kwargs)
    return _wrapped_view