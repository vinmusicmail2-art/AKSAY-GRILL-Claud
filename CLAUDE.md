# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask 3.1 restaurant website with admin panel for "Аксай Гриль" (Aksay Grill). Features online menu, order management, business lunch delivery, catering, event hall booking, and email notifications.

**Tech Stack:**
- Backend: Python 3.11, Flask 3.1, SQLAlchemy 2.0
- Database: SQLite (no migrations framework - uses inline ALTER TABLE)
- Frontend: Tailwind CSS (pre-built), Alpine.js, Material Symbols icons
- Auth: Flask-Login with bcrypt
- Server: Gunicorn

## Development Commands

```bash
# Run development server
python main.py

# Run with Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --reload main:app

# Access admin panel
# First time: http://localhost:5000/admin/setup
# Login: http://localhost:5000/admin/login
```

**No test suite, linter, or build commands** - this is a production-ready application without a test framework.

## Architecture

### Request Flow

```
main.py (entry point)
  ↓
app.py (Flask app initialization, middleware, context processors)
  ↓
routes_public.py OR routes_admin.py (route handlers)
  ↓
models.py (SQLAlchemy ORM) + forms.py (WTForms validation)
  ↓
templates/ (Jinja2) + mailer.py (async email notifications)
```

### Key Architectural Patterns

**1. Route Separation**
- `routes_public.py` - Public-facing pages (menu, orders, contact forms)
- `routes_admin.py` - Admin panel (requires `@login_required` decorator)
- Both imported at bottom of `app.py` after initialization

**2. Database Session Management**
- Manual session handling: `session = SessionLocal()` + `try/finally`
- No scoped sessions or automatic cleanup
- Sessions must be explicitly closed in every route

**3. Inline Migrations (No Alembic)**
- `app.py:init_db()` runs on startup
- Uses `PRAGMA table_info()` to check existing columns
- Executes `ALTER TABLE ADD COLUMN` if missing
- Migrations are idempotent but not versioned

**4. Site Texts System**
- `models.py:SITE_TEXT_CATALOG` - defines all editable site texts
- `models.py:SiteText` model stores key-value pairs in DB
- `app.py:get_cached_site_texts()` - 5-minute TTL cache
- `app.py:inject_site_texts()` - makes `texts` dict available in all templates
- Admin can edit via `/admin/texts`

**5. Email Notifications**
- `mailer.py` - uses threading for async email sending
- Functions like `send_order_notification_async()` spawn background threads
- SMTP config from environment variables (SMTP_HOST, SMTP_USER, SMTP_PASSWORD)
- All emails include admin panel links for quick access

**6. Form Handling**
- Public forms: WTForms + CSRF protection
- Rate limiting: 5 requests/min, 30 requests/hour per IP
- Sanitization utilities in `utils/form_helpers.py`
- JSON API for cart orders (`/order/delivery`) is CSRF-exempt

### Critical Files

**app.py** - Core initialization
- `init_db()` - creates tables + runs migrations on startup
- `get_cached_site_texts()` - caches site texts (TTL 5 min)
- `inject_site_texts()` - injects `texts` dict into all templates
- Rate limiter setup (Flask-Limiter with memory storage)

**models.py** - Database schema
- `SITE_TEXT_CATALOG` - defines all editable site texts with defaults
- `BUSINESS_LUNCH_MENU`, `CATERING_FORMATS`, `EVENT_TYPES` - static data catalogs
- All order models have `is_processed`, `processed_at`, `processed_by` fields
- `Admin` model uses bcrypt for password hashing

**routes_admin.py** - Admin panel (1800+ lines)
- Generic utilities used: `utils/admin_helpers.py`, `utils/admin_views.py`, `utils/csv_export.py`
- All list views use `build_admin_list_query()` for filtering/sorting/search
- CSV exports use `export_to_csv()` utility
- Toggle processed status uses `toggle_processed_status()` utility

**mailer.py** - Email notifications
- All `send_*_notification_async()` functions spawn threads
- Email templates are inline HTML strings (no separate template files)
- Includes admin panel links in all notification emails

