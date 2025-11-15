# Environment Variables Checklist

## ✅ Your Current .env File Contains:

### Django Settings
- ✅ `SECRET_KEY` - Generated secret key
- ✅ `DEBUG=True` - For local development
- ✅ `ALLOWED_HOSTS=localhost,127.0.0.1` - Local hosts

### Database (Local Development)
- ⚠️ `DB_NAME=retail_crm` - Update if different
- ⚠️ `DB_USER=postgres` - Update if different  
- ⚠️ `DB_PASSWORD=your_local_db_password` - **YOU MUST UPDATE THIS** with your actual PostgreSQL password
- ✅ `DB_HOST=localhost` - Correct for local
- ✅ `DB_PORT=5432` - Correct for local

### Brevo API
- ✅ `BREVO_API_KEY` - Your API key is configured
- ✅ `BREVO_SENDER_EMAIL=noreply@retailcrm.com` - Default sender
- ✅ `BREVO_SENDER_NAME=Retail CRM` - Display name

## 🔧 What You Need to Do:

### For Local Development:
1. **Update Database Password**: Change `DB_PASSWORD=your_local_db_password` to your actual PostgreSQL password
2. **Create Database** (if not exists):
   ```sql
   CREATE DATABASE retail_crm;
   ```
3. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Use **email** (not username) when creating!

### For Render.com Deployment:

You need to add these environment variables in Render dashboard:

| Variable | Value | Where to Get It |
|----------|-------|----------------|
| `SECRET_KEY` | Generate new one | Run: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` | Must be False for production |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Your Render app URL |
| `BREVO_API_KEY` | `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` | Your existing key |
| `BREVO_SENDER_EMAIL` | `noreply@retailcrm.com` | Your sender email |
| `BREVO_SENDER_NAME` | `Retail CRM` | Display name |
| `DATABASE_URL` | **Auto-provided** | Render provides this when you link database |

## 📋 Quick Checklist:

### Local Setup:
- [ ] Update `DB_PASSWORD` in `.env` file
- [ ] PostgreSQL is running locally
- [ ] Database `retail_crm` exists
- [ ] Run `pip install -r requirements.txt`
- [ ] Run migrations
- [ ] Create superuser with email
- [ ] Test OTP login

### Render.com Setup:
- [ ] Create PostgreSQL database on Render
- [ ] Create Web Service on Render
- [ ] Link database to web service (creates DATABASE_URL automatically)
- [ ] Add all environment variables listed above
- [ ] Generate new SECRET_KEY for production
- [ ] Set DEBUG=False
- [ ] Set ALLOWED_HOSTS to your Render URL
- [ ] Deploy and test

## 🔍 How the System Works:

1. **Local Development**: Uses `.env` file with individual DB variables
2. **Render.com**: Uses `DATABASE_URL` (auto-provided) + environment variables from dashboard
3. **Priority**: Render env vars > .env file > defaults in settings.py

## ⚠️ Important Notes:

- **Never commit `.env` file** to Git (it's in `.gitignore`)
- **Use different SECRET_KEY** for production
- **DATABASE_URL is automatic** on Render - don't add it manually
- **All users must have email addresses** for OTP login to work
- **Brevo free tier**: 300 emails/day - enough for testing

## 🐛 Troubleshooting:

### Can't connect to database locally?
- Check PostgreSQL is running: `pg_isready` or check services
- Verify password in `.env` matches your PostgreSQL password
- Check database exists: `psql -U postgres -l`

### OTP not sending?
- Verify `BREVO_API_KEY` is correct
- Check Brevo dashboard for sending logs
- Verify sender email is verified in Brevo
- Check Render logs for errors

### Render deployment fails?
- Check build logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` has all packages
- Check that database is linked to web service

