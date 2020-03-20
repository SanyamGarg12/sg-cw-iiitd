from random import choice
import os
import string
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from CW_Portal import settings


@deconstructible
class _PathAndRename(object):
	def __init__(self, path):
		self.path = path

	def __call__(self, instance, filename):
		extension = filename.split('.')[-1]
		a = string.letters + string.digits
		while True:
			filename = ''.join(choice(a) for _ in range(10))
			filename = '.'.join([filename, extension])
			if not os.path.isfile(filename):
				break
		return os.path.join(self.path.replace('%Y', str(timezone.now().year)), filename)


# this creates a function (in Python, functions are high level objects).
# Whenever `path_and_rename` is called, it'll apply the logic of creating
# and returning a random and unique name for the file.
path_and_rename = _PathAndRename(getattr(settings, 'UPLOAD_PATH', 'uploads/%Y/'))
