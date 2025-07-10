from utils.celery_worker import celery
from utils.email_sender import send_brevo_email
from utils.email_guesser import guess_emails
from utils.email_verifier import verify_email
import pandas as pd
import time
import random
import os

def log(msg):
    print(f"[BulkFinderTask] {msg}")

@celery.task
def process_bulk_file(user_email, output_filename):
    # Simulate file processing (replace with real logic)
    time.sleep(5)  # Simulate processing delay
    # Send notification email
    subject = "Your file is ready"
    body = f"""
    <p>Hello,</p>
    <p>Your file <b>{output_filename}</b> has been processed and is ready for download from your dashboard.</p>
    <p><a href='https://teck-translate.com/dashboard'>Go to Dashboard</a></p>
    <p>Thank you for using LeadFinder!</p>
    """
    send_brevo_email(user_email, subject, body)

@celery.task
def process_bulk_finder_file(user_email, input_filepath, output_filepath, original_filename):
    try:
        log(f"Started processing file: {input_filepath} for user: {user_email}")
        if input_filepath.endswith(".csv"):
            df = pd.read_csv(input_filepath)
        elif input_filepath.endswith(".xlsx"):
            df = pd.read_excel(input_filepath)
        else:
            log(f"Unsupported file format: {input_filepath}")
            return
        required_columns = ['Full Name', 'Domain']
        if not all(col in df.columns for col in required_columns):
            log(f"Missing required columns in {input_filepath}")
            return
        finder_results = []
        for idx, row in df.iterrows():
            name = str(row["Full Name"]).strip()
            domain = str(row["Domain"]).strip()
            company = str(row.get("Company", "")).strip() if "Company" in df.columns else None
            emails = guess_emails(name, domain)
            verified_emails = []
            found = False
            email_result = None
            found_email = "Not Found"
            for email in emails:
                vres = verify_email(email)
                verified_emails.append((email, vres))
                if vres["error"].startswith("No MX record found"):
                    email_result = vres
                    break
                if vres["valid"]:
                    found = True
                    email_result = vres
                    found_email = email
                    break
                delay = random.uniform(1, 3)
                log(f"Sleeping for {delay:.2f} seconds after verifying {email}")
                time.sleep(delay)
            if not email_result and verified_emails:
                email_result = verified_emails[0][1]
                found_email = emails[0] if emails else "Not Found"
            elif not email_result:
                email_result = {
                    "valid": False, "smtp_code": None, "smtp_message": "", "error": "No emails generated"
                }
            result = {
                'name': name,
                'company': company,
                'domain': domain,
                'emails': verified_emails,
                'found': found,
                'found_email': found_email,
                'email_valid': email_result["valid"],
                'smtp_code': email_result["smtp_code"],
                'smtp_message': email_result["smtp_message"],
                'error': email_result["error"]
            }
            finder_results.append(result)
            log(f"Processed row {idx+1}/{len(df)}: {found_email} valid={result['email_valid']}")
        df['Found Email'] = [r['found_email'] for r in finder_results]
        df['Email Valid'] = [r['email_valid'] for r in finder_results]
        df['SMTP Code'] = [r['smtp_code'] for r in finder_results]
        df['SMTP Message'] = [r['smtp_message'] for r in finder_results]
        df['Error'] = [r['error'] for r in finder_results]
        df.to_excel(output_filepath, index=False)
        log(f"Saved results to {output_filepath}")
        subject = "Your Bulk Finder file is ready"
        body = f"""
        <p>Hello,</p>
        <p>Your file <b>{original_filename}</b> has been processed and is ready for download from your dashboard.</p>
        <p><a href='https://teck-translate.com/dashboard'>Go to Dashboard</a></p>
        <p>Thank you for using LeadFinder!</p>
        """
        send_brevo_email(user_email, subject, body)
        log(f"Notification email sent to {user_email}")
    except Exception as e:
        log(f"Error processing bulk finder file: {e}") 