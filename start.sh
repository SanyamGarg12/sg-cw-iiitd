#! /bin/bash 
alias s='python manage.py runserver'
alias a='python manage.py shell'
python manage.py migrate
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CW_Portal.settings'); from supervisor.models import Category; Category.objects.create(name='Other', description='projects that do not fit into other categories')"
echo
