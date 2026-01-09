const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      // 确保 preload.js 正确加载，使用绝对路径
      preload: path.resolve(__dirname, 'preload.js'),
      // 启用 contextIsolation 以安全地使用 contextBridge
      contextIsolation: true,
      // 禁用 nodeIntegration 以增强安全性
      nodeIntegration: false,
      // 禁用 remote 模块
      enableRemoteModule: false,
      // 禁用 sandbox 以允许访问文件系统
      sandbox: false
    }
  });

  // 打开开发者工具，便于调试
  win.webContents.openDevTools();

  // 确保 index.html 正确加载
  win.loadFile(path.resolve(__dirname, 'index.html'));
  
  // 监听加载完成事件，确保 preload.js 已执行
  win.webContents.on('did-finish-load', () => {
    console.log('渲染进程加载完成');
  });
  
  // 监听 preload 脚本错误
  win.webContents.on('preload-error', (event, preloadPath, error) => {
    console.error('preload.js 错误：', error);
  });
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

// 监听前端请求：扫描目录
ipcMain.handle('scan-directory', async (event, rootPath) => {
  console.log('收到扫描请求，路径：', rootPath);
  
  function walk(dir, depth = 0) {
    console.log(`递归扫描目录：${dir}，深度：${depth}`);
    
    if (depth > 10) {
      console.log(`目录 ${dir} 深度超过限制，停止扫描`);
      return []; // 防止过深
    }
    
    try {
      const items = fs.readdirSync(dir);
      console.log(`目录 ${dir} 包含 ${items.length} 个项目`);
      
      const result = [];
      for (const item of items) {
        const fullPath = path.join(dir, item);
        console.log(`处理项目：${fullPath}`);
        
        try {
          const stat = fs.statSync(fullPath);
          if (stat.isDirectory()) {
            console.log(`${fullPath} 是文件夹，递归扫描`);
            result.push({
              name: item,
              type: 'folder',
              children: walk(fullPath, depth + 1)
            });
          } else {
            console.log(`${fullPath} 是文件`);
            result.push({ name: item, type: 'file' });
          }
        } catch (e) {
          console.error(`处理 ${fullPath} 时出错：`, e.message);
          result.push({ name: `⚠️ ${item} (${e.message})`, type: 'file' });
        }
      }
      
      console.log(`目录 ${dir} 扫描完成，返回 ${result.length} 个项目`);
      return result;
    } catch (e) {
      console.error(`扫描目录 ${dir} 时出错：`, e.message);
      return [{ name: `⚠️ 目录访问失败 (${e.message})`, type: 'file' }];
    }
  }

  try {
    console.log('检查路径是否存在：', rootPath);
    
    // 确保路径格式正确，处理 Windows 路径
    const normalizedPath = path.normalize(rootPath);
    console.log('标准化后的路径：', normalizedPath);
    
    if (!fs.existsSync(normalizedPath)) {
      const errorMsg = `路径不存在：${normalizedPath}`;
      console.error(errorMsg);
      throw new Error(errorMsg);
    }
    
    console.log('路径存在，开始扫描');
    const tree = walk(normalizedPath);
    
    console.log('扫描完成，结果：', tree);
    return { success: true, tree, rootPath: normalizedPath };
  } catch (err) {
    console.error('扫描过程中出错：', err.message);
    return { success: false, error: err.message };
  }
});