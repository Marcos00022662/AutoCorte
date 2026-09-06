"""
URL configuration for AutoCorte project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]


# Arquivos estáticos (CSS, JavaScript, imagens do projeto)
urlpatterns += [
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.BASE_DIR / "core" / "static"
        },
    ),
]


# Arquivos enviados pelo usuário (media/)
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)


handler404 = "core.views.erro_404"