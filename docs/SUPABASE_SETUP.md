# Supabase Database Setup Guide for SmartRail

This guide walks you through connecting SmartRail to a hosted **Supabase** PostgreSQL database.

---

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and log in or create a free account.
2. Click **"New Project"**.
3. Fill in:
   - **Name**: `smartrail` (or any name you prefer)
   - **Database Password**: Choose a strong password and **save it securely**!
   - **Region**: Choose the region closest to you (e.g., `South Asia (Mumbai)` for India).
4. Click **"Create new project"** and wait ~1-2 minutes for initialization.

---

## 2. Get Your Database Connection String

1. In your Supabase project dashboard, navigate to:
   **Project Settings** (gear icon in sidebar) → **Database**.
2. Scroll down to the **Connection string** section.
3. Select the **URI** tab.
4. Choose your connection method:

### Recommended: Connection Pooler (Session Mode)
- **Port**: `5432`
- **Use Case**: Best for running migrations, table creation, and seed data.
- **URI Format**:
  ```text
  postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
  ```

### Alternative: Connection Pooler (Transaction Mode)
- **Port**: `6543`
- **Use Case**: High-concurrency production API traffic.
- **URI Format**:
  ```text
  postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
  ```

> [!TIP]
> If your database password contains special characters (like `@`, `#`, `%`, `?`), make sure to URL-encode them (e.g., `@` becomes `%40`).

---

## 3. Configure Your Environment Variables

Open `backend/.env` (and root `.env` if using Docker):

```env
# Change this to your Supabase Session Pooler URL:
DATABASE_URL=postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
```

> **Note**: Even if you paste a URL starting with `postgresql://` or with `?sslmode=require`, SmartRail's backend automatically:
> - Converts it to the asyncpg driver (`postgresql+asyncpg://`)
> - Enables SSL encryption (`ssl=require`)
> - Disables prepared statement caching (`statement_cache_size=0`) if using transaction pooler on port 6543.

---

## 4. Initialize Database Tables & Seed Data

Once your `.env` contains the valid Supabase connection string:

### Run Backend Locally
From the `backend` directory:
```bash
# In Windows PowerShell:
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Upon startup, SmartRail will:
1. Connect to your Supabase database over SSL.
2. Automatically create all tables (`stations`, `trains`, `train_stops`, `train_runs`, `delay_records`, `seat_availability`, `users`).
3. Seed Indian Railways stations, trains, routes, and realistic delay patterns (idempotent, runs only once).

### Verify in Supabase
Open your Supabase dashboard and click **Table Editor** on the left menu. You will see all the created tables populated with data!

---

## 5. Docker Compose with Supabase

When running via `docker compose up`:
- SmartRail backend connects directly to your cloud Supabase database using the `DATABASE_URL` specified in `.env`.
- The local `postgres` Docker container in `docker-compose.yml` can be stopped or ignored since the backend will communicate directly with Supabase.
