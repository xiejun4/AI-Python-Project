import sys

sys.path.append(r'/opt/xiejun4/pro_PathFinder/functions/')
from unzip_otplus_helper import unzip_otplus_helper_rotate_log_file

# flask packages module path
sys.path.append(r'/usr/local/bin/python311/lib/python3.11/site-packages/')

# Adding this is to load the files and functions contained in 'functions/' under 'pro-PathFinder/'
sys.path.append(r'/opt/xiejun4/pro_PathFinder/')
from main_test import l2ar_process_log_file
from functions import bt_analysis, chat_debug

import os
import json
from flask import Flask, request, send_file
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
# CORS(app)  # 允许所有域名跨域访问

# 这里修改为实际的文件存储目录
UPLOAD_DIR = '../uploads'
DOWNLOAD_DIR = '../downloads'

# 确保上传和下载目录存在
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


@app.route('/test', methods=['GET'])
def test():
    return 'test'


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)
    return f'File {file.filename} uploaded successfully', 200


@app.route('/upload_new_ver1', methods=['POST'])
def upload_file_new_ver1():
    if 'file' not in request.files:
        return 'No file part', 400

    # request log file
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # save log file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(file_path)

    # process log file
    zip_path = get_absolute_file_path(file_path)
    json_content = l2ar_process_log_file(zip_path)

    # return json content
    if not json_content:
        res_msg = f'Json Content: null', 500
    else:
        res_msg = f'Json Content: {json_content}', 200
    return res_msg
    # return f'File {file.filename} FilePath {file_path} uploaded successfully', 200


@app.route('/upload_new_ver2', methods=['POST'])
def upload_file_new_ver2():
    result = {
        "success": False,
        "message": "",
        "code": 400,
        "result": {},
        "timestamp": int(datetime.now().timestamp() * 1000)
    }

    try:

        # 打印 request.files 的基本信息
        print('type(request.files):', type(request.files))
        print('request.files:', request.files)

        if 'file' not in request.files:
            result["message"] = 'No file part'
            return json.dumps(result), 400

        file = request.files['file']
        if file.filename == '':
            result["message"] = 'No selected file'
            return json.dumps(result), 400

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(file_path)

        zip_path = get_absolute_file_path(file_path)
        json_content = l2ar_process_log_file(zip_path)

        if not json_content:
            result["message"] = 'Failed to process log file'
            result["code"] = 500
            return json.dumps(result), 500
        else:
            result["success"] = True
            result["message"] = 'File processed successfully'
            result["code"] = 200
            result["result"] = json_content
            return json.dumps(result), 200

    except Exception as e:
        result["message"] = f'Internal server error: {str(e)}'
        result["code"] = 500
        return json.dumps(result), 500


@app.route('/upload_new_ver3', methods=['POST'])
def upload_file_new_ver3():
    result = {
        "success": False,
        "message": "",
        "code": 400,
        "result": {},
        "timestamp": int(datetime.now().timestamp() * 1000)
    }

    try:
        # Check if any files were uploaded
        if not request.files:
            result["message"] = 'No files were uploaded'
            return json.dumps(result), 400

        form_data = {}
        for key in request.form:
            form_data[key] = request.form[key]
            print(f"key = {key} | form_data_value = {form_data[key]}")

        files_data = {}
        for key in request.files:
            files_data[key] = request.files[key]
            print(f"key = {key} | files_data_value = {files_data[key]}")

        # Get the first file from the uploads
        language = request.form["lang"]
        filename = request.form["fileName"]
        file = request.files["file"]
        print(f"language: {language}")
        print(f"filename : {filename}")
        print(f"file: {file}")

        # Save the file to the upload directory
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)

        # Process the uploaded file
        zip_path = get_absolute_file_path(file_path)
        json_content = l2ar_process_log_file(zip_path, language)

        # When the capacity of the app.log file of uSWGI exceeds 32M,
        # the existing file will be backed up and a new file will be
        # created to record the log information.
        if os.name == 'posix':  # Linux
            log_file = r"/opt/xiejun4/pro_PathFinder/functions/log/uwsgi/app.log"
        else:  # Windows
            log_file = r".\functions\log\uwsgi\app.log"

        unzip_otplus_helper_rotate_log_file(log_file)

        # Check if file processing was successful
        if not json_content:
            result["message"] = 'Failed to process log file'
            result["code"] = 500
            return json.dumps(result), 500
        else:
            result["success"] = True
            result["message"] = 'File processed successfully'
            result["code"] = 200
            result["result"] = json_content
            return json.dumps(result), 200

    except Exception as e:
        result["message"] = f'Internal server error: {str(e)}'
        result["code"] = 500
        return json.dumps(result), 500


