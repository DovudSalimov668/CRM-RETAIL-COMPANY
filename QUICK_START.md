# 🚀 Quick Start Guide

## ✅ What's Already Done:

1. ✅ `.env` file created with your Brevo API key
2. ✅ Settings configured for both local and Render.com
3. ✅ Database connection supports Render's DATABASE_URL format
4. ✅ All required packages added to `requirements.txt`
5. ✅ OTP system integrated with Brevo
6. ✅ Email-based login implemented

## 📝 What You Need to Do Now:

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Update Database Password in .env
Open `.env` file and change:
```
DB_PASSWORD=your_local_db_password
```
to your actual PostgreSQL password.

### Step 3: Create Database (if needed)
```sql
CREATE DATABASE retail_crm;
```

### Step 4: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```
**Important**: Use EMAIL (not username) when creating!

### Step 6: Test Locally
```bash
python manage.py runserver
```
Then visit: http://127.0.0.1:8000

## 🌐 Deploying to Render.com:

### Quick Steps:
1. **Create PostgreSQL Database** on Render
2. **Create Web Service** on Render
3. **Link Database** to Web Service (this auto-creates DATABASE_URL)
4. **Add Environment Variables** in Render dashboard:
   - `SECRET_KEY` (generate new one)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app-name.onrender.com`
   - `BREVO_API_KEY` (your existing key)
   - `BREVO_SENDER_EMAIL`
   - `BREVO_SENDER_NAME`

See `RENDER_SETUP.md` for detailed instructions.

## 📋 Your .env File Contains:

✅ **SECRET_KEY** - Django secret key  
✅ **DEBUG=True** - For local development  
✅ **ALLOWED_HOSTS** - Local hosts  
✅ **Database variables** - For local PostgreSQL  
✅ **BREVO_API_KEY** - Your API key  
✅ **BREVO_SENDER_EMAIL** - Sender email  
✅ **BREVO_SENDER_NAME** - Display name  

## ⚠️ Important:

- **Update `DB_PASSWORD`** in `.env` with your actual PostgreSQL password
- **Never commit `.env`** to Git (already in `.gitignore`)
- **Use different SECRET_KEY** for production on Render
- **DATABASE_URL** is automatically provided by Render - don't add it manually

## 📚 Documentation Files:

- `SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `RENDER_SETUP.md` - Step-by-step Render.com deployment
- `ENV_VARIABLES_CHECKLIST.md` - Environment variables checklist

## 🎯 Next Steps:

1. Install dependencies: `pip install -r requirements.txt`
2. Update database password in `.env`
3. Run migrations
4. Create superuser
5. Test OTP login
6. Deploy to Render.com

Everything is ready! Just follow the steps above. 🚀

