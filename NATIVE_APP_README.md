# 🖥️ B-Transfer Native Desktop App

## Overview

B-Transfer is now available as a native desktop application for Windows, macOS, and Linux. The app provides the same military-grade security and ultra-fast file transfer capabilities as the web version, but with a native desktop interface.

## ✨ Features

### 🚀 **Ultra-Fast Performance**
- **Optimized for large files** - No more 2MB/s speed limits
- **Chunked uploads** - Better memory management
- **Streaming downloads** - Faster file retrieval
- **Background processing** - Non-blocking operations

### 🔒 **Enhanced Security**
- **Password-protected downloads** - Anyone with the password can download locked files
- **Military-grade encryption** - AES-256 with PBKDF2 key derivation
- **Session management** - Secure user sessions
- **Rate limiting** - Protection against abuse

### 🔑 **Improved Lock System**
- **Lock files** - Password protect sensitive files
- **Download with password** - Others can download locked files with correct password
- **Owner-only operations** - Only file owner can lock/unlock/delete
- **Secure deletion** - Password required to delete locked files

## 📦 Installation

### Prerequisites
- **Node.js** (v16 or higher)
- **Python 3.8+** with required packages
- **Git** (for cloning)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mr-singh-7112/B-Transfer.git
   cd B-Transfer
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

4. **Start the native app:**
   ```bash
   npm start
   ```

## 🛠️ Building Native Apps

### For macOS
```bash
npm run build-mac
```

### For Windows
```bash
npm run build-win
```

### For Linux
```bash
npm run build-linux
```

## 🎯 **Key Improvements**

### **Speed Optimizations:**
- **Chunked file processing** - Large files are processed in chunks
- **Streaming uploads** - Files are uploaded as they're read
- **Background compression** - Non-blocking file operations
- **Optimized memory usage** - Better handling of large files

### **Enhanced Lock System:**
- **Password-protected downloads** - Anyone with the password can download
- **Secure file sharing** - Share locked files with passwords
- **Owner controls** - Only file owner can lock/unlock
- **Protected deletion** - Password required for locked file deletion

### **Native App Benefits:**
- **Desktop integration** - Native menus and shortcuts
- **System tray** - Background operation support
- **Auto-start** - Launch with system startup
- **Cross-platform** - Windows, macOS, Linux support

## 🔧 **Configuration**

### **Environment Variables:**
```bash
# Google Cloud API Key
GOOGLE_API_KEY=your_api_key_here

# Server Port
PORT=8081

# Cloud Storage Settings
CLOUD_STORAGE_THRESHOLD=104857600  # 100MB
```

### **File Storage:**
- **Small files** (<100MB): Local storage
- **Large files** (>100MB): Google Cloud Storage
- **Automatic routing** based on file size

## 📱 **Usage**

### **Upload Files:**
1. Drag and drop files onto the upload area
2. Watch real-time progress with speed indicators
3. Files are automatically routed to appropriate storage

### **Lock Files:**
1. Upload a file (you own it)
2. Click the "🔒 Lock" button
3. Enter a password
4. File is encrypted and locked

### **Download Locked Files:**
1. Click "🔑 Download (Locked)" button
2. Enter the password when prompted
3. File is decrypted and downloaded

### **Share Locked Files:**
1. Lock a file with a password
2. Share the password with others
3. They can download using the password

## 🚀 **Performance Tips**

### **For Large Files:**
- Use wired network connection
- Close other bandwidth-heavy applications
- Monitor system resources during upload

### **For Better Security:**
- Use strong passwords for file locking
- Share passwords securely
- Regularly clean up old files

## 🔍 **Troubleshooting**

### **App Won't Start:**
1. Check Python installation: `python3 --version`
2. Install dependencies: `pip3 install -r requirements.txt`
3. Check Node.js: `node --version`

### **Slow Uploads:**
1. Check network connection
2. Close other applications
3. Use wired connection for large files

### **Lock System Issues:**
1. Ensure you own the file (uploaded it)
2. Check password is correct
3. Try unlocking and re-locking

## 📄 **License**

**Copyright (c) 2025 Balsim Technologies. All rights reserved.**

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## 🆘 **Support**

For technical support or feature requests:
- **GitHub Issues**: https://github.com/mr-singh-7112/B-Transfer/issues
- **Email**: support@balsimtech.com

---

**B-Transfer v2.3.0** | **Balsim Technologies** | **Military-Grade Security** 