// -------------------------- 变量 --------------------------
/**
 * 存储从所有选中的JSON文件中加载的原始数据
 * 格式：数组，每个元素为一个JSON对象
 */
let allData = [];

/**
 * 存储经过筛选条件过滤后的数据
 * 格式：数组，每个元素为一个符合筛选条件的JSON对象
 */
let filteredData = [];

/**
 * 当前显示的页码
 * 初始值为1，表示第一页
 */
let currentPage = 1;

/**
 * 每页显示的记录数
 * 可通过下拉菜单调整，默认值为10
 */
let recordsPerPage = 10;

/**
 * 存储从配置文件中读取的可用JSON文件列表
 * 格式：数组，每个元素为文件名（字符串）
 */
let availableJsonFiles = [];

/**
 * 图表对象引用
 *  - dateIssueChart: 日期与问题关系图表
 *  - statusChart: 问题状态分布图表
 *  - rootCauseChart: 根本原因分析图表
 *  - improvementChart: 改善措施效果图表
 */
let dateIssueChart = null;
let statusChart = null;
let rootCauseChart = null;
let improvementChart = null;

/**
 * 是否需要重新渲染图表的标志
 * 当数据更新或筛选条件变化时设置为true
 */
let shouldRenderCharts = false;

/**
 * 防止重复渲染的锁标志
 * 在渲染过程中设置为true，完成后恢复为false
 */
let isRendering = false;

// -------------------------- DOM 元素与相关事件、函数 --------------------------

/**
 * 数据表格主体
 * 用于显示加载和筛选后的数据行
 */
const dataTableBody = document.getElementById('dataTableBody');

/**
 * 筛选按钮事件监听
 * 点击后根据用户设置的筛选条件对数据进行过滤
 */
const filterBtn = document.getElementById('filterBtn');
filterBtn.addEventListener('click', () => {
    // 获取所有筛选条件组元素
    const filterGroups = document.querySelectorAll('.filter-group');
    // 复制原始数据用于筛选操作
    let newFilteredData = [...allData];

    // 遍历每个筛选条件组进行数据过滤
    filterGroups.forEach(group => {
        // 获取筛选字段
        const field = group.querySelector('.filter-field').value;
        // 获取筛选操作符
        const condition = group.querySelector('.filter-condition').value;
        // 获取筛选值
        const value = group.querySelector('.filter-value').value;

        // 跳过空值条件
        if (value.trim() === '') return;

        // 根据筛选条件过滤数据
        newFilteredData = newFilteredData.filter(item => {
            const itemValue = item[field];
            // 处理字段不存在或为空的情况
            if (itemValue === undefined || itemValue === null) return false;

            // 根据不同操作符执行筛选逻辑
            switch (condition) {
                case 'contains':
                    return itemValue.toString().includes(value);
                case 'equals':
                    return itemValue.toString() === value;
                case 'startsWith':
                    return itemValue.toString().startsWith(value);
                case 'endsWith':
                    return itemValue.toString().endsWith(value);
                case 'greater':
                    return parseFloat(itemValue) > parseFloat(value);
                case 'less':
                    return parseFloat(itemValue) < parseFloat(value);
                default:
                    return false;
            }
        });
    });

    // 更新筛选结果并刷新UI
    filteredData = newFilteredData;
    currentPage = 1; // 重置页码
    renderTable(filteredData);
    updateStats();
    document.getElementById('analysisBtn').classList.remove('hidden');
});

/**
 * 重置按钮事件监听
 * 点击后恢复所有数据并重置筛选条件
 */
const resetBtn = document.getElementById('resetBtn');
resetBtn.addEventListener('click', () => {
    // 恢复原始数据
    filteredData = [...allData];
    currentPage = 1; // 重置页码
    renderTable(filteredData);
    updateStats();

    // 隐藏分析按钮并重置图表标志
    document.getElementById('analysisBtn').classList.add('hidden');
    shouldRenderCharts = false;

    // 重置筛选条件UI
    const filterGroups = document.querySelectorAll('.filter-group');
    filterGroups.forEach((group, index) => {
        if (index > 0) {
            // 移除额外添加的筛选组
            group.remove();
        } else {
            // 重置默认筛选组
            group.querySelector('.filter-field').value = '日期';
            group.querySelector('.filter-condition').value = 'contains';
            group.querySelector('.filter-value').value = '';
        }
    });
});

