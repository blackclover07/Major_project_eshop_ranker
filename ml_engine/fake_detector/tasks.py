import joblib
import os
import re
import sys
import django


# allow python to find django project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# configure django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eshop_ranker.settings")
django.setup()

from django.db import transaction
from reviews.models import Review

from celery_worker.worker import app  # import standalone Celery
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Absolute path to the model file
MODEL_PATH = os.path.join(BASE_DIR, "fake_review_detector_pipeline.pkl")


print(f"Base dir {BASE_DIR}")
print(f"Loading model from {MODEL_PATH}")


pipeline = joblib.load(MODEL_PATH)
print(" Fake_dtector Model loaded Sucessfully")
BATCH_SIZE = 6
THRESHOLD = 0.995

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.task(bind=True)
def process_reviews(self):

    from django.db import transaction

    with transaction.atomic():

        reviews = list(
            Review.objects
            .select_for_update(skip_locked=True)
            .filter(processed=False)
            .only("id", "review_text")[:BATCH_SIZE]
        )

        if not reviews:
            print("No reviews found")
            return

        cleaned_texts = [clean_text(r.review_text) for r in reviews]

        probs = pipeline.predict_proba(cleaned_texts)[:, 1]

        for review, prob in zip(reviews, probs):
            prob = float(prob)
            review.is_fake = prob > THRESHOLD
            review.fake_score = round(prob, 3)
            review.processed = True

        Review.objects.bulk_update(
            reviews,
            ["is_fake", "fake_score", "processed"]
        )

    print(f"Processed {len(reviews)} reviews")

    if len(reviews) == BATCH_SIZE:
        self.retry(countdown=1, max_retries=5)


