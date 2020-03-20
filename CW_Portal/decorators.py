from django.core.cache import cache


# This decorator is used to ensure that the caching layer is initialised.
# It does this by setting a `cache-valid` key in the caching layer.
# If the memcached service is restarted, this decorator 
# triggers the cache initialising functions.
# This should be wrapped around all the functions which try to get a
# key from the cache. This will logically stop the caching layer from
# returning `None` just because it hasn't been initialised.
def validate_cache(view):
	def _wrapped_view(*args, **kwargs):
		if not cache.get('cache-valid'):
			import studentportal.startup
			studentportal.startup.work()
		return view(*args, **kwargs)

	return _wrapped_view
