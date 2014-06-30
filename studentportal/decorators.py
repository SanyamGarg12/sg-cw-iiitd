def path_and_rename(path):
	def wrapper(instance, filename):
		import os
		import string
		from django.utils import timezone
		from random import choice
		extension = filename.split('.')[-1]
		a = string.letters + string.digits
		while True:
			filename = ''.join(choice(a) for x in range(10))
			filename = '.'.join([filename, extension])
			if not os.path.isfile(filename):
				break
		return os.path.join(path.replace('%Y', str(timezone.now().year)), filename)
	return wrapper

def validate_credits(value):
	print value, type(value)
	from django.core.exceptions import ValidationError
	if value != 1 and value != 2:
		raise ValidationError('You can only work for 1 or 2 credits')