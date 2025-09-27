import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')

app = Celery('ecommerce_backend')

app.config_from_object('django.conf:settings', namespace='CELERY')
# Broker: RabbitMQ
app.conf.broker_url = os.environ.get("RABBITMQ_URL")

# Backend: Redis
app.conf.result_backend = os.environ.get("REDIS_URL")

# Optional: Task serialization and time limits
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # seconds
)

app.autodiscover_tasks()


