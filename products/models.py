from django.db import models


# Create your models here.

class Product(models.Model):
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering =['-created_at']
        unique_together = ('name','brand','model_number')

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('beauty', 'Beauty'),
        ('home', 'Home'),
    ]

    # core identity
    name=models.CharField(max_length=255)
    brand=models.CharField(max_length=255)

    # category hierarchy
    category=models.CharField(max_length=100,choices=CATEGORY_CHOICES)
    subcategory=models.CharField(max_length=100)

    # optional metadata
    launch_year=models.IntegerField(null=True,blank=True)

    # exact model
    model_number=models.CharField(max_length=100,null=True,blank=True)

    # system fields
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} | {self.brand} | {self.category} | {self.subcategory}"


class ProductListing(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='listings')

    source = models.CharField(max_length=100)  # amazon, flipkart

    price = models.DecimalField(max_digits=10, decimal_places=2)

    product_url = models.URLField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'source']
