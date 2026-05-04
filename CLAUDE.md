# Portfolio Site

Одностраничный сайт-портфолио. Темы: руководство строительными проектами,
веб- и Java-разработка, кибербезопасность. Без форм — только ссылки
в мессенджеры.

## Стек

- Python 3.12, Django 5.1
- PostgreSQL 16 (прод), SQLite (локально)
- TailwindCSS v4 через npm, vanilla JS, inline SVG
- python-dotenv, Pillow
- Без DRF, JS-фреймворков, CDN-ассетов и платных библиотек

## Структура

- Проект: portfolio_site, приложение: portfolio
- Модели: About (singleton), Project, Achievement, Skill, Contact (singleton)
- Шаблоны: portfolio/templates/portfolio/ (base.html + index.html + partials/_*.html)
- CSS: static_src/input.css → portfolio/static/portfolio/css/output.css
- Фикстуры: portfolio/fixtures/initial_data.json

## Соглашения

- Секреты только через .env (SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS, DEBUG)
- В продакшене DEBUG=False, активны SECURE_*-настройки
- Singleton-модели: запрет второго объекта в save() и has_add_permission
- Внешние ссылки: target="_blank" rel="noopener"
- Изображения: {% if obj.image %} с обязательным alt
- Пустые секции (нет данных в БД) скрываются целиком
- Места компромиссов (например, CSP unsafe-inline) — комментировать
- Логирование через logging, не print()

## Команды

- python manage.py runserver
- python manage.py makemigrations && python manage.py migrate
- python manage.py loaddata portfolio/fixtures/initial_data.json
- python manage.py check / check --deploy
- npm run dev / npm run build

## Дизайн-токены

CSS-переменные в @layer base:
--bg #0F1115, --text #E6E8EB, --text-muted #9AA0A6,
--accent #2D6A4F, --accent-it #4FB3BF,
--accent-construction #C99A3A, --border rgba(255,255,255,0.08)
Использовать через bg-[var(--accent)] или extend в tailwind.config.js.

## Не делать

- Формы, регистрацию, сбор персональных данных
- Внешние шрифты, Google Fonts, CDN-скрипты
- localStorage / sessionStorage
- JS-фреймворки и тяжёлые библиотеки
- Коммитить .env, node_modules/, output.css, staticfiles/, media/, db.sqlite3

## Рабочий процесс

1. Сначала прочитать релевантные файлы, потом писать код
2. При неоднозначности — уточнить, не угадывать
3. Минимальные правки, не переписывать соседний код
4. После моделей — напомнить про makemigrations
5. После шаблонов/CSS — напомнить про npm run build
6. Новая функциональность — сначала план, потом код

## Дополнительные файлы

- DEPLOY.md — инструкция по деплою на Debian 12
