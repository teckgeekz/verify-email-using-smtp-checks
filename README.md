# 📧 Email Verifier & Lead Contact Finder (Flask & Streamlit)

A professional-grade, authenticated web application for verifying email addresses using SMTP, finding lead contacts, and discovering business emails in bulk. Features Google Sign-In via Firebase Authentication, per-user usage tracking and limits via Firestore, and a modern, dynamic frontend user experience. Includes both classic and Tailwind CSS-based templates for flexible UI options, and a Streamlit desktop app for power users.

---

## 🚀 Features

### 🔐 **Authentication & Security**
- **Google Sign-In (Firebase Authentication):**
  - Secure login with Google accounts (required for bulk operations).
  - User authentication handled via Firebase JS SDK (frontend) and Firebase Admin SDK (backend).
  - Per-user file storage and usage tracking.

### 📊 **Usage Tracking & Limits (Firestore)**
- **Per-User Usage Tracking:**
  - Each user's usage is tracked in Firestore by their Firebase UID.
  - **Bulk Email Verification**: 2000-row limit per user
  - **Bulk Email Finder**: 20-row limit per user
  - Usage counters displayed and updated dynamically in the UI.
  - Admin dashboard for monitoring user activity.

### 📧 **Email Verification Features**

#### **Single Email Verification:**
- Instantly check if an email address is valid using SMTP handshake and MX checks.
- See EHLO/HELO handshake results, deliverability, and error logs.
- Real-time validation with detailed status reporting.

#### **Bulk Email Verification:**
- Upload CSV or Excel files with a list of emails (up to 2000 total per user).
- Get a downloadable Excel file with verification results.
- Includes score, EHLO/HELO, deliverability, and error details.
- Automatic file cleanup for security.

### 🔍 **Email Discovery Features**

#### **Lead Contact Finder (Single):**
- Enter a name, company, and domain to guess possible business emails and verify them.
- Generates multiple email patterns and tests each one.
- Stops at the first valid email found.
- Attempts to find LinkedIn profiles and job titles using the Serper API.

#### **Bulk Email Finder (NEW):**
- Upload CSV or Excel files with names and domains (up to 20 rows per user).
- **Required columns**: Full Name, Domain
- **Optional column**: Company
- Automatically generates and verifies email patterns for each person.
- Returns the first valid email found for each entry.
- Output includes: Original data + Found Email + Email Valid status.

### 🎨 **Modern UI & UX**
- **Two Template Sets:**
  - **Classic Templates** (`templates/`): Bootstrap-based, traditional look
  - **Tailwind Templates** (`templates-tail/`): Modern utility-first CSS
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dynamic Features:**
  - Loading spinners during processing
  - Real-time usage counter updates
  - File download management from dashboard
  - Processing status notifications

### 📱 **Dashboard & File Management**
- **User Dashboard:**
  - View Lead Contact Finder history
  - View Single Email Verification history
  - Download processed bulk verification files
  - Download processed bulk finder files
  - Delete files as needed
- **Admin Dashboard:**
  - Monitor all user activity
  - Track usage across all features
  - Download any user's files
  - View detailed statistics

### 🔧 **Robust Verification Engine**
- **SMTP Verification:**
  - Checks MX records and uses SMTP commands for real-time validation
  - Handles catch-all, greylisting, and common SMTP edge cases
  - Retries and delays for rate-limiting errors with error reporting
  - Returns detailed status and logs for each verification attempt

### 🖥️ **Streamlit Desktop App**
- All main features available in a desktop-friendly UI
- Modes: Single Email, Bulk Verify, Lead Contact Finder
- Perfect for power users and batch processing

---

## 🛠️ Installation & Setup

### 1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd verify-email-using-smtp-checks
```

### 2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### 3. **Set up Firebase:**
- Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
- Enable Google Sign-In in the Authentication section
- Create a Firestore database (in production or test mode as appropriate)
- Download your Firebase service account key as `firebase_key.json` and place it in the project root
- In the Firebase Console, go to Project Settings > General > Your Apps > Firebase SDK snippet > Config, and copy your web config

### 4. **Configure environment variables:**
Create a `.env` file in the project root with your Firebase web config:
```env
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id
SERPER_API_KEY=your_serper_api_key
```

---

## 💻 Usage

### 1. **Start the Application:**
```bash
python app.py
```
Then open `http://localhost:5000` in your browser.

