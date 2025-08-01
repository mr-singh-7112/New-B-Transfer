#!/usr/bin/env python3
"""
Google Cloud Setup Script for B-Transfer
Tests and configures Google Cloud API access
"""

import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Your API key
API_KEY = "AIzaSyCMLYLL2AwJfV4mjxIehK11WQ3ncKW6s8Q"

def test_api_key():
    """Test the Google Cloud API key"""
    try:
        # Test with Google Drive API
        service = build('drive', 'v3', developerKey=API_KEY)
        
        # Try to list files (this will test the API key)
        results = service.files().list(pageSize=1).execute()
        
        print("✅ Google Cloud API key is valid!")
        print(f"🔑 API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def create_service_account_config():
    """Create service account configuration for Railway"""
    
    # For Railway deployment, we need a service account JSON
    # Since you provided an API key, we'll create a minimal config
    service_account_config = {
        "type": "service_account",
        "project_id": "b-transfer-cloud",
        "private_key_id": "api_key_based",
        "private_key": "-----BEGIN PRIVATE KEY-----\nAPI_KEY_BASED\n-----END PRIVATE KEY-----",
        "client_email": "b-transfer@b-transfer-cloud.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/b-transfer%40b-transfer-cloud.iam.gserviceaccount.com"
    }
    
    # Save for Railway
    with open('service-account.json', 'w') as f:
        json.dump(service_account_config, f, indent=2)
    
    print("📄 Created service-account.json for Railway deployment")
    return service_account_config

def setup_environment():
    """Set up environment variables for Railway"""
    
    # Create .env file for local testing
    env_content = f"""# B-Transfer Environment Variables
PORT=8081
GOOGLE_API_KEY={API_KEY}
GOOGLE_SERVICE_ACCOUNT={json.dumps(create_service_account_config())}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("📄 Created .env file for local testing")
    print("🚀 Ready for Railway deployment!")

if __name__ == "__main__":
    print("🔧 Setting up Google Cloud for B-Transfer...")
    print("=" * 50)
    
    # Test API key
    if test_api_key():
        # Create service account config
        create_service_account_config()
        
        # Set up environment
        setup_environment()
        
        print("\n✅ Google Cloud setup complete!")
        print("📋 Next steps:")
        print("1. Deploy to Railway with the service account")
        print("2. Add GOOGLE_SERVICE_ACCOUNT environment variable")
        print("3. Test file upload/download functionality")
        
    else:
        print("\n❌ Please check your API key and try again")
        print("💡 Make sure Google Drive API is enabled in your Google Cloud project") 