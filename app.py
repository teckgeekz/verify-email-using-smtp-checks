from flask import Flask, render_template, request, send_from_directory, send_file
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
from utils.email_sender import send_brevo_email
from tasks import process_bulk_file

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
    import datetime
    result = None
    if request.method == "POST":
        name = request.form.get("name")
        company = request.form.get("company") or None
        domain = request.form.get("domain")

        emails = guess_emails(name, domain)
        verified_emails = []
        found = False
        for email in emails:
            valid = verify_email(email)
            print(f"[LeadFinder] Tested: {email} | Valid: {valid}")
            verified_emails.append((email, valid))
            if valid:
                found = True
                break
            delay = random.uniform(1, 3)
            print(f"Sleeping for {delay:.2f} seconds before next verification...")
            time.sleep(delay)
        # Build emails for frontend (list of arrays) and for Firestore (list of dicts)
        emails_for_frontend = [list(email_tuple) for email_tuple in verified_emails]
        emails_for_firestore = [
            {'email': email_tuple[0], 'valid': email_tuple[1]} for email_tuple in verified_emails
        ]
        result = {
            "name": name,
            "company": company,
            "linkedin": None,
            "title": None,
            "emails": emails_for_frontend
        }
        # --- Firestore logging for Lead Contact Finder ---
        if 'Authorization' in request.headers:
            id_token = None
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
            if id_token:
                try:
                    decoded_token = auth.verify_id_token(id_token)
                    user_id = decoded_token['uid']
                    user_doc = db.collection('usage').document(user_id)
                    lead_queries = user_doc.collection('lead_queries')
                    # Use emails_for_firestore for Firestore logging
                    safe_result = dict(result)
                    safe_result['emails'] = emails_for_firestore
                    log_data = {
                        'name': name,
                        'company': company,
                        'domain': domain,
                        'result': safe_result if found else 'Not Found',
                        'timestamp': datetime.datetime.now(datetime.timezone.utc)
                    }
                    print(f"[Firestore log] Attempting to add: {log_data}")
                    lead_queries.add(log_data)
                    print("[Firestore log] Successfully added log entry.")
                except Exception as e:
                    import traceback
                    print(f"[Firestore log error] {e}")
                    traceback.print_exc()
                    if 'log_data' in locals():
                        print(f"[Firestore log error] Data: {log_data}")
                    else:
                        print("[Firestore log error] log_data was not set")
            else:
                print("[Firestore log] No id_token found in Authorization header.")
        else:
            print("[Firestore log] No Authorization header present in request.")
        # Check if this is an AJAX request (has Authorization header)
        if 'Authorization' in request.headers:
            return jsonify(result)
    
    return render_template("index.html", result=result, firebase_config=firebase_config)


