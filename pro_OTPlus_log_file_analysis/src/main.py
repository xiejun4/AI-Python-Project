import zipfile
import os
import re
from datetime import datetime

def unzip_file(zip_path='D:\\PythonProject\\pro_python\\pro_OTPlus_log_file_analysis\\docs\\5GFR1BdTst_MUMBAI25_POWER_APEM.log_zip',
                extract_path='D:\\PythonProject\\pro_python\\pro_OTPlus_log_file_analysis\\docs'):
    """
    解压指定的 zip 文件到指定目录
    """
    # zip_path = 'D:\\PythonProject\\pro_python\\pro_OTPlus_log_file_analysis\\docs\\5GFR1BdTst_MUMBAI25_POWER_APEM.log_zip'
    # extract_path = 'D:\\PythonProject\\pro_python\\pro_OTPlus_log_file_analysis\\docs'
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"文件 {zip_path} 解压成功到 {extract_path}")
    except Exception as e:
        print(f"解压文件时出错: {e}")

def filter_log_files(directory):
    """
    过滤指定目录中的 .log 文件并返回文件列表

    :param directory: 指定的目录路径
    :return: .log 文件列表
    """
    log_files = []
    try:
        if os.path.isdir(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.log'):
                        log_files.append(os.path.join(root, file))
        return log_files
    except Exception as e:
        print(f"遍历目录时出错: {e}")
        return []

def remove_timestamp2log_level( input_file, output_file):
    # 定义正则表达式：匹配并删除时间戳、日志级别、测试模块及后续时间戳
    # 模式说明：
    # ^ 从行首开始匹配
    # 第一部分：匹配时间戳1（如：2025-01-19 19:41:47,170）-> (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)
    # 第二部分：匹配日志级别（如：[] INFO ）-> \s+\[]\s+
    # 第三部分：匹配测试模块（如：TEST_APP_2010）-> \w+\s+
    # 第四部分：匹配后续时间戳（如：09:33:27.4305803），确保删除到第二个制表符后 -> (\d{2}:\d{2}:\d{2}.\d+)
    # 第五部分：匹配制表符，确保删除到具体内容前的最后一个制表符 -> \t
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+\[]\s+\w+\s+[^\t]+\t(\d{2}:\d{2}:\d{2}.\d+)\t'
    try:
        # 使用utf-8编码并忽略解码错误
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f_in, \
                open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                # 使用正则表达式删除匹配部分，保留剩余内容（从第三个制表符后开始保留）
                processed_line = re.sub(pattern, '', line.strip())
                if processed_line:  # 跳过空行
                    f_out.write(processed_line + '\n')
        return True
    except FileNotFoundError:
        print(f"error：文件未找到。请检查输入文件 '{input_file}' 是否存在。")
    except UnicodeDecodeError:
        print(f"error：在读取文件 '{input_file}' 时出现编码问题。")
        # 尝试使用其他编码
        try:
            with open(input_file, 'r', encoding='gb18030', errors='ignore') as f_in, \
                    open(output_file, 'w', encoding='utf-8') as f_out:
                for line in f_in:
                    processed_line = re.sub(pattern, '', line.strip())
                    if processed_line:
                        f_out.write(processed_line + '\n')
            print("已成功使用gb18030编码处理文件。")
            return True
        except Exception as e:
            print(f"无法使用其他编码处理文件：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")
    return False

def group_log_by_first_column(file_path):
    """
    读取log文件内容，按照第一列的内容对log文件内容分组

    :param file_path: log文件的路径
    :return: 按第一列内容分组的字典，键为第一列内容，值为对应行列表
    """
    log_groups = {}
    try:
        # 使用utf-8编码并忽略解码错误
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    # 按空白字符分割行，获取第一列内容
                    parts = line.split()
                    if parts:
                        first_column = parts[0]
                        if first_column not in log_groups:
                            log_groups[first_column] = []
                        log_groups[first_column].append(line)
        return log_groups
    except FileNotFoundError:
        print(f"error：文件未找到。请检查文件 '{file_path}' 是否存在。")
    except UnicodeDecodeError:
        print(f"error：在读取文件 '{file_path}' 时出现编码问题。")
        # 尝试使用其他编码
        try:
            with open(file_path, 'r', encoding='gb18030', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if parts:
                            first_column = parts[0]
                            if first_column not in log_groups:
                                log_groups[first_column] = []
                            log_groups[first_column].append(line)
            print("已成功使用gb18030编码处理文件。")
            return log_groups
        except Exception as e:
            print(f"无法使用其他编码处理文件：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")
    return log_groups

def filter_failed_groups(grouped_logs):
    """
    过滤出grouped_logs中的分组中包含* FAILED *的分组，然后返回这些分组

    :param grouped_logs: 按第一列内容分组的字典，键为第一列内容，值为对应行列表
    :return: 包含* FAILED *的分组字典
    """
    failed_groups = {}
    for key, lines in grouped_logs.items():
        for line in lines:
            if '* FAILED *' in line:
                failed_groups[key] = lines
                break
    return failed_groups

def generate_failed_groups_to_html(grouped_logs,html_file_path='d:\\PythonProject\\pro_python\\pro_OTPlus_log_file_analysis\\docs\\failed_log_groups.html'):
    """
    过滤并打印出grouped_logs中的分组中包含* FAILED *的分组，同时将结果转成html文件

    :param grouped_logs: 按第一列内容分组的字典，键为第一列内容，值为对应行列表
    """
    failed_groups = filter_failed_groups(grouped_logs)
    for key, lines in failed_groups.items():
        print(f"包含 ' * FAILED * ' 的分组 '{key}':")
        for line in lines[:1]:
            print(line)
        print()

    # 生成 HTML 文件
    html_content = "<html><head><title>Failed Log Groups</title></head><body>"

    for key, lines in failed_groups.items():        
        # import os
        # file_name = os.path.basename(html_file_path)
        # html_content += f"<h4>'{file_name}'</h4>"
        html_content += f"<h4>包含 ' * FAILED * ' 的分组 '{key}'</h4>"
        html_content += "<div style='white-space: pre-wrap;'>"
        
        # 如果lines长度超过100，只过滤包含 * FAILED * 的行
        if len(lines) > 100:
            lines = [line for line in lines if '* FAILED *' in line]

            # 在生成 HTML 时调用该函数处理内容        
            joined_lines = '\n'.join(highlight_details(lines))        

            # 处理 * FAILED * 的内容
            processed_joined = re.sub(r'\* FAILED \*', lambda m: f'<span style="color:red;">{m.group()}</span>', joined_lines)

            # 将 * FAILED * 后面的内容去掉
            processed_joined = re.sub(r'\* FAILED \*.*', '* FAILED *', processed_joined)

            # 处理 * FAILED * 的内容，同时删除其前面的 2 个对象
            processed_joined = re.sub(r'(\S+\s+){2}\* FAILED \*', lambda m: f'<span style="color:red;">* FAILED *</span>', joined_lines)
           
            # 将 * FAILED * 后面的内容去掉
            processed_joined = re.sub(r'\* FAILED \*.*', '* FAILED *', processed_joined)

            # 处理 EvalAndLogResults 后面的 2 项，将删除的内容替换为制表符 \t，保持数据间距
            processed_joined = re.sub(r'EvalAndLogResults\s+\S+\s+\S+', 'EvalAndLogResults\t', processed_joined)

            # 先将 EvalAndLogResult 前后紧挨着的制表符替换成空字符串
            processed_joined = re.sub(r'\tEvalAndLogResults\t', 'EvalAndLogResults', processed_joined)

            # 将 EvalAndLogResults 替换成制表符 \t
            processed_joined = re.sub(r'EvalAndLogResults', '\t', processed_joined)

            # 将内容字体设置为当前的80%
            html_content += f'<div style="font-size: 50%;">{processed_joined}</div>'
            
            
        # 如果lines长度小于100
        elif len(lines) > 0 and len(lines) <= 100 :
            # 处理 ::Start到::End之间的内容高亮
            processed_lines = highlight_start_end_blocks(lines)
            joined_lines = '\n'.join(processed_lines)

            # 处理 details 内容
            joined_lines = '\n'.join(highlight_details(processed_lines))        

            # 先将 EvalAndLogResult 前后紧挨着的制表符替换成空字符串
            joined_lines = re.sub(r'\tEvalAndLogResults\t', 'EvalAndLogResults', joined_lines)
            # 再将 EvalAndLogResults 替换成制表符 \t
            joined_lines = re.sub(r'EvalAndLogResults', '\t', joined_lines)

            # 处理 * FAILED * 的内容
            processed_joined = re.sub(r'\* FAILED \*', lambda m: f'<span style="color:red;">{m.group()}</span>', joined_lines)
            # 将内容字体设置为当前的80%
            html_content += f'<div style="font-size: 50%;">{processed_joined}</div>'

    html_content += "</body></html>"

    try:
        # 确保文件写入到工作区根目录
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"已成功将失败分组日志保存到 {html_file_path} 文件中。")
    except Exception as e:
        print(f"保存 HTML 文件时出错: {e}")

def highlight_start_end_blocks(lines):
    """将::Start和::End之间的内容标记为红色"""
    processed_lines = []
    in_red_block = False
    
    for line in lines:
        # 检查是否包含::Start
        if '::Start' in line:
            in_red_block = True
            processed_lines.append(f'<span style="color:blue;">{line}</span>')
        # 检查是否包含::End
        elif '::End' in line:
            processed_lines.append(f'<span style="color:blue;">{line}</span>')
            in_red_block = False
        # 如果在红色块中
        elif in_red_block:
            processed_lines.append(f'<span style="color:blue;">{line}</span>')
        # 不在红色块中
        else:
            processed_lines.append(line)
    
    return processed_lines

def highlight_details(lines):
    """将包含 'Details' 的行及其下一行内容标记为红色"""
    processed_lines = []
    mark_next_red = False
    for line in lines:
        if 'Details' in line:
            processed_line = f'<span style="color:red;">{line}</span>'
            mark_next_red = True
        elif mark_next_red:
            processed_line = f'<span style="color:red;">{line}</span>'
            mark_next_red = False
        else:
            processed_line = line
        processed_lines.append(processed_line)
    return processed_lines

def remove_temp_files(root):
    """
    删除指定根目录下的临时文件和目录
    会删除 prod 目录、Qualcomm 目录和 [Content_Types].xml 文件

    :param root: 指定的根目录路径
    """
    print("[删除临时文件]")
    import shutil
    temp_path = f'{root}\\temp'
    prod_path = f'{root}\\prod'
    qualcomm_path = f'{root}\\Qualcomm'
    content_types_path = f'{root}\\[Content_Types].xml'

    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    if os.path.exists(prod_path):
        shutil.rmtree(prod_path)
    if os.path.exists(qualcomm_path):
        shutil.rmtree(qualcomm_path)
    if os.path.exists(content_types_path):
        os.remove(content_types_path)

# 以下函数用于汇总所有 HTML 文件内容到一个新的 HTML 文件中
def aggregate_html_files(docs_dir):

    """
    汇总指定目录下的所有 .html 文件内容到一个新的 HTML 文件中

    :param docs_dir: 指定目录路径
    """
    html_files = []
    # 收集指定目录下的所有 .html 文件，并过滤掉文件名包含 aggregated_failed_logs_ 的文件
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.html') and 'aggregated_failed_logs_' not in file:
                html_files.append(os.path.join(root, file))
    
    # 根据文件名中的Failed之后的内容对文件进行排序
    html_files.sort(key=lambda x: os.path.basename(x).split('Failed')[-1])
    
    if not html_files:
        print("未找到 HTML 文件可汇总。")
        return

    # 初始化汇总 HTML 文件内容
    aggregated_content = "<html><head><title>汇总失败日志</title></head><body>"
    # 添加索引目录
    aggregated_content += '<div id="index" style="position: fixed; left: 10px; top: 10px; width: 250px; margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; background: white; max-height: 90vh; overflow-y: auto; font-size: 50%; transition: all 0.3s ease;"><span id="toggleBtn" style="cursor: pointer; font-size: 1.2em; vertical-align: middle;">▼</span> <h3 style="display: inline-block; margin-left: 10px;">索引目录</h3><ul id="indexContent">'
    index_items = []
    file_contents = []  # 存储文件内容

    # 逐个读取 HTML 文件内容并添加到汇总内容中
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # 提取文件名作为标题
                file_name = os.path.basename(html_file)
                # 生成唯一id，替换特殊字符
                file_id = "file_" + re.sub(r'\W+', '_', file_name)
                index_items.append(f'<li><a href="#{file_id}">{file_name}</a></li>')
                file_contents.append(f"<h4 id='{file_id}'>文件来源: {file_name}</h4>")
                file_contents.append(content)
        except Exception as e:
            print(f"读取文件 {html_file} 时出错: {e}")

    # 添加索引目录项
    aggregated_content += ''.join(index_items)
    aggregated_content += '</ul></div>'  # 关闭目录的ul和div
    aggregated_content += "<div id='contentArea' style='margin-left: 280px; transition: margin-left 0.3s ease;'><h3>汇总的失败日志文件</h3>"
    
    # 添加所有文件内容
    aggregated_content += ''.join(file_contents)
    aggregated_content += '</div>'
    aggregated_content += """<script>
        function toggleIndex() {
            const indexDiv = document.getElementById('index');
            const indexContent = document.getElementById('indexContent');
            const toggleBtn = document.getElementById('toggleBtn');
            const h3 = indexDiv.querySelector('h3');
            const contentArea = document.getElementById('contentArea');
            const computedStyle = window.getComputedStyle(indexDiv);
            if (computedStyle.width === '25px') {
                indexDiv.style.width = '250px';
                indexDiv.style.background = 'white';
                indexContent.style.display = 'block';
                h3.style.display = 'inline-block';
                toggleBtn.textContent = '▼';
                toggleBtn.style.color = 'blue';
                contentArea.style.marginLeft = '280px';
            } else {
                indexDiv.style.width = '25px';
                indexDiv.style.background = 'red';
                indexContent.style.display = 'none';
                h3.style.display = 'none';
                toggleBtn.textContent = '▶';
                toggleBtn.style.color = 'white';
                contentArea.style.marginLeft = '50px';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const toggleBtn = document.getElementById('toggleBtn');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', toggleIndex);
            } else {
                console.error('Toggle button not found');
            }
        });</script>"""


    # 保存汇总后的 HTML 文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    aggregated_file_path = os.path.join(docs_dir, f'aggregated_failed_logs_{timestamp}.html')
    try:
        with open(aggregated_file_path, 'w', encoding='utf-8') as f:
            f.write(aggregated_content)
        print(f"已成功将所有 HTML 文件汇总到 {aggregated_file_path}")
    except Exception as e:
        print(f"保存汇总 HTML 文件时出错: {e}")






# 在主程序中调用新函数
if __name__ == "__main__":

    docs_dir = 'D:\\ProgramData\\projects\\pro_python\\pro_OTPlus_log_file_analysis\\docs'
    # 遍历指定目录下的文件，过滤出异常的log，然后将其转成html
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.log_zip'):                
                # 解压文件
                print("[开始解压文件]")
                zip_path = os.path.join(root, file)
                file_name = file.split('.')[0]
                extract_path = root
                unzip_file(zip_path,extract_path)
                
                # 过滤日志文件
                print("[过滤日志文件]")
                directory = f'{root}\\prod\\log'
                log_files = filter_log_files(directory=directory)
                print(log_files)

                # 过滤掉包含 "_startup" 的 log 文件
                log_files = [file for file in log_files if '_startup' not in file]
                print("过滤后的日志文件列表:", log_files)

                # 移除时间戳等无效数据列
                print("[移除时间戳等无效数据列]")
                remove_timestamp2log_level(log_files[0],output_file=f'{root}\\prod\\log\\{file_name}.log')

                # 分组日志
                print("[分组日志]")
                log_file_path = f'{root}\\prod\\log\\{file_name}.log'
                grouped_logs = group_log_by_first_column(log_file_path)

                # 将包含异常分组日志转成HTML文本
                print("[将包含异常分组日志转成HTML文本]")
                generate_failed_groups_to_html(grouped_logs,html_file_path=f'{root}\\{file_name}_failed_log.html')

            # 在主程序中调用该函数
            remove_temp_files(root)

    # # 汇总所有 HTML 文件
    # aggregate_html_files(docs_dir)