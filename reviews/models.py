from django.db import models
from products.models import Product
from django.template.defaultfilters import truncatewords


# Create your models here.
class Review(models.Model):
    class Meta:
        verbose_name= 'review'
        verbose_name_plural = 'reviews'
        ordering = ['-created_at']

    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')

    # core review content
    rating=models.FloatField(null=True,blank=True)
    review_text=models.TextField()

    @property
    def short_review(self):
        return truncatewords(self.review_text,10)

    # reviewer metadata
    reviewer_name=models.CharField(max_length=100,blank=True,null=True)
    source=models.CharField(max_length=100,blank=True,null=True)
    review_date=models.DateField(blank=True,null=True)


    # ml inputs (filled later)
    sentiment_label=models.CharField(max_length=100,blank=True,null=True)
    sentiment_score=models.FloatField(blank=True,null=True)
    is_fake=models.BooleanField(null=True,blank=True)
    fake_score=models.FloatField(blank=True,null=True)

    # system fields
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product} - {self.rating} - {self.review_text}"

