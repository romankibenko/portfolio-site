# Деплой portfolio_site на Debian 12

Стек: Python 3.12 · Django 5.1 · PostgreSQL 16 · Gunicorn · Nginx · Certbot · Node.js 20

Все команды помечены:
- `# VDS` — выполнять на сервере
- `$ local` — выполнять локально на своём компьютере

---

## 0. Предварительные требования

- VDS с Debian 12 (bookworm), минимум **1 ГБ RAM**, 20 ГБ диск
- Купленный домен (далее `example.ru`) с **A-записью**, указывающей на IP VDS
- SSH-доступ под root или пользователем с sudo
- Проект запушен на GitHub

---

## 1. Первичная настройка сервера

### 1.1 Обновить систему

```bash
# VDS (под root)
apt update && apt upgrade -y
apt install -y sudo curl wget gnupg2 lsb-release ca-certificates ufw fail2ban
```

### 1.2 Создать пользователя deploy

```bash
# VDS
adduser deploy
usermod -aG sudo deploy
```

### 1.3 Настроить SSH-ключ для deploy

```bash
# VDS
mkdir -p /home/deploy/.ssh
echo "ВАШ_ПУБЛИЧНЫЙ_КЛЮЧ" >> /home/deploy/.ssh/authorized_keys
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
```

> Проверьте, что можно войти: `ssh deploy@IP_VDS` — прежде чем закрывать root-сессию.

### 1.4 Файрвол ufw

```bash
# VDS
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status
```

### 1.5 fail2ban

```bash
# VDS
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled  = true
port     = ssh
maxretry = 5
bantime  = 1h
EOF

systemctl enable --now fail2ban
fail2ban-client status sshd
```

---

## 2. Установка системных пакетов

Дальше работаем под пользователем **deploy**:

```bash
# VDS
su - deploy
```

### 2.1 Python 3.12 через pyenv (рекомендуется)

Debian 12 идёт с Python 3.11. Для точного совпадения с разработкой
установите 3.12 через **pyenv**.

> **Альтернатива:** если 3.11 устраивает — пропустите этот раздел.
> Django 5.1 работает на 3.11. Замените `python` на `python3` в командах ниже.

```bash
# VDS — зависимости сборки Python
sudo apt install -y build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev git
```

```bash
# VDS — установить pyenv
curl https://pyenv.run | bash
```

```bash
# VDS — добавить в ~/.bashrc
cat >> ~/.bashrc << 'EOF'
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
EOF

source ~/.bashrc
```

```bash
# VDS — установить Python 3.12
pyenv install 3.12.9
pyenv global 3.12.9
python --version   # Python 3.12.9
```

**Если ошибка при `pyenv install`:** не хватает зависимостей сборки.
Повторите `sudo apt install -y build-essential libssl-dev zlib1g-dev libffi-dev` и попробуйте снова.

### 2.2 PostgreSQL 16

```bash
# VDS — официальный репозиторий
sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list'
wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    | sudo tee /etc/apt/trusted.gpg.d/postgresql.asc > /dev/null
sudo apt update
sudo apt install -y postgresql-16
sudo systemctl enable --now postgresql
```

### 2.3 Nginx

```bash
# VDS
sudo apt install -y nginx
sudo systemctl enable --now nginx
```

### 2.4 Certbot

```bash
# VDS
sudo apt install -y certbot python3-certbot-nginx
```

### 2.5 Node.js 20 LTS

```bash
# VDS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version   # v20.x.x
```

---

## 3. Настройка PostgreSQL

```bash
# VDS
sudo -u postgres psql
```

Внутри psql:

```sql
CREATE DATABASE portfolio_db;
CREATE USER portfolio_user WITH PASSWORD 'СИЛЬНЫЙ_ПАРОЛЬ';
ALTER ROLE portfolio_user SET client_encoding TO 'utf8';
ALTER ROLE portfolio_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE portfolio_user SET timezone TO 'Europe/Moscow';
GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO portfolio_user;
\c portfolio_db
GRANT ALL ON SCHEMA public TO portfolio_user;
\q
```

