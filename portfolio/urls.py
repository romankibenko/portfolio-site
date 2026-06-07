"""URL-маршруты приложения portfolio."""
from django.urls import path

from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.index, name='index'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
