from flask import Flask, render_template, request, send_from_directory
from utils.linkedin_scraper import find_linkedin_profile
from utils.email_guesser import guess_emails
from utils.email_verifier import verify_email
import os
import pandas as pd
from werkzeug.utils import secure_filename
import shutil
import time
import random

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"  # Set the upload folder path

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form.get("name")
        company = request.form.get("company")
        domain = request.form.get("domain")

        linkedin_url, title = find_linkedin_profile(name, company)
        emails = guess_emails(name, domain)
        verified_emails = []
        for email in emails:
            valid = verify_email(email)
            verified_emails.append((email, valid))
            if valid:
                break
            delay = random.uniform(2, 5)
            print(f"Sleeping for {delay:.2f} seconds before next verification...")
            time.sleep(delay)
        result = {
            "name": name,
            "company": company,
            "linkedin": linkedin_url,
            "title": title,
            "emails": verified_emails
        }
    return render_template("index.html", result=result)

@app.route("/bulk-verify", methods=["GET", "POST"])
def bulk_verify():
    results = []
    download_link = None
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Read the file
            if filename.endswith(".csv"):
                df = pd.read_csv(filepath)
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(filepath)
            else:
                return "Unsupported file format"

            # Check if 'Email' column exists
            if "Email" not in df.columns:
                return "Missing required column: 'Email'"

            # Verify each email
            for _, row in df.iterrows():
                email = str(row["Email"]).strip()
                result = {
                    "email": email,
                    "status": verify_email(email)
                }
                results.append(result)
                # Delay for better deliverability and to avoid rate-limiting
                delay = random.uniform(2, 5)
                print(f"Sleeping for {delay:.2f} seconds before next verification...")
                time.sleep(delay)

            # Save results to Excel
            result_df = pd.DataFrame(results)
            output_filename = f"verified_{filename.rsplit('.', 1)[0]}.xlsx"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)
            result_df.to_excel(output_path, index=False)
            download_link = f"/download/{output_filename}"

            # Clean uploads directory except the result file
            for f in os.listdir(app.config["UPLOAD_FOLDER"]):
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], f)
                if f != output_filename and os.path.isfile(file_path):
                    os.remove(file_path)

    return render_template("bulk_verify.html", results=results, download_link=download_link)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

def home():
    return "Flask is working!"

if __name__ == "__main__":
    app.run(debug=False)
