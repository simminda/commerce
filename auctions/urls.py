from django.urls import path
from .views import filtered_listings, search_listings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('post_ad/', views.create_listing, name='post_ad'),
    path('listing/<str:listing_name>/', views.view_listing, name='view_listing'),
    path('listing/<str:listing_name>/delete/',
         views.delete_listing, name='delete_listing'),
    path('listings/category/<str:category_name>/',
         filtered_listings, name='filtered_listings'),
    path('place_bid/<str:listing_name>/', views.place_bid, name='place_bid'),
    path('add_to_wishlist/<str:listing_name>/',
         views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<str:listing_name>/',
         views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('search/', search_listings, name='search_listings'),
    path('listing/<str:listing_name>/close/',
         views.close_auction, name='close_auction')
]
