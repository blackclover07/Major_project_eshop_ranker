from rest_framework.decorators import api_view
from rest_framework.response import Response
from reviews.models import Review
from .serializers import ReviewSerializer


# Create your views here.
@api_view(['GET'])
def get_unprocessed_reviews(request):
    limit=int(request.GET.get('limit',100))
    reviews=Review.objects.filter(processed=False)[:limit]
    serializer=ReviewSerializer(reviews,many=True)

    return Response(serializer.data)

@api_view(['POST'])
def update_review(request):
    results=request.data.get('results',[])
    for r in results:
        Review.objects.filter(pk=r['id']).update(is_fake=r['is_fake'],fake_score=r['fake_score'],processed=r['processed'])
    return Response({"Status":"Updated"})