# 🚀 B-Transfer Deployment Guide

## Railway Deployment with Cloud Storage

### Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Google Cloud Project**: Create a project at [console.cloud.google.com](https://console.cloud.google.com)
3. **GitHub Repository**: Your B-Transfer repository

### Step 1: Google Cloud Setup

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable Google Drive API

2. **Create Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `b-transfer-cloud`
   - Description: `B-Transfer cloud storage service account`
   - Grant "Editor" role

3. **Download Service Account Key**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file
   - Rename to `service-account.json`

### Step 2: Railway Deployment

1. **Connect Repository**:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your B-Transfer repository

2. **Add Service Account**:
   - In Railway project, go to "Variables" tab
   - Add the contents of `service-account.json` as a variable
   - Name: `GOOGLE_SERVICE_ACCOUNT`
   - Value: (paste the entire JSON content)

3. **Environment Variables**:
   ```
   PORT=8081
   GOOGLE_SERVICE_ACCOUNT=<your-service-account-json>
   ```

4. **Deploy**:
   - Railway will automatically deploy when you push to GitHub
   - Monitor deployment in Railway dashboard

### Step 3: Verify Deployment

1. **Check Health**:
   - Visit your Railway URL + `/health`
   - Should return healthy status

2. **Test Features**:
   - Upload small file (< 100MB) - stored locally
   - Upload large file (> 100MB) - stored in Google Drive
   - Test file locking and password protection
   - Test download from both local and cloud storage

### Step 4: Custom Domain (Optional)

1. **Add Custom Domain**:
   - In Railway project, go to "Settings" > "Domains"
   - Add your custom domain
   - Configure DNS as instructed

### Troubleshooting

#### Cloud Storage Issues

1. **Service Account Not Working**:
   - Verify JSON is correctly formatted
   - Check Google Drive API is enabled
   - Ensure service account has proper permissions

2. **Large File Upload Fails**:
   - Check file size limit (5GB)
   - Verify cloud storage credentials
   - Check Railway logs for errors

3. **Download Issues**:
   - Verify file exists in metadata
   - Check cloud storage connectivity
   - Review Railway logs

#### Railway Issues

1. **Deployment Fails**:
   - Check requirements.txt is correct
   - Verify Procfile exists
   - Check Railway logs for Python errors

2. **App Not Starting**:
   - Verify PORT environment variable
   - Check if port is available
   - Review startup logs

### Monitoring

1. **Railway Dashboard**:
   - Monitor deployment status
   - Check resource usage
   - View logs in real-time

2. **Health Checks**:
   - `/health` endpoint for status
   - Monitor response times
   - Check error rates

### Security Notes

1. **Service Account Security**:
   - Keep service account JSON secure
   - Use Railway environment variables
   - Never commit credentials to Git

2. **File Security**:
   - All files encrypted with AES-256
   - Password protection for sensitive files
   - Automatic cleanup after 24 hours

### Performance Optimization

1. **Cloud Storage**:
   - Files > 100MB automatically use Google Drive
   - Reduces Railway storage usage
   - Better for large file handling

2. **Caching**:
   - Railway provides CDN caching
   - Static files served efficiently
   - Global edge locations

### Cost Optimization

1. **Railway Free Tier**:
   - 500 hours/month free
   - 1GB storage included
   - Perfect for development/testing

2. **Google Drive**:
   - 15GB free storage
   - Sufficient for most use cases
   - Pay-as-you-go for additional storage

### Support

- **Railway Support**: [docs.railway.app](https://docs.railway.app)
- **Google Cloud Support**: [cloud.google.com/support](https://cloud.google.com/support)
- **B-Transfer Issues**: GitHub repository issues

---

**B-Transfer v2.1.0** | **Balsim Technologies** | **Copyright (c) 2025** 