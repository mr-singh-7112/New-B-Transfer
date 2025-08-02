from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import time
import threading
import hashlib
import secrets
import json
import base64
from datetime import datetime, timedelta
import tempfile
import shutil

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Setup upload directory
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Security settings
MAX_UPLOADS_PER_SESSION = 50
MAX_FILE_SIZE_PER_UPLOAD = 5 * 1024 * 1024 * 1024  # 5GB
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav',
    'zip', 'rar', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv'
}

def get_file_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_session_id():
    return hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:16]

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def log_security_event(event_type, details):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {event_type}: {details} - IP: {get_client_ip()}\n"
    print(log_entry)  # Vercel logs

@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'B-Transfer API is running on Vercel!',
        'service': 'B-Transfer by Balsim Technologies',
        'version': '2.1.0',
        'deployment': 'Vercel Serverless',
        'endpoints': {
            'health': '/health',
            'files': '/files',
            'upload': '/upload (POST)',
            'download': '/download/<filename>',
            'delete': '/delete/<filename> (DELETE)'
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/health')
def health_check():
    try:
        uploads_ok = os.path.exists(UPLOAD_FOLDER)
        
        health_status = {
            'status': 'healthy' if uploads_ok else 'unhealthy',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '2.1.0',
            'service': 'B-Transfer by Balsim Technologies',
            'deployment': 'Vercel Serverless',
            'checks': {
                'uploads_directory': uploads_ok,
                'temp_storage': True
            }
        }
        
        return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503
        
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return jsonify({'error': 'Health check failed'}), 500

@app.route('/files')
def list_files():
    try:
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    files.append({
                        'name': filename,
                        'size': size,
                        'size_formatted': get_file_size(size),
                        'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                    })
        
        return jsonify({
            'status': 'success',
            'files': files,
            'count': len(files)
        })
        
    except Exception as e:
        print(f"❌ List files error: {str(e)}")
        return jsonify({'error': 'Failed to list files'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Handle duplicate filenames
        counter = 1
        original_filename = filename
        while os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            counter += 1
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        log_security_event('UPLOAD_SUCCESS', f'{filename} ({get_file_size(file_size)})')
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded successfully',
            'filename': filename,
            'size': file_size,
            'size_formatted': get_file_size(file_size)
        })
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        log_security_event('DOWNLOAD_SUCCESS', filename)
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(filepath)
        log_security_event('DELETE_SUCCESS', filename)
        
        return jsonify({'status': 'success', 'message': 'File deleted successfully'})
        
    except Exception as e:
        print(f"❌ Delete error: {str(e)}")
        return jsonify({'error': 'Delete failed'}), 500

# Vercel serverless function handler
def handler(request, context):
    return app(request, context)

if __name__ == '__main__':
    app.run(debug=True) 