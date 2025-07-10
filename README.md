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

### **Production Deployment:**
- Use a production-ready WSGI server (Gunicorn/uWSGI) behind Nginx
- Set secure permissions on `firebase_key.json` and `.env`
- Restrict allowed origins for Firebase Auth in Firebase Console
- Use HTTPS in production
- For AWS: Use Elastic Beanstalk, ECS, or EC2 with proper environment management

### **Firestore Security:**
- Ensure Firestore security rules restrict access to authenticated users only
- Never expose `firebase_key.json` to frontend or public repos
- Monitor usage patterns for abuse prevention

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
