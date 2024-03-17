from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.entry, name="entry"),
    path("search/", views.title_search, name="title_search"),
    path("new/", views.new_page, name="new_page"),
    path("edit/<str:title>", views.edit_page, name="edit_page"),
    path("save_edit/", views.save_edit, name="save_edit"),
    path("random_page/", views.random_page, name="random_page"),

]
