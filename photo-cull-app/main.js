const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const https = require('https');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 900,
        backgroundColor: '#111111',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            webSecurity: false // Allow loading local resources
        }
    });

    mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

// --- IPC HANDLERS ---

// 1. Select Information
ipcMain.handle('dialog:openDirectory', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory']
    });
    if (canceled) {
        return;
    } else {
        return filePaths[0];
    }
});

// 2. Read Directory
ipcMain.handle('fs:readDir', async (event, dirPath) => {
    try {
        const files = await fs.promises.readdir(dirPath, { withFileTypes: true });
        // Filter images
        const images = files
            .filter(dirent => dirent.isFile() && /\.(jpg|jpeg|png|webp|heic)$/i.test(dirent.name))
            .map(dirent => ({
                name: dirent.name,
                path: path.join(dirPath, dirent.name)
            }));
        return images;
    } catch (error) {
        console.error("Error reading dir:", error);
        return [];
    }
});

// 3. Upload to Bunny (Simple wrapper)
ipcMain.handle('bunny:upload', async (event, { filePath, targetFolder, index }) => {
    const STORAGE_NAME = "kovertripweb";
    const API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4";

    return new Promise((resolve, reject) => {
        try {
            const fileName = path.basename(filePath);
            const ext = path.extname(fileName);
            const newName = `${targetFolder}_${index}${ext}`;
            const remotePath = `Двухдневка в Альпы/AutoSync/${targetFolder}/${newName}`;

            // Encode path properly
            const safeRemotePath = remotePath.split('/').map(encodeURIComponent).join('/');

            const options = {
                hostname: 'storage.bunnycdn.com',
                path: `/${STORAGE_NAME}/${safeRemotePath}`,
                method: 'PUT',
                headers: {
                    'AccessKey': API_KEY,
                    'Content-Type': 'application/octet-stream' // generic
                }
            };

            const req = https.request(options, (res) => {
                if (res.statusCode === 201) {
                    resolve({ success: true });
                } else {
                    resolve({ success: false, code: res.statusCode });
                }
            });

            req.on('error', (e) => {
                resolve({ success: false, error: e.message });
            });

            // Stream file
            const fileStream = fs.createReadStream(filePath);
            fileStream.pipe(req);

        } catch (e) {
            resolve({ success: false, error: e.message });
        }
    });
});
