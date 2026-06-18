import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('comments')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cleanup-expired-captchas': {
        'task': 'comments.tasks.cleanup_expired_captchas',
        'schedule': crontab(minute='*/10'),
    },
}
