from django.core.management.base import BaseCommand, CommandError
import csv
from decimal import Decimal
from django.utils.dateparse import parse_datetime
from products.models import Product, ProductListing
from reviews.models import Review

import logging
logger=logging.getLogger('importer')



class Command(BaseCommand):
    help = "Imports reviews from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:

                reader = csv.DictReader(csvfile)

                logger.info("csv import started")
                for row in reader:

                    # PRODUCT
                    product, created = Product.objects.get_or_create(
                        name=row['name'],
                        brand=row['brand'],
                        model_number=row.get('model_number') or None,
                        defaults={
                            'category': row.get('category'),
                            'subcategory': row.get('subcategory'),
                            'launch_year': row.get('launch_year') or None,
                        }
                    )

                    if created:
                        logger.info(f"created product : {product.name}")
                    else:
                        logger.info(f"product already exists : {product.name}")

                    # PRODUCT LISTING
                    ProductListing.objects.update_or_create(
                        product=product,
                        source=row.get('source'),
                        defaults={
                            'price': Decimal(row['price']) if row.get('price') else None,
                            'product_url': row.get('product_url'),
                            'last_updated': parse_datetime(row.get('last_updated')) if row.get('last_updated') else None,
                        }
                    )
                    logger.info(f"listing updated : {product.name} - {row.get('source')}")

                    # REVIEW
                    Review.objects.get_or_create(
                        product=product,
                        review_text=row['review_text'],
                        reviewer_name=row.get('reviewer_name'),
                        defaults={
                            'rating': row.get('rating') or None,
                            'review_date': row.get('review_date') or None,
                            'source': row.get('source') or 'csv_import',
                        }
                    )
                    logger.info(f"Review added for: {product.name}")

            # self.stdout.write(self.style.SUCCESS('Successfully imported reviews'))
            logger.info("csv importing completed")
            self.stdout.write(self.style.SUCCESS('Successfully imported reviews'))
        except FileNotFoundError:
            raise CommandError('CSV file not found')

        except Exception as e:
            raise CommandError(f'Error: {str(e)}')
