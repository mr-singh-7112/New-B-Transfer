# 🚀 B-Transfer

**Professional File Transfer Solution by Balsim Technologies**

Copyright (c) 2025 Balsim Technologies. All rights reserved.

---

## 📋 Overview

B-Transfer is a high-performance, secure file transfer solution designed for professional use. Built with modern web technologies, it provides ultra-fast file sharing capabilities with enterprise-grade security features.

## ✨ Features

### 🔐 Security
- **Rate Limiting**: Prevents abuse with intelligent upload throttling
- **File Type Validation**: Only allows safe file types
- **Session Management**: Secure session handling with unique IDs
- **Security Logging**: Comprehensive audit trail of all activities
- **IP Tracking**: Monitors client IP addresses for security

### ⚡ Performance
- **Ultra-Fast Transfers**: Direct file handling, no encryption overhead
- **Large File Support**: Up to 10GB per file
- **Real-time Progress**: Live upload speed and progress tracking
- **Cross-Platform**: Works on all devices and browsers

### 🎯 User Experience
- **Drag & Drop**: Intuitive file upload interface
- **Mobile Responsive**: Optimized for phones and tablets
- **Professional UI**: Clean, modern design
- **Auto-cleanup**: Files automatically deleted after 24 hours

## 🚀 Quick Deploy on Vercel

### One-Click Deployment
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mr-singh-7112/New-B-Transfer)

### Manual Deployment
1. **Fork this repository**
2. **Go to [Vercel](https://vercel.com/)**
3. **Import your forked repository**
4. **Deploy** - Vercel will automatically detect and deploy

## 🛠️ Local Development

### Prerequisites
- Python 3.7+
- Flask
- Werkzeug

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python3 b_transfer_server.py
   ```

## 📁 Project Structure

```
B-Transfer/
├── b_transfer_server.py    # Main server application
├── b_transfer_ui.html     # Professional web interface
├── cloud_storage.py       # Google Cloud Storage integration
├── requirements.txt        # Python dependencies
├── vercel.json           # Vercel deployment configuration
├── uploads/               # File storage directory
├── security.log          # Security event logs
└── README.md             # This file
```

## 🔧 Configuration

### Server Settings
- **Port**: Default 8081 (configurable via PORT environment variable)
- **File Size Limit**: 10GB per file
- **Upload Limit**: 50 files per session
- **Auto-delete**: 24 hours
- **Rate Limiting**: 1 second between uploads

### Security Settings
- **Allowed Extensions**: txt, pdf, png, jpg, jpeg, gif, mp4, avi, mov, mp3, wav, zip, rar, 7z, doc, docx, xls, xlsx, ppt, pptx, csv
- **Session Lifetime**: 24 hours
- **Security Logging**: All events logged with timestamps

## 🚀 Usage

### Starting the Server
```bash
python3 b_transfer_server.py
```

### Access URLs
- **Local Access**: http://localhost:8081
- **Network Access**: http://[YOUR_IP]:8081

### Features
1. **Upload**: Drag & drop or click to select files
2. **Download**: Click download button for any file
3. **Delete**: Click delete button to remove files
4. **Progress**: Real-time upload progress and speed

## 🔒 Security Features

### Rate Limiting
- Prevents rapid-fire uploads
- 1-second minimum interval between uploads
- Session-based upload limits

### File Validation
- Whitelist of allowed file types
- Secure filename handling
- File size validation

### Session Management
- Unique session IDs for each user
- Upload count tracking
- Automatic session cleanup

### Security Logging
- All upload/download/delete events logged
- IP address tracking
- Timestamp recording
- Error event logging

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8081/health
```

### Security Log
Monitor `security.log` for:
- Upload attempts
- Download activities
- Delete operations
- Rate limit violations
- Error events

## 🛡️ Additional Security Recommendations

### Network Security
1. **Firewall**: Configure firewall rules to restrict access
2. **VPN**: Use VPN for remote access
3. **HTTPS**: Implement SSL/TLS for production use
4. **IP Whitelist**: Restrict access to specific IP ranges

### Server Security
1. **User Authentication**: Add login system for production
2. **File Encryption**: Implement file-level encryption
3. **Backup System**: Regular file backups
4. **Monitoring**: Set up server monitoring

### Advanced Features to Consider
1. **User Management**: Multi-user support with roles
2. **File Sharing**: Generate shareable links
3. **Version Control**: File versioning system
4. **API Access**: REST API for integrations
5. **Webhook Support**: Notifications for events
6. **File Preview**: Preview images and documents
7. **Search Functionality**: File search and filtering
8. **Folder Support**: Organize files in folders
9. **Bulk Operations**: Multi-file upload/download
10. **Scheduled Cleanup**: Customizable retention policies

## 📄 License

**Copyright (c) 2025 Balsim Technologies. All rights reserved.**

This software is proprietary and confidential. Unauthorized copying, distribution, or use of this software is strictly prohibited.

## 🆘 Support

For technical support or licensing inquiries, contact Balsim Technologies.

---

**B-Transfer v2.1.0** | **Balsim Technologies** | **Copyright (c) 2025** 