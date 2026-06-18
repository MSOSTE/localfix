from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import translate_url
from django.utils import translation
from django.utils.translation import check_for_language
from django.views.i18n import set_language

from .forms import LoginForm, RegisterForm


def set_language_cookie(response, language):
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.preferred_language = translation.get_language()
            user.profile.save(update_fields=["preferred_language"])
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        language = self.request.user.profile.preferred_language
        if check_for_language(language):
            set_language_cookie(response, language)
            if response.has_header("Location"):
                response["Location"] = translate_url(response["Location"], language)
        return response


class UserLogoutView(LogoutView):
    pass


def set_preferred_language(request):
    if request.method == "POST" and request.user.is_authenticated:
        language = request.POST.get("language")
        if language and check_for_language(language):
            request.user.profile.preferred_language = language
            request.user.profile.save(update_fields=["preferred_language"])

    return set_language(request)
