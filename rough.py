from django.core.cache import cache

# Set a value in the cache
cache.set('my_key', 'my_value')

# Retrieve the value from the cache
value = cache.get('my_key')
print(value)
