// 初始化主题
if (localStorage.getItem('theme') === 'dark') {
  document.body.classList.add('dark-mode');
}

function toggleTheme() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
}

function exportToPDF() {
  window.print();
}

// 递归渲染树
function renderTree(items, container, rootPath) {
  const ul = document.createElement('ul');
  items.forEach(item => {
    const li = document.createElement('li');
    if (item.type === 'folder') {
      const span = document.createElement('span');
      span.className = 'folder';
      span.textContent = `📁 ${item.name}`;
      span.onclick = () => toggle(span);
      li.appendChild(span);
      li.appendChild(document.createTextNode(' '));
      const comment = document.createElement('span');
      comment.className = 'comment';
      comment.textContent = '# 文件夹';
      li.appendChild(comment);

      if (item.children && item.children.length > 0) {
        const subUl = document.createElement('ul');
        subUl.className = 'hidden';
        li.appendChild(subUl);
        renderTree(item.children, subUl, rootPath);
      }
    } else {
      const fileSpan = document.createElement('span');
      fileSpan.className = 'file';
      fileSpan.textContent = `📄 ${item.name}`;
      li.appendChild(fileSpan);
      const comment = document.createElement('span');
      comment.className = 'comment';
      comment.textContent = '# 文件';
      li.appendChild(comment);
    }
    ul.appendChild(li);
  });
  container.appendChild(ul);
}

function toggle(element) {
  const ul = element.nextElementSibling?.tagName === 'UL' ? element.nextElementSibling :
             element.parentNode.querySelector('ul');
  if (ul) ul.classList.toggle('hidden');
}

// 模拟数据，用于在浏览器环境中测试
const mockTreeData = [
  {
    name: '项目文档',
    type: 'folder',
    children: [
      { name: '需求文档.docx', type: 'file' },
      { name: '设计文档.pdf', type: 'file' },
      { name: '测试报告.md', type: 'file' }
    ]
  },
  {
    name: '源代码',
    type: 'folder',
    children: [
      {
        name: '前端',
        type: 'folder',
        children: [
          { name: 'index.html', type: 'file' },
          { name: 'app.js', type: 'file' },
          { name: 'styles.css', type: 'file' }
        ]
      },
      {
        name: '后端',
        type: 'folder',
        children: [
          { name: 'server.js', type: 'file' },
          { name: 'database.js', type: 'file' },
          { name: 'config.json', type: 'file' }
        ]
      }
    ]
  },
  { name: 'README.md', type: 'file' },
  { name: 'package.json', type: 'file' },
  { name: '.gitignore', type: 'file' }
];

async function scanDisk() {
  const pathInput = document.getElementById('pathInput').value.trim();
  if (!pathInput) {
    alert('请输入路径！');
    return;
  }

  document.getElementById('status').textContent = '⏳ 扫描中...';
  document.getElementById('treeContainer').innerHTML = '';

  try {
    let result;
    
    // 安全检查 process 对象是否存在
    const processExists = typeof process !== 'undefined';
    console.log('process 对象是否存在：', processExists);
    
    // 安全检测 Electron 环境
    const isElectronEnv = processExists && process.versions && process.versions.electron;
    console.log('是否在 Electron 环境中：', isElectronEnv);
    
    // 检查 electronAPI 是否可用
    const electronAPIReady = window.electronAPI && typeof window.electronAPI.scanDirectory === 'function';
    console.log('electronAPI 是否可用：', electronAPIReady);
    
    // 基于 electronAPI 可用性来决定扫描方式
    if (electronAPIReady) {
      // electronAPI 可用，使用真实扫描
      console.log('electronAPI 可用，使用真实扫描，路径：', pathInput);
      result = await window.electronAPI.scanDirectory(pathInput);
      console.log('真实扫描结果：', result);
    } else {
      // electronAPI 不可用，显示明确提示
      console.log('electronAPI 不可用，无法进行真实扫描');
      
      // 显示明确的错误信息
      const errorMsg = isElectronEnv 
        ? '❌ electronAPI 不可用，请检查 preload.js 配置和主进程设置' 
        : '⚠️ 当前在浏览器环境中，无法访问本地文件系统。请在 Electron 应用中运行以使用真实扫描功能。';
      
      document.getElementById('status').textContent = errorMsg;
      
      // 显示模拟数据并明确标记
      result = {
        success: true,
        tree: mockTreeData,
        rootPath: pathInput
      };
    }
    
    if (result.success) {
      // 显示扫描结果
      const statusText = isElectronEnv ? `✅ 扫描完成：${result.rootPath}` : `⚠️ 模拟数据演示：${result.rootPath}`;
      document.getElementById('status').textContent = statusText;
      console.log('渲染树数据：', result.tree);
      renderTree(result.tree, document.getElementById('treeContainer'), result.rootPath);
    } else {
      document.getElementById('status').textContent = `❌ 扫描错误：${result.error}`;
    }
  } catch (err) {
    document.getElementById('status').textContent = `💥 调用失败：${err.message}`;
    console.error('扫描失败详情：', err);
    console.error('错误堆栈：', err.stack);
    
    // 非 Electron 环境下才显示模拟数据
    const processExists = typeof process !== 'undefined';
    const isElectronEnv = processExists && process.versions && process.versions.electron;
    if (!isElectronEnv) {
      console.log('非 Electron 环境下显示模拟数据');
      renderTree(mockTreeData, document.getElementById('treeContainer'), document.getElementById('pathInput').value);
    }
  }
}