/**
 * 刷新按钮事件监听
 * 点击后重新加载选中的JSON文件
 */
const refreshBtn = document.getElementById('refreshBtn');
refreshBtn.addEventListener('click', loadSelectedJSONFiles);

/**
 * 导出按钮事件监听
 * 点击后将所有数据导出为CSV文件
 */
const exportBtn = document.getElementById('exportBtn');
exportBtn.addEventListener('click', () => {
    // 检查是否有数据可导出
    if (allData.length === 0) {
        alert('没有数据可导出');
        return;
    }

    // 构建CSV内容
    const headers = Object.keys(allData[0]);
    const csvContent = "data:text/csv;charset=utf-8," +
        headers.join(',') + '\n' +
        allData.map(item => headers.map(header => {
            // 处理特殊字符和引号
            const value = item[header] === undefined || item[header] === null ? '' : item[header];
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        }).join(',')).join('\n');

    // 创建下载链接并触发下载
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'data.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

/**
 * 详情模态框元素
 * 用于显示数据的详细信息
 */
const detailModal = document.getElementById('detailModal');
const closeModal = document.getElementById('closeModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const modalContent = document.getElementById('modalContent');
// 点击关闭图标时，隐藏模态框
closeModal.addEventListener('click', () => {
    detailModal.classList.add('hidden');
});
// 点击关闭按钮时，隐藏模态框
closeModalBtn.addEventListener('click', () => {
    detailModal.classList.add('hidden');
});


/**
 * 统计信息元素
 * 显示各类统计数据
 */
const totalRecords = document.getElementById('totalRecords');
const pendingIssues = document.getElementById('pendingIssues');
const severeIssues = document.getElementById('severeIssues');
const avgDefectRate = document.getElementById('avgDefectRate');

/**
 * 分页信息元素
 * 显示当前页码范围和总页数
 */
const currentPageRange = document.getElementById('currentPageRange');
const totalPages = document.getElementById('totalPages');

/**
 * 最后更新时间元素
 * 显示数据最后更新的时间
 */
const lastUpdated = document.getElementById('lastUpdated');

/**
 * 筛选条件容器
 * 用于动态添加和移除筛选条件组
 */
const filterConditionsContainer = document.getElementById('filterConditionsContainer');

/**
 * 每页记录数选择器事件监听
 * 用户可以选择每页显示的记录数
 */
const recordsPerPageSelect = document.getElementById('recordsPerPage');
recordsPerPageSelect.addEventListener('change', () => {
    // 更新每页记录数并刷新表格
    recordsPerPage = parseInt(recordsPerPageSelect.value);
    currentPage = 1; // 重置页码
    renderTable(filteredData);
});

/**
 * 文件选择复选框容器
 * 用于显示可用的JSON文件复选框
 */
const fileCheckboxesContainer = document.getElementById('fileCheckboxesContainer');

/**
 * 加载按钮事件监听
 * 点击后加载选中的JSON文件
 */
const loadBtn = document.getElementById('loadBtn');
loadBtn.addEventListener('click', loadSelectedJSONFiles);

/**
 * 问题统计分析按钮事件监听
 * 点击后从筛选条件中获取站点和问题描述，并触发图表渲染
 */
const analysisBtn = document.getElementById('analysisBtn');
analysisBtn.addEventListener('click', () => {
    // 获取当前筛选条件中的站点和问题描述
    const siteFilter = getFilterValueByField('站点');
    const issueDescFilter = getFilterValueByField('问题描述');

    // 设置图表渲染标志并传递参数调用渲染函数
    shouldRenderCharts = true;
    renderCharts(siteFilter, issueDescFilter);
});

/**
 * 辅助函数：根据字段名获取第一个匹配的筛选值
 * @param {string} fieldName - 要查找的字段名
 * @returns {string} - 筛选值，如果未找到则返回空字符串
 */
function getFilterValueByField(fieldName) {
    const filterGroups = document.querySelectorAll('.filter-group');

    // 查找第一个匹配的筛选条件组
    for (const group of filterGroups) {
        const field = group.querySelector('.filter-field').value;
        if (field === fieldName) {
            return group.querySelector('.filter-value').value.trim() || 'ALL';
        }
    }

    return 'ALL'; // 默认返回全部
}


/**
 * 动态筛选条件按钮事件委托
 * 处理添加和移除筛选条件组的操作
 */
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('add-filter-btn')) {
        // 克隆并添加新的筛选条件组
        const filterGroups = document.querySelectorAll('.filter-group');
        const lastGroup = filterGroups[filterGroups.length - 1];
        const newGroup = lastGroup.cloneNode(true);

        // 重置新组的值并更新按钮
        newGroup.querySelector('.filter-value').value = '';
        const buttonContainer = newGroup.querySelector('div.flex.items-end');
        buttonContainer.innerHTML = `
            <button class="remove-filter-btn px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors">
                <i class="fa fa-minus mr-1"></i> 移除条件
            </button>
        `;

        // 添加新组到DOM并设置自动补全
        lastGroup.after(newGroup);
        setupAutoComplete();
    }

    if (e.target.classList.contains('remove-filter-btn')) {
        // 移除当前筛选条件组
        e.target.closest('.filter-group').remove();
    }
});

