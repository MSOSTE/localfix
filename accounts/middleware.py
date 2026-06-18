from django.utils import translation
from django.utils.translation import check_for_language


class PreferredLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, "user", None)
        language = translation.get_language()

        # Keep the profile language in sync with the active site language.
        if user and user.is_authenticated and language and check_for_language(language):
            profile = user.profile
            if profile.preferred_language != language:
                profile.preferred_language = language
                profile.save(update_fields=["preferred_language"])

        return response
