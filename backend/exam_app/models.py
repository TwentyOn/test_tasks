from django.db import models
from django.contrib.auth.models import User

from common.models import IsDeletedModel
from sellers.models import Product

RATING_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))


class Review(IsDeletedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.CharField()

    class Meta:
        unique_together = [('user', 'product')]
