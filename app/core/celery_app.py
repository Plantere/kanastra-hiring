from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "kanastra_billing_project",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks.invoice_tasks", "app.tasks.email_tasks", "app.tasks.csv_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC", 
    enable_utc=True,
    task_routes={
        'app.tasks.invoice_tasks.*': {'queue': 'invoice_queue'},
        'app.tasks.email_tasks.*': {'queue': 'email_queue'},
        'app.tasks.csv_tasks.*': {'queue': 'csv_queue'},
    },
    task_track_started=True,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    worker_prefetch_multiplier=1
)