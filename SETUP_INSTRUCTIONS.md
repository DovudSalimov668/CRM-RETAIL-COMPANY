# Setup Instructions for Retail CRM with Email Login & OTP

## What You Need to Provide

### 1. Brevo (formerly Sendinblue) API Key

1. Go to https://www.brevo.com/
2. Sign up for a free account (or log in if you have one)
3. Navigate to **Settings** → **SMTP & API** → **API Keys**
4. Create a new API key or copy an existing one
5. Save this API key - you'll need it for `BREVO_API_KEY`

**Free Tier Limits:**
- 300 emails per day
- Perfect for development and small deployments

### 2. Brevo Sender Email (Optional but Recommended)

1. In Brevo, go to **Settings** → **Senders**
2. Add and verify your sender email address
3. This will be used as `BREVO_SENDER_EMAIL`
4. You can also set `BREVO_SENDER_NAME` (e.g., "Retail CRM")

### 3. Environment Variables

Create a `.env` file in your project root with the following:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-render-app.onrender.com,localhost,127.0.0.1

# Database (for local development)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Brevo API
BREVO_API_KEY=your-brevo-api-key-here
BREVO_SENDER_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=Retail CRM
```

### 4. Render.com Setup

#### Step 1: Create PostgreSQL Database
1. Go to https://render.com
2. Click **New +** → **PostgreSQL**
3. Name it: `retail-crm-db`
4. Select **Free** plan
5. Copy the database credentials

#### Step 2: Create Web Service
1. Connect your GitHub repository to Render
2. Click **New +** → **Web Service**
3. Select your repository
4. Configure:
   - **Name**: `retail-crm`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn retail_crm.wsgi:application`

#### Step 3: Add Environment Variables in Render
In your Render dashboard, go to your web service → **Environment** tab and add:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=Retail CRM
```

**Note:** Database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) are automatically provided by Render when you link the database.

### 5. Generate Django Secret Key

Run this command to generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your `SECRET_KEY`.

## Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create `.env` file with the variables listed above

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```
   Use an email address (not username) when creating the superuser.

5. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## How Email Login & OTP Works

1. User enters their **email address** (not username)
2. System sends a **6-digit OTP code** to their email via Brevo
3. User enters the OTP code
4. System verifies the code and logs them in
5. OTP codes expire after **10 minutes**
6. Each OTP can only be used **once**

## Testing OTP System

1. Make sure you have a user account with a valid email
2. Go to login page
3. Enter the email address
4. Click "Send OTP"
5. Check your email inbox for the OTP code
6. Enter the code to login

## Troubleshooting

### OTP Not Sending
- Check that `BREVO_API_KEY` is correct
- Verify your Brevo account is active
- Check Brevo dashboard for email sending logs
- Ensure `BREVO_SENDER_EMAIL` is verified in Brevo

### Database Connection Issues
- Verify database credentials in Render dashboard
- Check that database is running
- Ensure `DB_HOST` includes the full hostname from Render

### Static Files Not Loading
- Run `python manage.py collectstatic` locally
- Check that `STATIC_ROOT` is set correctly
- Verify WhiteNoise is in `MIDDLEWARE`

## Important Notes

- **Email is now required** for all user accounts
- Users must have a valid email to receive OTP codes
- OTP codes are case-sensitive and numeric only
- Each OTP expires after 10 minutes
- Old OTP codes are automatically deleted when new ones are sent

