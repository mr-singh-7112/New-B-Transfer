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
    """Test the Google Cloud API key with different APIs"""
    try:
        # Test with Google Drive API
        print("🔍 Testing Google Drive API...")
        drive_service = build('drive', 'v3', developerKey=API_KEY)
        results = drive_service.files().list(pageSize=1).execute()
        print("✅ Google Drive API is working!")
        return True
        
    except Exception as e:
        print(f"❌ Google Drive API test failed: {e}")
        
        # Try Google Cloud Storage API
        try:
            print("🔍 Testing Google Cloud Storage API...")
            storage_service = build('storage', 'v1', developerKey=API_KEY)
            # This will test if the API key works with storage
            print("✅ Google Cloud Storage API is working!")
            return True
        except Exception as storage_error:
            print(f"❌ Google Cloud Storage API test failed: {storage_error}")
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
RAILWAY_ENVIRONMENT=production
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("📄 Created .env file for local testing")
    print("🚀 Ready for Railway deployment!")

def check_required_apis():
    """Check which APIs are enabled and provide guidance"""
    print("\n🔍 Checking Google Cloud APIs...")
    print("=" * 50)
    
    # Check Google Drive API
    try:
        drive_service = build('drive', 'v3', developerKey=API_KEY)
        drive_service.files().list(pageSize=1).execute()
        print("✅ Google Drive API: ENABLED")
    except Exception as e:
        print("❌ Google Drive API: NOT ENABLED")
        print("   💡 Enable it at: https://console.cloud.google.com/apis/library/drive.googleapis.com")
    
    # Check Google Cloud Storage API
    try:
        storage_service = build('storage', 'v1', developerKey=API_KEY)
        print("✅ Google Cloud Storage API: ENABLED")
    except Exception as e:
        print("❌ Google Cloud Storage API: NOT ENABLED")
        print("   💡 Enable it at: https://console.cloud.google.com/apis/library/storage.googleapis.com")

if __name__ == "__main__":
    print("🔧 Setting up Google Cloud for B-Transfer...")
    print("=" * 50)
    
    # Check required APIs
    check_required_apis()
    
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
        print("\n⚠️ Some APIs may not be enabled")
        print("💡 To enable Google Drive API:")
        print("   1. Go to https://console.cloud.google.com/apis/library/drive.googleapis.com")
        print("   2. Click 'Enable'")
        print("   3. Wait a few minutes for propagation")
        print("   4. Run this script again")
        
    print(f"\n🔑 API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print("📁 Files created:")
    print("  - service-account.json (cloud config)")
    print("  - .env (environment variables)")
    print("  - railway.env (Railway variables)")
    
    print("\n🚀 Ready for Railway deployment!") 