```bash
# VDS
sudo systemctl restart postgresql
```

**Если ошибка подключения:** проверьте `/etc/postgresql/16/main/pg_hba.conf` —
должна быть строка `host all all 127.0.0.1/32 scram-sha-256`.
После изменений: `sudo systemctl reload postgresql`.

---

## 4. Получение кода

```bash
# VDS
cd /home/deploy
git clone https://github.com/ВАШ_АККАУНТ/portfolio_site.git
cd portfolio_site
```

```bash
# VDS — виртуальное окружение
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
# VDS — PostgreSQL-адаптер (выберите один вариант)
# Быстрый старт:
pip install psycopg2-binary==2.9.10
# Рекомендуется для прода (требует libpq-dev):
# sudo apt install -y libpq-dev && pip install psycopg2==2.9.10
```

---

## 5. Настройка .env

```bash
# VDS
cp .env.example .env
nano .env
```

```dotenv
SECRET_KEY=СГЕНЕРИРОВАННЫЙ_КЛЮЧ
DEBUG=False
ALLOWED_HOSTS=example.ru,www.example.ru

DB_ENGINE=django.db.backends.postgresql
DB_NAME=portfolio_db
DB_USER=portfolio_user
DB_PASSWORD=СИЛЬНЫЙ_ПАРОЛЬ
DB_HOST=localhost
DB_PORT=5432
```

Сгенерировать `SECRET_KEY`:

```bash
# VDS
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 6. Сборка Tailwind

```bash
# VDS
npm ci
```

```bash
# VDS
npm run build
```

```bash
# VDS — убедиться что файл создан
ls -lh portfolio/static/portfolio/css/output.css
```

**Если ошибка `npm ci`:** `package-lock.json` не закоммичен. Запустите `npm install` вместо `npm ci`, затем закоммитьте `package-lock.json`.

---

## 7. Django: миграции, статика, данные, суперпользователь

```bash
# VDS
source .venv/bin/activate
python manage.py migrate
```

```bash
# VDS — загрузить демо-данные (опционально)
python manage.py loaddata portfolio/fixtures/initial_data.json
```

```bash
# VDS
python manage.py collectstatic --noinput
```

```bash
# VDS
python manage.py createsuperuser
```

```bash
# VDS — финальная проверка
python manage.py check --deploy
```

> После certbot предупреждения о HSTS/SSL исчезнут. Пока их увидеть — нормально.

---

## 8. Gunicorn как systemd-сервис

```bash
# VDS
sudo cp /home/deploy/portfolio_site/deploy/gunicorn.socket \
        /etc/systemd/system/gunicorn.socket

sudo cp /home/deploy/portfolio_site/deploy/gunicorn.service \
        /etc/systemd/system/gunicorn.service
```

```bash
# VDS
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn.socket
sudo systemctl status gunicorn.socket
```

```bash
# VDS — проверить что Gunicorn отвечает
curl --unix-socket /run/gunicorn.sock http://localhost/
# Должны увидеть HTML (без CSS — это нормально, CSS раздаёт Nginx)
```

**Если сокет не создаётся:**

```bash
# VDS
sudo journalctl -u gunicorn.socket -n 50 --no-pager
```

**Если Gunicorn падает:**

```bash
# VDS
sudo journalctl -u gunicorn -n 50 --no-pager
# Чаще всего причина: ошибка в .env или не установлен psycopg2
```

---

## 9. Nginx

```bash
# VDS
sudo cp /home/deploy/portfolio_site/deploy/nginx-portfolio \
        /etc/nginx/sites-available/portfolio

# Заменить example.ru на свой домен
sudo nano /etc/nginx/sites-available/portfolio
```

```bash
# VDS
sudo ln -s /etc/nginx/sites-available/portfolio \
           /etc/nginx/sites-enabled/portfolio
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## 10. SSL через Certbot

```bash
# VDS
sudo certbot --nginx -d example.ru -d www.example.ru
```