// -------------------------- 页面加载相关 --------------------------
/**
 * 页面加载完成事件监听
 * 初始化配置并设置自动补全功能
 */
window.addEventListener('load', function() {
    loadConfig().then(() => {
        setupAutoComplete();
    });
});

// -------------------------- 功能函数 --------------------------

/**
 * 加载配置文件，获取可用的JSON文件列表，并渲染文件复选框
 * @returns {Promise<Array>} 可用的JSON文件列表
 */
async function loadConfig() {
    try {
        // 发送请求获取配置文件
        const response = await fetch("../docs/config.json");

        if (!response.ok) {
            throw new Error(`加载配置失败: 状态码 ${response.status}, 尝试路径: ${configPath}`);
        }
        // 解析响应为JSON数据
        const config = await response.json();
        // 获取可用的JSON文件列表
        availableJsonFiles = config.jsonFiles || [];
        // 渲染文件复选框
        renderFileCheckboxes();
        return availableJsonFiles;
    } catch (error) {
        // 处理加载配置文件时的错误
        console.error('加载配置文件时出错:', error);
        fileCheckboxesContainer.innerHTML = `
            <div class="flex items-center text-red-500">
                <i class="fa fa-exclamation-circle mr-2"></i>
                <span>无法加载文件列表: ${error.message}</span>
            </div>
        `;
        return [];
    }
}

/**
 * 根据可用的JSON文件列表，渲染文件复选框
 */
function renderFileCheckboxes() {
    if (availableJsonFiles.length === 0) {
        // 如果没有可用的JSON文件，显示错误信息
        fileCheckboxesContainer.innerHTML = `
            <div class="flex items-center text-red-500">
                <i class="fa fa-exclamation-circle mr-2"></i>
                <span>没有可用的JSON文件</span>
            </div>
        `;
        return;
    }

    // 清空文件复选框容器
    fileCheckboxesContainer.innerHTML = '';
    // 遍历可用的JSON文件列表，渲染复选框
    availableJsonFiles.forEach(file => {
        const checkboxHtml = `
            <label class="flex items-center mb-2">
                <input type="checkbox" class="file-checkbox mr-2" value="${file.path}">
                <span>${file.name}</span>
            </label>
        `;
        fileCheckboxesContainer.innerHTML += checkboxHtml;
    });
}