### 2. **Authentication:**
- Click "Sign in with Google" to authenticate
- Your usage counters will be displayed and updated dynamically

### 3. **Single Email Verification:**
- Enter an email address to verify instantly (no login required)
- See detailed results and logs in the UI

### 4. **Lead Contact Finder:**
- Enter a name, company (optional), and domain
- The system will generate and test multiple email patterns
- Returns the first valid email found

### 5. **Bulk Email Verification:**
- **Requires authentication**
- Upload CSV or Excel file with an "Email" column
- **Limit**: Up to 2000 rows total per user
- Processing shows loading spinner and status updates
- Download results as Excel file from dashboard

### 6. **Bulk Email Finder (NEW):**
- **Requires authentication**
- Upload CSV or Excel file with required columns:
  - **Full Name** (required)
  - **Domain** (required)
  - **Company** (optional)
- **Limit**: Up to 20 rows per user
- Automatically finds and verifies emails for each person
- Download results as Excel file from dashboard

### 7. **Dashboard:**
- View your usage history and download processed files
- Monitor your current usage limits
- Manage and delete your files

### 8. **Streamlit App:**
```bash
streamlit run streamlit_app.py
```
Desktop UI with all main features.

---

## 📂 Directory Structure

```
verify-email-using-smtp-checks/
├── app.py                  # Main Flask application
├── streamlit_app.py        # Streamlit desktop app
├── requirements.txt        # Python dependencies
├── firebase_key.json       # Firebase service account (backend)
├── .env                    # Environment variables
├── templates/              # Classic HTML templates (Bootstrap)
│   ├── index.html          # Lead Contact Finder
│   ├── single_verify.html  # Single Email Verification
│   ├── bulk_verify.html    # Bulk Email Verification
│   ├── bulk_finder.html    # Bulk Email Finder
│   ├── dashboard.html      # User Dashboard
│   └── admin_dashboard.html # Admin Dashboard
├── templates-tail/         # Tailwind CSS templates (Modern UI)
│   ├── index.html          # Lead Contact Finder
│   ├── single_verify.html  # Single Email Verification
│   ├── bulk_verify.html    # Bulk Email Verification
│   ├── bulk_finder.html    # Bulk Email Finder
│   ├── dashboard.html      # User Dashboard
│   └── admin_dashboard.html # Admin Dashboard
├── utils/                  # Core functionality modules
│   ├── email_verifier.py   # SMTP email verification
│   ├── email_guesser.py    # Email pattern generation
│   └── linkedin_scraper.py # LinkedIn profile scraping
├── uploads/                # User file storage (per-user folders)
└── static/                 # Static assets (favicons, etc.)
```

---

## 📊 **Feature Comparison**

| Feature | Auth Required | Row Limit | Input Format | Output |
|---------|---------------|-----------|--------------|---------|
| **Single Email Verify** | ❌ No | N/A | Email address | Instant result |
| **Lead Contact Finder** | ❌ No | N/A | Name + Domain | First valid email |
| **Bulk Email Verify** | ✅ Yes | 2000 | CSV/Excel with Email column | Verified emails list |
| **Bulk Email Finder** | ✅ Yes | 20 | CSV/Excel with Name + Domain | Found emails list |

---

## 🔒 Security & Deployment

### **Production Deployment with Gunicorn & Nginx:**

#### **1. Install Dependencies:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python, pip, and other dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Install Gunicorn
pip3 install gunicorn
```

#### **2. Application Setup:**
```bash
# Clone your repository
git clone <your-repo-url>
cd verify-email-using-smtp-checks

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install application dependencies
pip install -r requirements.txt
pip install gunicorn

