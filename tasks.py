from utils.celery_worker import celery
from utils.email_sender import send_brevo_email
import time

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