import os
from glob import glob

from django.conf import settings


def reset():
    if settings.PRODUCTION_SERVER:
        print("This file should not be executed on the production server. Please use migrations/fixtures instead.")
        print("Exiting...")
        return
    confirm = input("Are you sure to continue? (y/n).")
    if confirm.lower() == "y":
        for file in glob('*/migrations/000*.py'):
            print("removing", str(file))
            os.remove(file)

        os.system("python manage.py makemigrations")
    else:
        print("Cancelling operation")