@app.route('/upload_new', methods=['POST'])
def upload_file_new():
    # # TODO: this is the place for debugging the AI's API interface
    # # run_chat_debug_with_interpreter()
    # interpreter_path = '/usr/local/bin/python311/bin/python3'
    # function_name = 'debug_basic_api'
    # language = "中文"
    # test_item = "AUDIO_L2AR_EAR_10000_8KHz_TO_140Hz_MIC1_PORTO_EQ"
    # test_query = (f"使用通俗易懂的{language}语言解释说明：{test_item},"
    #               f"其中L2AR这样的是第二代音频测试站，"
    #               f"其中4500这样的是采样率，最后面的像PORTO_EQ是手机或平板的产品名称，"
    #               f"先将各部分含义解析汇总成有序或无序列表，"
    #               f"然后将其通俗易懂的语言，其内容缩写为50字左右，"
    #               f"然后按照MarkDown的格式输出给我。")
    # is_think = False
    # run_chat_debug_with_interpreter2(interpreter_path,function_name, test_query,test_item,language,is_think)
    # # TODO: ---------------------------------------------------

    result = {
        "success": False,
        "message": "",
        "code": 400,
        "result": {},
        "timestamp": int(datetime.now().timestamp() * 1000)
    }

    try:
        # Check if any files were uploaded
        if not request.files:
            result["message"] = 'No files were uploaded'
            return json.dumps(result), 400

        form_data = {}
        for key in request.form:
            form_data[key] = request.form[key]
            print(f"key = {key} | form_data_value = {form_data[key]}")

        files_data = {}
        for key in request.files:
            files_data[key] = request.files[key]
            print(f"key = {key} | files_data_value = {files_data[key]}")

        # Get the first file from the uploads
        language = request.form["lang"]
        filename = request.form["fileName"]

        # TODO:这里要从request中获取 is_ai 的状态
        is_ai_str = request.form["isAI"]
        is_ai = is_ai_str.lower() == "true"

        # TODO:这里要从request中获取 is_abroad 的状态
        is_abroad_str = request.form["isAbroad"]
        is_abroad = is_abroad_str.lower() == "true"
        # TODO:如果是海外ip，就关闭深度分析开关
        if is_abroad:
            is_ai = False

        file = request.files["file"]

        print(f"language: {language}")
        print(f"filename: {filename}")
        print(f"file: {file}")
        print(f"is_AI: {is_ai}")
        print(f"is_Abroad: {is_abroad}")

        # Save the file to the upload directory
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)

        # Process the uploaded file
        zip_path = get_absolute_file_path(file_path)
        json_content = l2ar_process_log_file(zip_path, language, is_ai=is_ai)
        if json_content == '':
            json_content = bt_analysis.process_log_file(zip_path, language)

        # When the capacity of the app.log file of uSWGI exceeds 32M,
        # the existing file will be backed up and a new file will be
        # created to record the log information.
        if os.name == 'posix':  # Linux
            log_file = r"/opt/xiejun4/pro_PathFinder/functions/log/uwsgi/app.log"
        else:  # Windows
            log_file = r".\functions\log\uwsgi\app.log"

        unzip_otplus_helper_rotate_log_file(log_file)

        # Check if file processing was successful
        if not json_content:
            result["message"] = 'Failed to process log file'
            result["code"] = 500
            return json.dumps(result), 500
        else:
            result["success"] = True
            result["message"] = 'File processed successfully'
            result["code"] = 200
            result["result"] = json_content
            return json.dumps(result), 200

    except Exception as e:
        result["message"] = f'Internal server error: {str(e)}'
        result["code"] = 500
        return json.dumps(result), 500


@app.route('/download', methods=['POST'])
def download_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    # 假设文件名为要下载的文件名
    filename = file.filename
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return 'File not found', 404


def get_absolute_file_path(response_data_decoded):
    # """
    # 将响应中返回的相对文件路径转换为系统无关的绝对路径
    #
    # 参数:
    #     response_data_decoded (str): 响应中解码后的路径字符串，通常包含"FilePath"前缀和相对路径
    #
    # 返回:
    #     Path: 转换后的绝对路径对象
    #
    # 功能说明:
    #     1. 从输入字符串中提取实际的文件路径（移除"FilePath"前缀）
    #     2. 根据当前操作系统类型自动处理路径分隔符差异
    #     3. 将相对路径转换为基于项目根目录的绝对路径
    #     4. 规范化路径格式，确保在不同系统上的一致性
    #
    # 示例:
    #     输入: "FilePath../uploads\\test.txt" (Windows响应格式)
    #     输出: /home/user/project/uploads/test.txt (Linux绝对路径)
    #
    #     输入: "FilePath../uploads/test.txt" (Linux响应格式)
    #     输出: C:\Users\user\project\uploads\test.txt (Windows绝对路径)
    #
    # 注意事项:
    #     - 函数假设web_log_server2.py位于项目根目录下的一级目录中
    #     - 如果项目结构不同，需要调整project_root的计算方式
    #     - 路径中的"FilePath"前缀会被自动移除
    # """

    # 提取实际路径并去除空白字符
    file_path = response_data_decoded.strip().replace('FilePath', '')

    # 根据操作系统类型处理路径分隔符
    if os.name == 'nt':  # Windows系统
        # 规范化路径（处理反斜杠和点号等）
        normalized_path = os.path.normpath(file_path)
    else:  # Linux/Unix/Mac系统
        # 将所有分隔符转换为正斜杠
        normalized_path = file_path.replace(os.sep, '/')

    # file name
    filename = os.path.basename(normalized_path)

    if os.name == 'nt':
        # 计算项目根目录（假设web_log_server2.py位于项目根目录的一级子目录中）
        project_root = Path(__file__).parent.parent

        # 构建并解析绝对路径
        absolute_file_path = fr"{project_root}\uploads\{filename}"
        print(f"绝对路径: {absolute_file_path}")
    else:
        # Specify a clear project root directory.
        project_root = Path('/opt/xiejun4/pro_PathFinder/uploads')

        # Bulid an absolute path without parsing
        absolute_file_path = f'{project_root}/{filename}'
        print(f"绝对路径: {absolute_file_path}")

    return absolute_file_path


if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.10', port=5000)
    # 使用Waitress运行Flask应用
    # serve(app, host='0.0.0.0', port=5000)
