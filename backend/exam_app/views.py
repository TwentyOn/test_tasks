from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView

from .models import Review
from .serializers import ReviewSerializer


# Create your views here.
class ReviewView(ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
