from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("my_listing", views.my_listing, name="my_listing"),
    path("bidded_listing", views.bidded_listing, name="bidded_listing"),
    path("category", views.display_category, name="display_category"),
    path("listing/<int:listing_id>", views.listing_page, name="listing_page"),
    path("remove_watchlist/<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("add_watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("my_watchlist", views.display_watchlist, name="my_watchlist"),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("add_bid/<int:listing_id>", views.add_bid, name="add_bid"),
    path("close_bid/<int:listing_id>", views.close_bid, name="close_bid"),
]
