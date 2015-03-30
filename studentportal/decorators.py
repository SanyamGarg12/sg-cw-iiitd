from random import choice
import os
import string
from django.utils import timezone
from django.utils.deconstruct import deconstructible


@deconstructible
class _PathAndRename(object):
    def __init__(self, filename):
        self.filename = filename

    def __call__(self, instance, filename):
        extension = filename.split('.')[-1]
        a = string.letters + string.digits
        while True:
            filename = ''.join(choice(a) for _ in range(10))
            filename = '.'.join([filename, extension])
            if not os.path.isfile(filename):
                break
        return os.path.join(path.replace('%Y', str(timezone.now().year)), filename)

path_and_rename = _PathAndRename('uploads/%Y/')
