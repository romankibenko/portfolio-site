#!/usr/bin/env bash
# backup.sh — резервное копирование БД и медиафайлов
# Путь на сервере: /home/deploy/backup.sh
# Запуск: cron (см. DEPLOY.md, раздел «Cron»)
set -euo pipefail

# ── Конфигурация ─────────────────────────────────────────────
DB_NAME="portfolio_db"
DB_USER="portfolio_user"
PROJECT_DIR="/home/deploy/portfolio_site"
BACKUP_DIR="/home/deploy/backups"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# ── Создать директорию если нет ──────────────────────────────
mkdir -p "$BACKUP_DIR"

# ── Дамп PostgreSQL ──────────────────────────────────────────
echo "[backup] Дамп БД..."
pg_dump -U "$DB_USER" "$DB_NAME" \
    | gzip > "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"

# ── Архив медиафайлов ────────────────────────────────────────
MEDIA_DIR="$PROJECT_DIR/media"
if [ -d "$MEDIA_DIR" ] && [ "$(ls -A "$MEDIA_DIR" 2>/dev/null)" ]; then
    echo "[backup] Архив media/..."
    tar -czf "$BACKUP_DIR/media_${TIMESTAMP}.tar.gz" -C "$MEDIA_DIR" .
else
    echo "[backup] media/ пуста, пропускаем."
fi

# ── Удалить старые бэкапы ────────────────────────────────────
echo "[backup] Удаляем бэкапы старше ${RETENTION_DAYS} дней..."
find "$BACKUP_DIR" -maxdepth 1 -name "*.gz" -mtime +"$RETENTION_DAYS" -delete

echo "[backup] Готово: $TIMESTAMP"
