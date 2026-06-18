from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Email"))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {"username": _("Username")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = _("Password")
        self.fields["password2"].label = _("Password confirmation")


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": _("Wrong username or password."),
        "inactive": _("This account is inactive."),
    }

    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
