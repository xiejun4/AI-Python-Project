const { contextBridge, ipcRenderer } = require('electron');

// 主进程日志
console.log('preload.js 开始执行');
console.log('contextBridge 是否可用:', typeof contextBridge !== 'undefined');
console.log('ipcRenderer 是否可用:', typeof ipcRenderer !== 'undefined');

// 确保 contextBridge 可用
if (contextBridge && ipcRenderer) {
  try {
    // 安全地暴露 API 到渲染进程
    contextBridge.exposeInMainWorld('electronAPI', {
      scanDirectory: (path) => {
        console.log('preload.js: 收到 scanDirectory 调用，路径:', path);
        return ipcRenderer.invoke('scan-directory', path);
      }
    });
    console.log('preload.js: electronAPI 已成功暴露到渲染进程');
  } catch (error) {
    console.error('preload.js: 暴露 electronAPI 时出错:', error);
  }
} else {
  console.error('preload.js: contextBridge 或 ipcRenderer 不可用');
  console.error('contextBridge:', contextBridge);
  console.error('ipcRenderer:', ipcRenderer);
}

// 确保渲染进程能访问到 electronAPI
window.electronAPI = window.electronAPI || {
  scanDirectory: (path) => {
    console.error('electronAPI.scanDirectory 未正确暴露');
    return Promise.reject(new Error('electronAPI.scanDirectory 未正确暴露'));
  }
};