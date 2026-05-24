"""
Модели контента портфолио.

Паттерны:
- Singleton (About, Contact): запрет второго объекта через save().
- choices-перечни: PROJECT_KIND_CHOICES, SKILL_CATEGORY_CHOICES.
- Свойство Contact.telegram_url собирает ссылку из username.
"""
import logging

from django.db import models

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# About — singleton: «О себе»
# ---------------------------------------------------------------------------
class About(models.Model):
    """
    Единственная запись с вводным текстом и фотографией владельца.
    Переносы строк в intro_text рендерятся через шаблонный фильтр |linebreaks.
    """
    intro_text = models.TextField(
        verbose_name='Вводный текст',
        help_text='Поддерживаются переносы строк (Enter). Используйте |linebreaks в шаблоне.',
    )
    photo = models.ImageField(
        upload_to='about/',
        blank=True,
        null=True,
        verbose_name='Фото',
        help_text='Рекомендуемый размер: 400×400 px, формат WEBP/JPEG.',
    )

    class Meta:
        verbose_name = 'О себе'
        verbose_name_plural = 'О себе'

    def __str__(self) -> str:
        return 'О себе'

    def save(self, *args, **kwargs):
        if not self.pk and About.objects.exists():
            raise ValueError(
                'Может существовать только один экземпляр About. '
                'Отредактируйте существующий объект.'
            )
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Project — проекты (строительные и IT)
# ---------------------------------------------------------------------------
class Project(models.Model):
    PROJECT_KIND_CHOICES = [
        ('construction', 'Строительство'),
        ('it', 'IT'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    kind = models.CharField(
        max_length=20,
        choices=PROJECT_KIND_CHOICES,
        verbose_name='Тип',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год',
    )
    image = models.ImageField(
        upload_to='projects/',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Меньшее число — выше в списке.',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликован',
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['order', '-year']

    def __str__(self) -> str:
        return f'{self.title} ({self.year})'


# ---------------------------------------------------------------------------
# Achievement — цифровые показатели («50 000 м² сданных объектов», «12+ лет»)
# ---------------------------------------------------------------------------
class Achievement(models.Model):
    value = models.CharField(
        max_length=50,
        verbose_name='Значение',
        help_text='Например: "50 000", "12+", "8". Хранится как строка.',
    )
    label = models.CharField(
        max_length=200,
        verbose_name='Подпись',
        help_text='Например: "м² сданных объектов", "лет опыта".',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок',
    )

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['order']

    def __str__(self) -> str:
        return f'{self.value} — {self.label}'


# ---------------------------------------------------------------------------
# Skill — навыки по категориям
# ---------------------------------------------------------------------------
class Skill(models.Model):
    SKILL_CATEGORY_CHOICES = [
        ('it', 'IT-разработка'),
        ('construction', 'Строительство'),
        ('security', 'Кибербезопасность'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Навык',
    )
    category = models.CharField(
        max_length=20,
        choices=SKILL_CATEGORY_CHOICES,
        verbose_name='Категория',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок',
    )

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['category', 'order']

    def __str__(self) -> str:
        return f'{self.get_category_display()} / {self.name}'


# ---------------------------------------------------------------------------
# Contact — singleton: контактная информация
# ---------------------------------------------------------------------------
class Contact(models.Model):
    """
    Единственная запись с контактами.
    Каждая кнопка в шаблоне рендерится только при заполненном поле.
    """
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Telegram username',
        help_text='Без символа @. Например: ivan_ivanov',
    )
    max_url = models.URLField(
        blank=True,
        verbose_name='Ссылка Max',
        help_text='Полный URL профиля в мессенджере Max (ex-VK Мессенджер).',
    )
    email = models.EmailField(
        blank=True,
        verbose_name='E-mail',
    )

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'

    def __str__(self) -> str:
        return 'Контакты'

    def save(self, *args, **kwargs):
        if not self.pk and Contact.objects.exists():
            raise ValueError(
                'Может существовать только один экземпляр Contact. '
                'Отредактируйте существующий объект.'
            )
        super().save(*args, **kwargs)

    @property
    def telegram_url(self) -> str | None:
        """Возвращает полную ссылку t.me/… или None, если username не задан."""
        if self.telegram_username:
            return f'https://t.me/{self.telegram_username}'
        return None
