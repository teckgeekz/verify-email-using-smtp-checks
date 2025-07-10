from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS
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
import datetime

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

# Configure CORS to allow requests from Next.js frontend
allowed_origins = [
    "http://localhost:3000",  # Next.js development server
    "http://127.0.0.1:3000",  # Alternative localhost
]

# Add production domain if specified in environment
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allowed_origins.extend(allowed_origins_env.split(","))

CORS(app, 
     origins=allowed_origins,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

app.config["UPLOAD_FOLDER"] = "uploads"  # Set the upload folder path
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize Firebase Admin and Firestore (if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.Client()

# CORS preflight handler
@app.route("/", methods=["OPTIONS"])
@app.route("/single-verify", methods=["OPTIONS"])
@app.route("/bulk-verify", methods=["OPTIONS"])
@app.route("/download/<filename>", methods=["OPTIONS"])
def handle_options():
    response = app.make_default_options_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

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
        
        # Always return JSON for POST requests (API calls)
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
        
        # Always return JSON for POST requests (API calls)
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
    
    if request.method == "GET":
        # Return simple success response for GET requests
        return jsonify({"message": "Bulk verify endpoint ready"})
    
    if request.method == "POST":
        # Authentication is still required for bulk operations
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
        
        # Process all emails in the file (no limit)
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
        
        result_df = pd.DataFrame(results)
        output_filename = f"verified_{filename.rsplit('.', 1)[0]}.xlsx"
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)
        result_df.to_excel(output_path, index=False)
        download_link = f"/download/{output_filename}"
        
        # Clean up uploaded file
        for f in os.listdir(app.config["UPLOAD_FOLDER"]):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], f)
            if f != output_filename and os.path.isfile(file_path):
                os.remove(file_path)
        
        return jsonify({
            "results": results,
            "download_link": download_link
        })

@app.route("/bulk-finder", methods=["POST"])
def bulk_finder():
    from flask import jsonify
    results = []
    row_limit = 20
    used_rows = 0
    user_id = None
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
    used_rows = user_data.get('bulk_finder_rows', 0)
    # Create per-user storage directory
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)
    os.makedirs(user_folder, exist_ok=True)
    file = request.files.get("file")
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)
    if filename.endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        os.remove(filepath)
        return jsonify({'error': 'Unsupported file format'}), 400
    # Check for required columns
    required_columns = ['Full Name', 'Domain']
    if not all(col in df.columns for col in required_columns):
        os.remove(filepath)
        return jsonify({'error': f"Missing required columns. Please include: {', '.join(required_columns)}"}), 400
    rows_to_process = min(row_limit - used_rows, len(df))
    if rows_to_process <= 0:
        os.remove(filepath)
        return jsonify({'error': 'You have reached your 20-row bulk finder limit.'}), 400
    df = df.head(rows_to_process)
    finder_results = []
    for idx, row in df.iterrows():
        name = str(row["Full Name"]).strip()
        domain = str(row["Domain"]).strip()
        company = str(row.get("Company", "")).strip() if "Company" in df.columns else None
        emails = guess_emails(name, domain)
        verified_emails = []
        found = False
        for email in emails:
            valid = verify_email(email)
            verified_emails.append((email, valid))
            if valid:
                found = True
                break
            delay = random.uniform(1, 3)
            print(f"Sleeping for {delay:.2f} seconds before next verification...")
            time.sleep(delay)
        result = {
            'name': name,
            'company': company,
            'domain': domain,
            'emails': verified_emails,
            'found': found
        }
        finder_results.append(result)
    df['Found Email'] = [result['emails'][0][0] if result['found'] else 'Not Found' for result in finder_results]
    df['Email Valid'] = [result['found'] for result in finder_results]
    user_doc.set({'bulk_finder_rows': used_rows + rows_to_process}, merge=True)
    output_filename = f"found_{filename.rsplit('.', 1)[0]}.xlsx"
    output_path = os.path.join(user_folder, output_filename)
    df.to_excel(output_path, index=False)
    try:
        bulk_finder_queries = user_doc.collection('bulk_finder_queries')
        log_data = {
            'filename': filename,
            'rows_processed': rows_to_process,
            'results': finder_results,
            'timestamp': datetime.datetime.now(datetime.timezone.utc)
        }
        bulk_finder_queries.add(log_data)
    except Exception as e:
        print(f"[Firestore log error] {e}")
    return jsonify({
        "results": finder_results,
        "download_link": f"/download/{output_filename}"
    })

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

def home():
    return "Flask is working!"

#if __name__ == "__main__":
#    app.run(debug=False)

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000)
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True  # ← This enables multiple requests
    )
