# 📧 Email Verifier (Flask)

A professional-grade, authenticated web application for verifying email addresses using SMTP, with both single and bulk verification modes. Features Google Sign-In via Firebase Authentication, per-user usage tracking and limits via Firestore, and a modern, dynamic frontend user experience. Upload CSV/Excel files for bulk checks, download results, and get instant feedback on email validity, deliverability, and SMTP handshake details.

---

## 🚀 Features

- **Google Sign-In (Firebase Authentication):**
  - Secure login with Google accounts (required for bulk verification).
  - User authentication handled via Firebase JS SDK (frontend) and Firebase Admin SDK (backend).

- **Per-User Usage Tracking (Firestore):**
  - Each user's bulk verification usage is tracked in Firestore by their Firebase UID.
  - Enforces a 200-row total limit per user for bulk verification.
  - Usage counter is displayed and updated dynamically in the UI.

- **Single Email Verification:**
  - Instantly check if an email address is valid using SMTP handshake.
  - See EHLO/HELO handshake results, deliverability, and error logs.
  - See LinkedIn profile and job title (if available).

- **Bulk Email Verification:**
  - Upload CSV or Excel files with a list of emails (up to 200 total per user).
  - Get a downloadable Excel file with verification results, including score, EHLO/HELO, deliverability, and error details.
  - Cleans up uploaded files automatically for security.

- **Modern UI & UX:**
  - Centered sign-in box for unauthenticated users.
  - Loading spinner during bulk verification processing.
  - Dynamic results display and download link after bulk verify (no page reload).
  - Usage counter updates after login and after uploads.
  - Disabled "Bulk Verify (Coming Soon)" button on single verify page for clarity.

- **Robust Verification:**
  - Checks MX records and uses SMTP commands for real-time validation.
  - Handles catch-all, greylisting, and common SMTP edge cases.
  - Retries and delays for rate-limiting errors (e.g., 421), with error reporting.
  - Returns a score and logs for each verification attempt.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd email-flask
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Firebase:**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/).
   - Enable Google Sign-In in the Authentication section.
   - Create a Firestore database (in production or test mode as appropriate).
   - Download your Firebase service account key as `firebase_key.json` and place it in the project root.
   - In the Firebase Console, go to Project Settings > General > Your Apps > Firebase SDK snippet > Config, and copy your web config.

4. **Configure environment variables:**
   - Create a `.env` file in the project root with your Firebase web config, e.g.:
     ```env
     FIREBASE_API_KEY=...
     FIREBASE_AUTH_DOMAIN=...
     FIREBASE_PROJECT_ID=...
     FIREBASE_STORAGE_BUCKET=...
     FIREBASE_MESSAGING_SENDER_ID=...
     FIREBASE_APP_ID=...
     FIREBASE_MEASUREMENT_ID=...
     ```

---

## 💻 Usage

1. **Run the Flask app:**
   ```bash
   python app.py
   ```
2. **Open in your browser:**
   - Go to `http://localhost:5000`

3. **Sign in with Google:**
   - Click the sign-in button to authenticate with your Google account.
   - Your usage counter will be displayed and updated dynamically.

4. **Single Email Verification:**
   - Enter an email address to verify instantly (no login required).
   - See results and logs in the UI.
   - The "Bulk Verify" button is disabled here for clarity.

5. **Bulk Email Verification:**
   - After signing in, upload a CSV or Excel file with up to 200 emails total (per user).
   - The app will process your file, show a loading spinner, and display results dynamically.
   - Download your results as an Excel file.
   - Your usage counter updates after each upload.

---

## 📂 File Structure

```
email-flask/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── firebase_key.json       # Firebase service account (backend)
├── .env                    # Firebase web config (frontend)
├── templates/              # HTML templates for Flask
│   ├── index.html
│   ├── single_verify.html
│   └── bulk_verify.html
├── utils/                  # Utility modules (email verification, scraping, etc.)
│   ├── email_verifier.py
│   ├── email_guesser.py
│   └── linkedin_scraper.py
```

---

## 🔒 Security & Deployment

- **Production Deployment:**
  - Use a production-ready WSGI server (e.g., Gunicorn or uWSGI) behind Nginx or similar.
  - Set secure permissions on `firebase_key.json` and `.env`.
  - Restrict allowed origins for Firebase Auth in the Firebase Console.
  - Use HTTPS in production.
  - For AWS, use Elastic Beanstalk, ECS, or EC2 with proper environment variable management.

- **Firestore & Firebase:**
  - Ensure Firestore security rules restrict access to authenticated users only.
  - Never expose your service account key (`firebase_key.json`) to the frontend or public repos.

---

## 🧑‍💻 Authors & Credits

- Developed by [Your Name]
- Inspired by best practices in email validation and web development.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Firebase](https://firebase.google.com/)
- [Google Cloud Firestore](https://firebase.google.com/docs/firestore)
- [pandas](https://pandas.pydata.org/)
- [dnspython](https://www.dnspython.org/)
- [Python SMTP Library](https://docs.python.org/3/library/smtplib.html)

---

> **Professional. Fast. Reliable. Authenticated. Usage-Limited. Industry Standard.**
