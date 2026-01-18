const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    selectFolder: () => ipcRenderer.invoke('dialog:openDirectory'),
    readDir: (path) => ipcRenderer.invoke('fs:readDir', path),
    uploadFile: (data) => ipcRenderer.invoke('bunny:upload', data),
    // Helper to get file protocol for images
    // In Electron, file paths in DOM might need 'file://' prefix explicitly usually handled by renderer but good to know
});
