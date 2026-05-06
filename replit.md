# Аксай Гриль

Restaurant/catering website for Aksay Grill with a public menu, ordering forms, and an admin dashboard.

## Run & Operate

- **Dev server**: `python -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`
- **Production**: `gunicorn --bind 0.0.0.0:5000 main:app`
- **Required env vars**: `SESSION_SECRET` (set), `DATABASE_URL` (set by Replit PostgreSQL), `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_FROM` (shared env), `SMTP_PASSWORD` (secret)

## Stack

- Python 3.11, Flask 3.x, SQLAlchemy 2.x, Flask-Login, Flask-WTF, Flask-Limiter, Flask-Compress
- PostgreSQL (Replit managed) via `psycopg2-binary`; SQLite fallback for local dev
- Gunicorn as WSGI server
- Jinja2 templates, vanilla JS frontend

## Where things live

- `app.py` — Flask app factory, extensions, DB init, rate limiting
- `db.py` — SQLAlchemy engine/session (PostgreSQL via `DATABASE_URL` env, SQLite fallback)
- `models.py` — All ORM models + seed data + site text catalog
- `routes_public.py` — Public-facing pages and form handlers
- `routes_admin.py` — Admin dashboard routes
- `forms.py` — Flask-WTF form definitions
- `mailer.py` — SMTP email notifications (async threading)
- `templates/` — Jinja2 templates (`admin/` subdirectory for admin views)
- `assets/` — Static files served at `/assets/`

## Architecture decisions

- Database uses `DATABASE_URL` env var to connect to Replit PostgreSQL; falls back to SQLite (`data.db`) if not set
- Inline `ALTER TABLE` migrations run at startup (`init_db()`), using `information_schema` for PostgreSQL and `PRAGMA` for SQLite
- Email notifications run in daemon threads to avoid blocking request handling
- Rate limiting uses in-memory storage (`memory://`) — resets on restart
- SMTP password can be stored in DB (`site_texts` table key `smtp_password`) as fallback to env var

## Product

- Public website: menu browsing, delivery ordering (cart), business lunch orders, catering requests, hall/banquet booking, quick order form
- Admin dashboard: manage menu items/categories, view and process all orders, edit all site texts, configure email notifications, manage admins

## User preferences

- Keep Russian-language comments and variable names as-is
- Do not use external auth services; app uses its own admin login with bcrypt passwords

## Gotchas

- `BASE_DIR` is exported from `db.py` and imported in `routes_public.py` for uploads directory
- Site texts are cached in-memory for 5 minutes (`_CACHE_TTL = 300`)
- Static assets get 30-day `Cache-Control` headers
- The `deploy/` directory contains Nginx/systemd configs for bare-metal hosting — not used on Replit
