#!/usr/bin/env python3
"""
Cloud Storage Module for B-Transfer
Handles file storage in Google Drive for large files (up to 5GB)
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

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class CloudStorage:
    def __init__(self):
        self.service = None
        self.folder_id = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            # Try API key first (for public access)
            api_key = os.environ.get('GOOGLE_API_KEY')
            if api_key:
                self.service = build('drive', 'v3', developerKey=api_key)
                print("🔑 Using Google Cloud API key authentication")
                self._ensure_folder()
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
            
            self.service = build('drive', 'v3', credentials=creds)
            print("🔐 Using Google Cloud service account authentication")
            self._ensure_folder()
            
        except Exception as e:
            print(f"❌ Google Cloud authentication failed: {e}")
            self.service = None
    
    def _ensure_folder(self):
        """Ensure B-Transfer folder exists in Google Drive"""
        try:
            # For API key access, we'll use a public folder or create one
            # Search for existing folder
            results = self.service.files().list(
                q="name='B-Transfer' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive'
            ).execute()
            
            if results['files']:
                self.folder_id = results['files'][0]['id']
                print(f"📁 Using existing B-Transfer folder: {self.folder_id}")
            else:
                # Try to create new folder (may not work with API key)
                try:
                    folder_metadata = {
                        'name': 'B-Transfer',
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    folder = self.service.files().create(
                        body=folder_metadata, fields='id'
                    ).execute()
                    self.folder_id = folder.get('id')
                    print(f"📁 Created new B-Transfer folder: {self.folder_id}")
                except Exception as create_error:
                    print(f"⚠️ Could not create folder with API key: {create_error}")
                    print("📁 Will use root folder for file storage")
                    self.folder_id = None
                
        except Exception as e:
            print(f"⚠️ Cloud storage initialization failed: {e}")
            self.folder_id = None
    
    def upload_file(self, file_path, filename, file_data=None):
        """Upload file to Google Drive"""
        try:
            if not self.service:
                return None
            
            # Prepare file metadata
            file_metadata = {
                'name': filename
            }
            
            # Add parent folder if available
            if self.folder_id:
                file_metadata['parents'] = [self.folder_id]
            
            # Upload file
            if file_data:
                media = MediaIoBaseUpload(
                    io.BytesIO(file_data),
                    mimetype='application/octet-stream',
                    resumable=True
                )
            else:
                media = MediaIoBaseUpload(
                    file_path,
                    mimetype='application/octet-stream',
                    resumable=True
                )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size'
            ).execute()
            
            print(f"☁️ File uploaded to cloud: {filename}")
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'size': file.get('size', 0)
            }
            
        except Exception as e:
            print(f"❌ Cloud upload failed: {e}")
            return None
    
    def download_file(self, file_id):
        """Download file from Google Drive"""
        try:
            if not self.service:
                return None
            
            # Get file metadata
            file = self.service.files().get(fileId=file_id).execute()
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
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
            print(f"❌ Cloud download failed: {e}")
            return None
    
    def delete_file(self, file_id):
        """Delete file from Google Drive"""
        try:
            if not self.service:
                return False
            
            self.service.files().delete(fileId=file_id).execute()
            return True
            
        except Exception as e:
            print(f"❌ Cloud delete failed: {e}")
            return False
    
    def list_files(self):
        """List all files in B-Transfer folder"""
        try:
            if not self.service or not self.folder_id:
                return []
            
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                fields="files(id,name,size,createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            print(f"❌ Cloud list failed: {e}")
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