#!/usr/bin/env python
# -*- coding: utf-8 -*-"""
# 项目入口文件

import sys
import platform
import os
import time
import requests
import json
import re
import datetime
import base64
import threading
from xml.sax.saxutils import escape
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from http.server import HTTPServer, SimpleHTTPRequestHandler


def print_environment_info():
    """打印当前Python环境信息"""
    print("=     当前Python环境信息     =")
    print("=     Python版本: ", sys.version)
    print("=     操作系统: ", platform.system(), platform.release())
    print("=     工作目录: ", os.getcwd())
    print("=     环境变量: ", os.environ)
    print("=     命令行参数: ", sys.argv)
    print("=     当前时间: ", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=     当前日期: ", time.strftime("%Y-%m-%d"))
    print("=     当前时间: ", time.strftime("%H:%M:%S"))
    print("=     当前时间: ", time.strftime("%H:%M:%S"))
    print("=     当前时间: ", time.strftime("%H:%M:%S"))

def main():
    """程序入口函数"""
    print_environment_info()

def generate_xml():
    # 我准备读取 'Audio (AR&ACT)' 工作表中的内容，然后按照 XML 格式的规范将其转换并输出。
    import pandas as pd

    # 读取 Excel 文件
    excel_file = pd.ExcelFile('./docs/Lenovo_Test_Item_Principle_And_Impact_v0.1.xlsx')

    # 获取指定工作表中的数据
    df = excel_file.parse('Audio(AR&ACT)')

    # 查看数据的基本信息
    print('数据基本信息：')
    df.info()

    # 重新设置列名
    df.columns = ['11.0  Audio Common Test Item', 'Test Group', 'Spectial test items', 'Test detail information', 'Dependency', 'Principle', 'Impact', 'Risk', 'Owner']

    # 从第2行(index=1)开始加载数据
    df = df[1:]

    # 重置索引
    df = df.reset_index(drop=True)
    
    # 处理合并单元格，向前填充空值
    merge_columns = ['Test Group', 'Test detail information', 'Dependency', 'Principle', 'Impact']
    df[merge_columns] = df[merge_columns].ffill()
    
    # 查看数据的基本信息
    print('数据基本信息：')
    df.info()

    # 查看数据集行数和列数
    rows, columns = df.shape

    if rows < 100 and columns < 20:
        # 短表数据（行数少于100且列数少于20）查看全量数据信息
        print('数据全部内容信息：')
        print(df.to_csv(sep='\t', na_rep='nan'))
    else:
        # 长表数据查看数据前几行信息
        print('数据前几行内容信息：')
        print(df.head().to_csv(sep='\t', na_rep='nan'))

    # 接下来，我会将这些数据转换为 XML 格式并保存到文件中。
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    # 创建根节点
    root = ET.Element('AudioCommonTestItems')

    # 遍历 DataFrame 的每一行
    for index, row in df.iterrows():
        test_item = ET.SubElement(root, 'TestItem')
        
        ET.SubElement(test_item, 'TestGroup').text = str(row['Test Group']) if pd.notnull(row['Test Group']) else ''
        ET.SubElement(test_item, 'SpecialTestItems').text = str(row['Spectial test items']) if pd.notnull(row['Spectial test items']) else ''
        ET.SubElement(test_item, 'TestDetailInformation').text = str(row['Test detail information']) if pd.notnull(row['Test detail information']) else ''
        ET.SubElement(test_item, 'Dependency').text = str(row['Dependency']) if pd.notnull(row['Dependency']) else ''
        ET.SubElement(test_item, 'Principle').text = str(row['Principle']) if pd.notnull(row['Principle']) else ''
        ET.SubElement(test_item, 'Impact').text = str(row['Impact']) if pd.notnull(row['Impact']) else ''
        ET.SubElement(test_item, 'Risk').text = str(row['Risk']) if pd.notnull(row['Risk']) else ''
        ET.SubElement(test_item, 'Owner').text = str(row['Owner']) if pd.notnull(row['Owner']) else ''

    # 将 XML 树转换为字符串并进行美化
    xml_str = ET.tostring(root, encoding='utf-8')
    parsed = minidom.parseString(xml_str)
    pretty_xml = parsed.toprettyxml(indent='  ')

    # 保存 XML 文件
    xml_file_path = './docs/Lenovo_Test_Item_Principle_And_Impact_v0.1_Audio_AR_ACT.xml'
    with open(xml_file_path, 'w', encoding='utf-8') as file:
        file.write(pretty_xml)        

def generate_xml_updated():
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    from xml.sax.saxutils import escape
    import re

    # 解析XML文件
    tree = ET.parse('./docs/Lenovo_Test_Item_Principle_And_Impact_v0.1_Audio_AR_ACT.xml')
    root = tree.getroot()

    # 遍历每个TestItem节点
    for test_item in root.findall('TestItem'):
        # 创建IssuesAndSuggestion节点
        issues_and_suggestion = ET.SubElement(test_item, 'IssuesAndSuggestion')
        issues_and_suggestion.text = escape('null')
        
        # 转义现有节点的特殊字符
        for child in test_item:
            if child.text is not None:
                child.text = escape(child.text)

    # 将XML树转换为字符串并进行美化
    xml_str = ET.tostring(root, encoding='utf-8')
    parsed = minidom.parseString(xml_str)
    pretty_xml = parsed.toprettyxml(indent='  ')

    # 保存修改后的XML文件
    xml_file_path = './docs/Lenovo_Test_Item_Principle_And_Impact_v0.1_Audio_AR_ACT_updated.xml'
    # 处理多余空行
    lines = pretty_xml.splitlines()  # 使用splitlines处理所有换行符
    processed_lines = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:  # 只保留非空行
            # 统一格式 - 确保标签闭合方式一致
            processed_line = re.sub(r'<(\w+)/>', r'<\1></\1>', stripped_line)
            processed_lines.append(processed_line)
    processed_xml = '\n  '.join(processed_lines)  # 统一缩进为2个空格
    processed_xml = processed_xml.replace('&amp;amp;', '和')  # 将&amp;amp;替换为中文“和”
    
    with open(xml_file_path, 'w', encoding='utf-8') as file:
        file.write(processed_xml)

def split_xml_by_test_items(input_file_path, items_per_file=10):
    import xml.etree.ElementTree as ET
    import os
    from xml.dom import minidom
    from xml.sax.saxutils import escape    

    # 解析XML文件
    tree = ET.parse(input_file_path)
    root = tree.getroot()

    # 获取所有TestItem节点
    test_items = root.findall('TestItem')
    total_items = len(test_items)
    total_files = (total_items + items_per_file - 1) // items_per_file  # 计算总文件数

    # 获取目录和文件名信息
    dir_path = os.path.dirname(input_file_path)
    file_name = os.path.basename(input_file_path)
    base_name, ext = os.path.splitext(file_name)

    for i in range(total_files):
        # 创建新的根节点
        new_root = ET.Element(root.tag)
        # 复制原根节点的属性
        for key, value in root.attrib.items():
            new_root.set(key, value)

        # 计算当前文件的TestItem范围
        start_idx = i * items_per_file
        end_idx = min((i + 1) * items_per_file, total_items)
        current_items = test_items[start_idx:end_idx]

        # 添加TestItem到新根节点
        for item in current_items:
            new_root.append(item)

        # 美化XML并处理特殊字符
        xml_str = ET.tostring(new_root, encoding='utf-8')
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent='  ')

        # 处理空行
        lines = pretty_xml.splitlines()
        processed_lines = [line for line in lines if line.strip()]
        processed_xml = '\n'.join(processed_lines)

        # 生成输出文件名
        output_file_name = f'{base_name}_part{i+1}{ext}'
        output_file_path = os.path.join(dir_path, output_file_name)

        # 保存文件
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(processed_xml)

    print(f'成功分割为{total_files}个文件，每个文件最多包含{items_per_file}个TestItem节点')