/**
 * 加载用户选中的JSON文件，将数据合并到allData中，更新filteredData，重新渲染表格和统计信息
 * @returns {Promise<Array>} 加载的所有数据
 */
async function loadSelectedJSONFiles() {
    // 获取所有选中的文件复选框
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');
    // 获取选中的文件路径列表
    const selectedFiles = Array.from(checkboxes).map(checkbox => checkbox.value);

    // 如果没有选中任何文件，提示用户
    if (selectedFiles.length === 0) {
        alert('请至少选择一个JSON文件');
        return;
    }

    try {
        // 并行请求所有选中的JSON文件
        const allResponses = await Promise.all(selectedFiles.map(path => fetch(path)));
        // 解析所有响应为JSON数据
        const allJsonData = await Promise.all(allResponses.map(response => {
            if (!response.ok) {
                throw new Error(`HTTP 错误! 状态: ${response.status}`);
            }
            return response.json();
        }));

        // 合并所有数据
        allData = [].concat(...allJsonData);
        // 更新筛选后的数据
        filteredData = [...allData];
        // 重新渲染表格
        renderTable(filteredData);
        // 更新统计信息
        updateStats();
        // 更新最后更新时间
        updateLastUpdated();
        // 重新设置自动补全功能
        setupAutoComplete();
        // 隐藏问题统计分析按钮
        document.getElementById('analysisBtn').classList.add('hidden');
        // 重置图表渲染标志
        shouldRenderCharts = false;
        // 新增：不渲染图表
        return allData;
    } catch (error) {
        // 处理加载JSON数据时的错误
        console.error('加载JSON数据时出错:', error);
        dataTableBody.innerHTML = `
            <tr>
                <td colspan="14" class="px-6 py-10 text-center text-red-500">
                    <div class="flex flex-col items-center">
                        <i class="fa fa-exclamation-circle text-3xl mb-2"></i>
                        <p>加载数据失败: ${error.message}</p>
                        <p class="text-sm mt-2">请确保JSON文件路径正确并且格式有效</p>
                    </div>
                </td>
            </tr>
        `;
        return [];
    }
}

/**
 * 根据当前页码和每页记录数，从filteredData中截取数据并渲染到表格中，同时更新分页信息
 * @param {Array} data 要渲染的数据
 */