Certbot спросит email и предложит редирект HTTP→HTTPS — выберите **2 (Redirect)**.

### 10.1 Добавить заголовки безопасности и location-блоки

После того как certbot изменил конфиг, откройте файл и добавьте
в `server { listen 443 ssl ... }` блок:

```bash
# VDS
sudo nano /etc/nginx/sites-available/portfolio
```

Добавьте внутрь HTTPS-блока:

```nginx
client_max_body_size 10M;
server_tokens off;

location /static/ {
    alias /home/deploy/portfolio_site/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /home/deploy/portfolio_site/media/;
    expires 7d;
}

location / {
    include proxy_params;
    proxy_pass http://unix:/run/gunicorn.sock;
    proxy_read_timeout 60s;
}

add_header X-Frame-Options        "DENY"                            always;
add_header X-Content-Type-Options "nosniff"                         always;
add_header Referrer-Policy        "strict-origin-when-cross-origin" always;
add_header Permissions-Policy     "geolocation=(), microphone=()"   always;

# CSP — настраивается здесь (не в Django), см. комментарий в settings.py.
# КОМПРОМИСС: 'unsafe-inline' нужен для inline JS бургер-меню,
# JSON-LD Schema.org и стилей Django Admin.
add_header Content-Security-Policy
    "default-src 'self'; script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
    "font-src 'self'; connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
    always;
```

```bash
# VDS
sudo nginx -t && sudo systemctl reload nginx
```

### 10.2 Проверить автообновление сертификата

```bash
# VDS
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

---

## 11. Бэкап

```bash
# VDS
cp /home/deploy/portfolio_site/deploy/backup.sh /home/deploy/backup.sh
chmod +x /home/deploy/backup.sh
mkdir -p /home/deploy/backups
```

```bash
# VDS — проверить вручную
/home/deploy/backup.sh
ls -lh /home/deploy/backups/
```

```bash
# VDS — добавить в crontab
crontab -e
```

Добавить строку:

```cron
0 3 * * * /home/deploy/backup.sh >> /home/deploy/backups/backup.log 2>&1
```

---

## 12. Обновление кода (при каждом релизе)

```bash
# VDS
cd /home/deploy/portfolio_site && source .venv/bin/activate
git pull origin main
```

```bash
# VDS
pip install -r requirements.txt
```

```bash
# VDS
npm ci && npm run build
```

```bash
# VDS
python manage.py migrate
```

```bash
# VDS
python manage.py collectstatic --noinput
```

```bash
# VDS
sudo systemctl restart gunicorn
```

---

## Чеклист после деплоя

- [ ] `https://example.ru` открывается, редирект с HTTP работает
- [ ] Сертификат SSL действителен (замок в браузере)
- [ ] `https://example.ru/admin/` открывается, вход работает
- [ ] CSS и favicon грузятся (DevTools → Network)
- [ ] `python manage.py check --deploy` — **0 issues**
- [ ] `curl -I https://example.ru` — заголовки `X-Frame-Options`, `Content-Security-Policy` присутствуют
- [ ] `sudo systemctl status gunicorn` — **active (running)**
- [ ] `sudo systemctl status nginx` — **active (running)**
- [ ] `sudo systemctl status postgresql` — **active (running)**
- [ ] `sudo certbot renew --dry-run` — без ошибок
- [ ] `/home/deploy/backup.sh` — выполняется без ошибок
- [ ] `sudo ufw status` — 22, 80, 443 открыты
- [ ] `sudo fail2ban-client status sshd` — работает

---

## Файлы деплоя в репозитории

| Файл | Куда копировать на сервере |
|------|---------------------------|
| `deploy/gunicorn.socket`  | `/etc/systemd/system/gunicorn.socket` |
| `deploy/gunicorn.service` | `/etc/systemd/system/gunicorn.service` |
| `deploy/nginx-portfolio`  | `/etc/nginx/sites-available/portfolio` |
| `deploy/backup.sh`        | `/home/deploy/backup.sh` |
| `portfolio/fixtures/initial_data.json` | `python manage.py loaddata ...` |