def image_to_base64(image_path):
    """将本地图片转换为Base64编码字符串"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    # 获取图片文件格式
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        raise ValueError(f"不支持的图片格式: {ext}")
    
    # 读取并编码图片
    with open(image_path, 'rb') as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8')
    
    return f"data:image/{ext[1:]};base64,{base64_data}"

def start_local_image_server(port=8000, directory='.'):
    """启动本地HTTP服务器以提供图片访问"""
    # 验证目录是否存在
    if not os.path.isdir(directory):
        raise ValueError(f"无效的目录路径: {directory}")
    os.chdir(directory)
    # 自定义请求处理器以记录访问日志
    class LoggingRequestHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            print(f"[服务器日志] {self.client_address[0]} - {format%args}")
    handler = LoggingRequestHandler
    # 显式绑定到IPv4回环地址以避免IPv6兼容性问题
    server = HTTPServer(('127.0.0.1', port), handler)
    
    # 在后台线程中运行服务器
    server_thread = threading.Thread(target=server.serve_forever)
    # 设置为非守护线程以确保服务器持续运行直到显式关闭
    server_thread.daemon = False
    server_thread.start()
    print(f"服务器线程已启动，PID: {os.getpid()}")
    print(f"服务器绑定地址: 127.0.0.1:{port}")
    
    # 等待服务器启动并验证
    import time
    import requests
    max_retries = 5
    retry_delay = 2
    server_ready = False
    
    for attempt in range(max_retries):
        try:
            test_url = f"http://127.0.0.1:{port}/"
            print(f"验证服务器连接 (尝试 {attempt+1}/{max_retries}): {test_url}")
            response = requests.get(test_url, timeout=3)
            if response.status_code == 200:
                server_ready = True
                break
            print(f"服务器返回状态码: {response.status_code}, 重试中...")
        except requests.exceptions.RequestException as e:
            print(f"服务器连接尝试 {attempt+1} 失败: {str(e)}")
        time.sleep(retry_delay)
    
    if not server_ready:
        server.shutdown()
        raise RuntimeError(f"经过 {max_retries} 次尝试后仍无法连接到服务器")
    print("本地服务器验证成功，已准备就绪")
    
    print(f"本地图片服务器已启动: http://localhost:{port}")
    print(f"服务目录: {os.path.abspath(directory)}")
    return server, port

def call_doubao_api(messages, model="doubao-seed-1.6-250615", temperature=0.7):
    """
    调用豆包API进行对话补全
    
    参数:
    messages: 消息列表，每个消息包含role和content
              content可以包含文本和图片等多模态内容
    model: 使用的模型ID
    temperature: 生成文本的随机性参数
    
    示例:
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": "图片主要讲了什么?"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
    }]
    response = call_doubao_api(messages)
    
    返回:
    API响应的JSON结果

    图片处理说明:
    1. 使用Base64编码(适用于小图片):
       将本地图片转换为Base64编码字符串，直接嵌入请求中
       示例: image_to_base64("path/to/image.png")
    2. 使用本地服务器(适用于大图片):
       server, port = start_local_image_server(directory="path/to/images")
       然后使用: f"http://localhost:{port}/image.png"
       使用完毕后关闭服务器: server.shutdown()
    """
    import os
    import re
    import json
    import requests
    import time
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry

    
    api_url = os.getenv("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
    api_key = "c5566d4b-deae-4b7a-bffc-85ad4e103ad5"  # 注意：生产环境应使用环境变量
    
    # 验证API密钥
    if not api_key:
        raise ValueError("API密钥未设置")
    if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', api_key, re.I):
        print(f"[警告] API密钥格式可能不正确: {api_key[:8]}...{api_key[-4:]}")
    
    headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json"
        }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    
    # 调试输出（脱敏敏感信息）
    debug_headers = headers.copy()
    if 'Authorization' in debug_headers:
        token = debug_headers['Authorization'][7:]
        debug_headers['Authorization'] = f'Bearer {token[:8]}************{token[-4:]}'
        print(f"[调试] API请求头: {json.dumps(debug_headers, ensure_ascii=False, indent=2)}")
        print(f"[调试] API请求体: {json.dumps(payload, ensure_ascii=False, indent=2)[:500]}...")
    
    try:
        # 创建带有重试机制的Session
        session = requests.Session()
        retry_strategy = Retry(
            total=6,  # 增加总重试次数
            backoff_factor=3,  # 增加退避因子
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP状态码重试
            allowed_methods=["POST"],  # 允许POST重试
            connect=5,  # 增加连接错误重试次数
            read=5,     # 增加读取错误重试次数
            redirect=0  # 不重试重定向
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # 记录请求大小和开始时间
        payload_size = len(json.dumps(payload))
        print(f"[调试] 请求 payload 大小: {payload_size} 字节")
        start_time = time.time()
        
        # 发送请求，增加超时时间至30秒
        response = session.post(api_url, json=payload, headers=headers, timeout=30)
        
        # 记录响应时间
        duration = time.time() - start_time
        print(f"[调试] API 请求耗时: {duration:.2f} 秒")
        response.raise_for_status()
        print(f"[调试] API响应状态码: {response.status_code}")
        print(f"[调试] API响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)[:500]}...")
        
        # 关闭本地服务器（如果已启动）
        if 'server' in locals():
            print("API调用完成，正在关闭本地服务器...")
            server.shutdown()
            server.server_close()
            print("本地服务器已成功关闭")
            
        return response.json()
    except requests.exceptions.HTTPError as e:
            print(f"API请求错误: {str(e)}")
            print(f"响应状态码: {response.status_code if 'response' in locals() else '未知'}")
            try:
                if 'response' in locals():
                    error_details = response.json()
                    print(f"API错误详情: {json.dumps(error_details, ensure_ascii=False, indent=2)}")
                    print(f"响应头: {json.dumps(dict(response.headers), ensure_ascii=False, indent=2)}")
                else:
                    print("未收到响应内容")
            except json.JSONDecodeError:
                print(f"API错误响应: {response.text[:500] if 'response' in locals() else '无响应内容'}")
            raise
    except ConnectionResetError as e:
        print(f"[严重] 连接被远程主机重置: {str(e)}")
        print(f"可能原因: 网络问题、服务器负载过高或请求过大")
        print(f"请求大小: {payload_size} 字节")
        raise
    except Exception as e:
        print(f"[异常] 请求发生未知错误: {str(e)}")
        raise
    except Exception as e:
        print(f"请求发生异常: {str(e)}")
        raise

def call_doubao_with_image_prompt(
    api_url=os.getenv("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions"), 
    api_key="c5566d4b-deae-4b7a-bffc-85ad4e103ad5", 
    image_path="./pics/test_20250710170011.png", 
    network_image_url="https://pss.bdstatic.com/static/superman/img/logos/wenku-aaf198d89f.png",
    text_prompt="这个图片主要讲了什么?"):
    
    """
    调用豆包API，使用包含图片的提示信息
    
    参数:
    api_url: API请求地址，默认为从环境变量获取
    api_key: API密钥，默认为示例密钥
    image_path: 本地图片路径，用于小图片（小于500k）
    network_image_url: 网络图片URL，用于大图片
    text_prompt: 文本提示信息
    json: JSON 数据，用于填充请求内容
    
    返回:
    API响应的JSON结果
    """



    # 验证API密钥
    if not api_key:
        raise ValueError("API密钥未设置")
    if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', api_key, re.I):
        print(f"[警告] API密钥格式可能不正确: {api_key[:8]}...{api_key[-4:]}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    
    # 根据传入参数确定图片URL
    if image_path:
        image_url = image_to_base64(image_path)
    elif network_image_url:
        image_url = network_image_url
    else:
        raise ValueError("必须提供本地图片路径或网络图片URL")

    payload = {
        "model": "doubao-seed-1-6-250615",
        "messages": [
            {
                "content": [
                    {
                        "text": str(text_prompt),
                        "type": "text"
                    },
                    {                        
                        "image_url": {
                            "url": image_url
                        },
                        "type": "image_url"
                    }
                ],
                "role": "user"
            }
        ]
    }


    # 调试输出（脱敏敏感信息）
    debug_headers = headers.copy()
    if 'Authorization' in debug_headers:
        token = debug_headers['Authorization'][7:]
        debug_headers['Authorization'] = f'Bearer {token[:8]}************{token[-4:]}'
    print(f"[调试] API请求头: {json.dumps(debug_headers, ensure_ascii=False, indent=2)}")
    print(f"[调试] API请求体: {json.dumps(payload, ensure_ascii=False, indent=2)[:500]}...")
    
    try:
        # 创建带有重试机制的Session
        session = requests.Session()
        retry_strategy = Retry(
            total=6,  # 增加总重试次数
            backoff_factor=3,  # 增加退避因子
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP状态码重试
            allowed_methods=["POST"],  # 允许POST重试
            connect=5,  # 增加连接错误重试次数
            read=5,     # 增加读取错误重试次数
            redirect=0  # 不重试重定向
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # 记录请求大小和开始时间
        payload_size = len(json.dumps(payload))
        print(f"[调试] 请求 payload 大小: {payload_size} 字节")
        start_time = time.time()
        
        # 发送请求，增加超时时间至30秒
        response = session.post(api_url, json=payload, headers=headers, timeout=30)
        
        # 记录响应时间
        duration = time.time() - start_time
        print(f"[调试] API 请求耗时: {duration:.2f} 秒")
        response.raise_for_status()
        print(f"[调试] API响应状态码: {response.status_code}")
        print(f"[调试] API响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)[:500]}...")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"API请求错误: {str(e)}")
        print(f"响应状态码: {response.status_code if 'response' in locals() else '未知'}")
        try:
            if 'response' in locals():
                error_details = response.json()
                print(f"API错误详情: {json.dumps(error_details, ensure_ascii=False, indent=2)}")
                print(f"响应头: {json.dumps(dict(response.headers), ensure_ascii=False, indent=2)}")
            else:
                print("未收到响应内容")
        except json.JSONDecodeError:
            print(f"API错误响应: {response.text[:500] if 'response' in locals() else '无响应内容'}")
        raise
    except ConnectionResetError as e:
        print(f"[严重] 连接被远程主机重置: {str(e)}")
        print(f"可能原因: 网络问题、服务器负载过高或请求过大")
        print(f"请求大小: {payload_size} 字节")
        raise
    except Exception as e:
        print(f"[异常] 请求发生未知错误: {str(e)}")
        raise

def call_doubao_with_text_prompt(
    api_url=os.getenv("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions"), 
    api_key="c5566d4b-deae-4b7a-bffc-85ad4e103ad5", 
    text_prompt="根据各<TestItem>节点内容编写的<IssuesAndSuggestion>部分，分析问题并给出建议措施各至少1到3条，每1条数字控制在100个字以内，内容不要太专业，要言简意赅，浅显易懂:",
    payload_json={
        "TestItem": {
            "TestGroup": "硬件控制和状态检查",
            "SpecialTestItems": "ENTRY_HANDLER_L2AUDIO",
            "TestDetailInformation": "　",
            "Dependency": "站点各器件加载和moto USB驱动检查",
            "Principle": "检查站点硬件环境和通信环境",
            "Impact": "测试环境不满足测试要求，无法测试",
            "Risk": "Low",
            "Owner": "zhigang",
            "IssuesAndSuggestion": "null"
        }
    }):
    
    """
    调用豆包API，使用包含图片的提示信息
    
    参数:
    api_url: API请求地址，默认为从环境变量获取
    api_key: API密钥，默认为示例密钥
    image_path: 本地图片路径，用于小图片（小于500k）
    network_image_url: 网络图片URL，用于大图片
    text_prompt: 文本提示信息
    json: JSON 数据，用于填充请求内容
    
    返回:
    API响应的JSON结果
    """

    # 验证API密钥
    if not api_key:
        raise ValueError("API密钥未设置")
    if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', api_key, re.I):
        print(f"[警告] API密钥格式可能不正确: {api_key[:8]}...{api_key[-4:]}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    
    payload = {
        "model": "doubao-seed-1-6-250615",
        "messages": [
            {
                "content": 
                [
                    {
                        "text": str(text_prompt) + json.dumps(payload_json, ensure_ascii=False),
                        "type": "text"
                    }
                ],
                "role": "user"
            }
        ]
    }

    # 调试输出（脱敏敏感信息）
    debug_headers = headers.copy()
    if 'Authorization' in debug_headers:
        token = debug_headers['Authorization'][7:]
        debug_headers['Authorization'] = f'Bearer {token[:8]}************{token[-4:]}'
    print(f"[调试] API请求头: {json.dumps(debug_headers, ensure_ascii=False, indent=2)}")
    print(f"[调试] API请求体: {json.dumps(payload, ensure_ascii=False, indent=2)[:500]}...")
    
    try:
        # 创建带有重试机制的Session
        session = requests.Session()
        retry_strategy = Retry(
            total=6,  # 增加总重试次数
            backoff_factor=3,  # 增加退避因子
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP状态码重试
            allowed_methods=["POST"],  # 允许POST重试
            connect=5,  # 增加连接错误重试次数
            read=5,     # 增加读取错误重试次数
            redirect=0  # 不重试重定向
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # 记录请求大小和开始时间
        payload_size = len(json.dumps(payload))
        print(f"[调试] 请求 payload 大小: {payload_size} 字节")
        start_time = time.time()
        
        # 发送请求，增加超时时间至30秒
        response = session.post(api_url, json=payload, headers=headers, timeout=30)
        
        # 记录响应时间
        duration = time.time() - start_time
        print(f"[调试] API 请求耗时: {duration:.2f} 秒")
        response.raise_for_status()
        print(f"[调试] API响应状态码: {response.status_code}")
        print(f"[调试] API响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)[:500]}...")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"API请求错误: {str(e)}")
        print(f"响应状态码: {response.status_code if 'response' in locals() else '未知'}")
        try:
            if 'response' in locals():
                error_details = response.json()
                print(f"API错误详情: {json.dumps(error_details, ensure_ascii=False, indent=2)}")
                print(f"响应头: {json.dumps(dict(response.headers), ensure_ascii=False, indent=2)}")
            else:
                print("未收到响应内容")
        except json.JSONDecodeError:
            print(f"API错误响应: {response.text[:500] if 'response' in locals() else '无响应内容'}")
        raise
    except ConnectionResetError as e:
        print(f"[严重] 连接被远程主机重置: {str(e)}")
        print(f"可能原因: 网络问题、服务器负载过高或请求过大")
        print(f"请求大小: {payload_size} 字节")
        raise
    except Exception as e:
        print(f"[异常] 请求发生未知错误: {str(e)}")
        raise

def log_res(res, include_details=True):
    """记录res的函数"""
    try:
        # 打开或创建日志文件，以追加模式写入，使用UTF-8编码
        # 'a' 模式会自动处理文件不存在的情况，若不存在则创建，存在则在文件末尾追加
        with open('./docs/execution_result.log', 'a', encoding='utf-8') as file:
            # 尝试将res转换为JSON格式，便于阅读
            # 添加时间戳
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f'[{timestamp}]\n')
            
            # 尝试将res转换为JSON格式，便于阅读
            # 尝试从JSON结构体中提取特定字段
            if isinstance(res, dict) and 'choices' in res:
                for choice in res.get('choices', []):
                    message = choice.get('message', {})
                    content = message.get('content', '').strip()
                    reasoning = message.get('reasoning_content', '').strip()
                    
                    # 写入提取的内容
                    if include_details:
                        if content:
                            file.write(f'{content}\n')
                        if reasoning:
                            file.write(f'{reasoning}\n')
                    else:
                        if content:
                            file.write(f'{content}\n')
                file.write('\n')  # 条目间空行分隔
            else:
                # 保留原有的JSON格式化处理
                if isinstance(res, (dict, list)):
                    file.write(json.dumps(res, ensure_ascii=False, indent=2) + '\n')
                else:
                    file.write(str(res) + '\n')
    except Exception as e:
        print(f"写入日志文件时出错: {str(e)}")


if __name__ == "__main__":
    # main()
    # print_environment_info()
    # generate_xml()
    # generate_xml_updated()
    # # 调用分割函数
    # xml_file_path='./docs/Lenovo_Test_Item_Principle_And_Impact_v0.1_Audio_AR_ACT_updated.xml'
    # split_xml_by_test_items(xml_file_path, items_per_file=10)
    # 调用豆包分析更新函数处理part11
    # res =  call_doubao_with_image_prompt()
    # log_res(res)

    res = call_doubao_with_text_prompt()
    log_res(res,include_details=False)