function renderTable(data) {
    // 计算当前页数据的起始索引
    const startIndex = (currentPage - 1) * recordsPerPage;
    // 计算当前页数据的结束索引
    const endIndex = startIndex + recordsPerPage;
    // 截取当前页的数据
    const currentPageData = data.slice(startIndex, endIndex);

    if (currentPageData.length === 0) {
        // 如果当前页没有数据，显示提示信息
        dataTableBody.innerHTML = `
            <tr>
                <td colspan="14" class="px-6 py-10 text-center text-gray-500">
                    <p>没有找到匹配的记录</p>
                </td>
            </tr>
        `;
        return;
    }

    // 构建表格行的HTML内容
    let html = '';
    currentPageData.forEach((item, index) => {
        // 格式化日期
        const date = item['日期'] ? new Date(item['日期']).toLocaleDateString() : '-';
        // 格式化截止日期
        const dueDate = item['截止日期'] ? new Date(item['截止日期']).toLocaleDateString() : '-';

        // 根据严重等级设置背景和文本颜色
        let severityClass = '';
        if (item['严重等级'] === 'severity1') severityClass = 'bg-red-100 text-red-800';
        else if (item['严重等级'] === 'severity2') severityClass = 'bg-orange-100 text-orange-800';
        else if (item['严重等级'] === 'severity3') severityClass = 'bg-yellow-100 text-yellow-800';
        else severityClass = 'bg-gray-100 text-gray-800';

        // 根据状态设置背景和文本颜色
        let statusClass = '';
        if (item['状态'] === 'Open') statusClass = 'bg-red-100 text-red-800';
        else if (item['状态'] === 'In Progress') statusClass = 'bg-blue-100 text-blue-800';
        else if (item['状态'] === 'Resolved') statusClass = 'bg-green-100 text-green-800';
        else statusClass = 'bg-gray-100 text-gray-800';

        // 格式化不良率
        const defectRate = item['不良率']!== undefined? (item['不良率'] * 100).toFixed(2) + '%' : '-';
        // 截断根本原因文本
        const rootCause = item['根本原因']? truncateText(item['根本原因'], 30) : '-';
        // 截断改善措施文本
        const improvement = item['改善措施']? truncateText(item['改善措施'], 30) : '-';

        // 构建表格行的HTML
        html += `
            <tr class="hover:bg-gray-50 transition-colors cursor-pointer" data-index="${index}">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${date}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${item['站点'] || '-'}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${item['问题描述'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['阶段'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${severityClass}">
                        ${item['严重等级'] || '-'}</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${item['SN'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['不良数'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['投入数'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${defectRate}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['责任人'] || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
                        ${item['状态'] || '-'}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${item['类别'] || '-'}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${rootCause}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${improvement}</td>
            </tr>
        `;
    });

    // 将表格行的HTML内容添加到表格主体中
    dataTableBody.innerHTML = html;

    // 为表格行添加点击事件，点击时显示详情模态框
    document.querySelectorAll('#dataTableBody tr').forEach(row => {
        row.addEventListener('click', () => {
            const index = parseInt(row.getAttribute('data-index'));
            showDetailModal(currentPageData[index]);
        });
    });

    // 计算当前页码范围
    const start = startIndex + 1;
    const end = Math.min(startIndex + recordsPerPage, data.length);
    // 更新当前页码范围显示
    currentPageRange.textContent = `${start}-${end}`;
    // 更新总页数显示
    totalPages.textContent = Math.ceil(data.length / recordsPerPage);
}

/**
 * 截断文本，当文本长度超过指定长度时，显示截断后的文本并添加省略号
 * @param {string} text 要截断的文本
 * @param {number} maxLength 最大长度
 * @returns {string} 截断后的文本
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}

/**
 * 显示详情模态框，展示选中行数据的详细信息
 * @param {Object} item 要显示详细信息的数据项
 */
