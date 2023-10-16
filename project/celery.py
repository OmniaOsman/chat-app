import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Create the Celery application instance.
app = Celery('tasks')

# Load the Celery configuration from the Django settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover and import task modules from all registered Django app configs.
app.autodiscover_tasks()
