"""
ASGI config for portfolio_site project.
Сайт не использует WebSocket/async, но файл нужен для совместимости
с некоторыми серверами (uvicorn, daphne).
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_site.settings')

application = get_asgi_application()
