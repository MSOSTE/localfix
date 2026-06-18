"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from core.error_views import page_not_found

urlpatterns = [
    # POST: change language
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    # GET/POST: Django admin
    path("admin/", admin.site.urls),
    # Account endpoints
    path("accounts/", include("accounts.urls")),
    # Main app endpoints
    path("", include("core.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # GET: local custom 404 preview
    urlpatterns += [re_path(r"^.*$", page_not_found)]
else:
    # GET: uploaded media files in the Docker deployment
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]

handler403 = "core.error_views.permission_denied"
handler404 = "core.error_views.page_not_found"
