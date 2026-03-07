from django.urls import path
from .views import ReviewView, RetrieveReviewView

urlpatterns = [
    path('product/<slug:product_slug>/reviews/', ReviewView.as_view()),
    path('product/<slug:product_slug>/reviews/<str:review_id>/', RetrieveReviewView.as_view()),
]