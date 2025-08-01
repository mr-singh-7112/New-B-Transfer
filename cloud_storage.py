#!/usr/bin/env python3
"""
Cloud Storage Module for B-Transfer
Handles file storage in Google Cloud Storage for large files (up to 5GB)
"""

import os
import io
import tempfile
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import pickle

# Google Cloud Storage API scopes
SCOPES = ['https://www.googleapis.com/auth/devstorage.read_write']

class CloudStorage:
    def __init__(self):
        self.service = None
        self.bucket_name = 'b-transfer-files'
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Cloud Storage API"""
        try:
            # Try API key first (for public access)
            api_key = os.environ.get('GOOGLE_API_KEY')
            if api_key:
                self.service = build('storage', 'v1', developerKey=api_key)
                print("🔑 Using Google Cloud Storage API key authentication")
                self._ensure_bucket()
                return
            
            # Try service account (for private access)
            creds = None
            
            # Load existing credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # For Railway deployment, use service account
                    if os.path.exists('service-account.json'):
                        from google.oauth2 import service_account
                        creds = service_account.Credentials.from_service_account_file(
                            'service-account.json', scopes=SCOPES)
                    elif os.environ.get('GOOGLE_SERVICE_ACCOUNT'):
                        # Railway environment variable
                        import json
                        from google.oauth2 import service_account
                        service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
                        creds = service_account.Credentials.from_service_account_info(
                            service_account_info, scopes=SCOPES)
                    else:
                        # Fallback to local development
                        if os.path.exists('credentials.json'):
                            flow = InstalledAppFlow.from_client_secrets_file(
                                'credentials.json', SCOPES)
                            creds = flow.run_local_server(port=0)
                        else:
                            print("⚠️ No Google Cloud credentials found")
                            return None
                
                # Save credentials
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('storage', 'v1', credentials=creds)
            print("🔐 Using Google Cloud Storage service account authentication")
            self._ensure_bucket()
            
        except Exception as e:
            print(f"❌ Google Cloud Storage authentication failed: {e}")
            self.service = None
    
    def _ensure_bucket(self):
        """Ensure B-Transfer bucket exists in Google Cloud Storage"""
        try:
            # For API key access, we'll use a public bucket or create one
            # Search for existing bucket
            try:
                bucket = self.service.buckets().get(bucket=self.bucket_name).execute()
                print(f"📦 Using existing B-Transfer bucket: {self.bucket_name}")
            except:
                # Try to create new bucket (may not work with API key)
                try:
                    bucket_body = {
                        'name': self.bucket_name,
                        'location': 'US'
                    }
                    bucket = self.service.buckets().insert(project='b-transfer-cloud', body=bucket_body).execute()
                    print(f"📦 Created new B-Transfer bucket: {self.bucket_name}")
                except Exception as create_error:
                    print(f"⚠️ Could not create bucket with API key: {create_error}")
                    print("📦 Will use default bucket for file storage")
                    self.bucket_name = None
                
        except Exception as e:
            print(f"⚠️ Cloud storage initialization failed: {e}")
            self.bucket_name = None
    
    def upload_file(self, file_path, filename, file_data=None):
        """Upload file to Google Cloud Storage"""
        try:
            if not self.service:
                return None
            
            # Prepare file metadata
            media_body = None
            
            if file_data:
                media_body = MediaIoBaseUpload(
                    io.BytesIO(file_data),
                    mimetype='application/octet-stream',
                    resumable=True
                )
            else:
                media_body = MediaIoBaseUpload(
                    file_path,
                    mimetype='application/octet-stream',
                    resumable=True
                )
            
            # Upload to bucket
            if self.bucket_name:
                request = self.service.objects().insert(
                    bucket=self.bucket_name,
                    name=filename,
                    media_body=media_body
                )
            else:
                # Use default bucket
                request = self.service.objects().insert(
                    bucket='b-transfer-files',
                    name=filename,
                    media_body=media_body
                )
            
            response = request.execute()
            
            print(f"☁️ File uploaded to cloud storage: {filename}")
            return {
                'id': response.get('id'),
                'name': response.get('name'),
                'size': response.get('size', 0)
            }
            
        except Exception as e:
            print(f"❌ Cloud storage upload failed: {e}")
            return None
    
    def download_file(self, file_id):
        """Download file from Google Cloud Storage"""
        try:
            if not self.service:
                return None
            
            # Get file metadata
            if self.bucket_name:
                file = self.service.objects().get(bucket=self.bucket_name, object=file_id).execute()
            else:
                file = self.service.objects().get(bucket='b-transfer-files', object=file_id).execute()
            
            # Download file content
            if self.bucket_name:
                request = self.service.objects().get_media(bucket=self.bucket_name, object=file_id)
            else:
                request = self.service.objects().get_media(bucket='b-transfer-files', object=file_id)
            
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return {
                'name': file.get('name'),
                'content': file_content.getvalue(),
                'size': file.get('size', 0)
            }
            
        except Exception as e:
            print(f"❌ Cloud storage download failed: {e}")
            return None
    
    def delete_file(self, file_id):
        """Delete file from Google Cloud Storage"""
        try:
            if not self.service:
                return False
            
            if self.bucket_name:
                self.service.objects().delete(bucket=self.bucket_name, object=file_id).execute()
            else:
                self.service.objects().delete(bucket='b-transfer-files', object=file_id).execute()
            
            return True
            
        except Exception as e:
            print(f"❌ Cloud storage delete failed: {e}")
            return False
    
    def list_files(self):
        """List all files in B-Transfer bucket"""
        try:
            if not self.service:
                return []
            
            if self.bucket_name:
                results = self.service.objects().list(bucket=self.bucket_name).execute()
            else:
                results = self.service.objects().list(bucket='b-transfer-files').execute()
            
            return results.get('items', [])
            
        except Exception as e:
            print(f"❌ Cloud storage list failed: {e}")
            return []

# Global cloud storage instance
cloud_storage = None

def get_cloud_storage():
    """Get or create cloud storage instance"""
    global cloud_storage
    if cloud_storage is None:
        try:
            cloud_storage = CloudStorage()
        except Exception as e:
            print(f"⚠️ Cloud storage not available: {e}")
            cloud_storage = None
    return cloud_storage 