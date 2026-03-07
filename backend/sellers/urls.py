from django.urls import path

from .views import SellerProductsView, SellersView

urlpatterns = [
    path('seller/', SellersView.as_view()),
    path('product/', SellerProductsView.as_view())
]