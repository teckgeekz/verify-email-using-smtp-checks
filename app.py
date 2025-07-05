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
import json

from dotenv import load_dotenv
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, auth

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firebase_key.json"

# Load Firebase config from .env
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"  # Set the upload folder path
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize Firebase Admin and Firestore (if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.Client()

@app.route("/", methods=["GET", "POST"])
def index():
    from flask import jsonify
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
        
        # Check if this is an AJAX request (has Authorization header)
        if 'Authorization' in request.headers:
            return jsonify(result)
    
    return render_template("index.html", result=result, firebase_config=firebase_config)


@app.route("/single-verify", methods=["GET", "POST"])
def single_verify():
    from flask import jsonify
    result = None
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            return jsonify({"error": "Email address is required"}), 400
        
        verify_result = verify_email(email)
        result = {
            "email": email,
            "status": verify_result
        }
        
        # Check if this is an AJAX request (has Authorization header)
        if 'Authorization' in request.headers:
            return jsonify(result)
    
    return render_template("single_verify.html", result=result, firebase_config=firebase_config)    

def firebase_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        id_token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
        if not id_token:
            return {'error': 'Authorization token required'}, 401
        try:
            decoded_token = auth.verify_id_token(id_token)
            request.user = decoded_token
        except Exception as e:
            return {'error': 'Authentication failed', 'details': str(e)}, 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/bulk-verify", methods=["GET", "POST"])
def bulk_verify():
    from flask import jsonify
    results = []
    download_link = None
    row_limit = 200
    used_rows = 0
    user_id = None
    # For GET, try to get user usage if authenticated
    if request.method == "GET":
        id_token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
        if id_token:
            try:
                decoded_token = auth.verify_id_token(id_token)
                user_id = decoded_token['uid']
                user_doc = db.collection('usage').document(user_id)
                user_data = user_doc.get().to_dict() or {}
                used_rows = user_data.get('bulk_rows', 0)
            except Exception:
                used_rows = 0
        # else: used_rows stays 0
        return render_template(
            "bulk_verify.html",
            results=[],
            download_link=None,
            used_rows=used_rows,
            row_limit=row_limit,
            firebase_config=firebase_config
        )
    if request.method == "POST":
        id_token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
        if not id_token:
            return jsonify({'error': 'Authorization token required'}), 401
        try:
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token['uid']
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
        user_doc = db.collection('usage').document(user_id)
        user_data = user_doc.get().to_dict() or {}
        used_rows = user_data.get('bulk_rows', 0)
        file = request.files.get("file")
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        if filename.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            os.remove(filepath)
            return jsonify({'error': 'Unsupported file format'}), 400
        if "Email" not in df.columns:
            os.remove(filepath)
            return jsonify({'error': "Missing required column: 'Email'"}), 400
        rows_to_process = min(row_limit - used_rows, len(df))
        if rows_to_process <= 0:
            os.remove(filepath)
            return jsonify({'error': 'You have reached your 200-row bulk verify limit.'}), 400
        df = df.head(rows_to_process)
        for _, row in df.iterrows():
            email = str(row["Email"]).strip()
            result = {
                "email": email,
                "status": verify_email(email)
            }
            results.append(result)
            delay = random.uniform(2, 5)
            print(f"Sleeping for {delay:.2f} seconds before next verification...")
            time.sleep(delay)
        user_doc.set({'bulk_rows': used_rows + rows_to_process}, merge=True)
        result_df = pd.DataFrame(results)
        output_filename = f"verified_{filename.rsplit('.', 1)[0]}.xlsx"
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)
        result_df.to_excel(output_path, index=False)
        download_link = f"/download/{output_filename}"
        for f in os.listdir(app.config["UPLOAD_FOLDER"]):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], f)
            if f != output_filename and os.path.isfile(file_path):
                os.remove(file_path)
        return jsonify({
            "results": results,
            "download_link": download_link
        })
    # GET request: render template
    return render_template(
        "bulk_verify.html",
        results=[],
        download_link=None,
        used_rows=used_rows,
        row_limit=row_limit,
        firebase_config=firebase_config
    )

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

def home():
    return "Flask is working!"

if __name__ == "__main__":
    app.run(debug=False)

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000)
