import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jira.settings')

app = Celery('jira')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all registered Django app configs
app.autodiscover_tasks()

# Periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-overdue-reminders': {
        'task': 'notifications.tasks.send_overdue_reminders',
        'schedule': crontab(hour=21, minute=4),
    },
    # 'cleanup-old-notifications': {
    #     'task': 'notifications.tasks.cleanup_old_notifications',
    #     'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    # },
    # 'cleanup-inactive-connections': {
    #     'task': 'notifications.tasks.cleanup_inactive_websocket_connections',
    #     'schedule': crontab(minute='*/30'),  # Every 30 minutes
    # },
}