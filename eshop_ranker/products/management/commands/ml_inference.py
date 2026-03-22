from django.core.management.base import BaseCommand, CommandError
import requests
from reviews.models import Review


class Command(BaseCommand):
    help = 'Inference ML model'

    def handle(self, *args, **options):
        reviews = list(Review.objects.filter(processed=False))
        print("Unprocessed Reviews count : ",reviews.count())

        texts=[r.review_text for r in reviews]
        if not texts:
            print("No reviews found")
            return


        url="http://127.0.0.1:4000/reviews"
        response = requests.post(url,json={"items":texts})

        results=response.json()["results"]
        print("Inference ML model results : ",results)
        for review,result in zip(reviews,results):
            review.is_fake = result['Flag']
            review.fake_score = round(result['Fake_score'],3)
            review.processed = True
            review.save()
        self.stdout.write(self.style.SUCCESS('Inference ML process completed successfully'))
