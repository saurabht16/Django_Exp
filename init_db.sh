#!/bin/sh
echo "------ Create database tables ------"
python manage.py migrate --noinput

echo "------ create default admin user ------"
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@myapp.local', 'Passw0rd')" | python manage.py shell

echo "------ starting gunicorn &nbsp;------"
gunicorn tpagui.wsgi --workers 2
