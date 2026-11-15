from django.contrib import admin
from django.urls import include, path
from archive import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("", views.home, name="home"),
    path("match/<int:pk>/", views.match_detail, name="match_detail"),
    path("match/<int:pk>/player/<int:player_pk>/rating/", views.save_player_rating, name="save_player_rating"),
    path("me/", views.my_page, name="my_page"),
]
