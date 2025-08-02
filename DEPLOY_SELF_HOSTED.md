# 🖥️ Self-Hosting B-Transfer Guide

## 📋 Overview

This guide shows you how to deploy B-Transfer on your own server, VPS, or local machine without using any third-party platforms.

## 🎯 **Option 1: Local Machine Deployment (Free)**

### Prerequisites
- Python 3.7+
- Internet connection (for external access)

### Steps:
1. **Clone the repository:**
   ```bash
   git clone https://github.com/mr-singh-7112/New-B-Transfer.git
   cd New-B-Transfer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python3 b_transfer_server.py
   ```

4. **Access locally:**
   - **Local**: http://localhost:8081
   - **Network**: http://YOUR_IP:8081

### For External Access:
1. **Configure your router** to forward port 8081
2. **Get your public IP** from whatismyip.com
3. **Access from anywhere**: http://YOUR_PUBLIC_IP:8081

---

## 🌐 **Option 2: VPS Deployment (Recommended)**

### Step 1: Choose a VPS Provider
- **DigitalOcean**: $5/month (1GB RAM, 1 CPU)
- **Linode**: $5/month (1GB RAM, 1 CPU)
- **Vultr**: $2.50/month (512MB RAM, 1 CPU)
- **AWS EC2**: Pay as you go
- **Google Cloud**: Pay as you go

### Step 2: Set Up Your VPS

1. **Create a VPS** with Ubuntu 20.04 or newer
2. **SSH into your server:**
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

3. **Update the system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Install Python and dependencies:**
   ```bash
   sudo apt install python3 python3-pip python3-venv nginx -y
   ```

5. **Create a user for the application:**
   ```bash
   sudo adduser btransfer
   sudo usermod -aG sudo btransfer
   ```

### Step 3: Deploy the Application

1. **Switch to the user:**
   ```bash
   sudo su - btransfer
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/mr-singh-7112/New-B-Transfer.git
   cd New-B-Transfer
   ```

3. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install gunicorn
   ```

5. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/btransfer.service
   ```

   Add this content:
   ```ini
   [Unit]
   Description=B-Transfer File Server
   After=network.target

   [Service]
   User=btransfer
   WorkingDirectory=/home/btransfer/New-B-Transfer
   Environment="PATH=/home/btransfer/New-B-Transfer/venv/bin"
   ExecStart=/home/btransfer/New-B-Transfer/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8081 b_transfer_server:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable btransfer
   sudo systemctl start btransfer
   ```

### Step 4: Configure Nginx (Optional)

1. **Create Nginx configuration:**
   ```bash
   sudo nano /etc/nginx/sites-available/btransfer
   ```

   Add this content:
   ```nginx
   server {
       listen 80;
       server_name YOUR_DOMAIN_OR_IP;

       location / {
           proxy_pass http://127.0.0.1:8081;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

2. **Enable the site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/btransfer /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Configure firewall:**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

---

## 🍓 **Option 3: Raspberry Pi Deployment**

### Prerequisites
- Raspberry Pi 3 or 4
- MicroSD card (16GB+)
- Power supply

### Steps:

1. **Install Raspberry Pi OS** (Raspbian)
2. **SSH into your Pi:**
   ```bash
   ssh pi@YOUR_PI_IP
   ```

3. **Update the system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Install Python:**
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

5. **Clone and deploy:**
   ```bash
   git clone https://github.com/mr-singh-7112/New-B-Transfer.git
   cd New-B-Transfer
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Run the server:**
   ```bash
   python3 b_transfer_server.py
   ```

7. **Access**: http://YOUR_PI_IP:8081

---

## 🔧 **Production Configuration**

### Environment Variables
Create a `.env` file:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
PORT=8081
```

### Security Recommendations

1. **Use HTTPS:**
   ```bash
   # Install Certbot for Let's Encrypt SSL
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

2. **Configure firewall:**
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

3. **Regular updates:**
   ```bash
   # Set up automatic security updates
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

---

## 📊 **Monitoring and Maintenance**

### Check Service Status
```bash
sudo systemctl status btransfer
```

### View Logs
```bash
sudo journalctl -u btransfer -f
```

### Restart Service
```bash
sudo systemctl restart btransfer
```

### Update Application
```bash
cd /home/btransfer/New-B-Transfer
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart btransfer
```

---

## 💰 **Cost Comparison**

| Option | Setup Cost | Monthly Cost | Control Level |
|--------|------------|--------------|---------------|
| **Local Machine** | $0 | $0 | Full |
| **Raspberry Pi** | ~$50 | $0 | Full |
| **VPS (Basic)** | $0 | $2.50-$5 | Full |
| **VPS (Premium)** | $0 | $10-$20 | Full |

---

## 🎯 **Quick Start Recommendation**

**For beginners**: Start with **Local Machine** deployment
**For production**: Use **VPS** with Nginx
**For home server**: Use **Raspberry Pi**

---

**B-Transfer v2.1.0** | **Self-Hosting Guide** | **Copyright (c) 2025 Balsim Technologies** 