### Utils Package

- `admin_helpers.py` - Generic `toggle_processed_status()` for marking orders processed
- `admin_views.py` - Generic `build_admin_list_query()` for admin list filtering/sorting
- `csv_export.py` - Generic `export_to_csv()` for exporting data
- `form_helpers.py` - `sanitize_optional()`, `sanitize_required()`, `sanitize_phone()`, `sanitize_email()`
- `db_helpers.py` - `get_session()` context manager (rarely used, most code uses manual session handling)

## Critical Rules for Code Changes

### ⚠️ NEVER Change Without Explicit Request

**Frontend (HTML/CSS/JS):**
- `templates/*.html` - structure, classes, inline styles, font sizes
- `assets/css/*.css` - all CSS rules, especially font-family and font-size
- `tailwind.config.js` - size scales, font families, colors
- `.replit` - startup commands and paths

**Why:** User has specific design requirements. Any visual change will be noticed immediately.

### ✅ Safe to Refactor

**Backend Python code:**
- `routes_*.py` - route handlers, business logic
- `models.py` - add fields, methods (but don't change existing field types)
- `utils/*.py` - create new utilities, refactor existing ones
- `forms.py` - add validation, new forms

### Verification Procedure for New Repositories

**CRITICAL:** When creating a new repository or copying files, ALWAYS compare with the GitHub source, NOT local folders.

**Why:** Local folders may contain uncommitted experiments or outdated versions.

**Procedure:**
1. Clone the working GitHub repository as reference
2. Compare all critical files with `md5sum` or `diff`
3. Check especially:
   - `templates/*.html` - font sizes, styles, classes
   - `assets/css/*.css` - all CSS rules
   - `tailwind.config.js` - configuration
   - `.replit` - paths and commands

**Example:**
```bash
# Clone reference
git clone https://github.com/user/repo.git reference_repo

# Compare critical files
md5sum reference_repo/templates/index.html new_repo/templates/index.html
diff -u reference_repo/assets/css/main.css new_repo/assets/css/main.css
```

### If User Reports Visual Changes

**Algorithm:**
1. Clone original repository from GitHub
2. Compare all HTML/CSS files byte-by-byte
3. Find differences with `diff`
4. If differences exist - restore from GitHub
5. If no differences - issue is browser cache or Replit

**DO NOT argue** with user. Verify facts first.

## Database Schema Notes

**No foreign key constraints** - SQLite foreign keys are not enforced by default in this app.

**Seeding:**
- `models.py:seed_site_texts()` - populates SiteText table from SITE_TEXT_CATALOG
- `models.py:seed_menu()` - creates default menu categories and dishes
- Both called from `app.py:init_db()` on startup

**Common patterns:**
- All order tables have: `id`, `created_at`, `is_processed`, `processed_at`, `processed_by`, `ip_address`
- Menu items have: `is_visible`, `sort_order`, `image_url`
- Admin actions are logged via `processed_by` field (username)

## Email Configuration

Required environment variables:
- `SMTP_HOST` - SMTP server (e.g., smtp.mail.ru)
- `SMTP_PORT` - SMTP port (e.g., 465 for SSL)
- `SMTP_USER` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `SMTP_FROM` - From email address

**Note:** Email sending is fire-and-forget (threaded). Failures are logged but don't block requests.

## Deployment

See `DEPLOY.md` for full instructions.

**Quick start:**
- Render.com / Railway.app - auto-deploy from GitHub
- Replit - import from GitHub, runs via `.replit` config
- VPS - systemd service + nginx reverse proxy (see `deploy/` folder)

**Required environment variable:**
- `SESSION_SECRET` - random 64+ character string for Flask sessions

## Git Workflow

**Commit format:**
```
<type>: <description>

<optional body>

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>
```

**Types:** `Fix:`, `Add:`, `Refactor:`, `Update:`

**Branch:** Work on `main` branch (no feature branches in this project)