function showDetailModal(item) {
    // 格式化日期
    const date = item['日期']? new Date(item['日期']).toLocaleDateString() : '-';
    // 格式化截止日期
    const dueDate = item['截止日期']? new Date(item['截止日期']).toLocaleDateString() : '-';
    // 格式化不良率
    const defectRate = item['不良率']!== undefined? (item['不良率'] * 100).toFixed(2) + '%' : '-';

    // 构建模态框内容的HTML
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

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">根本原因</h4>
                <p class="text-base">${item['根本原因'] || '-'}</p>

                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">改善措施</h4>
                <p class="text-base">${item['改善措施'] || '-'}</p>
    `;

    if (item['截止日期']) {
        // 如果有截止日期，添加到模态框内容中
        html += `
                <h4 class="text-sm font-medium text-gray-500 mb-1 mt-4">截止日期</h4>
                <p class="text-base">${dueDate}</p>
        `;
    }

    // 完成模态框内容的HTML构建
    html += `
            </div>
        </div>
    `;

    // 将模态框内容添加到模态框中
    modalContent.innerHTML = html;
    // 显示模态框
    detailModal.classList.remove('hidden');
}

/**
 * 更新统计信息，包括总记录数、待处理问题数、严重问题数和平均不良率
 */
function updateStats() {
    // 计算总记录数
    const total = filteredData.length;
    // 计算待处理问题数
    const pending = filteredData.filter(item => item['状态'] === 'Open').length;
    // 计算严重问题数
    const severe = filteredData.filter(item => item['严重等级'] === 'severity1' || item['严重等级'] === 'severity2').length;
    // 计算总不良率
    const totalDefectRate = filteredData.reduce((sum, item) => {
        return item['不良率']!== undefined? sum + item['不良率'] : sum;
    }, 0);
    // 计算平均不良率
    const avgRate = total > 0? (totalDefectRate / total * 100).toFixed(2) + '%' : '0%';

    // 更新总记录数显示
    totalRecords.textContent = total;
    // 更新待处理问题数显示
    pendingIssues.textContent = pending;
    // 更新严重问题数显示
    severeIssues.textContent = severe;
    // 更新平均不良率显示
    avgDefectRate.textContent = avgRate;
}

/**
 * 更新最后更新时间
 */
function updateLastUpdated() {
    // 获取当前时间
    const now = new Date();
    // 格式化时间显示
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
    // 更新最后更新时间显示
    lastUpdated.textContent = now.toLocaleDateString('zh-CN', options);
}

// 自动补全功能
/**
 * 为筛选值输入框设置自动补全功能，根据用户输入的字段和值提供建议
 */
function setupAutoComplete() {
    // 获取所有的筛选值输入框
    const filterValueInputs = document.querySelectorAll('.filter-value');
    filterValueInputs.forEach(input => {
        // 监听输入框的输入事件
        input.addEventListener('input', function() {
            // 获取筛选字段
            const field = this.closest('.filter-group').querySelector('.filter-field').value;
            // 获取输入的值
            const inputValue = this.value;
            // 获取建议列表
            const suggestions = getSuggestions(field, inputValue);
            // 显示建议列表
            showSuggestions(this, suggestions);
        });

        // 监听输入框的失去焦点事件
        input.addEventListener('blur', function() {
            setTimeout(() => {
                // 移除建议列表
                const suggestionsList = this.nextElementSibling;
                if (suggestionsList && suggestionsList.classList.contains('suggestions-list')) {
                    suggestionsList.remove();
                }
            }, 200);
        });
    });
}

/**
 * 根据用户输入的字段和值，从allData中获取匹配的唯一值作为建议
 * @param {string} field 筛选字段
 * @param {string} inputValue 输入的值
 * @returns {Array} 建议列表
 */
function getSuggestions(field, inputValue) {
    // 使用Set存储唯一值
    const uniqueValues = new Set();
    allData.forEach(item => {
        const value = item[field];
        // 如果值包含输入的值，添加到Set中
        if (value!== undefined && value.toString().toLowerCase().includes(inputValue.toLowerCase())) {
            uniqueValues.add(value.toString());
        }
    });
    // 将Set转换为数组并返回
    return Array.from(uniqueValues);
}

/**
 * 将建议显示在输入框下方的列表中，用户点击建议项后，将建议项的值填充到输入框中
 * @param {HTMLElement} input 输入框元素
 * @param {Array} suggestions 建议列表
 */
function showSuggestions(input, suggestions) {
    // 创建建议列表元素
    const suggestionsList = document.createElement('ul');
    suggestionsList.classList.add('suggestions-list', 'absolute', 'bg-white', 'border', 'border-gray-300', 'mt-1', 'z-10', 'max-h-40', 'overflow-y-auto');

    // 遍历建议列表，创建列表项
    suggestions.forEach(suggestion => {
        const listItem = document.createElement('li');
        listItem.textContent = suggestion;
        listItem.classList.add('px-4', 'py-2', 'hover:bg-gray-100', 'cursor-pointer');

        // 监听列表项的点击事件，点击时将建议项的值填充到输入框中
        listItem.addEventListener('click', function() {
            input.value = this.textContent;
            const suggestionsList = this.closest('.suggestions-list');
            if (suggestionsList) {
                // 移除建议列表
                suggestionsList.remove();
            }
        });

        // 将列表项添加到建议列表中
        suggestionsList.appendChild(listItem);
    });

    // 如果输入框已经有建议列表，移除旧的列表
    const existingSuggestionsList = input.nextElementSibling;
    if (existingSuggestionsList && existingSuggestionsList.classList.contains('suggestions-list')) {
        existingSuggestionsList.remove();
    }

    // 将新的建议列表添加到输入框后面
    input.parentNode.insertBefore(suggestionsList, input.nextSibling);
}

/**
 * 渲染所有图表，包括日期与问题关系、状态分布、根本原因分布和改善措施实施情况
 * @param {string} site - 要筛选的站点名称
 * @param {string} issueDescription - 要筛选的问题描述
 */
function renderCharts(site = 'ALL', issueDescription = 'ALL') {
    // 只有当!isRendering且shouldRenderCharts为true时才渲染图表
    if (isRendering || !shouldRenderCharts) return;

    try {
        // // 筛选数据 - 使用传入的站点和问题描述参数
        // const filteredChartData = filteredData.filter(item =>
        //     item['站点'] === site &&
        //     item['问题描述'] === issueDescription
        // );

        // 筛选数据 - 处理"ALL"的情况
        const filteredChartData = filteredData.filter(item => {
        const siteMatch = site === 'ALL' || item['站点'] === site;
        const issueMatch = issueDescription === 'ALL' || item['问题描述'] === issueDescription;
        return siteMatch && issueMatch;
    });

        if (filteredChartData.length === 0) {
            // 如果没有数据，清空所有图表
            clearAllCharts();
            console.log(`没有找到站点为 "${site}" 且问题描述为 "${issueDescription}" 的数据`);
            return;
        }

        // 按日期排序
        filteredChartData.sort((a, b) => new Date(a['日期']) - new Date(b['日期']));

        // 渲染日期与问题关系图表
        // 自定义点大小（更大的点）
        renderDateIssueChart(filteredData, {
            pointRadius: 6,
            pointHoverRadius: 8
        });

    } finally {
        isRendering = false;
    }
}

/**
 * 渲染日期与问题关系图表
 * @param {Array} data - 图表数据
 * @param {Object} [chartOptions] - 可选的图表配置选项
 * @param {number} [chartOptions.pointRadius=4] - 数据点的半径大小
 * @param {number} [chartOptions.pointHoverRadius=6] - 鼠标悬停时点的半径大小
 * @param {number} [chartOptions.pointBorderWidth=1] - 点边框宽度
 */
function renderDateIssueChart(data, chartOptions = {}) {
    // 防止重复渲染
    if (isRendering) return;
    isRendering = true;

    // 确保DOM元素存在
    const container = document.getElementById('dateIssueChartContainer');
    const canvas = document.getElementById('dateIssueChart');

    if (!container || !canvas) {
        console.error('Chart elements not found');
        isRendering = false;
        return;
    }

    // 重置容器和画布尺寸
    container.style.height = '350px';
    canvas.width = container.offsetWidth;
    canvas.height = 300;

    const ctx = canvas.getContext('2d');

    try {
        // 如果图表已存在，彻底销毁它
        if (dateIssueChart) {
            dateIssueChart.destroy();
            dateIssueChart = null;
        }

        // 处理数据，按日期和根本原因分组
        const dateGroups = {};
        data.forEach(item => {
            const date = new Date(item['日期']).toLocaleDateString();
            const rootCause = item['根本原因'] || '未分类';

            if (!dateGroups[date]) {
                dateGroups[date] = {};
            }

            dateGroups[date][rootCause] = (dateGroups[date][rootCause] || 0) + 1;
        });

        // 准备图表数据
        const dateLabels = Object.keys(dateGroups);
        const rootCauses = [...new Set(
            data.map(item => item['根本原因'] || '未分类')
        )];

        // 合并默认点大小配置
        const defaultPointOptions = {
            pointRadius: 4,          // 数据点的默认半径
            pointHoverRadius: 6,     // 鼠标悬停时的半径
            pointBorderWidth: 1,     // 点边框宽度
            pointHoverBorderWidth: 2 // 鼠标悬停时的边框宽度
        };

        const mergedPointOptions = {
            ...defaultPointOptions,
            ...chartOptions
        };

        const datasets = rootCauses.map(rootCause => {
            return {
                label: rootCause,
                data: dateLabels.map(date => dateGroups[date][rootCause] || 0),
                backgroundColor: getRootCauseColor(rootCause),
                borderWidth: 1,
                borderSkipped: false,
                // 添加点样式配置
                pointRadius: mergedPointOptions.pointRadius,
                pointHoverRadius: mergedPointOptions.pointHoverRadius,
                pointBorderWidth: mergedPointOptions.pointBorderWidth,
                pointHoverBorderWidth: mergedPointOptions.pointHoverBorderWidth,
                pointBackgroundColor: getRootCauseColor(rootCause),
                pointHoverBackgroundColor: getRootCauseColor(rootCause),
                tension: 0.1 // 稍微平滑线条
            };
        });

        // 动态计算 y 轴的最大值
        let maxYValue = 0;
        datasets.forEach(dataset => {
            dataset.data.forEach(value => {
                if (value > maxYValue) {
                    maxYValue = value;
                }
            });
        });

        // 设置合理的Y轴最大值和步长
        const yMax = Math.max(5, Math.ceil(maxYValue * 1.2));
        const stepSize = Math.max(1, Math.ceil(yMax / 5));

        // 创建图表
        dateIssueChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dateLabels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 0 // 禁用动画，防止渲染过程中尺寸变化
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'right',
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '日期'
                        },
                        stacked: true,
                    },
                    y: {
                        title: {
                            display: true,
                            text: '问题数量'
                        },
                        beginAtZero: true,
                        stacked: true,
                        min: 0,
                        max: yMax,
                        ticks: {
                            stepSize: stepSize,
                            callback: function(value) {
                                return Number.isInteger(value)? value : '';
                            }
                        },
                        reverse: false
                    }
                },
                onClick: function(e, elements) {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const datasetIndex = elements[0].datasetIndex;
                        const date = dateLabels[index];
                        const rootCause = datasets[datasetIndex].label;

                        // 查找对应的数据项
                        const filteredItems = data.filter(item =>
                            new Date(item['日期']).toLocaleDateString() === date &&
                            (item['根本原因'] || '未分类') === rootCause
                        );

                        if (filteredItems.length > 0) {
                            showRootCause(filteredItems[0]);
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error rendering dateIssueChart:', error);
        dateIssueChart = null;
    } finally {
        isRendering = false;
    }
}

/**
 * 为不同的根本原因分配颜色
 */
function getRootCauseColor(rootCause) {
    // 简单的哈希函数将根本原因映射到颜色
    const colors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(255, 205, 86, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(201, 203, 207, 0.7)'
    ];

    let hash = 0;
    for (let i = 0; i < rootCause.length; i++) {
        hash = rootCause.charCodeAt(i) + ((hash << 5) - hash);
    }

    return colors[Math.abs(hash) % colors.length];
}

/**
 * 显示问题的根本原因
 */
function showRootCause(item) {
    const container = document.getElementById('rootCauseContainer');
    const text = document.getElementById('rootCauseText');

    if (!container || !text) {
        console.error('Root cause elements not found');
        return;
    }

    text.textContent = item['根本原因'] || '未提供根本原因';
    container.classList.remove('hidden');

    // 添加动画效果
    container.style.opacity = '0';
    container.style.transform = 'translateY(10px)';
    container.style.transition = 'opacity 0.3s ease, transform 0.3s ease';

    setTimeout(() => {
        container.style.opacity = '1';
        container.style.transform = 'translateY(0)';
    }, 10);
}

/**
 * 清空所有图表
 */
function clearAllCharts() {
    try {
        if (dateIssueChart) dateIssueChart.destroy();
        if (statusChart) statusChart.destroy();
        if (rootCauseChart) rootCauseChart.destroy();
        if (improvementChart) improvementChart.destroy();
    } catch (error) {
        console.error('Error clearing charts:', error);
        // 重置所有图表变量
        dateIssueChart = null;
        statusChart = null;
        rootCauseChart = null;
        improvementChart = null;
    }
}