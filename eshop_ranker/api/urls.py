from django.urls import path
from . import views
urlpatterns = [
    path('reviews/unprocessed',views.get_unprocessed_reviews,name='unprocessed_reviews'),
    path('reviews/update',views.update_review,name='update_reviews'),
]
