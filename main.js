const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let serverProcess;

function createWindow() {
    // Create the browser window
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        title: 'B-Transfer - Military-Grade File Transfer',
        show: false
    });

    // Load the app
    mainWindow.loadFile('b_transfer_ui.html');

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Create menu
    createMenu();
}

function createMenu() {
    const template = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'Open B-Transfer',
                    accelerator: 'CmdOrCtrl+O',
                    click: () => {
                        mainWindow.loadFile('b_transfer_ui.html');
                    }
                },
                {
                    label: 'Server Status',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`
                            fetch('/health')
                                .then(response => response.json())
                                .then(data => {
                                    alert('Server Status: ' + data.status + '\\nVersion: ' + data.version);
                                })
                                .catch(() => {
                                    alert('Server not responding');
                                });
                        `);
                    }
                },
                { type: 'separator' },
                {
                    label: 'Quit',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'About B-Transfer',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'About B-Transfer',
                            message: 'B-Transfer v2.3.0',
                            detail: 'Ultra-fast file transfer with military-grade security\n\nCopyright (c) 2025 Balsim Technologies\nAll rights reserved.',
                            buttons: ['OK']
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

function startServer() {
    return new Promise((resolve, reject) => {
        // Check if Python is available
        const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
        
        // Start the server
        serverProcess = spawn(pythonCommand, ['b_transfer_server.py'], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let serverStarted = false;

        serverProcess.stdout.on('data', (data) => {
            const output = data.toString();
            console.log('Server:', output);
            
            // Check if server is ready
            if (output.includes('Access from this computer: http://localhost:8081')) {
                serverStarted = true;
                resolve();
            }
        });

        serverProcess.stderr.on('data', (data) => {
            console.error('Server Error:', data.toString());
        });

        serverProcess.on('error', (error) => {
            console.error('Failed to start server:', error);
            reject(error);
        });

        // Timeout after 10 seconds
        setTimeout(() => {
            if (!serverStarted) {
                reject(new Error('Server startup timeout'));
            }
        }, 10000);
    });
}

// App event handlers
app.whenReady().then(async () => {
    try {
        console.log('Starting B-Transfer server...');
        await startServer();
        console.log('Server started successfully');
        createWindow();
    } catch (error) {
        console.error('Failed to start server:', error);
        dialog.showErrorBox('Server Error', 'Failed to start B-Transfer server. Please check if Python is installed.');
        app.quit();
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('before-quit', () => {
    if (serverProcess) {
        console.log('Stopping server...');
        serverProcess.kill();
    }
});

// Handle app quit
app.on('quit', () => {
    if (serverProcess) {
        serverProcess.kill();
    }
}); 