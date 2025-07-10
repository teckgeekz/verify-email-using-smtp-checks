import os
from dotenv import load_dotenv
load_dotenv()  # This will load .env when Celery starts

from celery import Celery

# Modular Celery app factory

def make_celery(app_name=__name__):
    redis_url = os.getenv("CELERY_BROKER_URL")
    print(f"Celery will use broker: {redis_url}")  # For debugging
    if not redis_url:
        redis_url = "redis://localhost:6379/0"
    return Celery(app_name, broker=redis_url)

celery = make_celery() 