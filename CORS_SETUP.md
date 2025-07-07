# CORS Configuration for Flask API

This document explains the CORS (Cross-Origin Resource Sharing) configuration for the Flask API to allow communication with the Next.js frontend.

## What's Been Added

### 1. Flask-CORS Dependency
- Added `flask-cors` to `requirements.txt`
- Install with: `pip install flask-cors`

### 2. CORS Configuration in app.py

```python
from flask_cors import CORS

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
```

### 3. CORS Preflight Handlers
Added OPTIONS route handlers for all endpoints to handle preflight requests:

```python
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
```

## Configuration Details

### Allowed Origins
- **Development**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Production**: Can be configured via `ALLOWED_ORIGINS` environment variable

### Allowed Methods
- `GET` - For retrieving data
- `POST` - For submitting forms and file uploads
- `OPTIONS` - For CORS preflight requests

### Allowed Headers
- `Content-Type` - For JSON and form data
- `Authorization` - For Firebase authentication tokens

### Credentials Support
- `supports_credentials=True` - Allows cookies and authentication headers

## Environment Variables

### ALLOWED_ORIGINS
Set this environment variable to specify additional allowed origins for production:

```bash
# Single domain
ALLOWED_ORIGINS=https://yourdomain.com

# Multiple domains (comma-separated)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Installation

1. Install the new dependency:
   ```bash
   pip install flask-cors
   ```

2. Or update all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Testing CORS

You can test if CORS is working by:

1. Starting the Flask API: `python app.py`
2. Starting the Next.js frontend: `npm run dev`
3. Making requests from the frontend to the API

The browser should no longer show CORS errors when making requests from `localhost:3000` to `localhost:5000`.

## Security Considerations

- Only allow necessary origins
- Use HTTPS in production
- Consider implementing rate limiting
- Validate all incoming requests
- Keep dependencies updated

## Troubleshooting

### Common Issues

1. **CORS errors still appearing**
   - Check that flask-cors is installed
   - Verify the origins list includes your frontend URL
   - Ensure the Flask app is restarted after changes

2. **Authentication headers not working**
   - Verify `Authorization` is in the allowed_headers list
   - Check that `supports_credentials=True` is set

3. **File uploads failing**
   - Ensure `Content-Type` is in allowed_headers
   - Check that the request includes proper CORS headers 