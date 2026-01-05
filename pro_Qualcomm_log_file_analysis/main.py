import re
import logging
from datetime import datetime

# 定义日志文件路径常量
CONSOLE_APP_LOG_PATH = 'D:\PythonProject\pro_python\pro_Qualcomm_log_file_analysis\docs\ConsoleApp.txt'
EQUIP_LOG_PATH = 'D:\PythonProject\pro_python\pro_Qualcomm_log_file_analysis\docs\EQUIP.txt'
EQUIP_LOG_OUTPUT_PATH = 'D:\PythonProject\pro_python\pro_Qualcomm_log_file_analysis\docs\EQUIP_formatted.txt'

class LogAnalyzer:
    def __init__(self):
        self.console_log_data = []
        self.equip_log_data = []
        self.matched_results = []
        self.format_equip_log_data=[]

    def read_log_file(self, file_path):
        """读取日志文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.readlines()
        except FileNotFoundError:
            print(f"错误：文件 {file_path} 未找到")
            return []
        except Exception as e:
            print(f"读取文件 {file_path} 时发生错误: {e}")
            return []

    def parse_timestamp(self, timestamp_str):
        """解析并标准化时间戳"""
        try:
            # 这里假设时间戳格式为 'YYYY-MM-DD HH:MM:SS'，可根据实际情况修改
            return datetime.strptime(timestamp_str.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"无法解析时间戳: {timestamp_str}")
            return None

    def build_data_structure(self, log_lines, is_console_log=True):
        """构建日志数据结构"""
        data = []
        # 解析带时间戳和日志级别的系统日志（如 [INFO], [DEBUG]）
        pattern = re.compile(r'^(\d+:\d+:\d+:\d+)\t+\[(INFO|DEBUG|ERROR|WARN)\]\s+(.*)$')
        
        for line_num, line in enumerate(log_lines, 1):
            stripped_line = line.strip()
            match = pattern.match(stripped_line)
            if match:
                timestamp_str = match.group(1)
                content = f'[{match.group(2)}],{match.group(3)}' 
                entry = {
                    'timestamp': timestamp_str,
                    'content': content,
                    'type': 'EQUIP',
                    'line_number': line_num
                }
                data.append(entry)
            else:
                logging.warning(f"无法解析日志行 {line_num}: {stripped_line[:100]}...")
        return data

    def classify_command_type(self, content):
        """根据指令内容分类指令类型"""
        if not content: return '未知指令'
        
        # 带引号的设备响应数据
        if content.startswith('"') and content.endswith('"'):
            return '设备响应数据'
        
        # 系统基础指令
        if content.startswith(':SYST:'):
            if 'BASE' in content: return '系统基础配置'
            if 'ERR' in content: return '系统错误查询'
            return '系统指令'
        
        # 路由配置指令
        if content.startswith(':ROUT:'):
            return '路由配置指令'
        
        # 信号源配置指令
        if content.startswith(':SOUR:'):
            if 'SEQ' in content: return '序列生成指令'
            if 'RFS' in content: return '射频配置指令'
            return '信号源控制'
        
        # 配置指令
        if content.startswith(':CONF:'):
            if 'LTE:MEAS' in content: return 'LTE测量配置'
            return '系统配置指令'
        
        # 查询指令
        if '?' in content: return '查询指令'
        
        # 操作完成指令
        if content.startswith('*OPC?'): return '操作完成查询'
        
        # 默认返回基础类型
        return '通用指令'

    def build_data_structure2(self, log_lines, is_console_log=True):
        """构建日志数据结构，支持操作标记(---WRITE---/---READ---)和时间戳关联"""
        data = []
        current_operation = None  # 记录当前操作类型(WRITE/READ)
        last_timestamp = None     # 记录最后出现的时间戳，用于无时间戳命令关联
        current_block = None      # 跟踪当前操作块
        
        # 增强正则表达式：精确匹配时间戳后的制表符，支持带引号内容
        pattern = re.compile(r'^---(WRITE|READ)---$|^(\d+:\d+:\d+:\d+)	+(.*)$|^(.*)$')
        
        for line_num, line in enumerate(log_lines, 1):
            stripped_line = line.strip()
            if not stripped_line:  # 跳过空行
                continue
            
            match = pattern.match(stripped_line)
            if match:
                # 情况1: 匹配操作标记行(---WRITE---/---READ---)
                if match.group(1):
                    # 如果有当前块，完成并添加到数据
                    if current_block:
                        data.append(current_block)
                        current_block = None
                    
                    # 开始新块
                    operation_type = match.group(1)
                    current_operation = operation_type  # 更新当前操作类型
                    current_block = {
                        'type': 'OperationBlock',
                        'operation_type': operation_type,
                        'timestamp': None,
                        'content': '',
                        'start_line': line_num,
                        'end_line': line_num,
                        'line_number': line_num,
                        'command_type': None
                    }
                # 情况2: 匹配带时间戳命令
                elif match.group(2):
                    timestamp_str = match.group(2)
                    content = match.group(3)
                    last_timestamp = timestamp_str  # 更新最后时间戳
                    
                    if current_block:
                        # 添加到当前块
                        current_block['timestamp'] = timestamp_str
                        current_block['associated_timestamp'] = timestamp_str
                        current_block['content'] = content
                        current_block['end_line'] = line_num
                        current_block['command_type'] = self.classify_command_type(content)
                    else:
                        # 创建单独条目
                        entry = {
                            'timestamp': timestamp_str,
                            'content': content,
                            'operation_type': current_operation,
                            'associated_timestamp': timestamp_str,
                            'type': 'ConsoleApp' if is_console_log else 'EQUIP',
                            'line_number': line_num,
                            'command_type': self.classify_command_type(content)
                        }
                        data.append(entry)
                # 情况3: 匹配无时间戳命令
                elif match.group(4):
                    content = match.group(4)
                    
                    if current_block and current_block['timestamp']:
                        # 添加到当前块的内容
                        if current_block['content']:
                            current_block['content'] += '\n' + content
                        else:
                            current_block['content'] = content
                        current_block['end_line'] = line_num
                    else:
                        # 创建单独条目
                        entry = {
                            'timestamp': None,
                            'content': content,
                            'operation_type': current_operation,
                            'associated_timestamp': last_timestamp,  # 关联最近时间戳
                            'type': 'ConsoleApp' if is_console_log else 'EQUIP',
                            'line_number': line_num,
                            'command_type': self.classify_command_type(content)  # 自动分类指令类型
                        }
                        data.append(entry)
            else:
                logging.warning(f"无法解析日志行 {line_num}: {stripped_line[:100]}...")
        
        # 完成任何剩余的块
        if current_block:
            data.append(current_block)
            
        return data

    def match_timestamps(self):
        """匹配两个日志文件中的时间戳"""
        # 简单示例：按时间戳排序后进行线性匹配，可根据实际需求优化
        self.console_log_data.sort(key=lambda x: x['timestamp'])
        self.equip_log_data.sort(key=lambda x: x['timestamp'])
        
        i = j = 0
        while i < len(self.console_log_data) and j < len(self.equip_log_data):
            console_time = self.console_log_data[i]['timestamp']
            equip_time = self.equip_log_data[j]['timestamp']
            
            if console_time == equip_time:
                self.matched_results.append((self.console_log_data[i], self.equip_log_data[j]))
                i += 1
                j += 1
            elif console_time < equip_time:
                i += 1
            else:
                j += 1

    def match_timestamps2(self):
        """匹配两个日志文件中的时间戳"""
        # 简单示例：按时间戳排序后进行线性匹配，可根据实际需求优化
        self.console_log_data.sort(key=lambda x: x['timestamp'])
        self.format_equip_log_data.sort(key=lambda x: x['timestamp'])
        
        i = j = 0
        while i < len(self.console_log_data) and j < len(self.format_equip_log_data):
            console_time = self.console_log_data[i]['timestamp']
            equip_time = self.format_equip_log_data[j]['timestamp']
            
            # 若格式化设备日志条目的内容长度超过100，插入换行符
            if len(self.format_equip_log_data[j]['content']) > 100:
                content = self.format_equip_log_data[j]['content']
                self.format_equip_log_data[j]['content'] = content[:100] + '\n' + content[100:]


            if console_time == equip_time:

                # 计算格式化设备日志条目中内容的换行符数量
                newline_count = self.format_equip_log_data[j]['content'].count('\n')                
                # print(f"{j},{self.format_equip_log_data[j]['content']}->{newline_count}")
                
                # 给控制台日志条目内容添加相同数量的换行符
                self.console_log_data[i]['content'] += '\n' * (newline_count + 1)                
                # print(f"{i},{self.console_log_data[i]['content']}->{newline_count}")

                self.matched_results.append((self.console_log_data[i], self.format_equip_log_data[j]))
                i += 1
                j += 1
            elif console_time < equip_time:
                i += 1
            else:
                j += 1                

    def detect_anomalies(self):
        """异常检测与报告"""
        anomalies = []
        # 简单示例：检测空内容的日志条目
        for log in self.console_log_data + self.equip_log_data:
            if not log['content'].strip():
                anomalies.append({
                    'timestamp': log['timestamp'],
                    'type': log['type'],
                    'message': '空内容日志条目'
                })
        return anomalies

    def output_results2(self):
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>diff_modelfile_txt_result</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                }
                .container {
                    display: flex;
                    width: 100%;
                    height: 100vh;
                    overflow: hidden;
                    margin-top: 50px;
                }
                .pane {
                    width: 50%;
                    height: 100%;
                    overflow: auto;
                    border: 1px solid #ccc;
                }
                .pane1 {
                    background: #f0f0f0;
                }
                .pane2 {
                    background: #e0e0e0;
                }
                .content {
                    width: 2000px;
                    height: 2000px;
                }
                .diff_next { background-color: #c0c0c0; }
                .diff_add { background-color: #aaffaa; }
                .diff_chg { background-color: #ffff77; }
                .diff_sub { background-color: #ffaaaa; }
                .toolbar { position: fixed; top: 0; left: 0; right: 0; background: #f5f5f5; padding: 10px; border-bottom: 1px solid #ccc; display: flex; justify-content: center; gap: 10px; z-index: 100; transition: all 0.3s ease; } .toolbar.collapsed { height: 2px; padding: 0; background: #ff0000; border-bottom: none; } .toolbar-btn { padding: 8px 16px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; background: #fff; } .toolbar.collapsed .toolbar-btn { display: none; } .collapse-btn { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #333; cursor: pointer; font-size: 16px; } .toolbar.collapsed .collapse-btn { color: #ff0000; top: 0; transform: none; }
                .toolbar-btn { padding: 8px 16px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; background: #fff; }
                .toolbar-btn.active { background: #007bff; color: white; border-color: #007bff; } .log-row { cursor: pointer; } .log-row.selected { background-color: #7CCC63; border-left: 3px solid #007bff; } .pagination { text-align: center; padding: 10px; background: #f5f5f5; border-top: 1px solid #ccc; } .pagination button { margin: 0 5px; padding: 5px 10px; cursor: pointer; } .pagination span { margin: 0 10px; }
                
                br { content: '\A'; white-space: pre-line; display: block; height: 1.5em; margin-bottom: 1em; }
                tr { min-height: 60px; vertical-align: top; }
                td { padding: 4px 8px; line-height: 1.8; min-height: 60px; overflow-y: auto; box-sizing: border-box; font-size: 12px; }
                table.diff { width: 100%; table-layout: fixed; }
                td:first-child { width: 150px; white-space: normal; overflow: visible; text-overflow: clip; padding-right: 8px; }
                .pane1 td:last-child { width: calc(100% - 150px); white-space: pre-wrap; word-wrap: break-word; line-height: 2.0; min-height: 40px; } .pane2 td:last-child { width: calc(100% - 150px); white-space: nowrap; line-height: 2.0; min-height: 40px; }
            </style>
        </head>
        <body>
            <div class="toolbar"> <button class="collapse-btn">▲</button>
                <button id="syncScrollBtn" class="toolbar-btn active">两边内容同时滚动</button>
                <button id="independentScrollBtn" class="toolbar-btn">两边内容各自滚动</button>
                <div class="pagination-controls">
                    <button id="prevPage" title="上一页">上一页</button>
                    <span id="pageInfo"></span>
                    <button id="nextPage" title="下一页">下一页</button>
                    <button id="showAllBtn" title="显示全部内容">显示全部</button>
                </div>
                <style>
                    .pagination-controls {
                        display: inline-block;
                        margin-left: 15px;
                        padding: 5px;
                    }
                    .pagination-controls button {
                        margin: 0 5px;
                        padding: 3px 8px;
                        font-size: 12px;
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        cursor: pointer;
                    }
                    .pagination-controls button:disabled {
                        opacity: 0.5;
                        cursor: not-allowed;
                    }
                    .pagination-controls span {
                        margin: 0 5px;
                        color: #333;
                        font-size: 12px;
                    }
                </style>
            </div>
            <div class="container">
                <div class="pane pane1" id="pane1">
                    <div class="content">
                        <table class="diff" id="oldFileTable" cellspacing="0" cellpadding="0" rules="groups">
                            <tbody>
        """
        for loop_index, (console_entry, equip_entry) in enumerate(self.matched_results):
            html_content += f"""
                                <tr class='log-row' data-index="{loop_index}" data-page="{loop_index // 200}">
                                    <td>{console_entry['timestamp']}</td>
                                    <td>{console_entry['content'].replace('\n', '<br>')}</td>
                                </tr>
            """
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="pane pane2" id="pane2">
                    <div class="content">
                        <table class="diff" id="newFileTable" cellspacing="0" cellpadding="0" rules="groups">
                            <tbody>
        """
        for loop_index, (console_entry, equip_entry) in enumerate(self.matched_results):
            html_content += f"""
                                <tr class='log-row' data-index="{loop_index}" data-page="{loop_index // 200}">
                                    <td>{equip_entry['timestamp']}</td>
                                    <td>{equip_entry['operation_type']} -> {equip_entry['content'].replace('\n', '<br>')}</td>
                                </tr>
            """
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <script>
                const pane1 = document.getElementById('pane1');
                const pane2 = document.getElementById('pane2');

                function syncScroll(e) {
                    if (!scrollSyncEnabled) return;
                    const target = e.target;
                    if (target === pane1) {
                        pane2.scrollLeft = pane1.scrollLeft;
                        pane2.scrollTop = pane1.scrollTop;
                    } else if (target === pane2) {
                        pane1.scrollLeft = pane2.scrollLeft;
                        pane1.scrollTop = pane2.scrollTop;
                    }
                }

                // 滚动同步控制变量
                let scrollSyncEnabled = true;

                pane1.addEventListener('scroll', syncScroll);
                pane2.addEventListener('scroll', syncScroll);

                // 修复行选择同步功能
                function setupRowSelectionSync() {
                    const rows = document.querySelectorAll('.log-row');
                    if (rows.length === 0) {
                        // 如果当前没有行，延迟后重试
                        setTimeout(setupRowSelectionSync, 100);
                        return;
                    }

                    rows.forEach(row => {
                        // 先移除可能存在的旧事件监听器
                        row.removeEventListener('click', handleRowClick);
                        // 添加新的事件监听器
                        row.addEventListener('click', handleRowClick);
                    });
                }

                function handleRowClick() {
                    if (scrollSyncEnabled) {
                        const index = this.getAttribute('data-index');
                        if (!index) return;

                        // 清除所有选中状态
                        document.querySelectorAll('.log-row.selected').forEach(r => {
                            r.classList.remove('selected');
                        });

                        // 选中当前行及对应行
                        const correspondingRows = document.querySelectorAll(`.log-row[data-index='${index}']`);
                        if (correspondingRows.length < 2) {
                            console.warn(`未找到对应行: index=${index}`);
                        }
                        correspondingRows.forEach(r => {
                            r.classList.add('selected');
                        });
                    }
                }

                // 初始化行选择同步
                setupRowSelectionSync();

                // 工具栏折叠/展开功能
                const toolbar = document.querySelector('.toolbar');
                const collapseBtn = document.querySelector('.collapse-btn');
                const container = document.querySelector('.container');

                collapseBtn.addEventListener('click', function() {
                    toolbar.classList.toggle('collapsed');
                    if (toolbar.classList.contains('collapsed')) {
                        collapseBtn.textContent = '▼';
                        container.style.marginTop = '5px';
                    } else {
                        collapseBtn.textContent = '▲';
                        container.style.marginTop = '50px';
                    }
                });

                // 工具栏按钮事件
                document.getElementById('syncScrollBtn').addEventListener('click', function() {
                    scrollSyncEnabled = true;
                    this.classList.add('active');
                    document.getElementById('independentScrollBtn').classList.remove('active');
                });

                document.getElementById('independentScrollBtn').addEventListener('click', function() {
                    scrollSyncEnabled = false;
                    this.classList.add('active');
                    document.getElementById('syncScrollBtn').classList.remove('active');
                });

                // 分页功能
                // 确保DOM加载完成后初始化分页
                  document.addEventListener('DOMContentLoaded', function() {
                      const itemsPerPage = 200;
                      let currentPage = 0;
                      const totalItems = document.querySelectorAll('.log-row').length;
                      const totalPages = Math.ceil(totalItems / itemsPerPage);

                    function showPage(page) {
                        document.querySelectorAll('.log-row').forEach(row => {
                            const rowPage = parseInt(row.getAttribute('data-page'));
                            row.style.display = rowPage === page ? '' : 'none';
                        });
                        document.getElementById('pageInfo').textContent = `第 ${page + 1} 页 / 共 ${totalPages} 页`;
                        document.getElementById('prevPage').disabled = page === 0;
                        document.getElementById('nextPage').disabled = page >= totalPages - 1;
                    }

                    document.getElementById('prevPage').addEventListener('click', () => {
                        if (currentPage > 0) {
                            currentPage--;
                            showPage(currentPage);
                        }
                    });

                    document.getElementById('nextPage').addEventListener('click', () => {
                        if (currentPage < totalPages - 1) {
                            currentPage++;
                            showPage(currentPage);
                        }
                    });

                    // 初始显示第一页
                    showPage(currentPage);
                });
                const totalPages = Math.ceil(totalItems / itemsPerPage);

                function showPage(page) {
                    document.querySelectorAll('.log-row').forEach(row => {
                        const rowPage = parseInt(row.getAttribute('data-page'));
                        row.style.display = rowPage === page ? '' : 'none';
                    });
                    document.getElementById('pageInfo').textContent = `第 ${page + 1} 页 / 共 ${totalPages} 页`;
                    document.getElementById('prevPage').disabled = page === 0;
                    document.getElementById('nextPage').disabled = page >= totalPages - 1;
                }

                document.getElementById('prevPage').addEventListener('click', () => {
                    if (currentPage > 0) {
                        currentPage--;
                        showPage(currentPage);
                    }
                });

                document.getElementById('nextPage').addEventListener('click', () => {
                    if (currentPage < totalPages - 1) {
                        currentPage++;
                        showPage(currentPage);
                    }
                });

                // 显示全部内容功能
                document.getElementById('showAllBtn').addEventListener('click', () => {
                    try {
                        // 显示全部日志内容（同时处理左右两个面板）
                        document.querySelectorAll('#oldFileTable .log-row, #newFileTable .log-row').forEach(row => {
                            row.style.display = 'table-row';
                        });
                        // 更新状态文本
                        document.getElementById('pageInfo').textContent = '显示全部内容';
                        // 隐藏分页控件
                        document.getElementById('prevPage').style.display = 'none';
                        document.getElementById('nextPage').style.display = 'none';
                        document.getElementById('showAllBtn').style.display = 'none';
                        // 重置滚动位置到顶部
                        const container = document.querySelector('.container');
                        if (container) container.scrollTop = 0;
                    } catch (error) {
                        console.error('显示全部内容时出错:', error);
                    }
                });

                // 初始显示第一页
                showPage(currentPage);
            </script>

        </body>
        </html>
        """
        
        # 将HTML内容写入文件
        try:
            with open('.\pro_Qualcomm_log_file_analysis\docs\log_analysis_results2.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("结果已输出到 log_analysis_results2.html")
        except Exception as e:
            print(f"写入文件时出错: {e}")        

    def output_results(self):
        """结果输出与展示"""
        # 构建HTML内容
        html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日志分析结果</title>
    <style>
        /* 设置页面主体的字体和外边距 */
        body {
            font-family: Arial, sans-serif;  /* 使用Arial字体，若不可用则使用无衬线字体 */
            margin: 20px;  /* 页面主体四周设置20px的外边距 */
        }
        /* 定义容器样式，用于布局日志展示区域 */
        .container {
    display: flex;  /* 使用弹性布局 */
    gap: 20px;  /* 设置子元素之间的间距为20px */
    align-items: stretch; /* 强制子元素等高 */
    margin-top: 50px; /* 添加顶部边距防止被工具栏遮挡 */
}
        /* 定义容器中第一个列的样式，通常用于展示ConsoleApp日志 */
        .container .column:nth-child(1) {
            width: 800px;  /* 设置列的宽度为1250px */
            min-width: 800px;  /* 设置列的最小宽度为1250px */
            border: 1px solid #ccc;  /* 设置1px宽的灰色边框 */
            padding: 10px;  /* 设置内边距为10px */
            border-radius: 5px;  /* 设置圆角边框，半径为5px */
            background-color: #e8f5e9; /* 淡淡的草绿 */      
            white-space: nowrap !important; /* 防止自动换行 */
            word-wrap: normal !important;  /* 恢复默认的单词换行行为 */          
            overflow-x: auto;  /* 当内容超出宽度时显示水平滚动条 */
        }      
        /* 定义容器中第二个列的样式，通常用于展示EQUIP日志 */
        .column:nth-child(2) {
            width: 1250px !important;  /* 设置列的宽度为1250px */
            min-width: 1250px !important;  /* 设置列的最小宽度为1250px */
            border: 1px solid #ccc;  /* 设置1px宽的灰色边框 */
            padding: 10px;  /* 设置内边距为10px */
            border-radius: 5px;  /* 设置圆角边框，半径为5px */
            background-color: #ffebee; /* 淡淡的红色 */
            white-space: nowrap !important; /* 防止自动换行 */
            word-wrap: normal !important;  /* 恢复默认的单词换行行为 */
            overflow-x: auto;  /* 当内容超出宽度时显示水平滚动条 */
        }
        /* 定义匹配日志条目的样式 */
        .matched-item {
            margin-bottom: 10px;  /* 设置底部外边距为10px */
            padding-bottom: 10px;  /* 设置底部内边距为10px */
            border-bottom: 1px dashed #ccc;  /* 设置底部虚线边框 */
        }     
        /* 定义异常信息的样式 */
        .anomaly {
            color: red;  /* 设置文字颜色为红色 */
            margin-top: 20px;  /* 设置顶部外边距为20px */
        }        
        /* 定义二级标题的样式 */
        h2 {
            color: #333;  /* 设置文字颜色为深灰色 */
        }
    </style>
</head>
<body>
    <h1>匹配的日志条目</h1>
    <div class="container">
        <div class="column">
            <h2>ConsoleApp</h2>
"""
        for console_entry, equip_entry in self.matched_results:
            html_content += f"""
            <div class="matched-item">
                <strong>{console_entry['timestamp']}</strong><br>
                {console_entry['content'].replace('\n', '<br>')}
            </div>
"""
        html_content += """
        </div>

        <div class="column">
            <h2>EQUIP</h2>
"""
        for console_entry, equip_entry in self.matched_results:
            html_content += f"""
            <div class="matched-item">
                <strong>{equip_entry['timestamp']}</strong><br>
                {equip_entry['operation_type']} -> {equip_entry['content'].replace('\n', '<br>')}
            </div>
"""
        html_content += """
        </div>        

    </div>
"""
        anomalies = self.detect_anomalies()
        if anomalies:
            html_content += """
    <div class="anomaly">
        <h2>检测到的异常</h2>
"""
            for anomaly in anomalies:
                html_content += f"""
        <p>{anomaly['type']} [{anomaly['timestamp']}]: {anomaly['message']}</p>
"""
            html_content += """
    </div>
"""
        else:
            html_content += """
    <div class="anomaly">
        <p>未检测到异常</p>
    </div>
"""
        html_content += """
</body>
</html>
"""

    # 将HTML内容写入文件
    try:
        with open('.\pro_Qualcomm_log_file_analysis\docs\log_analysis_results.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("结果已输出到 log_analysis_results.html")
    except Exception as e:
        print(f"写入文件时出错: {e}")


    def format_equip_log_content(self, input_file_path, output_file_path):
        """格式化EQUIP日志文件内容并将结果写入新文件
        
        Args:
            input_file_path (str): 输入的EQUIP日志文件路径
            output_file_path (str): 输出的格式化结果文件路径
            
        Returns:
            list: 格式化后的日志条目，每个条目包含指令类型、时间戳和指令内容
        """
        try:
            # 打开输入文件
            with open(input_file_path, 'r', encoding='utf-8') as infile:
                log_lines = infile.readlines()

            formatted_entries = []
            current_operation = None
            current_timestamp = None
            content_parts = []

            for line in log_lines:
                stripped_line = line.strip()
                if not stripped_line:  # 跳过空行
                    continue

                # 检查是否为操作标记行
                if stripped_line.startswith('---') and stripped_line.endswith('---'):
                    # 如果有当前操作块，完成并添加到结果
                    if current_operation and (current_timestamp or content_parts):
                        entry = {
                            'operation_type': current_operation,
                            'timestamp': current_timestamp,
                            'content': '\n'.join(content_parts)
                        }
                        formatted_entries.append(entry)
                        content_parts = []

                    current_operation = stripped_line.strip('-')
                    current_timestamp = None
                # 检查是否为带时间戳的行
                elif re.match(r'^\d+:\d+:\d+:\d+\s+', stripped_line):
                    parts = stripped_line.split(maxsplit=1)
                    if len(parts) >= 2:
                        current_timestamp = parts[0]
                        content_parts.append(parts[1])
                    else:
                        current_timestamp = parts[0]
                # 普通内容行
                else:
                    content_parts.append(stripped_line)

            # 添加最后一个操作块
            if current_operation and (current_timestamp or content_parts):
                entry = {
                    'operation_type': current_operation,
                    'timestamp': current_timestamp,
                    'content': '\n'.join(content_parts)
                }
                formatted_entries.append(entry)

            # 将格式化结果写入输出文件
            try:
                with open(output_file_path, 'w', encoding='utf-8') as outfile:
                    for entry in formatted_entries:
                        outfile.write(f"操作类型: {entry['operation_type']}\n")
                        outfile.write(f"时间戳: {entry['timestamp']}\n")
                        outfile.write(f"内容:\n{entry['content']}\n")
                        outfile.write("-" * 40 + "\n")
            except Exception as e:
                print(f"写入输出文件时出错: {e}")

            return formatted_entries
        except Exception as e:
            print(f"读取输入文件时出错: {e}")
            return []

    def run(self):
        """主运行方法"""

        # 格式化EQUIP日志文件
        self.format_equip_log_data = self.format_equip_log_content(EQUIP_LOG_PATH, EQUIP_LOG_OUTPUT_PATH)   

        # 读取日志文件
        console_lines = self.read_log_file(CONSOLE_APP_LOG_PATH)
        # equip_lines = self.read_log_file(EQUIP_LOG_PATH)
        
        # 构建数据结构
        self.console_log_data = self.build_data_structure(console_lines, is_console_log=True)
        # self.equip_log_data = self.build_data_structure2(equip_lines, is_console_log=False)
        
        # 时间戳匹配
        self.match_timestamps2()
        
        # 输出结果
        # self.output_results()
        self.output_results2()





if __name__ == "__main__":
    analyzer = LogAnalyzer()
    analyzer.run()
