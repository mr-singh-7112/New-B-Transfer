#!/usr/bin/env python3
"""
B-Transfer Server v2.3.0
Ultra-fast file transfer with military-grade security
Copyright (c) 2025 Balsim Technologies. All rights reserved.
"""

import os
import time
import threading
import hashlib
import secrets
import json
import base64
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template_string, session, Response
from werkzeug.utils import secure_filename
import socket
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cloud_storage import get_cloud_storage
import tempfile
import shutil

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5GB limit

# Security settings
MAX_UPLOADS_PER_SESSION = 50
MAX_FILE_SIZE_PER_UPLOAD = 5 * 1024 * 1024 * 1024  # 5GB
CLOUD_STORAGE_THRESHOLD = 100 * 1024 * 1024  # 100MB - use cloud for files > 100MB
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

# Military-grade encryption functions
def derive_key(password, salt):
    """Derive encryption key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_file(file_data, password):
    """Encrypt file data with AES-256"""
    salt = os.urandom(16)
    key = derive_key(password, salt)
    
    # Generate random IV
    iv = os.urandom(16)
    
    # Create cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Pad data to block size
    block_size = 16
    padding_length = block_size - (len(file_data) % block_size)
    padded_data = file_data + bytes([padding_length] * padding_length)
    
    # Encrypt
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Create HMAC for integrity
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(iv + encrypted_data)
    mac = h.finalize()
    
    return salt + iv + mac + encrypted_data

def decrypt_file(encrypted_data, password):
    """Decrypt file data with AES-256"""
    try:
        # Extract components
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        mac = encrypted_data[32:64]
        encrypted = encrypted_data[64:]
        
        # Derive key
        key = derive_key(password, salt)
        
        # Verify HMAC
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(iv + encrypted)
        h.verify(mac)
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted) + decryptor.finalize()
        
        # Remove padding
        padding_length = decrypted_data[-1]
        return decrypted_data[:-padding_length]
        
    except Exception as e:
        raise ValueError("Incorrect password or corrupted data")

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
        
        file_size = 0
        storage_type = 'local'
        cloud_file_id = None
        
        # Check if file should be stored in cloud
        if file.content_length and file.content_length > CLOUD_STORAGE_THRESHOLD:
            # Use cloud storage for large files
            cloud_storage = get_cloud_storage()
            if cloud_storage:
                # Save to temp file first for faster processing
                temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{filename}")
                file.save(temp_path)
                
                # Upload to cloud
                cloud_result = cloud_storage.upload_file(temp_path, filename)
                if cloud_result:
                    file_size = cloud_result['size']
                    cloud_file_id = cloud_result['id']
                    storage_type = 'cloud'
                    # Remove temp file
                    os.remove(temp_path)
                else:
                    # Fallback to local storage
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    os.rename(temp_path, filepath)
                    file_size = os.path.getsize(filepath)
                    storage_type = 'local'
            else:
                # Cloud storage not available, use local
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                file_size = os.path.getsize(filepath)
                storage_type = 'local'
        else:
            # Use local storage for small files
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            file_size = os.path.getsize(filepath)
            storage_type = 'local'
        
        # Save metadata
        metadata = {
            'original_name': original_filename,
            'size': file_size,
            'upload_time': datetime.now().isoformat(),
            'session_id': session['session_id'],
            'is_locked': False,
            'password_hash': None,
            'storage_type': storage_type,
            'cloud_file_id': cloud_file_id
        }
        save_file_metadata(filename, metadata)
        
        log_security_event('UPLOAD_SUCCESS', f'{filename} ({get_file_size(file_size)})')
        print(f"✅ File uploaded: {filename} ({get_file_size(file_size)})")
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'size': file_size,
            'storage_type': storage_type
        }), 200
        
    except Exception as e:
        log_security_event('UPLOAD_ERROR', f'Exception: {str(e)}')
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/lock/<filename>', methods=['POST'])
def lock_file(filename):
    """Lock file with password protection"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'error': 'Password required'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Load metadata
        metadata = load_file_metadata(filename)
        if not metadata:
            return jsonify({'error': 'File metadata not found'}), 404
        
        # Check ownership (only file owner can lock)
        if metadata.get('session_id') != session.get('session_id'):
            log_security_event('LOCK_ERROR', f'Unauthorized lock attempt: {filename}')
            return jsonify({'error': 'You can only lock your own files'}), 403
        
        # Read file data
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        # Encrypt file
        encrypted_data = encrypt_file(file_data, password)
        
        # Save encrypted file
        with open(filepath, 'wb') as f:
            f.write(encrypted_data)
        
        # Update metadata
        metadata['is_locked'] = True
        metadata['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
        save_file_metadata(filename, metadata)
        
        log_security_event('LOCK_SUCCESS', filename)
        print(f"🔒 File locked: {filename}")
        
        return jsonify({
            'status': 'success',
            'message': 'File locked successfully'
        }), 200
        
    except Exception as e:
        log_security_event('LOCK_ERROR', f'Exception: {str(e)}')
        print(f"❌ Lock error: {str(e)}")
        return jsonify({'error': f'Lock failed: {str(e)}'}), 500

@app.route('/unlock/<filename>', methods=['POST'])
def unlock_file(filename):
    """Unlock file with password"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'error': 'Password required'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Load metadata
        metadata = load_file_metadata(filename)
        if not metadata:
            return jsonify({'error': 'File metadata not found'}), 404
        
        # Check if file is locked
        if not metadata.get('is_locked'):
            return jsonify({'error': 'File is not locked'}), 400
        
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if metadata.get('password_hash') != password_hash:
            log_security_event('UNLOCK_ERROR', f'Wrong password for: {filename}')
            return jsonify({'error': 'Incorrect password'}), 401
        
        # Read and decrypt file
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = decrypt_file(encrypted_data, password)
        except ValueError as e:
            log_security_event('UNLOCK_ERROR', f'Decryption failed: {filename}')
            return jsonify({'error': 'Incorrect password or corrupted file'}), 401
        
        # Save decrypted file
        with open(filepath, 'wb') as f:
            f.write(decrypted_data)
        
        # Update metadata
        metadata['is_locked'] = False
        metadata['password_hash'] = None
        save_file_metadata(filename, metadata)
        
        log_security_event('UNLOCK_SUCCESS', filename)
        print(f"🔓 File unlocked: {filename}")
        
        return jsonify({
            'status': 'success',
            'message': 'File unlocked successfully'
        }), 200
        
    except Exception as e:
        log_security_event('UNLOCK_ERROR', f'Exception: {str(e)}')
        print(f"❌ Unlock error: {str(e)}")
        return jsonify({'error': f'Unlock failed: {str(e)}'}), 500

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
    """Download file with password support for locked files"""
    try:
        # Load metadata
        metadata = load_file_metadata(filename)
        if not metadata:
            log_security_event('DOWNLOAD_ERROR', f'File not found: {filename}')
            return jsonify({'error': 'File not found'}), 404
        
        # Check if file is locked
        is_locked = metadata.get('is_locked', False)
        
        storage_type = metadata.get('storage_type', 'local')
        
        if storage_type == 'cloud':
            # Download from cloud storage
            cloud_storage = get_cloud_storage()
            if not cloud_storage:
                return jsonify({'error': 'Cloud storage not available'}), 500
            
            cloud_file_id = metadata.get('cloud_file_id')
            if not cloud_file_id:
                return jsonify({'error': 'Cloud file ID not found'}), 404
            
            # Download from cloud
            cloud_result = cloud_storage.download_file(cloud_file_id)
            if not cloud_result:
                return jsonify({'error': 'Failed to download from cloud'}), 500
            
            # Create temporary file
            temp_path = os.path.join(UPLOAD_FOLDER, f"temp_download_{filename}")
            with open(temp_path, 'wb') as f:
                f.write(cloud_result['content'])
            
            # If locked, decrypt the temp file
            if is_locked:
                # Check for password in request
                password = request.args.get('password')
                if not password:
                    return jsonify({'error': 'Password required for locked file'}), 401
                
                # Verify password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if metadata.get('password_hash') != password_hash:
                    return jsonify({'error': 'Incorrect password'}), 401
                
                # Decrypt file
                with open(temp_path, 'rb') as f:
                    encrypted_data = f.read()
                
                try:
                    decrypted_data = decrypt_file(encrypted_data, password)
                except ValueError:
                    return jsonify({'error': 'Incorrect password or corrupted file'}), 401
                
                # Save decrypted temp file
                with open(temp_path, 'wb') as f:
                    f.write(decrypted_data)
            
            log_security_event('DOWNLOAD_SUCCESS', f'{filename} (cloud)')
            print(f"📥 File downloaded from cloud: {filename}")
            
            # Return file and clean up after sending
            response = send_file(temp_path, as_attachment=True, download_name=metadata.get('original_name', filename))
            
            # Clean up temp file after response
            def cleanup():
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            response.call_on_close(cleanup)
            return response
            
        else:
            # Local file download
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if not os.path.exists(filepath) or not os.path.isfile(filepath):
                log_security_event('DOWNLOAD_ERROR', f'File not found: {filename}')
                return jsonify({'error': 'File not found'}), 404
            
            # If locked, check password
            if is_locked:
                password = request.args.get('password')
                if not password:
                    return jsonify({'error': 'Password required for locked file'}), 401
                
                # Verify password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if metadata.get('password_hash') != password_hash:
                    return jsonify({'error': 'Incorrect password'}), 401
                
                # Create temp decrypted file
                temp_path = os.path.join(UPLOAD_FOLDER, f"temp_download_{filename}")
                with open(filepath, 'rb') as f:
                    encrypted_data = f.read()
                
                try:
                    decrypted_data = decrypt_file(encrypted_data, password)
                except ValueError:
                    return jsonify({'error': 'Incorrect password or corrupted file'}), 401
                
                with open(temp_path, 'wb') as f:
                    f.write(decrypted_data)
                
                # Return decrypted file
                response = send_file(temp_path, as_attachment=True, download_name=metadata.get('original_name', filename))
                
                # Clean up temp file after response
                def cleanup():
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                
                response.call_on_close(cleanup)
                return response
            
            log_security_event('DOWNLOAD_SUCCESS', filename)
            print(f"📥 File downloaded: {filename}")
            return send_file(filepath, as_attachment=True, download_name=metadata.get('original_name', filename))
        
    except Exception as e:
        log_security_event('DOWNLOAD_ERROR', f'Exception: {str(e)}')
        print(f"❌ Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete file with password protection for locked files"""
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
        
        # Check if file is locked and requires password
        if metadata.get('is_locked'):
            data = request.get_json()
            password = data.get('password') if data else None
            
            if not password:
                log_security_event('DELETE_ERROR', f'Password required for locked file: {filename}')
                return jsonify({'error': 'Password required to delete locked file'}), 401
            
            # Verify password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if metadata.get('password_hash') != password_hash:
                log_security_event('DELETE_ERROR', f'Wrong password for locked file: {filename}')
                return jsonify({'error': 'Incorrect password'}), 401
        
        # Delete file based on storage type
        storage_type = metadata.get('storage_type', 'local')
        
        if storage_type == 'cloud':
            # Delete from cloud storage
            cloud_storage = get_cloud_storage()
            if cloud_storage:
                cloud_file_id = metadata.get('cloud_file_id')
                if cloud_file_id:
                    cloud_storage.delete_file(cloud_file_id)
        else:
            # Delete local file
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
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
            'version': '2.3.0',
            'service': 'B-Transfer by Balsim Technologies',
            'copyright': 'Copyright (c) 2025 Balsim Technologies. All rights reserved.',
            'features': ['file_locking', 'military_grade_encryption', 'rate_limiting', 'cloud_storage', 'password_protected_downloads'],
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
        print("☁️ Cloud deployment with Google Cloud Storage integration")
        print("🔄 Server supports up to 5GB file transfers")
        print("🔐 Enhanced security with rate limiting")
        print("🔒 Military-grade file locking with AES-256")
        print("🔑 Password-protected downloads for locked files")
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
        print("📁 Files saved in 'uploads' folder and Google Cloud Storage")
        print("🔄 Server supports up to 5GB file transfers")
        print("☁️ Large files (>100MB) stored in Google Cloud Storage")
        print("🔐 Enhanced security with rate limiting")
        print("🔒 Military-grade file locking with AES-256")
        print("🔑 Password-protected downloads for locked files")
        print("⚡ Optimized for large file uploads")
        print("🕐 Auto-delete after 24 hours")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("")
        
        app.run(host='0.0.0.0', port=port, threaded=True, debug=False) 