# celery_worker/celery_app.py
from celery import Celery
import sys, os
import django

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "eshop_ranker"))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eshop_ranker.settings")
django.setup()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# create an celery app
app = Celery("standalone_celery")


# importing the configs from celery_config file
app.config_from_object("celery_worker.celery_config", namespace="CELERY")

@app.task(bind=True)
def fake_detector_task(self):
    print("fake_detector_task")
    print("fake_detector_task completed")

import ml_engine.fake_detector.tasks
import ml_engine.sentiment_analysis.tasks


