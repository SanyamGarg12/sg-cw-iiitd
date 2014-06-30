#! /bin/bash
alias s='python manage.py runserver'
alias a='python manage.py shell'
mkdir -p studentportal/static/statistics
python manage.py syncdb