# Set proper permissions
sudo chown -R www-data:www-data /path/to/your/app
sudo chmod 755 /path/to/your/app
sudo chmod 600 /path/to/your/app/firebase_key.json
sudo chmod 600 /path/to/your/app/.env
```

#### **3. Create Gunicorn Service:**
Create `/etc/systemd/system/email-finder.service`:
```ini
[Unit]
Description=Email Finder Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/app/email-finder.sock --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log app:app

[Install]
WantedBy=multi-user.target
```

#### **4. Configure Gunicorn:**
Create `/path/to/your/app/gunicorn.conf.py`:
```python
# Gunicorn configuration file
bind = "unix:/path/to/your/app/email-finder.sock"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

#### **5. Setup Logging:**
```bash
# Create log directory
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# Create logrotate configuration
sudo tee /etc/logrotate.d/email-finder << EOF
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF
```

#### **6. Configure Nginx:**
Create `/etc/nginx/sites-available/email-finder`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Client max body size for file uploads
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Uploads directory (protected)
    location /uploads/ {
        alias /path/to/your/app/uploads/;
        internal;
    }

    # Main application
    location / {
        proxy_pass http://unix:/path/to/your/app/email-finder.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Gunicorn health check
    location /health {
        proxy_pass http://unix:/path/to/your/app/email-finder.sock;
        access_log off;
    }
}
```

#### **7. Enable SSL with Let's Encrypt:**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### **8. Start Services:**
```bash
# Enable and start Gunicorn service
sudo systemctl enable email-finder
sudo systemctl start email-finder

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Check status
sudo systemctl status email-finder
sudo systemctl status nginx
```

#### **9. Firewall Configuration:**
```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

#### **10. Monitoring & Maintenance:**
```bash
# View logs
sudo journalctl -u email-finder -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart email-finder
sudo systemctl restart nginx

# Check Gunicorn processes
ps aux | grep gunicorn
```

### **Alternative: uWSGI Setup:**

#### **1. Install uWSGI:**
```bash
pip install uwsgi
```

#### **2. Create uWSGI Configuration:**
Create `/path/to/your/app/uwsgi.ini`:
```ini
[uwsgi]
module = app:app
master = true
processes = 4
threads = 2
socket = /path/to/your/app/email-finder.sock
chmod-socket = 666
vacuum = true
die-on-term = true
max-requests = 1000
harakiri = 30
harakiri-verbose = true
logto = /var/log/uwsgi/email-finder.log
```

#### **3. Create uWSGI Service:**
Create `/etc/systemd/system/email-finder-uwsgi.service`:
```ini
[Unit]
Description=Email Finder uWSGI daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/uwsgi --ini uwsgi.ini

[Install]
WantedBy=multi-user.target
```

### **Firestore Security:**
- Ensure Firestore security rules restrict access to authenticated users only
- Never expose `firebase_key.json` to frontend or public repos
- Monitor usage patterns for abuse prevention

### **Environment Variables for Production:**
```bash
# Add to your .env file
FLASK_ENV=production
FLASK_DEBUG=False
```

### **Performance Optimization:**
- **Gunicorn**: Use `--workers` based on CPU cores (2-4x CPU cores)
- **Nginx**: Enable gzip compression and caching
- **Database**: Use connection pooling for Firestore
- **Monitoring**: Set up log rotation and monitoring tools

---

## 🧑‍💻 Authors & Credits

- Developed by [Tecgeekz](https://teckgeekz.com/)
- Inspired by best practices in email validation and web development

---

## 📜 License

- This project is licensed for **Non-commercial Use Only**
- Commercial use, resale, or redistribution is prohibited without explicit permission
- See the LICENSE file for full terms

---

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Firebase](https://firebase.google.com/) - Authentication & database
- [Google Cloud Firestore](https://firebase.google.com/docs/firestore) - NoSQL database
- [pandas](https://pandas.pydata.org/) - Data manipulation
- [dnspython](https://www.dnspython.org/) - DNS operations
- [Python SMTP Library](https://docs.python.org/3/library/smtplib.html) - Email verification
- [Tailwind CSS](https://tailwindcss.com/) - Modern styling
- [Streamlit](https://streamlit.io/) - Desktop app framework

---

> **Professional. Fast. Reliable. Authenticated. Usage-Limited. Industry Standard. Modern UI.**
