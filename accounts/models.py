from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    class Role(models.TextChoices):
        USER = "user", _("User")
        MODERATOR = "moderator", _("Moderator")

    class Language(models.TextChoices):
        LATVIAN = "lv", _("Latvian")
        ENGLISH = "en", _("English")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    preferred_language = models.CharField(max_length=5, choices=Language.choices, default=Language.LATVIAN)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Every user gets a role record automatically.
        Profile.objects.create(user=instance)
