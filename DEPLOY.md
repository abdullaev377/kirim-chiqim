# Деплой на Railway

Проект настроен как **один сервис**: Django собирает React-фронтенд и отдаёт
его сам (через WhiteNoise), поэтому CORS не нужен — фронт и API живут на
одном домене.

## Что уже готово в репозитории

- `nixpacks.toml` — устанавливает Python- и Node-зависимости, собирает
  `frontend` (`npm run build`) и запускает `collectstatic`.
- `railway.json` / `Procfile` — команда запуска:
  `python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
- `config/settings.py` — читает `DATABASE_URL` (Postgres), `RAILWAY_PUBLIC_DOMAIN`,
  `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` и т.д. из переменных окружения.
- SPA fallback в `config/urls.py` — любой путь, не относящийся к
  `/admin`, `/api`, `/auth`, `/swagger`, `/redoc`, `/media`, `/static`,
  отдаёт `frontend/dist/index.html`, поэтому обновление страницы на
  `/transactions` и т.п. не даёт 404.

## Шаги

1. **Создать проект на Railway** → New Project → Deploy from GitHub repo
   (залейте содержимое этой папки в свой репозиторий, это должен быть
   корень репо — там, где лежит `manage.py`).

2. **Добавить базу данных**: New → Database → PostgreSQL.
   Railway сам создаст переменную `DATABASE_URL` и подключит её к сервису
   (или скопируйте вручную в Variables вашего web-сервиса).

3. **Переменные окружения** сервиса (Variables):
   ```
   DJANGO_SECRET_KEY=<длинная случайная строка>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
   ```
   `RAILWAY_PUBLIC_DOMAIN` Railway подставляет сам — его отдельно указывать
   не нужно, `settings.py` подхватит его автоматически для
   `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`.

4. **Сгенерировать публичный домен**: Settings → Networking → Generate
   Domain.

5. **Deploy**. Railway прогонит `nixpacks.toml` (установит зависимости,
   соберёт фронт, выполнит `collectstatic`), затем при старте выполнит
   `migrate` и поднимет `gunicorn`.

6. Проверьте `https://<ваш-домен>.up.railway.app/` — должен открыться сам
   интерфейс Ledgerly. `/swagger/` — документация API, `/admin/` — админка
   Django (создайте суперпользователя через Railway Shell:
   `python manage.py createsuperuser`).

## Важно про медиа-файлы

Файловая система на Railway эфемерна: фото профиля, загруженные через
`/auth/change-photo`, не переживут redeploy/restart контейнера. Для
продакшна стоит подключить внешнее хранилище (S3-совместимое, например
Cloudflare R2 или Backblaze B2) через `django-storages`. Для учебного/демо
проекта текущей настройки достаточно.

## Локальная разработка (без изменений)

Бэкенд:
```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Фронтенд (в отдельном терминале, прокси на 127.0.0.1:8000 уже настроен в
`vite.config.js`):
```
cd frontend
npm install
npm run dev
```
