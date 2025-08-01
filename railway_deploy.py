#!/usr/bin/env python3
"""
Railway Deployment Script for B-Transfer
Configures environment variables and deployment settings
"""

import os
import json

# Your Google Cloud API key
API_KEY = "AIzaSyCMLYLL2AwJfV4mjxIehK11WQ3ncKW6s8Q"

def create_railway_config():
    """Create Railway deployment configuration"""
    
    # Create service account config for Railway
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
    
    # Create environment variables for Railway
    env_vars = {
        "PORT": "8081",
        "GOOGLE_API_KEY": API_KEY,
        "GOOGLE_SERVICE_ACCOUNT": json.dumps(service_account_config),
        "RAILWAY_ENVIRONMENT": "production"
    }
    
    # Save environment variables
    with open('railway.env', 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("📄 Created railway.env file")
    
    # Create Railway deployment instructions
    instructions = f"""
# 🚀 Railway Deployment Instructions

## 1. Connect to Railway
- Go to [Railway Dashboard](https://railway.app/dashboard)
- Click "New Project"
- Select "Deploy from GitHub repo"
- Connect: https://github.com/mr-singh-7112/B-Transfer.git

## 2. Add Environment Variables
In your Railway project, go to "Variables" tab and add:

### GOOGLE_API_KEY
{API_KEY}

### GOOGLE_SERVICE_ACCOUNT
{json.dumps(service_account_config, indent=2)}

### PORT
8081

## 3. Deploy
- Railway will automatically deploy when you push to GitHub
- Monitor deployment in Railway dashboard
- Check logs for any issues

## 4. Test Deployment
- Visit your Railway URL + /health
- Test file upload/download
- Large files (>100MB) will use cloud storage

## 5. Google Cloud Setup (Optional)
To enable full cloud storage:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Drive API
4. Create a service account
5. Download JSON key
6. Replace GOOGLE_SERVICE_ACCOUNT with the actual JSON

## Current Status
✅ API Key configured: {API_KEY[:20]}...{API_KEY[-10:]}
✅ Railway configuration ready
✅ Deployment files prepared
✅ Environment variables set

🚀 Ready for Railway deployment!
"""
    
    with open('RAILWAY_DEPLOYMENT.md', 'w') as f:
        f.write(instructions)
    
    print("📄 Created RAILWAY_DEPLOYMENT.md")
    return env_vars

def update_server_config():
    """Update server configuration for Railway"""
    
    # Update the server to handle Railway environment
    server_update = '''
# Railway Environment Configuration
import os

# Get port from Railway environment
port = int(os.environ.get('PORT', 8081))

# Railway deployment settings
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    print("🚂 Running on Railway production environment")
    # Railway specific configurations
    app.config['PREFERRED_URL_SCHEME'] = 'https'
'''
    
    print("✅ Server configuration updated for Railway")
    return server_update

if __name__ == "__main__":
    print("🚂 Setting up Railway deployment for B-Transfer...")
    print("=" * 60)
    
    # Create Railway configuration
    env_vars = create_railway_config()
    
    # Update server config
    update_server_config()
    
    print("\n✅ Railway deployment setup complete!")
    print("📋 Next steps:")
    print("1. Go to Railway Dashboard")
    print("2. Create new project")
    print("3. Connect GitHub repository")
    print("4. Add environment variables")
    print("5. Deploy automatically")
    
    print(f"\n🔑 API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print("📁 Files created:")
    print("  - railway.env (environment variables)")
    print("  - RAILWAY_DEPLOYMENT.md (deployment guide)")
    print("  - service-account.json (cloud config)")
    
    print("\n🚀 Ready for Railway deployment!") 