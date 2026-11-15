from django.contrib import admin
from django.urls import include, path
from archive import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("", views.home, name="home"),
    path("match/<int:pk>/", views.match_detail, name="match_detail"),
    path("match/<int:pk>/review/", views.save_review, name="save_review"),
    path("match/<int:pk>/moment/", views.add_moment, name="add_moment"),
    path("review/<int:pk>/like/", views.toggle_like, name="toggle_like"),
    path("me/", views.my_page, name="my_page"),
]
