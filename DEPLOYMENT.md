# PROOFly Deployment Guide

This guide details how to deploy PROOFly's Next.js Frontend and FastAPI Python Backend to production environments.

## 1. Environment Configuration

### Supabase Setup
1. Create a new Supabase project.
2. Run the SQL schema from `backend/db/001_initial_schema.sql` in the Supabase SQL Editor.
3. Obtain your `Project URL`, `anon_key`, and `service_role_key`.

### Backend Environment Variables (Render / Cloud Run)
Create a production environment with the following keys:
```env
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-service-role-key" # IMPORTANT: Use service_role_key for backend ML insertion
SUPABASE_JWT_SECRET="your-jwt-secret-from-api-settings"
GEMINI_API_KEY="AIza..."
CORS_ORIGINS="https://your-frontend-domain.vercel.app"
```

### Frontend Environment Variables (Vercel)
```env
NEXT_PUBLIC_SUPABASE_URL="https://your-project.supabase.co"
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY="your-publishable-key"
NEXT_PUBLIC_API_URL="https://your-deployed-backend-url.onrender.com"
```

## 2. Deploying the Backend (Render / Cloud Run)

### Using Render (Easiest)
1. Connect your GitHub repository to Render.
2. Create a new **Web Service**.
3. Set the Root Directory to `/` (or leave blank).
4. Set the Build Command:
   ```bash
   pip install -r requirements.txt
   ```
5. Set the Start Command:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
6. Add the environment variables listed above.

### Using Google Cloud Run (Docker)
A `Dockerfile` is provided in the project root.
```bash
gcloud run deploy proofly-backend --source . --port 8000
```

## 3. Deploying the Frontend (Vercel)
1. Connect your repository to Vercel.
2. Set the Root Directory to `frontend`.
3. The framework preset should automatically detect **Next.js**.
4. Add your frontend environment variables.
5. Click **Deploy**.

## 4. Verification
1. Access the frontend URL.
2. Create an instructor account via the `/login` route.
3. Ensure the backend `/api/health` returns `200 OK`.
4. Upload a document from the `/submissions` tab and verify the investigation report generates properly.
