from celery import Celery
import os

# Modular Celery app factory

def make_celery(app_name=__name__):
    redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    return Celery(app_name, broker=redis_url)

celery = make_celery() 