from transformers import pipeline
import torch
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

def preprocess(text):
    text = text.lower()
    text = re.sub(r'http\S+', 'http', text)
    text = re.sub(r'@\w+', '@user', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


BATCH_SIZE = 8

# Load pipeline once globally
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=MODEL,
    tokenizer=MODEL,
    device=-1
)
print(" Sentiment analyzer Model loaded Successfully")

@app.task(bind=True)
def sentiment_analysis_func(self):
    with transaction.atomic():

        reviews = list(
            Review.objects
            .select_for_update(skip_locked=True)
            .filter(sentiment_checked=False)
            .only("id", "review_text")[:BATCH_SIZE]
        )
        if not reviews:
            print("No reviews found")
            return

        print("Reviews found")
        texts = [preprocess(r.review_text or " ") for r in reviews]

        # Run inference using pipeline
        results = sentiment_pipeline(texts, truncation=True, max_length=256)

        # Update reviews
        for review, result in zip(reviews, results):
            review.sentiment_label = result['label'].upper()
            review.sentiment_score = float(result['score'])
            review.sentiment_checked = True

        Review.objects.bulk_update(
            reviews,
            ["sentiment_label", "sentiment_score", "sentiment_checked"]
        )

        print(f"Processed {len(reviews)} reviews")

        if len(reviews) == BATCH_SIZE:
            sentiment_analysis_func.delay()