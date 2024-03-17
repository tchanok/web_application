
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profile/<int:user_id>", views.view_profile, name="view_profile"),
    path("following", views.view_following, name="following"),
    # API route
    path("follow", views.toggle_follow, name="follow"),
    path("like", views.toggle_like, name="like"),
    path("edit_post", views.edit_post, name="edit_post"),
]
