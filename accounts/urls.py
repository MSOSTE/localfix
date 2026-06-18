from django.urls import path

from .views import UserLoginView, UserLogoutView, register_view, set_preferred_language

urlpatterns = [
    # GET: register form, POST: create account
    path("register/", register_view, name="register"),
    # GET: login form, POST: log in
    path("login/", UserLoginView.as_view(), name="login"),
    # POST: log out
    path("logout/", UserLogoutView.as_view(), name="logout"),
    # POST: change language and save it in the user profile
    path("language/", set_preferred_language, name="set_preferred_language"),
]
