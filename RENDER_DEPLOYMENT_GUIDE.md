# Render Deployment Guide – My LMS

## Summary

Your Flask LMS is now prepared for deployment on [Render.com](https://render.com). All configuration files, environment variable handling, and health checks are in place.

---

## Pre-Deployment Checklist

### 1. Repository & Branches
- ✅ **Active branch:** `prepare-render` (pushed to GitHub)
- ⚠️ **Next step:** Merge `prepare-render` → `main` via pull request (or manually)
- 📝 **Important:** Do not commit `.env` file (already in `.gitignore`)

### 2. Configuration Files in Place
| File | Purpose | Status |
|------|---------|--------|
| `render.yaml` | Render service configuration | ✅ Configured |
| `Procfile` | Startup command for web dyno | ✅ Uses gunicorn + eventlet |
| `runtime.txt` | Python version specification | ✅ Python 3.11 |
| `requirements.txt` | Python dependencies | ✅ Has gunicorn, eventlet, psycopg2-binary |
| `config.py` | Flask configuration | ✅ Reads from environment |
| `.env` | Local environment variables | ✅ Created (ignored by git) |
| `app.py` | Flask application entry point | ✅ Optimized for Render |

### 3. Key Features Added
- ✅ **Database URL handling:** `config.py` respects `DATABASE_URL` and converts `postgres://` → `postgresql://`
- ✅ **Health check endpoint:** `/health` (used by Render for readiness checks)
- ✅ **Release command:** `flask db upgrade` (runs migrations on deployment)
- ✅ **Early dotenv loading:** `.env` loaded before `Config` initialization
- ✅ **Production eventlet support:** Enabled when `FLASK_ENV=production`

---

## Render Setup Instructions

### Step 1: Create a Render Web Service

1. Log in to [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository (`my-lms`)
4. Select the branch to deploy (e.g., `main` or `prepare-render`)
5. Configure:
   - **Name:** `lms-web` (or your choice)
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --worker-class eventlet -w 1 app:app`
   - **Plan:** Starter (or higher for production)

### Step 2: Configure Environment Variables

Add these to the Render service **Environment** section:

#### **Required Variables**
- `SECRET_KEY` – A strong random string (generate via `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `DATABASE_URL` – PostgreSQL URL from Render's managed database or external service
- `FLASK_ENV` – Set to `production`
- `MAIL_USERNAME` – Gmail address (with app password)
- `MAIL_PASSWORD` – Gmail app password (NOT your account password)

#### **Optional Variables**
- `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET` – If using Zoom integration
- `SENTRY_DSN` – For error monitoring (optional)

**Security tip:** Mark sensitive vars (SECRET_KEY, MAIL_PASSWORD) as **Secure** in Render's UI.

### Step 3: Set Up PostgreSQL Database (Optional)

If you don't have a PostgreSQL service:

1. In Render, click **New +** → **PostgreSQL**
2. Configure:
   - **Name:** `lms-db` (or your choice)
   - **Database:** `lms`
   - **User:** `lms_user`
   - **Region:** Same as your web service (for lower latency)
   - **Plan:** Starter (or higher)

3. Copy the provided **External Database URL** and add it as `DATABASE_URL` env var in your web service.

### Step 4: Deploy

1. Once all environment variables are set, click **Deploy**
2. Watch the build logs:
   - `pip install -r requirements.txt` should complete without errors
   - Flask app should start with `SocketIO async_mode=eventlet`
   - Database migrations should run (`flask db upgrade`)
3. Check the `/health` endpoint: `https://<your-service-name>.onrender.com/health`
   - Should return JSON: `{"status": "ok", "service": "lms", "now": "..."}`

---

## Local Development

### Using `.env` Locally

1. **Development mode** (local SQLite):
   ```powershell
   $env:FLASK_ENV = "development"
   $env:PORT = "5000"
   python app.py
   ```

2. **Production-like mode** (using PostgreSQL):
   - Set `DATABASE_URL` in `.env` to a local or remote Postgres connection string
   - Set `FLASK_ENV=production` in `.env`
   - `python app.py` will load `.env` and use it

### Updating `.env` for Local Testing
- Edit `.env` and add your local credentials (email, database, etc.)
- Never commit `.env` to git (it's in `.gitignore`)

---

## Deployment Workflow

### Updating Code After Deployment

1. Make changes locally in a feature branch
2. Push to GitHub and open a PR
3. Merge to `main` after review
4. Render automatically triggers a new deploy when `main` is updated
5. Database migrations run automatically via `preDeployCommand: flask db upgrade`

### Rolling Back

If something goes wrong:
1. In Render, go to your web service's **Deploy** tab
2. Find the previous successful deploy
3. Click **Redeploy** next to it

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Build fails: "No module named..."** | Ensure the package is in `requirements.txt`; check versions. |
| **App crashes: "database connection refused"** | Verify `DATABASE_URL` is set and the database is accessible from Render's IP. |
| **502 Bad Gateway** | Check logs in Render's **Logs** tab; common causes are import errors or missing env vars. |
| **SocketIO errors** | Ensure `FLASK_ENV=production` is set; eventlet should load automatically. |
| **Health check fails** | The `/health` endpoint may be misconfigured; check app logs. |

For more details, see [Render Docs](https://docs.render.com/).

---

## Summary of Files Prepared

| File | Changes | Impact |
|------|---------|--------|
| `app.py` | Removed hardcoded SQLite; added `/health` endpoint; `load_dotenv()` called early | Respects `DATABASE_URL`; Render can monitor app health |
| `config.py` | Unchanged (already Render-safe) | Reads env vars: `SECRET_KEY`, `DATABASE_URL`, `MAIL_*` |
| `.env` | Created locally with placeholders | Supports local development; never committed |
| `runtime.txt` | Set to `python-3.11` | Specifies Python version for Render |
| `Procfile` | Uses `gunicorn --worker-class eventlet` | Ensures async support in production |
| `render.yaml` | Added with service config and health check | Render can auto-deploy from this manifest |
| `DEPLOY_RENDER.md` | Quick start guide | Reference for deployment steps |

---

## Next Steps

1. **Merge `prepare-render` to `main`** (create a PR on GitHub)
2. **Set environment variables** in Render service settings
3. **Create/configure PostgreSQL** (or use external DB)
4. **Deploy** and monitor logs
5. **Test** the app and `/health` endpoint

---

## Support

- **Render Docs:** https://docs.render.com/
- **Flask Deployment:** https://flask.palletsprojects.com/deployment/
- **Issues:** Check the `Logs` tab in Render dashboard for detailed error messages

---

**Ready to deploy!** 🚀
