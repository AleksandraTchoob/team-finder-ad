from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("list/", views.participants_list_view, name="participants_list"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("<int:pk>/", views.user_detail_view, name="user_detail"),
]
