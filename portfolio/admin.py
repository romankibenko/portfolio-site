"""
Регистрация моделей в Django Admin.

Особенности:
- SingletonModelAdmin — базовый класс для About и Contact:
    * has_add_permission() → False, если объект уже существует.
    * changelist_view() → редирект на change-страницу единственного объекта.
- ProjectAdmin — search_fields, list_filter, list_editable для order и is_published.
- AchievementAdmin / SkillAdmin — list_editable для order.

КОМПРОМИСС: Стандартный django.contrib.admin использует inline JS и inline CSS,
поэтому CSP-заголовок для /admin/ должен содержать 'unsafe-inline'.
Это приемлемо, т.к. путь /admin/ закрыт от публики и защищён авторизацией.
"""
import logging

from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from .models import About, Achievement, Contact, Project, Skill

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Вспомогательный базовый класс для singleton-моделей
# ---------------------------------------------------------------------------
class SingletonModelAdmin(admin.ModelAdmin):
    """
    Запрещает создание второго объекта и перенаправляет список → change-форму.
    Наследуйте этот класс для About и Contact.
    """

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Разрешаем добавление только если объект ещё не существует."""
        return not self.model.objects.exists()

    def changelist_view(self, request: HttpRequest, extra_context=None):
        """
        Если объект уже создан — сразу переходим на страницу редактирования.
        Если объекта нет — показываем кнопку «Добавить» (стандартный список).
        """
        obj = self.model.objects.first()
        if obj is not None:
            app = self.model._meta.app_label
            model = self.model._meta.model_name
            url = reverse(f'admin:{app}_{model}_change', args=[obj.pk])
            return redirect(url)
        return super().changelist_view(request, extra_context)


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
@admin.register(About)
class AboutAdmin(SingletonModelAdmin):
    list_display = ('__str__', 'has_photo')
    readonly_fields = ('has_photo',)

    @admin.display(description='Фото загружено', boolean=True)
    def has_photo(self, obj: About) -> bool:
        return bool(obj.photo)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'year', 'order', 'is_published')
    list_editable = ('order', 'is_published')
    list_filter = ('kind', 'year', 'is_published')
    search_fields = ('title', 'description')
    ordering = ('order', '-year')

    # Разбивка полей в форме редактирования для удобства.
    fieldsets = (
        (None, {
            'fields': ('title', 'kind', 'year', 'is_published', 'order'),
        }),
        ('Содержимое', {
            'fields': ('description', 'image'),
        }),
        ('Ссылки', {
            'fields': ('repo_url', 'live_url'),
        }),
    )


# ---------------------------------------------------------------------------
# Achievement
# ---------------------------------------------------------------------------
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'order')
    list_editable = ('order',)
    ordering = ('order',)


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order')
    list_editable = ('order',)
    list_filter = ('category',)
    ordering = ('category', 'order')


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------
@admin.register(Contact)
class ContactAdmin(SingletonModelAdmin):
    list_display = ('__str__', 'telegram_username', 'email', 'telegram_url_preview')
    readonly_fields = ('telegram_url_preview',)

    @admin.display(description='Ссылка Telegram')
    def telegram_url_preview(self, obj: Contact) -> str:
        return obj.telegram_url or '—'
