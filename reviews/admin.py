from django.contrib import admin
from reviews.models import Review


# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product','source','rating','short_review','is_fake','sentiment_label','review_date']
    list_filter = ('is_fake','sentiment_label','source')
    search_fields = ('review_text','reviewer_name')