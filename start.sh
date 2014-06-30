#! /bin/bash
alias s='python manage.py runserver'
alias a='python manage.py shell'
mkdir -p studentportal/static/statistics
python manage.py syncdb
#python -i manage.py 'from studentportal.models import Category; Category.objects.create(name="Others", description="Everything else")'
echo
echo "Remember to add the 'other' category"
echo
