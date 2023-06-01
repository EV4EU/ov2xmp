import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ov2xmp.settings")
app = Celery("ov2xmp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
