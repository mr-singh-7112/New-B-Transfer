#!/usr/bin/env python3
"""
B-Transfer Server v2.3.2 - Simplified Stable Version
Ultra-fast file transfer with basic security
Copyright (c) 2025 Balsim Technologies. All rights reserved.
"""

import os
import time
import threading
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template_string, session
from werkzeug.utils import secure_filename
import socket

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5GB limit

# Security settings
MAX_UPLOADS_PER_SESSION = 50
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav',
    'zip', 'rar', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv'
}

# Create uploads folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_session_id():
    """Generate unique session ID"""
    return secrets.token_hex(16)

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def log_security_event(event_type, details):
    """Log security events"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {event_type}: {details}\n"
    with open('security.log', 'a') as f:
        f.write(log_entry)

def save_file_metadata(filename, metadata):
    """Save file metadata"""
    metadata_file = os.path.join(UPLOAD_FOLDER, f"{filename}.meta")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)

def load_file_metadata(filename):
    """Load file metadata"""
    metadata_file = os.path.join(UPLOAD_FOLDER, f"{filename}.meta")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return None

def cleanup_old_files():
    """Clean up files older than 24 hours"""
    while True:
        try:
            current_time = time.time()
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath) and not filename.endswith('.meta'):
                    # Check file age
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > 24 * 3600:  # 24 hours
                        try:
                            os.remove(filepath)
                            # Remove metadata file
                            meta_file = f"{filepath}.meta"
                            if os.path.exists(meta_file):
                                os.remove(meta_file)
                            print(f"🗑️ Auto-deleted old file: {filename}")
                        except Exception as e:
                            print(f"❌ Failed to delete old file {filename}: {e}")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
        
        time.sleep(3600)  # Run every hour

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.before_request
def security_check():
    """Security checks before each request"""
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
        session['upload_count'] = 0
        session['last_upload_time'] = 0
    
    # Rate limiting
    current_time = time.time()
    if request.endpoint == 'upload_file':
        # Check upload count per session
        if session['upload_count'] >= MAX_UPLOADS_PER_SESSION:
            log_security_event('RATE_LIMIT_EXCEEDED', f'Session: {session["session_id"]}')
            return jsonify({'error': 'Upload limit exceeded for this session'}), 429
        
        # Check time between uploads
        if current_time - session['last_upload_time'] < 1:  # 1 second between uploads
            log_security_event('RATE_LIMIT_EXCEEDED', f'Session: {session["session_id"]}')
            return jsonify({'error': 'Please wait before uploading another file'}), 429
        
        session['upload_count'] += 1
        session['last_upload_time'] = current_time
    
    # Log request
    client_ip = get_client_ip()
    log_security_event('REQUEST', f'{request.method} {request.endpoint} from {client_ip}')

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(open('b_transfer_ui.html').read())

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file with improved speed for large files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            log_security_event('INVALID_FILE_TYPE', file.filename)
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate secure filename
        original_filename = file.filename
        filename = secure_filename(file.filename)
        
        # Handle duplicate filenames
        counter = 1
        original_name = filename
        while os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            name, ext = os.path.splitext(original_name)
            filename = f"{name}_{counter}{ext}"
            counter += 1
        
        # Save file directly
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        # Save metadata
        metadata = {
            'original_name': original_filename,
            'size': file_size,
            'upload_time': datetime.now().isoformat(),
            'session_id': session['session_id'],
            'is_locked': False,
            'password_hash': None
        }
        save_file_metadata(filename, metadata)
        
        log_security_event('UPLOAD_SUCCESS', f'{filename} ({get_file_size(file_size)})')
        print(f"✅ File uploaded: {filename} ({get_file_size(file_size)})")
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'size': file_size
        }), 200
        
    except Exception as e:
        log_security_event('UPLOAD_ERROR', f'Exception: {str(e)}')
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/files')
def list_files():
    """List all files"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath) and not filename.endswith('.meta'):
                metadata = load_file_metadata(filename)
                file_info = {
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'is_locked': metadata.get('is_locked', False) if metadata else False,
                    'is_owner': metadata.get('session_id') == session.get('session_id') if metadata else False
                }
                files.append(file_info)
        
        files.sort(key=lambda x: x['name'])
        return jsonify(files)
        
    except Exception as e:
        log_security_event('LIST_ERROR', f'Exception: {str(e)}')
        print(f"❌ List files error: {str(e)}")
        return jsonify({'error': 'Failed to list files'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            log_security_event('DOWNLOAD_ERROR', f'File not found: {filename}')
            return jsonify({'error': 'File not found'}), 404
        
        # Load metadata for original filename
        metadata = load_file_metadata(filename)
        original_name = metadata.get('original_name', filename) if metadata else filename
        
        log_security_event('DOWNLOAD_SUCCESS', filename)
        print(f"📥 File downloaded: {filename}")
        return send_file(filepath, as_attachment=True, download_name=original_name)
        
    except Exception as e:
        log_security_event('DOWNLOAD_ERROR', f'Exception: {str(e)}')
        print(f"❌ Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Load metadata
        metadata = load_file_metadata(filename)
        if not metadata:
            return jsonify({'error': 'File metadata not found'}), 404
        
        # Check ownership
        if metadata.get('session_id') != session.get('session_id'):
            log_security_event('DELETE_ERROR', f'Unauthorized delete attempt: {filename}')
            return jsonify({'error': 'You can only delete your own files'}), 403
        
        # Delete file
        os.remove(filepath)
        
        # Remove metadata file
        meta_file = os.path.join(UPLOAD_FOLDER, f"{filename}.meta")
        if os.path.exists(meta_file):
            os.remove(meta_file)
        
        log_security_event('DELETE_SUCCESS', filename)
        print(f"🗑️ File deleted: {filename}")
        return jsonify({'status': 'success', 'message': 'File deleted successfully'})
        
    except Exception as e:
        log_security_event('DELETE_ERROR', f'Exception: {str(e)}')
        print(f"❌ Delete error: {str(e)}")
        return jsonify({'error': 'Delete failed'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        uploads_ok = os.path.exists(UPLOAD_FOLDER)
        
        health_status = {
            'status': 'healthy' if uploads_ok else 'unhealthy',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '2.3.2',
            'service': 'B-Transfer by Balsim Technologies',
            'copyright': 'Copyright (c) 2025 Balsim Technologies. All rights reserved.',
            'features': ['file_transfer', 'rate_limiting', 'session_management'],
            'checks': {
                'uploads_directory': uploads_ok
            }
        }
        
        return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503
        
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return jsonify({'error': 'Health check failed'}), 500

if __name__ == '__main__':
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    port = int(os.environ.get('PORT', 8081))
    
    # Check if running on Railway
    if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
        print("🚂 B-Transfer Server Starting on Railway...")
        print("=" * 60)
        print("Copyright (c) 2025 Balsim Technologies. All rights reserved.")
        print("Proprietary and confidential software.")
        print("=" * 60)
        print("☁️ Cloud deployment - Simplified Stable Version")
        print("🔄 Server supports up to 5GB file transfers")
        print("🔐 Enhanced security with rate limiting")
        print("⚡ Optimized for large file uploads")
        print("🕐 Auto-delete after 24 hours")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("")
        
        # Railway production settings
        app.config['PREFERRED_URL_SCHEME'] = 'https'
        app.run(host='0.0.0.0', port=port, threaded=True, debug=False)
        
    else:
        # Local development
        local_ip = get_local_ip()
        
        print("🚀 B-Transfer Server Starting...")
        print("=" * 60)
        print("Copyright (c) 2025 Balsim Technologies. All rights reserved.")
        print("Proprietary and confidential software.")
        print("=" * 60)
        print(f"📱 Access from your phone: http://{local_ip}:{port}")
        print(f"💻 Access from this computer: http://localhost:{port}")
        print("=" * 60)
        print("📁 Files saved in 'uploads' folder")
        print("🔄 Server supports up to 5GB file transfers")
        print("🔐 Enhanced security with rate limiting")
        print("⚡ Optimized for large file uploads")
        print("🕐 Auto-delete after 24 hours")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("")
        
        app.run(host='0.0.0.0', port=port, threaded=True, debug=False) 