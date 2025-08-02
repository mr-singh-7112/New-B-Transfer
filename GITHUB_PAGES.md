# 🚀 B-Transfer GitHub Pages Deployment

This document explains how B-Transfer is deployed on GitHub Pages and how to access the live demo.

## 📋 Overview

B-Transfer is deployed on GitHub Pages as a static landing page that showcases the project features and provides links to the live demo server.

## 🌐 Live Demo

- **GitHub Pages Site**: https://mr-singh-7112.github.io/B-Transfer/
- **Local Demo Server**: http://localhost:4000 (when running locally)
- **Health Check**: http://localhost:4000/health

## 🛠️ Deployment Setup

### Automatic Deployment

The site is automatically deployed using GitHub Actions. When you push changes to the `main` branch, the site is automatically built and deployed to GitHub Pages.

### Manual Deployment

1. **Enable GitHub Pages**:
   - Go to your repository settings
   - Navigate to "Pages" section
   - Select "Deploy from a branch"
   - Choose "gh-pages" branch
   - Click "Save"

2. **Build and Deploy**:
   ```bash
   # The GitHub Actions workflow handles this automatically
   # But you can also deploy manually if needed
   ```

## 📁 File Structure

```
B-Transfer/
├── index.html              # GitHub Pages landing page
├── .github/workflows/      # GitHub Actions deployment
├── b_transfer_server.py    # Flask backend server
├── b_transfer_ui.html     # Full application UI
└── README.md              # Project documentation
```

## 🎯 Features on GitHub Pages

### Static Landing Page
- **Project Showcase**: Beautiful landing page showcasing B-Transfer features
- **Live Demo Links**: Direct links to the running server
- **GitHub Integration**: Links to source code and downloads
- **Responsive Design**: Works on all devices and browsers

### Dynamic Features
- **Health Check**: Real-time server status monitoring
- **File Management**: Full file upload/download functionality
- **Security Features**: Military-grade encryption and access control

## 🔧 Configuration

### GitHub Pages Settings
- **Source**: Deploy from branch
- **Branch**: gh-pages
- **Folder**: / (root)
- **Custom domain**: (optional)

### Environment Variables
The GitHub Actions workflow uses the following secrets:
- `GITHUB_TOKEN`: Automatically provided by GitHub

## 📊 Monitoring

### Deployment Status
- Check the "Actions" tab in your repository
- Monitor deployment logs for any issues
- Verify the site is accessible at the GitHub Pages URL

### Health Monitoring
- The landing page includes links to health checks
- Monitor server status through the health endpoint
- Check logs for any deployment issues

## 🚀 Quick Start

1. **Access the Site**: Visit https://mr-singh-7112.github.io/B-Transfer/
2. **Launch Demo**: Click "Launch Demo" to access the full application
3. **Health Check**: Click "Health Check" to verify server status
4. **View Source**: Click "View on GitHub" to see the source code

## 🔒 Security Notes

- GitHub Pages serves static content only
- The actual file transfer functionality runs on the Flask server
- All sensitive operations happen on the backend server
- The landing page is purely for demonstration and navigation

## 📞 Support

For issues with:
- **GitHub Pages**: Check the Actions tab and deployment logs
- **Server**: Check the health endpoint and server logs
- **Features**: Refer to the main README.md file

---

**B-Transfer v2.1.0** | **GitHub Pages Deployment** | **Copyright (c) 2025 Balsim Technologies** 