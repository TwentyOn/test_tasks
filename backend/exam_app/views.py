from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.utils import IntegrityError

from .models import Review
from sellers.models import Product
from .serializers import ReviewSerializer

tags = ['Отзывы']


# Create your views here.
class ReviewView(ListAPIView, GenericAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Запрос всех отзывов к товару",
        description="""
            Эта конечная точка возвращает отзывы к товару.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создание отзыва к товару",
        description="""
            Эта конечная точка создает отзыв к товару.
        """,
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('product_slug')
        product = Product.objects.get_or_none(slug=product_slug, is_deleted=False)

        if not product:
            return Response({'detail': 'продукт не найден'}, status=404)

        serializer = self.serializer_class(data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save(product=product, user=request.user)
                return Response(serializer.data, status=201)
        except IntegrityError as err:
            return Response({'detail': str(err)}, status=400)


class RetrieveReviewView(UpdateModelMixin, GenericAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'review_id'

    @extend_schema(
        summary="Изменение отзыва к товару",
        description="""
                Эта конечная точка изменяет отзыв к товару.
            """,
        tags=tags,
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление отзыва к товару",
        description="""
                Эта конечная точка удаляет отзыв к товару.
            """,
        tags=tags,
    )
    def delete(self, request, *args, **kwargs):
        product_slug = kwargs.get('product_slug')
        product = Product.objects.get_or_none(slug=product_slug, is_deleted=False)

        review_id = kwargs.get('review_id')
        review = Review.objects.get_or_none(id=review_id, is_deleted=False)

        if not product:
            return Response({'detail': 'продукт не найден'}, status=404)
        elif not review:
            return Response({'detail': 'отзыв не найден'}, status=404)

        if review.user != request.user:
            return Response(data={"detail": "Действие невозможно"}, status=400)

        review.delete()
        return Response(status=204)
