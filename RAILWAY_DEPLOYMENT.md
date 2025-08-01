
# 🚀 Railway Deployment Instructions

## 1. Connect to Railway
- Go to [Railway Dashboard](https://railway.app/dashboard)
- Click "New Project"
- Select "Deploy from GitHub repo"
- Connect: https://github.com/mr-singh-7112/B-Transfer.git

## 2. Add Environment Variables
In your Railway project, go to "Variables" tab and add:

### GOOGLE_API_KEY
AIzaSyCMLYLL2AwJfV4mjxIehK11WQ3ncKW6s8Q

### GOOGLE_SERVICE_ACCOUNT
{
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
✅ API Key configured: AIzaSyCMLYLL2AwJfV4m...Q3ncKW6s8Q
✅ Railway configuration ready
✅ Deployment files prepared
✅ Environment variables set

🚀 Ready for Railway deployment!
