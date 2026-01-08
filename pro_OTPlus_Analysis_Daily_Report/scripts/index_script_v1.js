// 全局变量
let allData = [];
let filteredData = [];
const jsonFilePath = '../docs/TITANS项目_SOVP2_Report_0615_FE_NTF.json';
let currentPage = 1;
let recordsPerPage = 10;

// DOM 元素
const dataTableBody = document.getElementById('dataTableBody');
const filterBtn = document.getElementById('filterBtn');
const resetBtn = document.getElementById('resetBtn');
const refreshBtn = document.getElementById('refreshBtn');
const exportBtn = document.getElementById('exportBtn');
const detailModal = document.getElementById('detailModal');
const closeModal = document.getElementById('closeModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const modalContent = document.getElementById('modalContent');
const totalRecords = document.getElementById('totalRecords');
const pendingIssues = document.getElementById('pendingIssues');
const severeIssues = document.getElementById('severeIssues');
const avgDefectRate = document.getElementById('avgDefectRate');
const currentPageRange = document.getElementById('currentPageRange');
const totalPages = document.getElementById('totalPages');
const lastUpdated = document.getElementById('lastUpdated');
const filterConditionsContainer = document.getElementById('filterConditionsContainer');
const recordsPerPageSelect = document.getElementById('recordsPerPage');

// 加载 JSON 数据
async function loadJSON() {
    try {
        console.log('开始加载 JSON 数据');
        const response = await fetch(jsonFilePath);
        console.log('响应状态:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP 错误! 状态: ${response.status}`);
        }
        allData = await response.json();
        console.log('成功加载 JSON 数据，数据长度:', allData.length);
        filteredData = [...allData];
        renderTable(filteredData);
        updateStats();
        updateLastUpdated();
        return allData;
    } catch (error) {
        console.error('加载 JSON 数据时出错:', error);
        dataTableBody.innerHTML = `
            <tr>
                <td colspan="12" class="px-6 py-10 text-center text-red-500">
                    <div class="flex flex-col items-center">
                        <i class="fa fa-exclamation-circle text-3xl mb-2"></i>
                        <p>加载数据失败: ${error.message}</p>
                        <p class="text-sm mt-2">请确保 JSON 文件路径正确并且格式有效</p>
                    </div>
                </td>
            </tr>
        `;
        return [];
    }
}

// 渲染表格数据
function renderTable_v1(data) {
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const currentPageData = data.slice(startIndex, endIndex);

    if (currentPageData.length === 0) {
        dataTableBody.innerHTML = `
            <tr>
                <td colspan="12" class="px-6 py-10 text-center text-gray-500">
                    <p>没有找到匹配的记录</p>
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    currentPageData.forEach((item, index) => {
        // 格式化日期
        const date = item['日期'] ? new Date(item['日期']).toLocaleDateString() : '-';
        const dueDate = item['截止日期'] ? new Date(item['截止日期']).toLocaleDateString() : '-';

        // 设置严重等级的样式
        let severityClass = '';
        if (item['严重等级'] === 'severity1') severityClass = 'bg-red-100 text-red-800';
        else if (item['严重等级'] === 'severity2') severityClass = 'bg-orange-100 text-orange-800';
        else if (item['严重等级'] === 'severity3') severityClass = 'bg-yellow-100 text-yellow-800';
        else severityClass = 'bg-gray-100 text-gray-800';

        // 设置状态的样式
        let statusClass = '';
        if (item['Status'] === 'Open') statusClass = 'bg-red-100 text-red-800';
        else if (item['Status'] === 'In Progress') statusClass = 'bg-blue-100 text-blue-800';
        else if (item['状态'] === 'Resolved') statusClass = 'bg-green-100 text-green-800';
        else statusClass = 'bg-gray-100 text-gray-800';

        // 格式化不良率
        const defectRate = item['不良率'] !== undefined ? (item['不良率'] * 100).toFixed(2) + '%' : '-';

        html += `
            <tr class="hover:bg-gray-50 transition-colors cursor-pointer" data-index="${index}">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${date}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item['站点'] || '-'}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${item['问题描述'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['阶段'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${severityClass}">
                        ${item['严重等级'] || '-'}
                    </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${item['SN'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['不良数'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['投入数'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${defectRate}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['责任人'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
                        ${item['状态'] || '-'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['类别'] || '-'}</td>
            </tr>
        `;
    });

    dataTableBody.innerHTML = html;

    // 添加行点击事件
    document.querySelectorAll('#dataTableBody tr').forEach(row => {
        row.addEventListener('click', () => {
            const index = parseInt(row.getAttribute('data-index'));
            showDetailModal(currentPageData[index]);
        });
    });

    // 更新分页信息
    const start = startIndex + 1;
    const end = Math.min(startIndex + recordsPerPage, data.length);
    currentPageRange.textContent = `${start}-${end}`;
    totalPages.textContent = Math.ceil(data.length / recordsPerPage);
}

// 渲染表格数据
function renderTable(data) {
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const currentPageData = data.slice(startIndex, endIndex);

    if (currentPageData.length === 0) {
        dataTableBody.innerHTML = `
            <tr>
                <td colspan="14" class="px-6 py-10 text-center text-gray-500">
                    <p>没有找到匹配的记录</p>
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    currentPageData.forEach((item, index) => {
        // 格式化日期
        const date = item['日期'] ? new Date(item['日期']).toLocaleDateString() : '-';
        const dueDate = item['截止日期'] ? new Date(item['截止日期']).toLocaleDateString() : '-';

        // 设置严重等级的样式
        let severityClass = '';
        if (item['严重等级'] === 'severity1') severityClass = 'bg-red-100 text-red-800';
        else if (item['严重等级'] === 'severity2') severityClass = 'bg-orange-100 text-orange-800';
        else if (item['严重等级'] === 'severity3') severityClass = 'bg-yellow-100 text-yellow-800';
        else severityClass = 'bg-gray-100 text-gray-800';

        // 设置状态的样式
        let statusClass = '';
        if (item['状态'] === 'Open') statusClass = 'bg-red-100 text-red-800';
        else if (item['状态'] === 'In Progress') statusClass = 'bg-blue-100 text-blue-800';
        else if (item['状态'] === 'Resolved') statusClass = 'bg-green-100 text-green-800';
        else statusClass = 'bg-gray-100 text-gray-800';

        // 格式化不良率
        const defectRate = item['不良率'] !== undefined ? (item['不良率'] * 100).toFixed(2) + '%' : '-';

        // 截断过长的文本
        const rootCause = item['根本原因'] ? truncateText(item['根本原因'], 30) : '-';
        const improvement = item['改善措施'] ? truncateText(item['改善措施'], 30) : '-';

        html += `
            <tr class="hover:bg-gray-50 transition-colors cursor-pointer" data-index="${index}">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${date}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item['站点'] || '-'}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${item['问题描述'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['阶段'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${severityClass}">
                        ${item['严重等级'] || '-'}
                    </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${item['SN'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['不良数'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['投入数'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${defectRate}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['责任人'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
                        ${item['状态'] || '-'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['类别'] || '-'}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${rootCause}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${improvement}</td>
            </tr>
        `;
    });

    dataTableBody.innerHTML = html;

    // 添加行点击事件
    document.querySelectorAll('#dataTableBody tr').forEach(row => {
        row.addEventListener('click', () => {
            const index = parseInt(row.getAttribute('data-index'));
            showDetailModal(currentPageData[index]);
        });
    });

    // 更新分页信息
    const start = startIndex + 1;
    const end = Math.min(startIndex + recordsPerPage, data.length);
    currentPageRange.textContent = `${start}-${end}`;
    totalPages.textContent = Math.ceil(data.length / recordsPerPage);
}

// 文本截断辅助函数
function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

// 显示详情模态框
function showDetailModal(item) {
    // 格式化日期
    const date = item['日期'] ? new Date(item['日期']).toLocaleDateString() : '-';
    const dueDate = item['截止日期'] ? new Date(item['截止日期']).toLocaleDateString() : '-';

    // 格式化不良率
    const defectRate = item['不良率'] !== undefined ? (item['不良率'] * 100).toFixed(2) + '%' : '-';

    // 生成详情内容
    let html = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h4 class="text-sm font-medium text-gray-500 mb-1">日期</h4>
                <p class="text-base font-semibold">${date}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">站点</h4>
                <p class="text-base">${item['站点'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">问题描述</h4>
                <p class="text-base">${item['问题描述'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">阶段</h4>
                <p class="text-base">${item['阶段'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">严重等级</h4>
                <p class="text-base">${item['严重等级'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">SN</h4>
                <p class="text-base">${item['SN'] || '-'}</p>
            </div>

            <div>
                <h4 class="text-sm font-medium text-gray-500 mb-1">不良数</h4>
                <p class="text-base">${item['不良数'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">投入数</h4>
                <p class="text-base">${item['投入数'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">不良率</h4>
                <p class="text-base">${defectRate}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">责任人</h4>
                <p class="text-base">${item['责任人'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">状态</h4>
                <p class="text-base">${item['状态'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">类别</h4>
                <p class="text-base">${item['类别'] || '-'}</p>
            </div>
        </div>

        <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-500 mb-2">根本原因</h4>
            <p class="text-base p-3 bg-gray-50 rounded-lg">${item['根本原因'] || '未提供'}</p>
        </div>

        <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-500 mb-2">改善措施</h4>
            <p class="text-base p-3 bg-gray-50 rounded-lg">${item['改善措施'] || '未提供'}</p>
        </div>

        <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-500 mb-2">截止日期</h4>
            <p class="text-base">${dueDate}</p>
        </div>
    `;

    modalContent.innerHTML = html;
    detailModal.classList.remove('hidden');
}

// 关闭详情模态框
function closeDetailModal() {
    detailModal.classList.add('hidden');
}

// 执行多条件筛选
function filterData() {
    const filterGroups = document.querySelectorAll('.filter-group');
    const filters = [];

    // 收集所有筛选条件
    filterGroups.forEach(group => {
        const field = group.querySelector('.filter-field').value;
        const condition = group.querySelector('.filter-condition').value;
        const value = group.querySelector('.filter-value').value.trim();

        if (value) {
            filters.push({ field, condition, value });
        }
    });

    // 如果没有设置筛选条件，则显示全部数据
    if (filters.length === 0) {
        filteredData = [...allData];
    } else {
        // 应用多条件筛选
        filteredData = allData.filter(item => {
            // 所有条件都必须满足（AND逻辑）
            return filters.every(filter => {
                const fieldValue = item[filter.field];

                // 如果字段值不存在，返回false
                if (fieldValue === undefined || fieldValue === null) {
                    return false;
                }

                // 根据不同的筛选条件进行匹配
                switch (filter.condition) {
                    case 'contains':
                        return String(fieldValue).includes(filter.value);
                    case 'equals':
                        return String(fieldValue) === filter.value;
                    case 'startsWith':
                        return String(fieldValue).startsWith(filter.value);
                    case 'endsWith':
                        return String(fieldValue).endsWith(filter.value);
                    case 'greater':
                        // 尝试将值转换为数字进行比较
                        const numFieldValue = parseFloat(fieldValue);
                        const numValue = parseFloat(filter.value);
                        return !isNaN(numFieldValue) && !isNaN(numValue) && numFieldValue > numValue;
                    case 'less':
                        // 尝试将值转换为数字进行比较
                        const numFieldVal = parseFloat(fieldValue);
                        const numVal = parseFloat(filter.value);
                        return !isNaN(numFieldVal) && !isNaN(numVal) && numFieldVal < numVal;
                    default:
                        return false;
                }
            });
        });
    }

    currentPage = 1;
    renderTable(filteredData);
    updateStats();
}

// 重置筛选
function resetFilter() {
    // 移除所有添加的筛选条件，只保留第一个
    const filterGroups = document.querySelectorAll('.filter-group');
    for (let i = 1; i < filterGroups.length; i++) {
        filterGroups[i].remove();
    }

    // 重置第一个筛选条件的值
    const firstGroup = filterGroups[0];
    firstGroup.querySelector('.filter-field').value = '日期';
    firstGroup.querySelector('.filter-condition').value = 'contains';
    firstGroup.querySelector('.filter-value').value = '';

    // 恢复默认数据
    filteredData = [...allData];
    currentPage = 1;
    renderTable(filteredData);
    updateStats();
}

// 添加新的筛选条件
function addFilterCondition() {
    const container = document.getElementById('filterConditionsContainer');
    const lastGroup = container.querySelector('.filter-group:last-child');

    // 创建新的筛选条件组
    const newGroup = document.createElement('div');
    newGroup.className = 'filter-group grid grid-cols-1 md:grid-cols-4 gap-4 mb-4';

    newGroup.innerHTML = `
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">筛选字段</label>
            <select class="filter-field w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary/20 transition-all">
                <option value="日期">日期</option>
                <option value="站点">站点</option>
                <option value="问题描述">问题描述</option>
                <option value="阶段">阶段</option>
                <option value="严重等级">严重等级</option>
                <option value="SN">SN</option>
                <option value="不良数">不良数</option>
                <option value="投入数">投入数</option>
                <option value="不良率">不良率</option>
                <option value="供应商">供应商</option>
                <option value="根本原因">根本原因</option>
                <option value="改善措施">改善措施</option>
                <option value="责任人">责任人</option>
                <option value="状态">状态</option>
                <option value="类别">类别</option>
                <option value="截止日期">截止日期</option>
                <option value="配置">配置</option>
                <option value="图片">图片</option>
            </select>
        </div>

        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">筛选条件</label>
            <select class="filter-condition w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary/20 transition-all">
                <option value="contains">包含</option>
                <option value="equals">等于</option>
                <option value="startsWith">以...开始</option>
                <option value="endsWith">以...结束</option>
                <option value="greater">大于</option>
                <option value="less">小于</option>
            </select>
        </div>

        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">筛选值</label>
            <input type="text" class="filter-value w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary/20 transition-all" placeholder="输入筛选值">
        </div>

        <div class="flex items-end">
            <button class="add-filter-btn px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors" onclick="removeFilterCondition(this)">
                <i class="fa fa-minus mr-1"></i> 移除条件
            </button>
        </div>
    `;

    container.appendChild(newGroup);
}

// 移除筛选条件
function removeFilterCondition(button) {
    const group = button.closest('.filter-group');
    if (document.querySelectorAll('.filter-group').length > 1) {
        group.remove();
    }
}

// 更新统计信息
function updateStats() {
    totalRecords.textContent = filteredData.length;
    pendingIssues.textContent = filteredData.filter(item => item['状态'] === 'Open').length;
    severeIssues.textContent = filteredData.filter(item => item['严重等级'] === 'severity1').length;

    const validDefectRates = filteredData.filter(item => typeof item['不良率'] === 'number');
    const totalDefectRate = validDefectRates.reduce((sum, item) => sum + item['不良率'], 0);
    const averageDefectRate = validDefectRates.length > 0 ? (totalDefectRate / validDefectRates.length) * 100 : 0;
    avgDefectRate.textContent = averageDefectRate.toFixed(2) + '%';
}

// 更新最后更新时间
function updateLastUpdated() {
    const now = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
    lastUpdated.textContent = now.toLocaleDateString('zh-CN', options);
}

// 刷新数据
function refreshData() {
    loadJSON();
}

// 导出结果
function exportData() {
    const csvContent = "data:text/csv;charset=utf-8," +
        Object.keys(filteredData[0]).join(",") + "\n" +
        filteredData.map(item => Object.values(item).join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "TITANS项目日报表分析.csv");
    document.body.appendChild(link); // Required for FF
    link.click();
    document.body.removeChild(link);
}

// 切换每页记录数
function changeRecordsPerPage() {
    recordsPerPage = parseInt(recordsPerPageSelect.value);
    currentPage = 1;
    renderTable(filteredData);
}

// 分页功能
function goToPage(page) {
    if (page >= 1 && page <= Math.ceil(filteredData.length / recordsPerPage)) {
        currentPage = page;
        renderTable(filteredData);
    }
}

// 初始化事件监听
function init() {
    loadJSON();

    filterBtn.addEventListener('click', filterData);
    resetBtn.addEventListener('click', resetFilter);
    refreshBtn.addEventListener('click', refreshData);
    exportBtn.addEventListener('click', exportData);
    closeModal.addEventListener('click', closeDetailModal);
    closeModalBtn.addEventListener('click', closeDetailModal);
    document.querySelectorAll('.add-filter-btn').forEach(btn => {
        btn.addEventListener('click', addFilterCondition);
    });
    recordsPerPageSelect.addEventListener('change', changeRecordsPerPage);

    // 分页按钮事件监听
    document.querySelectorAll('#pagination a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = parseInt(link.textContent);
            if (!isNaN(page)) {
                goToPage(page);
            }
        });
    });
}

window.onload = init;