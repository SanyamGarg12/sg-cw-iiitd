#! /bin/bash 
alias s='sudo python manage.py runserver'
alias a='sudo python manage.py shell'
sudo python manage.py migrate
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CW_Portal.settings'); from supervisor.models import Category; Category.objects.create(name='Other', description='projects that do not fit into other categories')"
echo
