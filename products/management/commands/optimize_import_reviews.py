from django.core.management.base import BaseCommand, CommandError
import csv
from decimal import Decimal
from django.utils.dateparse import parse_datetime
from products.models import Product, ProductListing
from reviews.models import Review
from django.db import transaction

import logging
logger = logging.getLogger('importer')


class Command(BaseCommand):
    help = "Imports reviews from CSV file (Optimized Version)"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                logger.info("CSV import started")

                # Preload existing products
                existing_products = {
                    (p.name, p.brand, p.model_number): p
                    for p in Product.objects.all()
                }

                new_products = []
                review_batch = []
                listing_batch = []

                BATCH_SIZE = 1000

                for row in reader:
                    key = (
                        row['name'],
                        row['brand'],
                        row.get('model_number') or None
                    )

                    # PRODUCT
                    product = existing_products.get(key)

                    if not product:
                        product = Product(
                            name=row['name'],
                            brand=row['brand'],
                            model_number=row.get('model_number') or None,
                            category=row.get('category'),
                            subcategory=row.get('subcategory'),
                            launch_year=row.get('launch_year') or None,
                        )
                        new_products.append(product)
                        existing_products[key] = product

                    # LISTING
                    listing_batch.append(
                        ProductListing(
                            product=product,
                            source=row.get('source'),
                            price=Decimal(row['price']) if row.get('price') else None,
                            product_url=row.get('product_url'),
                            last_updated=parse_datetime(row.get('last_updated'))
                            if row.get('last_updated') else None,
                        )
                    )

                    # REVIEW
                    review_batch.append(
                        Review(
                            product=product,
                            review_text=row['review_text'],
                            reviewer_name=row.get('reviewer_name'),
                            rating=row.get('rating') or None,
                            review_date=row.get('review_date') or None,
                            source=row.get('source') or 'csv_import',
                        )
                    )

                    # Batch Insert
                    if len(review_batch) >= BATCH_SIZE:
                        self._bulk_insert(new_products, listing_batch, review_batch)
                        new_products.clear()
                        listing_batch.clear()
                        review_batch.clear()

                # Insert remaining
                self._bulk_insert(new_products, listing_batch, review_batch)

                logger.info("CSV importing completed")
                self.stdout.write(self.style.SUCCESS('Successfully imported reviews'))

        except FileNotFoundError:
            raise CommandError('CSV file not found')

        except Exception as e:
            raise CommandError(f'Error: {str(e)}')

    @transaction.atomic
    def _bulk_insert(self, new_products, listing_batch, review_batch):

        # 1️⃣ Save new products first
        if new_products:
            Product.objects.bulk_create(new_products, ignore_conflicts=True)

        # 2️⃣ Reload products with IDs
        product_keys = [
            (p.name, p.brand, p.model_number)
            for p in new_products
        ]

        if product_keys:
            refreshed_products = {
                (p.name, p.brand, p.model_number): p
                for p in Product.objects.filter(
                    name__in=[k[0] for k in product_keys]
                )
            }

            # 3️⃣ Update product references in listings & reviews
            for listing in listing_batch:
                key = (
                    listing.product.name,
                    listing.product.brand,
                    listing.product.model_number
                )
                listing.product = refreshed_products.get(key)

            for review in review_batch:
                key = (
                    review.product.name,
                    review.product.brand,
                    review.product.model_number
                )
                review.product = refreshed_products.get(key)

        # 4️⃣ Now safe to insert related objects
        if listing_batch:
            ProductListing.objects.bulk_create(listing_batch, ignore_conflicts=True)

        if review_batch:
            Review.objects.bulk_create(review_batch, batch_size=1000)