"""
Представления портфолио.
Единственный публичный view — index: отдаёт весь контент одностраничного лендинга.
Навыки разбиты по категориям, чтобы шаблон не делал групповых вычислений.
Секции с пустыми данными скрываются через {% if %} в шаблонах.
"""
import logging

from django.shortcuts import render

from .models import About, Achievement, Contact, Project, Skill

logger = logging.getLogger(__name__)


def index(request):
    """Главная (и единственная) страница лендинга."""
    context = {
        'about':                About.objects.first(),
        'projects':             Project.objects.filter(is_published=True),
        'achievements':         Achievement.objects.all(),
        'skills_it':            Skill.objects.filter(category='it'),
        'skills_construction':  Skill.objects.filter(category='construction'),
        'skills_security':      Skill.objects.filter(category='security'),
        'contact':              Contact.objects.first(),
    }
    return render(request, 'portfolio/index.html', context)
