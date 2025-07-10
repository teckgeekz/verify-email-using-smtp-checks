import smtplib
from email.mime.text import MIMEText
import os

def send_brevo_email(to_email, subject, body):
    smtp_host = os.getenv("BREVO_SMTP_HOST")
    smtp_port = os.getenv("BREVO_SMTP_PORT", "587")
    smtp_user = os.getenv("BREVO_SMTP_USER")
    smtp_pass = os.getenv("BREVO_SMTP_PASSWORD")
    from_email = smtp_user

    # Ensure all required credentials are present
    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, from_email]):
        raise ValueError("Missing one or more required BREVO SMTP environment variables.")

    msg = MIMEText(body, "html")
    msg["Subject"] = str(subject)
    msg["From"] = str(from_email)
    msg["To"] = str(to_email)

    with smtplib.SMTP(str(smtp_host), int(smtp_port)) as server:
        server.starttls()
        server.login(str(smtp_user), str(smtp_pass))
        server.sendmail(str(from_email), [str(to_email)], msg.as_string()) 