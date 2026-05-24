"""
URL-конфигурация проекта portfolio_site.

Медиафайлы раздаются Django только в DEBUG-режиме (settings.DEBUG=True).
На проде статику и медиа отдаёт Nginx — см. DEPLOY.md.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls', namespace='portfolio')),
]

# В продакшене (DEBUG=False) эти строки не добавляют ничего — static() вернёт [].
# КОМПРОМИСС: для локальной разработки удобнее держать это здесь, а не в Nginx.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
