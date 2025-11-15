# Render.com Deployment Guide

## Step-by-Step Setup for Render.com

### 1. Create PostgreSQL Database on Render

1. Go to https://render.com and sign in
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `retail-crm-db`
   - **Database**: `retail_crm` (or leave default)
   - **User**: `retail_crm_user` (or leave default)
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15 (or latest)
   - **Plan**: Free (for testing) or Starter (for production)
4. Click **Create Database**
5. **Wait for database to be ready** (takes 1-2 minutes)
6. Once ready, note the **Internal Database URL** and **External Database URL**

### 2. Connect Your GitHub Repository

1. In Render dashboard, click **New +** → **Web Service**
2. Connect your GitHub account if not already connected
3. Select your repository (the one containing this CRM project)
4. Click **Connect**

### 3. Configure Web Service

Fill in the following:

- **Name**: `retail-crm` (or your preferred name)
- **Region**: Same as your database
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (if project is in root)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```
- **Start Command**: 
  ```
  gunicorn retail_crm.wsgi:application
  ```

### 4. Link Database to Web Service

1. In the web service configuration, scroll to **Environment Variables**
2. Click **Link Database**
3. Select your `retail-crm-db` database
4. This automatically creates `DATABASE_URL` environment variable

### 5. Add Environment Variables

In the **Environment** section, add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | `[Generate a new secret key]` | **IMPORTANT**: Use a different key than local! |
| `DEBUG` | `False` | Must be False for production |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Replace with your actual Render URL |
| `BREVO_API_KEY` | `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` | Your Brevo API key |
| `BREVO_SENDER_EMAIL` | `noreply@retailcrm.com` | Your verified sender email |
| `BREVO_SENDER_NAME` | `Retail CRM` | Display name for emails |

**Note**: `DATABASE_URL` is automatically added when you link the database - **DO NOT** add it manually!

### 6. Generate Production Secret Key

Run this command locally to generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as `SECRET_KEY` in Render.

### 7. Deploy

1. Click **Create Web Service**
2. Render will:
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start the application
3. Wait for deployment to complete (usually 2-5 minutes)
4. Your app will be available at: `https://your-app-name.onrender.com`

### 8. Create Superuser

After deployment, you need to create a superuser:

1. In Render dashboard, go to your web service
2. Click **Shell** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Enter email (not username), and password
5. Use this account to log in to the admin panel

### 9. Verify Everything Works

1. Visit your app URL: `https://your-app-name.onrender.com`
2. Test login with OTP:
   - Go to login page
   - Enter your email
   - Check email for OTP code
   - Enter OTP to login
3. Test admin panel: `https://your-app-name.onrender.com/admin/`

## Important Notes

### Database Connection
- Render automatically provides `DATABASE_URL` when you link the database
- The app will use `DATABASE_URL` if available, otherwise fall back to individual DB variables
- **Never commit** `.env` file to Git (it's in `.gitignore`)

### Static Files
- Static files are automatically collected during build
- WhiteNoise serves static files (no need for separate static file service)

### Media Files (Uploads)
- For production, consider using AWS S3 or similar for media storage
- Local media storage works but files are lost on redeploy
- Current setup uses local storage (`MEDIA_ROOT`)

### Environment Variables Priority
1. Render Environment Variables (highest priority)
2. `.env` file (for local development)
3. Default values in `settings.py` (lowest priority)

## Troubleshooting

### Database Connection Errors
- Verify database is running in Render dashboard
- Check that database is linked to web service
- Verify `DATABASE_URL` is set (should be automatic)

### OTP Not Sending
- Check `BREVO_API_KEY` is correct
- Verify Brevo account is active
- Check Brevo dashboard for sending limits
- Check Render logs for error messages

### Static Files Not Loading
- Verify `collectstatic` ran during build (check build logs)
- Check `STATIC_ROOT` is set correctly
- Verify WhiteNoise middleware is in `MIDDLEWARE`

### 500 Errors
- Check Render logs for detailed error messages
- Verify all environment variables are set
- Ensure `DEBUG=False` in production
- Check database migrations completed successfully

## Render.com Free Tier Limits

- **Web Services**: Sleep after 15 minutes of inactivity
- **PostgreSQL**: 90 days free, then $7/month
- **Build Time**: 500 minutes/month
- **Bandwidth**: 100 GB/month

For production, consider upgrading to paid plans.

