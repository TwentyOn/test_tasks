from django.urls import path

from .views import SellerProductsView, SellersView, CategoriesView

urlpatterns = [
    path('sellers/', SellersView.as_view()),
    path('sellers/products/', SellerProductsView.as_view()),
    path('categories/', CategoriesView.as_view())
]