@app.route("/single-verify", methods=["GET", "POST"])
def single_verify():
    from flask import jsonify
    import datetime
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
        # --- Firestore logging for Single Email Verify ---
        if 'Authorization' in request.headers:
            id_token = None
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                id_token = auth_header.split('Bearer ')[1]
            if id_token:
                try:
                    decoded_token = auth.verify_id_token(id_token)
                    user_id = decoded_token['uid']
                    user_doc = db.collection('usage').document(user_id)
                    single_queries = user_doc.collection('single_verify_queries')
                    log_data = {
                        'email': email,
                        'result': result if verify_result else 'Invalid or unverifiable',
                        'timestamp': datetime.datetime.now(datetime.timezone.utc)
                    }
                    print(f"[Firestore log] Attempting to add: {log_data}")
                    single_queries.add(log_data)
                    print("[Firestore log] Successfully added log entry.")
                except Exception as e:
                    import traceback
                    print(f"[Firestore log error] {e}")
                    traceback.print_exc()
                    if 'log_data' in locals():
                        print(f"[Firestore log error] Data: {log_data}")
                    else:
                        print("[Firestore log error] log_data was not set")
            else:
                print("[Firestore log] No id_token found in Authorization header.")
        else:
            print("[Firestore log] No Authorization header present in request.")
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
    row_limit = 2000
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
        if "Email" not in df.columns:
            os.remove(filepath)
            return jsonify({'error': "Missing required column: 'Email'"}), 400
        rows_to_process = min(row_limit - used_rows, len(df))
        if rows_to_process <= 0:
            os.remove(filepath)
            return jsonify({'error': 'You have reached your 2000-row bulk verify limit.'}), 400
        df = df.head(rows_to_process)
        verification_results = []
        for idx, row in df.iterrows():
            email = str(row["Email"]).strip()
            status = verify_email(email)
            verification_results.append(status)
            delay = random.uniform(1, 3)
            print(f"Sleeping for {delay:.2f} seconds before next verification...")
            time.sleep(delay)
        df['Verification Result'] = verification_results
        user_doc.set({'bulk_rows': used_rows + rows_to_process}, merge=True)
        output_filename = f"verified_{filename.rsplit('.', 1)[0]}.xlsx"
        output_path = os.path.join(user_folder, output_filename)
        df.to_excel(output_path, index=False)
        # Send notification email to user asynchronously with Celery
        if user_id:
            process_bulk_file.delay(user_id, output_filename)
        return jsonify({
            "results": results,
            "message": "File received and is being processed. It will be available for download from your dashboard."
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

@app.route("/bulk-finder", methods=["GET", "POST"])
def bulk_finder():
    from flask import jsonify
    results = []
    download_link = None
    row_limit = 20
    used_rows = 0
    user_id = None
    user_email = None
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
                user_email = decoded_token.get('email')
                if user_email in ["abhishek.roney@gmail.com", "jeoffrey.mathews@gmail.com"]:
                    row_limit = 2000
                user_doc = db.collection('usage').document(user_id)
                user_data = user_doc.get().to_dict() or {}
                used_rows = user_data.get('bulk_finder_rows', 0)
            except Exception:
                used_rows = 0
        # else: used_rows stays 0
        return render_template(
            "bulk_finder.html",
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
            user_email = decoded_token.get('email')
            if user_email in ["abhishek.roney@gmail.com", "jeoffrey.mathews@gmail.com"]:
                row_limit = 2000
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
        user_doc = db.collection('usage').document(user_id)
        user_data = user_doc.get().to_dict() or {}
        used_rows = user_data.get('bulk_finder_rows', 0)
        # Create per-user storage directory
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)
        os.makedirs(user_folder, exist_ok=True)
        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify({'error': 'No file uploaded'}), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(user_folder, filename)
        file.save(filepath)
        # Prepare output file path
        output_filename = f"found_{filename.rsplit('.', 1)[0]}.xlsx"
        output_path = os.path.join(user_folder, output_filename)
        print(f"[BulkFinder] Enqueuing Celery task for user: {user_email}, input: {filepath}, output: {output_path}")
        from tasks import process_bulk_finder_file
        process_bulk_finder_file.delay(user_email, filepath, output_path, filename)
        print(f"[BulkFinder] Task enqueued for {user_email}")
        # Update usage (20 row limit)
        user_doc.set({'bulk_finder_rows': used_rows + 1}, merge=True)
        return jsonify({
            "message": "File received and is being processed. It will be available for download from your dashboard."
        })
    # GET request: render template
    return render_template(
        "bulk_finder.html",
        results=[],
        download_link=None,
        used_rows=used_rows,
        row_limit=row_limit,
        firebase_config=firebase_config
    )

@app.route("/upgrade-click", methods=["POST"])
def upgrade_click():
    from flask import jsonify
    if 'Authorization' not in request.headers:
        return jsonify({'error': 'Authorization token required'}), 401
    id_token = None
    auth_header = request.headers['Authorization']
    if auth_header.startswith('Bearer '):
        id_token = auth_header.split('Bearer ')[1]
    if not id_token:
        return jsonify({'error': 'Authorization token required'}), 401
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        user_doc = db.collection('usage').document(user_id)
        user_data = user_doc.get().to_dict() or {}
        current_count = user_data.get('UpgradeCount', 0)
        new_count = current_count + 1
        user_doc.set({'Upgrade': True, 'UpgradeCount': new_count}, merge=True)
        return jsonify({'Upgrade': True, 'UpgradeCount': new_count})
    except Exception as e:
        import traceback
        print(f"[Upgrade log error] {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to record upgrade click', 'details': str(e)}), 500

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template('dashboard.html', firebase_config=firebase_config)

@app.route("/api/dashboard-data", methods=["GET"])
def dashboard_data():
    from flask import jsonify
    if 'Authorization' not in request.headers:
        return jsonify({'error': 'Authorization token required'}), 401
    id_token = None
    auth_header = request.headers['Authorization']
    if auth_header.startswith('Bearer '):
        id_token = auth_header.split('Bearer ')[1]
    if not id_token:
        return jsonify({'error': 'Authorization token required'}), 401
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        user_doc = db.collection('usage').document(user_id)
        # Fetch Lead Contact Finder history
        lead_queries = list(user_doc.collection('lead_queries').order_by('timestamp', direction=firestore.Query.DESCENDING).stream())
        lead_history = [doc.to_dict() for doc in lead_queries]
        # Fetch Single Email Verification history
        single_queries = list(user_doc.collection('single_verify_queries').order_by('timestamp', direction=firestore.Query.DESCENDING).stream())
        single_history = [doc.to_dict() for doc in single_queries]
        return jsonify({'lead_history': lead_history, 'single_history': single_history})
    except Exception as e:
        import traceback
        print(f"[Dashboard error] {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch dashboard data', 'details': str(e)}), 500

@app.route("/admin", methods=["GET"])
def admin_dashboard():
    return render_template('admin_dashboard.html', firebase_config=firebase_config)

@app.route("/api/admin-dashboard-data", methods=["GET"])
def admin_dashboard_data():
    from flask import jsonify
    if 'Authorization' not in request.headers:
        return jsonify({'error': 'Authorization token required'}), 401
    id_token = None
    auth_header = request.headers['Authorization']
    if auth_header.startswith('Bearer '):
        id_token = auth_header.split('Bearer ')[1]
    if not id_token:
        return jsonify({'error': 'Authorization token required'}), 401
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_email = decoded_token.get('email')
        if user_email != 'jeoffrey.mathews@gmail.com':
            return jsonify({'error': 'Unauthorized'}), 403
        users_ref = db.collection('usage').stream()
        user_docs = list(users_ref)
        print(f"[Admin Dashboard] All user_ids in Firestore: {[doc.id for doc in user_docs]}")
        user_stats = []
        for user_doc in user_docs:
            user_id = user_doc.id
            try:
                user_data = user_doc.to_dict() or {}
                # Try to get email from user_data, fallback to Firebase Auth user record
                email = user_data.get('email')
                if not email:
                    try:
                        user_record = auth.get_user(user_id)
                        email = user_record.email
                        print(f"[Admin Dashboard] user_id: {user_id}, email from auth: {email}")
                    except Exception as e:
                        print(f"[Admin Dashboard] user_id: {user_id}, error fetching email: {e}")
                        email = user_id  # fallback if user not found
                else:
                    print(f"[Admin Dashboard] user_id: {user_id}, email from Firestore: {email}")
                lead_queries = list(db.collection('usage').document(user_id).collection('lead_queries').stream())
                single_queries = list(db.collection('usage').document(user_id).collection('single_verify_queries').stream())
                bulk_finder_queries = list(db.collection('usage').document(user_id).collection('bulk_finder_queries').stream())
                user_stats.append({
                    'user_id': user_id,
                    'email': email,
                    'lead_count': len(lead_queries),
                    'single_count': len(single_queries),
                    'bulk_rows': user_data.get('bulk_rows', 0),
                    'bulk_finder_rows': user_data.get('bulk_finder_rows', 0),
                    'files': []
                })
                user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)
                files = []
                if os.path.exists(user_folder):
                    verified_files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f)) and f.startswith('verified_')]
                    found_files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f)) and f.startswith('found_')]
                    files = verified_files + found_files
                user_stats[-1]['files'] = files
            except Exception as e:
                print(f"[Admin Dashboard] Exception processing user_id {user_id}: {e}")
        print(f"[Admin Dashboard] Total users processed: {len(user_stats)}")
        return jsonify({'user_stats': user_stats})
    except Exception as e:
        import traceback
        print(f"[Admin Dashboard error] {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch admin dashboard data', 'details': str(e)}), 500

@app.route("/api/user-files", methods=["GET"])
def user_files():
    from flask import jsonify
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
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)
        if not os.path.exists(user_folder):
            return jsonify({'files': []})
        files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f))]
        # Return files sorted by modified time, newest first
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(user_folder, f)), reverse=True)
        return jsonify({'files': files})
    except Exception as e:
        import traceback
        print(f"[User files error] {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch user files', 'details': str(e)}), 500

@app.route("/download/<filename>")
def download_file(filename):
    from flask import request
    id_token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            id_token = auth_header.split('Bearer ')[1]
    if not id_token:
        return {'error': 'Authorization token required'}, 401
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        user_email = decoded_token.get('email')
        # Check for admin override
        admin_user_id = request.args.get('admin_user')
        if admin_user_id and user_email == 'jeoffrey.mathews@gmail.com':
            user_folder = os.path.join(app.config["UPLOAD_FOLDER"], admin_user_id)
        else:
            user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)
        file_path = os.path.join(user_folder, filename)
        if not os.path.exists(file_path):
            return {'error': 'File not found'}, 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        import traceback
        print(f"[Download error] {e}")
        traceback.print_exc()
        return {'error': 'Failed to download file', 'details': str(e)}, 500

@app.route("/api/delete-file", methods=["POST"])
def delete_file_api():
    from flask import jsonify
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
        user_folder = os.path.join(app.config["UPLOAD_FOLDER"], user_id)
        data = request.get_json()
        filename = data.get('filename') if data else None
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        file_path = os.path.join(user_folder, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        os.remove(file_path)
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        print(f"[Delete file error] {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete file', 'details': str(e)}), 500

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
