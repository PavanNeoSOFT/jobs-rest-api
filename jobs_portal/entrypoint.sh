#!/bin/bash

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create a superuser if none exists
echo "Creating a superuser..."
echo "from django.contrib.auth import get_user_model; \
      User = get_user_model(); \
      User.objects.filter(username='admin').exists() or \
      User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell

# Create groups (employer and applicant)
echo "Creating default groups..."
echo "from django.contrib.auth.models import Group; \
      Group.objects.get_or_create(name='employer'); \
      Group.objects.get_or_create(name='applicant')" | python manage.py shell

# Start the server
echo "Starting the Django server..."
exec python manage.py runserver 0.0.0.0:8000
