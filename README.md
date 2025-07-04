# 📧 Email Verifier (Flask & Streamlit)

A professional-grade application for verifying email addresses using SMTP, with both single and bulk verification modes. Supports a web interface (Flask) and a modern, interactive UI (Streamlit). Upload CSV/Excel files for bulk checks, download results, and get instant feedback on email validity, deliverability, and SMTP handshake details.

---

## 🚀 Features

- **Single Email Verification:**
  - Instantly check if an email address is valid using SMTP handshake.
  - See EHLO/HELO handshake results, deliverability, and error logs.
  - See LinkedIn profile and job title (if available).

- **Bulk Email Verification:**
  - Upload CSV or Excel files with a list of emails.
  - Get a downloadable Excel file with verification results, including score, EHLO/HELO, deliverability, and error details.
  - Cleans up uploaded files automatically for security.

- **Modern UI:**
  - Flask web app for classic web experience.
  - Streamlit app for a fast, interactive dashboard with detailed logs.

- **Robust Verification:**
  - Checks MX records and uses SMTP commands for real-time validation.
  - Handles catch-all, greylisting, and common SMTP edge cases.
  - Retries and delays for rate-limiting errors (e.g., 421), with error reporting.
  - Returns a score and logs for each verification attempt.

---

## ⚡ How the App Verifies Emails (Industry Standard)

1. **Syntax Check:**
   - Uses regex to filter out obviously invalid email formats before any network requests.

2. **MX Record Lookup:**
   - Checks if the domain has valid mail exchange (MX) records using DNS.

3. **SMTP Handshake:**
   - Connects to the mail server and performs both `EHLO` and `HELO` commands, logging their success.
   - Attempts to verify the recipient using `VRFY` (if supported) and `RCPT TO` commands.
   - Scores each email (+1 for EHLO, +1 for HELO, +1 for deliverability).
   - Handles and retries on temporary errors (e.g., 421 rate limits) with exponential backoff.

4. **Detailed Logging:**
   - Returns a dictionary for each email with score, EHLO/HELO status, deliverability, and error details.
   - All results and logs are shown in the UI and included in downloadable files.

---

## 🎯 Accuracy & Limitations

- **Overall Accuracy:**
  - For standard business and ISP domains, SMTP verification is accurate in **80–95%** of cases.
  - For invalid/non-existent addresses, accuracy is often **90–99%**.
  - For catch-all or privacy-protected domains (e.g., Google, Yahoo, Microsoft), accuracy may be lower due to always-accept or ambiguous responses.

- **Why Not 100%?**
  - Many mail servers use catch-all addresses, greylisting, tarpitting, or privacy features that prevent reliable verification.
  - Too many rapid requests can trigger rate-limiting or blocking (handled by retry/delay logic in this app).
  - No SMTP-based verifier can guarantee 100% accuracy due to these industry-wide limitations.

- **How This App Meets Industry Standards:**
  - Uses the same SMTP handshake and MX lookup techniques as leading commercial verifiers.
  - Implements retries, delays, and error handling for robust, real-world use.
  - Provides detailed logs and scoring for transparency and troubleshooting.
  - Does not send actual emails—only checks server responses, as per best practices.

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd email-flask
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Set up environment variables:**
   - Create a `.env` file for any API keys or secrets if needed.

---

## 💻 Usage

### Flask Web App

1. **Run the Flask app:**
   ```bash
   python app.py
   ```
2. **Open in your browser:**
   - Go to `http://localhost:5000`

### Streamlit App

1. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```
2. **Open in your browser:**
   - Streamlit will provide a local URL.

---

## 📂 File Structure

```
email-flask/
├── app.py                  # Flask application
├── streamlit_app.py        # Streamlit application
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates for Flask
├── utils/                  # Utility modules (email verification, scraping, etc.)
│   ├── email_verifier.py
│   ├── email_guesser.py
│   └── linkedin_scraper.py
├── uploads/                # Temporary upload folder (auto-cleaned)
```

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
- [Streamlit](https://streamlit.io/)
- [pandas](https://pandas.pydata.org/)
- [dnspython](https://www.dnspython.org/)
- [Python SMTP Library](https://docs.python.org/3/library/smtplib.html)

---

> **Professional. Fast. Reliable. Industry Standard.**
