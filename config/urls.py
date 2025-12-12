from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=settings.STATIC_URL + "favicon/favicon.ico", permanent=True
        ),
        name="favicon",
    ),
    path("users/", include("users.urls")),
    path("", include("notes.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
