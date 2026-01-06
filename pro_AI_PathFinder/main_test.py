import json
import subprocess
import os
import re
import copy
from pathlib import Path
import sys

from functions.Issue_Suggestion_DataUtil_L2AR import (
    wlan_tx_issue_suggestion,
    generate_issue_from_container,
    generate_issue_analysis_mtk_meta_trackid_from_md_nvram
)
from functions.basic_band_test_purpose2items_parser import BasicBand_TestPurposeAndItems_parser
# from functions.chat_debug import debug_failure_analysis
# from functions.chat_debug import debug_basic_api

from functions.unzip_otplus_helper import (
    unzip_otplus_helper_unzip_file,
    unzip_otplus_helper_filter_files2,
    unzip_otplus_helper_rename_log_zip,
    unzip_otplus_helper_delete_zip_files,
    unzip_otplus_helper_rotate_log_file)

from functions.CleanFilterDataUtil_L2AR import DataCleaningAndFiltering
from functions.JsonDataUtil_L2AR import JsonDataUtil
from functions.CleanFilterDataEntity_L2AR import (
    TestSites,
    Platforms,
    TestTypes)


# TODO:this is place for writing ai's api functions.
def run_chat_debug_with_interpreter(interpreter_path='/usr/local/bin/python311/bin/python3'):
    """
    Call the main function in chat_debug.py using the specified Python interpreter

    Args:
        interpreter_path (str): Absolute path to the Python interpreter
    """
    try:
        # Construct command: [interpreter path, script path]
        command = [interpreter_path, "chat_debug.py"]

        # Execute command and capture output
        # Specify encoding as utf-8 to handle all characters
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',  # New: Specify encoding as utf-8
            errors='replace'  # New: Use replacement character for undecodable characters
        )

        # Print execution result
        print("Execution successful, output as follows:")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Execution failed, return code: {e.returncode}")
        print("Error output:")
        print(e.stderr)
    except FileNotFoundError:
        print(f"Error: Specified Python interpreter not found - {interpreter_path}")
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")


def run_ai_api_test_name_describe_for_linux_v1(
        interpreter_path='/usr/local/bin/python311/bin/python3',
        function_name='debug_basic_api',
        *args
):
    """
    Call a specific function in chat_debug.py with arguments using the specified Python interpreter
    and extract content after "过滤后结果：" from stdout

    Args:
        interpreter_path (str): Absolute path to the Python interpreter
        function_name (str): Name of the function to execute (e.g., "main")
        *args: Arguments to pass to the function
    """
    try:
        # Construct command to call the specific function
        # Format: python -c "from chat_debug import function_name; function_name(args...)"
        args_str = ", ".join([f'"{arg}"' for arg in args])  # Handle string arguments
        command = [
            interpreter_path,
            "-c",
            f"from chat_debug import {function_name}; {function_name}({args_str})"
        ]

        # Execute command and capture output
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("AI：1.全部内容； 2.过滤<think>...</think>后的内容。")
        print(result.stdout)

        # 提取过滤后结果
        filter_marker = "过滤后结果："
        if filter_marker in result.stdout:
            filtered_content = result.stdout.split(filter_marker, 1)[1].strip()
            print("\n2.过滤<think>...</think>后的内容:")
            print(filtered_content)
            return filtered_content
        else:
            print("\nNo '2.过滤<think>...</think>后的内容：' <think>...</think> found in output")
            return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Execution failed, return code: {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: Specified Python interpreter not found - {interpreter_path}")
        return None
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        return None


def run_ai_api_test_name_describe_for_linux(
        interpreter_path='/usr/local/bin/python311/bin/python3',
        function_name='debug_basic_api',
        *args
):
    """
    Call a specific function in chat_debug.py with arguments using the specified Python interpreter
    and extract content after "过滤后结果：" from stdout. Fixed boolean parameter handling and added proper path handling.

    Args:
        interpreter_path (str): Absolute path to the Python interpreter
        function_name (str): Name of the function to execute (e.g., "main")
        *args: Arguments to pass to the function
    """
    try:
        # 获取chat_debug.py所在的目录（Linux系统路径）
        chat_debug_dir = '/opt/xiejun4/pro_PathFinder/functions'  # 根据实际Linux路径修改

        # 构建参数字符串，对不同类型参数进行适当处理
        args_str_parts = []
        for arg in args:
            if isinstance(arg, str):
                # 对字符串进行引号转义
                escaped_arg = arg.replace('"', '\\"')
                args_str_parts.append(f'"{escaped_arg}"')
            elif isinstance(arg, bool):
                # 布尔值处理：使用Python正确的大写形式
                args_str_parts.append('True' if arg else 'False')
            else:
                # 其他类型直接转换为字符串
                args_str_parts.append(str(arg))

        # 构建命令调用特定函数
        args_str = ", ".join(args_str_parts)
        command = [
            interpreter_path,
            "-c",
            f"import sys; sys.path.append('{chat_debug_dir}'); "
            # 强制设置标准输出编码为utf-8
            f"import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); "
            # Linux环境：从chat_debug导入函数
            f"from chat_debug import {function_name}; {function_name}({args_str})"
        ]

        # 执行命令并捕获输出
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("AI：1.全部内容； 2.过滤...后的内容。")
        print(result.stdout)

        # 提取过滤后结果
        filter_marker = "过滤后结果："
        if filter_marker in result.stdout:
            filtered_content = result.stdout.split(filter_marker, 1)[1].strip()
            print("\n2.过滤...后的内容:")
            print(filtered_content)
            return filtered_content
        else:
            print("\nNo '过滤后结果：' found in output")
            return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Execution failed, return code: {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: Specified Python interpreter not found - {interpreter_path}")
        return None
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        return None


def run_ai_api_test_name_describe_for_windows(
        interpreter_path=r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe',
        function_name='debug_basic_api',
        *args
):
    """
    修复布尔值参数导致的'replace'属性错误
    """
    try:
        # 获取chat_debug.py所在的目录
        chat_debug_dir = r'C:\Users\xiejun4\Desktop\pro_PathFinder\functions'

        # 构建参数字符串，对字符串类型才进行replace处理
        args_str_parts = []
        for arg in args:
            if isinstance(arg, str):
                # 仅对字符串进行引号转义
                # args_str_parts.append(f'"{arg.replace('"', '\\"')}"')
                escaped_arg = arg.replace('"', '\\"')
                args_str_parts.append(f'"{escaped_arg}"')
            elif isinstance(arg, bool):
                # 布尔值处理：使用Python正确的大写形式
                args_str_parts.append('True' if arg else 'False')  # 关键修复点
            else:
                # 其他类型直接转换为字符串
                args_str_parts.append(str(arg))

        # Construct command to call the specific function
        # Format: python -c "from chat_debug import function_name; function_name(args...)"
        args_str = ", ".join(args_str_parts)
        command = [
            interpreter_path,
            "-c",
            f"import sys; sys.path.append(r'{chat_debug_dir}'); "
            # 出现乱码通常是由于编码设置不匹配导致的，并非不支持中文。Windows 系统默认编码是 GBK，而你的代码中使用了 UTF-8 编码，两者不匹配就会产生乱码。
            # 强制设置标准输出编码为utf-8
            f"import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); "
            # windows环境：functions.chat_debug
            f"from functions.chat_debug import {function_name}; {function_name}({args_str})"
        ]

        # Execute command and capture output
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("AI：1.全部内容； 2.过滤<think>...</think>后的内容。")
        print(result.stdout)

        # 提取过滤后结果
        filter_marker = "过滤后结果："
        if filter_marker in result.stdout:
            filtered_content = result.stdout.split(filter_marker, 1)[1].strip()
            print("\n2.过滤<think>...</think>后的内容:")
            print(filtered_content)
            return filtered_content
        else:
            print("\nNo '2.过滤<think>...</think>后的内容：' <think>...</think> found in output")
            return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Execution failed, return code: {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: Specified Python interpreter not found - {interpreter_path}")
        return None
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        return None


def run_ai_api_failed_log_analysis_suggest_for_linux_v1(
        interpreter_path='/usr/local/bin/python311/bin/python3',
        function_name='debug_failure_analysis',
        *args
):
    """
    Call a specific function in chat_debug.py with arguments using the specified Python interpreter
    and extract content after "过滤后结果：" from stdout

    Args:
        interpreter_path (str): Absolute path to the Python interpreter
        function_name (str): Name of the function to execute (e.g., "main")
        *args: Arguments to pass to the function
    """
    try:
        # Construct command to call the specific function
        # Format: python -c "from chat_debug import function_name; function_name(args...)"
        args_str = ", ".join([f'"{arg}"' for arg in args])  # Handle string arguments
        command = [
            interpreter_path,
            "-c",
            f"from chat_debug import {function_name}; {function_name}({args_str})"
        ]

        # Execute command and capture output
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("AI：1.全部内容； 2.过滤<think>...</think>后的内容。")
        print(result.stdout)

        # 提取过滤后结果
        filter_marker = "过滤后结果："
        if filter_marker in result.stdout:
            filtered_content = result.stdout.split(filter_marker, 1)[1].strip()
            print("\n2.过滤<think>...</think>后的内容:")
            print(filtered_content)
            return filtered_content
        else:
            print("\nNo '2.过滤<think>...</think>后的内容：' <think>...</think> found in output")
            return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Execution failed, return code: {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: Specified Python interpreter not found - {interpreter_path}")
        return None
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        return None


def run_ai_api_failed_log_analysis_suggest_for_linux(
        interpreter_path='/usr/local/bin/python311/bin/python3',
        function_name='debug_failure_analysis',
        *args
):
    """
    Call a specific function in chat_debug.py with arguments using the specified Python interpreter
    and extract content after "过滤后结果：" from stdout, optimized for Linux environment.

    优化内容：
    1. 修复布尔值参数处理问题
    2. 增加对字符串参数的引号转义
    3. 添加chat_debug.py所在目录到系统路径
    4. 强制设置标准输出编码为utf-8以避免中文乱码
    5. 完善返回值处理，提取过滤后的结果

    Args:
        interpreter_path (str): Absolute path to the Python interpreter
        function_name (str): Name of the function to execute (e.g., "debug_failure_analysis")
        *args: Arguments to pass to the function

    Returns:
        str: Filtered content after "过滤后结果：" or full output if marker not found, None if error
    """
    try:
        # 获取chat_debug.py所在的目录（Linux系统路径）
        chat_debug_dir = '/opt/xiejun4/pro_PathFinder/functions'  # 根据实际Linux路径修改

        # 构建参数字符串，对不同类型参数进行适当处理
        args_str_parts = []
        for arg in args:
            if isinstance(arg, str):
                # 对字符串参数进行引号转义处理
                escaped_arg = arg.replace('"', '\\"')
                args_str_parts.append(f'"{escaped_arg}"')
            elif isinstance(arg, bool):
                # 布尔值处理：使用Python正确的大写形式
                args_str_parts.append('True' if arg else 'False')
            else:
                # 其他类型直接转换为字符串
                args_str_parts.append(str(arg))

        # 拼接所有参数
        args_str = ", ".join(args_str_parts)

        # 构建命令，适配Linux环境
        command = [
            interpreter_path,
            "-c",
            # 添加chat_debug.py所在目录到系统路径
            f"import sys; sys.path.append('{chat_debug_dir}'); "
            # 强制设置标准输出编码为utf-8，解决中文乱码问题
            f"import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); "
            # 从chat_debug模块导入并执行指定函数（Linux环境）
            f"from chat_debug import {function_name}; {function_name}({args_str})"
        ]

        # 执行命令并捕获输出
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("AI：1.全部内容； 2.过滤...后的内容。")
        print(result.stdout)

        # 提取过滤后结果
        filter_marker = "过滤后结果："
        if filter_marker in result.stdout:
            filtered_content = result.stdout.split(filter_marker, 1)[1].strip()
            print("\n2.过滤...后的内容:")
            print(filtered_content)
            return filtered_content
        else:
            print("\nNo '过滤后结果：' found in output")
            return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Execution failed, return code: {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: Specified Python interpreter not found - {interpreter_path}")
        return None
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        return None


def run_ai_api_failed_log_analysis_suggest_for_windows(
        interpreter_path=r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe',
        function_name='debug_failure_analysis',
        *args
):
    """
    Call a specific function in chat_debug.py with arguments using the specified Python interpreter
    and extract content after "过滤后结果：" from stdout, optimized for Windows environment.

    优化内容：
    1. 修复布尔值参数处理问题
    2. 增加对字符串参数的引号转义
    3. 添加chat_debug.py所在目录到系统路径
    4. 强制设置标准输出编码为utf-8以避免中文乱码
    5. 完善返回值处理，提取过滤后的结果

    Args:
        interpreter_path (str): Absolute path to the Python interpreter
        function_name (str): Name of the function to execute (e.g., "debug_failure_analysis")
        *args: Arguments to pass to the function

    Returns:
        str: Filtered content after "过滤后结果：" or full output if marker not found, None if error
    """
    try:
        # 获取chat_debug.py所在的目录（Windows路径）
        chat_debug_dir = r'C:\Users\xiejun4\Desktop\pro_PathFinder\functions'

        # 构建参数字符串，对不同类型参数进行适当处理
        args_str_parts = []
        for arg in args:
            if isinstance(arg, str):
                # 对字符串参数进行引号转义处理
                # args_str_parts.append(f'"{arg.replace('"', '\\"')}"')
                escaped_arg = arg.replace('"', '\\"')
                args_str_parts.append(f'"{escaped_arg}"')
            elif isinstance(arg, bool):
                # 布尔值处理：使用Python正确的大写形式
                args_str_parts.append('True' if arg else 'False')
            else:
                # 其他类型直接转换为字符串
                args_str_parts.append(str(arg))

        # 拼接所有参数
        args_str = ", ".join(args_str_parts)

        # 构建命令，适配Windows环境
        command = [
            interpreter_path,
            "-c",
            # 添加chat_debug.py所在目录到系统路径
            f"import sys; sys.path.append(r'{chat_debug_dir}'); "
            # 强制设置标准输出编码为utf-8，解决中文乱码问题
            f"import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); "
            # 从chat_debug模块导入并执行指定函数
            f"from functions.chat_debug import {function_name}; {function_name}({args_str})"
        ]

        # 执行命令并捕获输出
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("AI：1.全部内容； 2.过滤<think>...</think>后的内容。")
        print(result.stdout)

        # 提取过滤后结果
        filter_marker = "过滤后结果："
        if filter_marker in result.stdout:
            filtered_content = result.stdout.split(filter_marker, 1)[1].strip()
            print("\n2.过滤<think>...</think>后的内容:")
            print(filtered_content)
            return filtered_content
        else:
            print("\nNo '2.过滤<think>...</think>后的内容：' <think>...</think> found in output")
            return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Execution failed, return code: {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: Specified Python interpreter not found - {interpreter_path}")
        return None
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        return None


# 从外部配置文件读取判定规则
def load_file_info_rules():
    # 根据操作系统选择不同的配置路径
    if sys.platform.startswith('linux'):
        # Linux系统使用指定路径
        config_path = os.path.join('/opt', 'xiejun4', 'pro_PathFinder', 'config', 'file_info_rules.json')
    else:
        # Windows系统保持原有路径不变
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'file_info_rules.json')

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        # 返回默认规则
        return {
            "site_rules": {
                "L2AR Site": ["_L2_AR_", "_L2AR", "_L2AR_", "_LAR"],
                "default": "Non-L2AR Site"
            },
            "platform_rules": {
                "_QC_": "Qualcomm Platform",
                "_MTK_": "MTK Platform",
                "default": "Generic Platform"
            }
        }


# TODO: 未来可以添加: 从文件内容判断site和platform的逻辑
def check_file_info(zip_path, _file_info_rules):
    """
    Determine site and platform type based on filename

    Parameters:
    zip_path (str): Full path of the ZIP file

    Returns:
    tuple: A tuple containing site and platform information (site, platform)
    """
    # Get the base filename
    zip_file_name = os.path.basename(zip_path)

    # Determine site type using config rules
    site = _file_info_rules['site_rules']['default']
    for site_name, keywords in _file_info_rules['site_rules'].items():
        if site_name == 'default':
            continue
        if any(keyword in zip_file_name for keyword in keywords):
            site = site_name
            break

    # Determine platform type using config rules
    platform = _file_info_rules['platform_rules']['default']
    for keyword, platform_name in _file_info_rules['platform_rules'].items():
        if keyword == 'default':
            continue
        if keyword in zip_file_name:
            platform = platform_name
            break

    # Determine test type using config rules
    base_band_test_item = _file_info_rules.get('default_test_item', 'Other Test Type')

    # 遍历测试项规则
    for rule in _file_info_rules.get('test_item_rules', []):
        keywords = rule.get('keywords', [])
        all_required = rule.get('all_required', True)

        if all_required:
            # 检查是否包含所有必需的关键词
            if all(keyword in zip_file_name for keyword in keywords):
                base_band_test_item = rule.get('name', base_band_test_item)
                # 检查是否需要覆盖平台
                if 'platform_override' in rule:
                    platform = rule['platform_override']
                break
        else:
            # 检查是否包含任一关键词
            if any(keyword in zip_file_name for keyword in keywords):
                base_band_test_item = rule.get('name', base_band_test_item)
                # 检查是否需要覆盖平台
                if 'platform_override' in rule:
                    platform = rule['platform_override']
                break

    return site, platform, base_band_test_item


def check_file_info_v1(zip_path):
    """
    Determine site and platform type based on filename

    Parameters:
    zip_path (str): Full path of the ZIP file

    Returns:
    tuple: A tuple containing site and platform information (site, platform)
    """
    # Get the base filename
    zip_file_name = os.path.basename(zip_path)

    # Determine site type
    if '_L2_AR_' in zip_file_name or '_L2AR' in zip_file_name or '_L2AR_' in zip_file_name or '_LAR' in zip_file_name:
        site = 'L2AR Site'
    else:
        site = 'Non-L2AR Site'

    # Determine platform type
    if '_QC_' in zip_file_name:
        platform = 'Qualcomm Platform'
    else:
        platform = 'MTK Platform'

    return site, platform


def check_calibration(file_path):
    """
    Check if calibration markers exist in the file

    Parameters:
    file_path (str): Full path to the file

    Returns:
    str: "Calibration" if markers found, "Testing" otherwise
    """
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if '_CAL' in line:
                    return "Calibration"
        return "Testing"
    except Exception as e:
        print(f"Error reading file: {e}")
        return "Testing"  # Default to testing if error occurs


def keep_first_subdict(new_filtered_dict):
    """
    深拷贝嵌套字典，并仅保留第一个子字典，移除其他子字典

    参数:
    new_filtered_dict (dict): 两层嵌套的字典

    返回:
    dict: 处理后的字典，仅包含第一个子字典
    """
    from copy import deepcopy

    # 深拷贝原始字典，避免修改原数据
    copied_dict = deepcopy(new_filtered_dict)

    # 检查是否为嵌套字典
    if not isinstance(copied_dict, dict) or len(copied_dict) == 0:
        return copied_dict  # 非字典或空字典直接返回

    # 获取第一个子字典的键
    first_key = next(iter(copied_dict.keys()))

    # 仅保留第一个子字典，构建新的字典
    filtered_dict = {first_key: copied_dict[first_key]}

    return filtered_dict


def keep_first_subdict2(new_filtered_dict):
    """
    深拷贝嵌套字典，仅保留第一个子字典，并在该子字典中只保留第一个列表，删除其他列表

    参数:
    new_filtered_dict (dict): 两层嵌套的字典，子字典中可能包含多个列表值

    返回:
    dict: 处理后的字典，仅包含第一个子字典，且该子字典中只保留第一个列表
    """
    from copy import deepcopy

    # 深拷贝原始字典，避免修改原数据
    copied_dict = deepcopy(new_filtered_dict)

    # 检查是否为嵌套字典
    if not isinstance(copied_dict, dict) or len(copied_dict) == 0:
        return copied_dict  # 非字典或空字典直接返回

    # 获取第一个子字典的键
    first_key = next(iter(copied_dict.keys()))

    # 仅保留第一个子字典，构建新的字典
    filtered_dict = {first_key: copied_dict[first_key]}

    # 处理第一个子字典，只保留第一个列表，删除其他列表
    if isinstance(filtered_dict[first_key], dict):
        # 存储第一个找到的列表
        first_list = None
        first_list_key = None

        # 遍历子字典寻找第一个列表
        for key, value in filtered_dict[first_key].items():
            if isinstance(value, list):
                first_list = value
                first_list_key = key
                break

        # 如果找到列表，则只保留这个列表，删除其他键值对
        if first_list is not None:
            filtered_dict[first_key] = {first_list_key: first_list}

    return filtered_dict


def execute_abnormal_log_of_generic_audio(cleaner, grouped_dict, jsoner, test_item_count,
                                          language, pattern_name="generic_speaker", is_ai=False):
    json_file_path = None
    json_content = None
    _test_item_count = test_item_count[0]
    second_key_index = 0

    # 获取过滤后的多层字典表
    filtered_dict = cleaner.filter_mic_async_items(grouped_dict)

    # 深拷贝原字典
    new_filtered_dict = copy.deepcopy(filtered_dict)

    # 遍历第一层键
    for first_key in filtered_dict:
        print(f"\n处理第一层键: {first_key}")

        # 获取第二层字典
        second_level_dict = filtered_dict[first_key]

        # 获取新字典中对应的第二层字典
        new_filtered_dict_second_level = new_filtered_dict[first_key]

        # 遍历第二层键
        for second_key in second_level_dict:
            second_key_index = second_key_index + 1
            _test_item_count = _test_item_count + 1
            print(f"  处理第二层键: {second_key}, index：{second_key_index}")

            # 提取 异常测试项中异常的日志内容
            failed_logs = cleaner.extract_mic_failed_logs(second_level_dict[second_key])

            # If failed_logs is an empty list, exit the current second-level
            # loop and continue to the next second_key.
            if not failed_logs:  # Empty list is considered False in boolean judgment
                # Remove this sub-dictionary from the new dictionary
                if second_key in new_filtered_dict_second_level:
                    del new_filtered_dict_second_level[second_key]
                    second_key_index = second_key_index - 1
                    _test_item_count = _test_item_count - 1
                    print(
                        f"  Deleted second-level key: {second_key}, index: {second_key_index} (subtracted the accumulated 1).")

                # Check if the sub-dictionary is empty, delete the first-level key if it is empty.
                if not new_filtered_dict_second_level:
                    del new_filtered_dict[first_key]
                    print(f"  Deleted first-level key: {first_key} because its sub-dictionary is empty.")
                else:
                    print(f"  Retained first-level key: {first_key} because its sub-dictionary still contains content.")

                continue

            # 生成异常测试项的 错误日志字典表（格式化 异常测试项中异常的日志内容）
            failed_logs_dict = cleaner.generic_mic_failed_logs_dict(keep_first_subdict2(new_filtered_dict), failed_logs)
            # failed_logs_dict = generic_failed_logs_dict(filtered_dict, failed_logs)

            # 过滤异常测试项的 错误日志字典表的 重复日志内容
            cleaned_failed_logs_dict = cleaner.filter_mic_duplicate_logs_in_dict(failed_logs_dict)

            # 异常测试项的 错误日志字典表 进行格式化处理
            structured_failed_logs_dict = cleaner.extract_mic_log_data(cleaned_failed_logs_dict)

            # 生成异常测试项的 测试数据分布趋势（中英文）
            mic_test_position = cleaner.analyze_mic_test_position(structured_failed_logs_dict)
            # print(analyzed_data['your_key'][0]['position_cn'])  # 输出中文位置分类
            # print(analyzed_data['your_key'][0]['position'])     # 输出位置比例

            # 使用示例
            structured_failed_logs_dict = cleaner.merge_mic_test_position_v1(structured_failed_logs_dict,
                                                                             mic_test_position)

            def load_patterns_from_json(pattern_name="generic_speaker", json_relative_path='config/clean_filter_data_entity.json'):
                """从JSON文件加载模式列表"""
                json_path = ''
                try:
                    # 拼接得到正确的JSON文件路径
                    if sys.platform.startswith('linux'):
                        # Linux系统使用指定路径
                        json_path = '/opt/xiejun4/pro_PathFinder/config/clean_filter_data_entity.json'
                    else:
                        # Windows系统保持原有路径不变
                        current_dir = os.path.dirname(__file__)
                        json_path = os.path.join(current_dir, json_relative_path)

                    # 读取JSON文件内容
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 截取并处理后拼接
                    result = pattern_name.split("_")[1].upper() + "_TEST_GROUP"
                    print(result)  # 输出: SPEAKER_TEST_GROUP
                    return data.get('Patterns', {}).get('GenericPatterns', {}).get(result, [])

                except FileNotFoundError:
                    print(f"错误: 找不到文件 {json_path}")
                    return []
                except json.JSONDecodeError:
                    print(f"错误: {json_path} 不是有效的JSON文件")
                    return []
                except Exception as e:
                    print(f"加载模式时发生错误: {str(e)}")
                    return []

            # 生成异常测试项的 解释与说明
            # 生成方式：1.正则匹配模板与函数；2.AI模型
            mic_test_purpose2items = None
            if not is_ai:
                try:
                    test_patterns = load_patterns_from_json(pattern_name)
                    mic_test_purpose2items = cleaner.parse_mic_test_purpose2items4(second_key, test_patterns)
                    print(json.dumps(mic_test_purpose2items, ensure_ascii=False, indent=2))
                except ValueError as e:
                    print(e)
            else:
                # 测试目的和测试项说明
                if os.name == 'posix':  # Linux
                    interpreter_path = '/usr/local/bin/python311/bin/python3'
                else:  # windows
                    interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'

                function_name = 'debug_basic_api'
                test_language = '中文' if language == 'zh' else '英文'
                test_item = second_key
                is_filter_think = True
                test_query = (f"使用通俗易懂的{test_language}语言解释说明：{test_item},"
                              f"这里的AUDIO_L2AR_ALERT是扬声器测试，"
                              f"这里的LEFT是左边，LEFT1是左边第1个，LEFT2是左边第2个，以此类推LEFTn是左边第n个，"
                              f"这里的RIGHT是右边，RIGHT1是右边第1个，RIGHT2是右边第2个，以此类推RIGHTn是右边第n个，"
                              f"这里的LEFT，LEFT2，LEFTn后面的_7545_或_12865_这一串数字是采样率，"
                              f"这里的采样率后面的7100_TO_1000Hz的意思是频率范围从7100Hz到1000Hz，格式：数字_TO_数字Hz"
                              f"这里的AUDIO_SAMPLE_MIC是手机MIC录音测试，"
                              f"这里的MIC_1、MIC1都表示是手机麦克1，依次类推MIC_n、MICn表示是手机麦克n，"
                              f"这里的SPK1表示是手机扬声器1，依次类推SPKn表示是手机扬声器n，"
                              f"这里的SPKR1表示是手机右边扬声器1，依次类推SPKRn手机右边扬声器n，"
                              f"这里的SPKL1表示是手机左边扬声器1，依次类推SPKLn手机左边扬声器n，"
                              f"这里的SPKR1,SPKL1后面的_300-5200_是频率范围从300Hz到5200Hz，格式：数字Hz_数字Hz，"
                              f"这里的AUDIO_L2AR_EAR是手机听筒测试，"
                              f"这里的EAR后面的_14705_这一串数字是采样率，"
                              f"这里的采样率后面的7100_TO_1000Hz的意思是频率范围从7100Hz到1000Hz，格式：数字_TO_数字Hz"
                              f"这里的频率范围后的_MIC1_是麦克1，_MIC2_是麦克2，以此类推_MICn_是麦克n，"
                              f"先将：{test_item} 各部分含义解析汇总成有序或无序列表，"
                              f"然后：使用通俗易懂的语言描述，描述内容缩写为50字左右，"
                              f"最后：按照MarkDown的格式输出给我。")

                # 调用外部函数可能产生的异常
                if os.name == 'posix':
                    result = run_ai_api_test_name_describe_for_linux(interpreter_path, function_name, test_query, test_item, test_language, is_filter_think)
                else:
                    result = run_ai_api_test_name_describe_for_windows(interpreter_path, function_name, test_query, test_item, test_language, is_filter_think)

                mic_test_purpose2items = {
                    "test_purpose_zh": result,
                    "test_items_zh": result,
                    "test_purpose_en": result,
                    "test_items_en": result
                }

                # 处理结果可能为空或格式异常的情况
                if not result:
                    raise ValueError("AI 解析返回结果为空")

            # 使用示例
            structured_failed_logs_dict = cleaner.merge_mic_test_purpose2items(structured_failed_logs_dict,
                                                                               mic_test_purpose2items,
                                                                               second_key=second_key + '_FAILED')

            # 绘制异常测试项的图形
            if os.name == 'nt':  # Windows系统
                folder_path = r".\uploads\extracted_logs"
            else:  # Linux/Unix系统
                folder_path = r"/opt/xiejun4/pro_PathFinder/uploads/extracted_logs/"
            chart_items = cleaner.plot_mic_test_results10(structured_failed_logs_dict,
                                                          title=second_key + '_FAILED',
                                                          folder_path=folder_path,
                                                          test_index=1,
                                                          show_image=False)

            if chart_items['base64_content']:
                print(f"图片路径: {chart_items['image_path']}")
                print(f"Base64内容长度: {len(chart_items['base64_content'])}")
                json_content = chart_items['base64_content']
            else:
                print("未生成有效的base64内容")
                json_content = ''

            # 使用示例
            structured_failed_logs_dict = cleaner.merge_mic_test_results_to_dict(structured_failed_logs_dict,
                                                                                 chart_items,
                                                                                 second_key=second_key + '_FAILED')

            # 生成异常测试项的 原因分析与建议
            # 生成方式：1.正则匹配模板与函数；2.AI模型
            chinese_failure_reasons_suggestion = ''
            english_failure_reasons_suggestion = ''
            # TODO: this is place for test item's failure reasons and suggestions
            if not is_ai:
                if pattern_name == "generic_SPEAKER":
                    # 使用示例
                    chinese_failure_reasons_suggestion = cleaner.analyze_speaker_failure_reasons_suggestion4(
                        structured_failed_logs_dict,
                        language='zh',
                        first_key=first_key + '.*FAILED')
                    english_failure_reasons_suggestion = cleaner.analyze_speaker_failure_reasons_suggestion4(
                        structured_failed_logs_dict,
                        language='en',
                        first_key=first_key + '.*FAILED')
                elif pattern_name == "generic_MIC":
                    # 使用示例
                    chinese_failure_reasons_suggestion = cleaner.analyze_mic_failure_reasons_suggestion3(
                        structured_failed_logs_dict,
                        language='zh',
                        first_key=first_key + '.*FAILED')
                    english_failure_reasons_suggestion = cleaner.analyze_mic_failure_reasons_suggestion3(
                        structured_failed_logs_dict,
                        language='en',
                        first_key=first_key + '.*FAILED')
                elif pattern_name == "generic_EAR":
                    # 使用示例
                    chinese_failure_reasons_suggestion = cleaner.analyze_ear_failure_reasons_suggestion3(
                        structured_failed_logs_dict,
                        language='zh',
                        first_key=first_key + '.*FAILED')
                    english_failure_reasons_suggestion = cleaner.analyze_ear_failure_reasons_suggestion3(
                        structured_failed_logs_dict,
                        language='en',
                        first_key=first_key + '.*FAILED')

                # 使用示例
                structured_failed_logs_dict = cleaner.merge_mic_failure_reasons_suggestion(structured_failed_logs_dict,
                                                                                           chinese_failure_reasons_suggestion=chinese_failure_reasons_suggestion,
                                                                                           english_failure_reasons_suggestion=english_failure_reasons_suggestion,
                                                                                           first_key=first_key + '.*FAILED')
            else:
                # TODO: this is place for ai functions
                if os.name == 'posix':  # Linux
                    interpreter_path = '/usr/local/bin/python311/bin/python3'
                else:  # windows
                    interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'
                function_name = 'debug_failure_analysis'
                test_language = language
                test_name = second_key

                # 将测试数据转成AI接口需要的测试数据格式
                def convert_data_items(data_items):
                    # 确保输入可以是单个字典或字典列表
                    if isinstance(data_items, dict):
                        data_items = [data_items]

                    sub_items = []
                    for item in data_items:
                        # 提取各项信息
                        item_name = item.get('Item', '未知项')
                        state = item.get('state', '未知状态').strip('* ').upper()
                        data = item.get('data', '无数据')
                        unit = item.get('unit', '')
                        lowlimit = item.get('lowlimit', '无下限')
                        uplimit = item.get('uplimit', '无上限')
                        position_cn = item.get('position_cn', '位置未知')

                        # 组合成更详细的描述格式
                        detail = (f"{item_name} - {state}，测量值: {data} {unit}，"
                                  f"范围: {lowlimit}-{uplimit} {unit}，结果{position_cn}")
                        sub_items.append(detail)

                    return sub_items

                data_items = structured_failed_logs_dict[first_key][second_key + '_FAILED'].get('data_items', [])
                test_items = convert_data_items(data_items)
                test_status = 'FAILED'
                test_query = (f"这里的AUDIO_L2AR_ALERT是扬声器测试，"
                              f"这里的LEFT是左边，LEFT1是左边第1个，LEFT2是左边第2个，以此类推LEFTn是左边第n个，"
                              f"这里的RIGHT是右边，RIGHT1是右边第1个，RIGHT2是右边第2个，以此类推RIGHTn是右边第n个，"
                              f"这里的LEFT，LEFT2，LEFTn后面的_7545_或_12865_这一串数字是采样率，"
                              f"这里的采样率后面的7100_TO_1000Hz的意思是频率范围从7100Hz到1000Hz，格式：数字_TO_数字Hz"
                              f"这里的AUDIO_SAMPLE_MIC是手机MIC录音测试，"
                              f"这里的MIC_1、MIC1都表示是手机麦克1，依次类推MIC_n、MICn表示是手机麦克n，"
                              f"这里的SPK1表示是手机扬声器1，依次类推SPKn表示是手机扬声器n，"
                              f"这里的SPKR1表示是手机右边扬声器1，依次类推SPKRn手机右边扬声器n，"
                              f"这里的SPKL1表示是手机左边扬声器1，依次类推SPKLn手机左边扬声器n，"
                              f"这里的SPKR1,SPKL1后面的_300-5200_是频率范围从300Hz到5200Hz，格式：数字Hz_数字Hz，"
                              f"这里的AUDIO_L2AR_EAR是手机听筒测试，"
                              f"这里的EAR后面的_14705_这一串数字是采样率，"
                              f"这里的采样率后面的7100_TO_1000Hz的意思是频率范围从7100Hz到1000Hz，格式：数字_TO_数字Hz"
                              f"这里的频率范围后的_MIC1_是麦克1，_MIC2_是麦克2，以此类推_MICn_是麦克n，")
                is_filter_think = True
                test_log_details = None
                # 调用外部函数可能产生的异常
                if os.name == 'posix':  # Linux
                    failure_reasons_suggestion = run_ai_api_failed_log_analysis_suggest_for_linux(interpreter_path, function_name,
                                                                                                  test_name, test_status,
                                                                                                  test_items, test_log_details,
                                                                                                  test_language, test_query,
                                                                                                  is_filter_think)

                else:
                    failure_reasons_suggestion = run_ai_api_failed_log_analysis_suggest_for_windows(interpreter_path, function_name,
                                                                                                    test_name, test_status,
                                                                                                    test_items, test_log_details,
                                                                                                    test_language, test_query,
                                                                                                    is_filter_think)

                # 使用示例
                structured_failed_logs_dict = cleaner.merge_mic_failure_reasons_suggestion(structured_failed_logs_dict,
                                                                                           chinese_failure_reasons_suggestion=failure_reasons_suggestion,
                                                                                           english_failure_reasons_suggestion=failure_reasons_suggestion,
                                                                                           first_key=first_key + '.*FAILED')

            # 生成异常测试项的 json文件
            # 加载json文件对象
            # 5-1.转换 将 json文件 转换为 report类对象
            # 构建JSON模板文件的绝对路径
            if _test_item_count == 1:
                file_path = jsoner.json_template_file
                is_clear = True
            else:
                file_path = jsoner.json_template_file
                is_clear = False

            report = jsoner.convert_json_to_object3(file_path,
                                                    is_clear=is_clear)
            print(report)

            # 使用示例
            if _test_item_count == 1:
                is_clear = True
            else:
                is_clear = False

            updated_report = cleaner.update_mic_report4(report,
                                                        structured_failed_logs_dict,
                                                        first_key=first_key + '.*FAILED',
                                                        language=language,
                                                        is_clear=is_clear)

            # 5-4.保存 json文件
            if _test_item_count == 1:
                is_clear = True
            else:
                is_clear = False

            json_file_path = jsoner.save_json(
                updated_report,
                jsoner.json_template_file,
                is_clear=is_clear)
            jsoner.json_template_file = json_file_path

            # 5-5.将当前子字典表中的第一个list删除
            if new_filtered_dict and first_key in new_filtered_dict:
                # 检查第一个子字典是否包含元素
                if isinstance(new_filtered_dict_second_level[second_key], list) and len(new_filtered_dict_second_level[second_key]) > 0:
                    # 移除第一个子字典中的第一list，因为这个list的异常信息已经处理过了。
                    del new_filtered_dict_second_level[second_key]
                    print(f"已移除子字典'{first_key}'中的第一个list{second_key}")
                else:
                    print(f"子字典'{second_key}'为空或不是列表类型，无法移除元素")
            else:
                print("new_filtered_dict为空或不包含指定的子字典键，无法执行移除操作")

        # 5-6.将当前子字典表删除
        """检查字典中是否包含列表，包括嵌套字典中的列表"""
        if len(new_filtered_dict) > 0:
            # 先判断new_filtered_dict中是否包含first_key
            if first_key in new_filtered_dict:
                # 再检查对应的value是否为字典类型
                if isinstance(new_filtered_dict[first_key], dict):
                    del new_filtered_dict[first_key]
                    print(f"已移除子字典'{first_key}'")
                else:
                    print(f"子字典'{first_key}'不是字典类型，无法移除")
            else:
                print(f"new_filtered_dict中不包含键'{first_key}'，无法执行删除操作")
        else:
            print(f"父字典的子字典表为空，没有可删除的子字典")

        test_item_count[0] = _test_item_count

    return json_content, json_file_path


def execute_abnormal_log_of_wcn_lte_of_mtk(cleaner,
                                           file_dir,
                                           jsoner,
                                           language,
                                           grouped_dict,
                                           is_ai=False):
    # 初始化 容器，变量
    test_process_container = []
    eval_and_log_results_container = []
    satisifed_container = []
    route_container = []
    exception_error_container = []
    exception_error_container_parse = {}
    route_container_parse = {}
    tx_radiated_calibrate = []
    rx_radiated_calibrate = []
    folder_path = ''
    target_pattern = ''
    loop_index = 0
    key_name_test_process1 = ''
    key_name_test_process2 = ''
    key_name_test_process3 = ''
    key_name_test_process4 = ''
    json_file_path = ''
    json_content = ''
    save_path = ''
    test_type = ''
    # 遍历 第一层的key，正则表达式
    for first_key, first_value in grouped_dict.items():
        print(f"第一层键: {first_key}")
        # 检查第一层值是否为字典
        if isinstance(first_value, dict):
            # 遍历 第二层：key是测试项名称，value是每一行记录
            for second_key, second_value in first_value.items():
                print(f"  第二层键: {second_key}")
                print(f"  第二层值: {second_value}")

                # 初始化 容器，变量
                test_process_container = []
                eval_and_log_results_container = []
                satisifed_container = []
                route_container = []
                exception_error_container = []
                exception_error_container_parse = {}
                route_container_parse = {}
                tx_radiated_calibrate = []
                rx_radiated_calibrate = []
                parsed_eval_and_log_results_container = {}
                parsed_eval_and_log_results_cal_container = {}
                parsed_test_process_cal_container = {}

                # 记录循环的index，后面用来表示chart图片的index。
                loop_index = loop_index + 1

                # 3.获取原始数据
                # test_process_container 测试过程中的数据容器
                # eval_and_log_results_container 测试结果的数据容器
                # satisifed_container 测试数据是否稳定的数据容器
                # route_container LTE测试的测试通路的数据容器
                if 'MTK_WLAN2.4G_TX' in second_key or 'MTK_WLAN5G_TX' in second_key:
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_wifi_tx_cal_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'TX_POWER'
                    key_name_test_process2 = 'Measure Process\tTX_POWER Reading '
                    key_name_test_process3 = 'TX_POWER'

                elif 'MTK_WLAN2.4G_RX' in second_key or 'MTK_WLAN5G_RX' in second_key:
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     rx_radiated_calibrate,
                     folder_path) = cleaner.get_wifi_rx_cal_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'RSSI_ANT'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'RSSI_ANT'

                elif re.match(r'MTK_GPS_RX_V\d+_L\d+_-\d+DB', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     rx_radiated_calibrate,
                     folder_path) = cleaner.get_gps_rx_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'GPS_SIGNAL_RX'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'GPS_SIGNAL_RX'

                elif re.match(r'(MTK_BLUETOOTH_TX_POWER_V\d+_CH\d+|'
                              r'MTK_BLUETOOTH_TX_POWER_V\d+_CH\d+_X)', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_bluetooth_tx_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'BLUETOOTH_POWER'
                    key_name_test_process2 = 'Measure Process\tTX_POWER Reading '
                    key_name_test_process3 = 'BLUETOOTH_POWER'

                elif re.match(r'(MTK_MMRF_LTE_BC\d+_TX_\d+DB_V\d+_(H|M|L)CH\d+|'
                              r'^MTK_MMRF_LTE_BC\\d+_TX_\\d+DB_V\\d+_(H|M|L)CH\\d+_ANT_CW)', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     route_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_lte_tx_log_info(second_key, second_value, file_dir)

                    # 3-1.解析 route_container
                    route_container_parse = cleaner.parse_lte_route_info(route_container, second_key)

                    key_name_test_process1 = 'MTK_MMRF_LTE'
                    key_name_test_process2 = 'Measure Process\tTX_POWER Reading '
                    key_name_test_process3 = 'MTK_MMRF_LTE'

                elif re.match(r'(^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_(H|M|L)CH\d+_(EP|ROW)|'
                              r'^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_(H|M|L)CH\d+)', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     route_container,
                     exception_error_container,
                     rx_radiated_calibrate,
                     folder_path) = cleaner.get_lte_rx_log_info(second_key, second_value, file_dir)

                    # 3-1.解析 route_container
                    route_container_parse = cleaner.get_lte_route_info(route_container, second_key)

                    key_name_test_process1 = 'MTK_MMRF_LTE'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'MTK_MMRF_LTE'
                    key_name_test_process4 = 'PREV_CAL'

                    # 4.解析
                    # 4-0.解析 exception_error_container的数据
                    if (re.match(r'^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_(H|M|L)CH\d+_(EP|ROW)', second_key)
                            and exception_error_container
                            and len(exception_error_container) > 1):
                        exception_error_container_parse = cleaner.get_lte_rx_cal_exception_info2(
                            exception_error_container)

                    key_name_test_process1 = 'MTK_MMRF_LTE'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'MTK_MMRF_LTE'
                    key_name_test_process4 = 'PREV_CAL'

                elif 'MTK_META_TRACKID_READ_FROM_MD_NVRAM' in second_key:
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_mtk_meta_trackid_read_from_md_nvram_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'COMMON'
                    key_name_test_process2 = 'COMMON'
                    key_name_test_process3 = 'COMMON'
                    test_type = 'COMMON'

                elif re.match(r'(^MTK_MMRF_NR\d+G_NS\d+_RX_C\d+_V\d+_RSSI_(H|M|L)CH\d+|'
                              r'^MTK_MMRF_NR\d+G_NS\d+_RX_C\d+_V\d+_RSSI_(H|M|L)CH\d+_ANT_CW)', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     route_container,
                     exception_error_container,
                     rx_radiated_calibrate,
                     folder_path) = cleaner.get_ns_rx_log_info_for_mtk(second_key, second_value, file_dir)

                    key_name_test_process1 = 'MTK_MMRF_NR'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'MTK_MMRF_NR'
                    key_name_test_process4 = 'PREV_CAL'

                # 4-0. filter duplicate test items
                def filter_duplicate_test_items(eval_and_log_results_container):
                    """
                    过滤测试结果容器中的重复项和无效记录，保留：
                    1. '# test_result' 标题记录
                    2. 包含完整测试数据的有效记录（每个测试项保留最后一次出现）

                    有效测试记录判定标准：
                    - 以'EvalAndLogResults'开头
                    - 包含至少8个字段（通过制表符分割）
                    - 第4个字段为测试项名称（如MTK_NR5G_...）
                    - 包含具体测试数值（如信号强度、结果状态等）
                    """
                    unique_tests = {}

                    for item in eval_and_log_results_container:
                        # 严格判断有效测试记录：确保字段充足且包含测试项名称和数据
                        if item.startswith("EvalAndLogResults"):
                            fields = item.split('\t')
                            # 有效记录至少需要8个字段（包含测试项名称、数值、状态等）
                            if len(fields) >= 8 and fields[3].strip() != "":  # 测试项名称不为空
                                test_item = fields[3]  # 以测试项名称作为去重依据
                                unique_tests[test_item] = item  # 保留最后一次出现的记录

                    # 提取去重后的有效测试记录
                    filtered_test_results = list(unique_tests.values())

                    # 保留标题记录
                    header_item = [item for item in eval_and_log_results_container if item == '# test_result']

                    # 合并结果
                    final_results = header_item + filtered_test_results

                    return final_results

                eval_and_log_results_container = filter_duplicate_test_items(eval_and_log_results_container)

                # 4-0. Parse the data in exception_error_container
                if len(exception_error_container) > 1:
                    exception_error_container_parse = cleaner.parse_exception_errors(exception_error_container)

                if '_CAL' not in second_key and test_type == '':
                    json_file_path, save_path = generate_json_file_without_using_cal_data(cleaner,
                                                                                          eval_and_log_results_container,
                                                                                          exception_error_container,
                                                                                          exception_error_container_parse,
                                                                                          folder_path,
                                                                                          jsoner,
                                                                                          loop_index,
                                                                                          route_container_parse,
                                                                                          satisifed_container,
                                                                                          save_path,
                                                                                          second_key,
                                                                                          test_process_container,
                                                                                          language,
                                                                                          show_state='FAILED',
                                                                                          platform='MTK',
                                                                                          is_ai=is_ai)

                if '_CAL' in second_key and test_type == '':
                    json_file_path, save_path = generate_json_file_using_cal_data(cleaner,
                                                                                  eval_and_log_results_container,
                                                                                  exception_error_container,
                                                                                  exception_error_container_parse,
                                                                                  folder_path,
                                                                                  json_file_path,
                                                                                  jsoner,
                                                                                  key_name_test_process1,
                                                                                  key_name_test_process2,
                                                                                  key_name_test_process3,
                                                                                  key_name_test_process4,
                                                                                  loop_index,
                                                                                  route_container_parse,
                                                                                  satisifed_container,
                                                                                  save_path,
                                                                                  second_key,
                                                                                  test_process_container,
                                                                                  language,
                                                                                  show_state='FAILED',
                                                                                  platform='MTK',
                                                                                  is_ai=is_ai)

                if '_CAL' not in second_key and test_type == 'COMMON':
                    json_file_path, save_path = generate_json_file_common_data(cleaner,
                                                                               eval_and_log_results_container,
                                                                               exception_error_container,
                                                                               exception_error_container_parse,
                                                                               folder_path,
                                                                               json_file_path,
                                                                               jsoner,
                                                                               key_name_test_process1,
                                                                               key_name_test_process2,
                                                                               key_name_test_process3,
                                                                               key_name_test_process4,
                                                                               loop_index,
                                                                               route_container_parse,
                                                                               satisifed_container,
                                                                               save_path,
                                                                               second_key,
                                                                               test_process_container,
                                                                               language,
                                                                               show_state='FAILED',
                                                                               platform='MTK',
                                                                               is_ai=is_ai)


        else:
            print(f"  第一层值: {first_value}")
    return json_content, json_file_path


def execute_abnormal_log_of_wcn_lte_of_qc(cleaner, file_dir, jsoner, language, grouped_dict, is_ai=False):
    # 初始化 容器，变量
    test_process_container = []
    eval_and_log_results_container = []
    satisifed_container = []
    route_container = []
    exception_error_container = []
    exception_error_container_parse = {}
    route_container_parse = {}
    tx_radiated_calibrate = []
    rx_radiated_calibrate = []
    folder_path = ''
    target_pattern = ''
    loop_index = 0
    key_name_test_process1 = ''
    key_name_test_process2 = ''
    key_name_test_process3 = ''
    key_name_test_process4 = ''
    json_file_path = ''
    json_content = ''
    save_path = ''
    # 遍历 第一层的key，正则表达式
    for first_key, first_value in grouped_dict.items():
        print(f"第一层键: {first_key}")
        # 检查第一层值是否为字典
        if isinstance(first_value, dict):
            # 遍历 第二层：key是测试项名称，value是每一行记录
            for second_key, second_value in first_value.items():
                print(f"  第二层键: {second_key}")
                print(f"  第二层值: {second_value}")

                # 初始化 容器，变量
                test_process_container = []
                eval_and_log_results_container = []
                satisifed_container = []
                route_container = []
                exception_error_container = []
                exception_error_container_parse = {}
                route_container_parse = {}
                tx_radiated_calibrate = []
                rx_radiated_calibrate = []
                parsed_eval_and_log_results_container = {}
                parsed_eval_and_log_results_cal_container = {}
                parsed_test_process_cal_container = {}

                # 记录循环的index，后面用来表示chart图片的index。
                loop_index = loop_index + 1

                # 3.获取原始数据
                # test_process_container 测试过程中的数据容器
                # eval_and_log_results_container 测试结果的数据容器
                # satisifed_container 测试数据是否稳定的数据容器
                # route_container LTE测试的测试通路的数据容器
                if re.match(
                        r'^(QC_WLAN_2\.4GHz_80211[na]_RADIATED_TX_C\d+_(H|M|L)CH_P2K_(TRUE|FALSE)|'
                        r'QC_WLAN_5\.0GHz_80211[na]_RADIATED_TX_C\d+_(H|M|L)CH(\d*?)_P2K_(TRUE|FALSE))',
                        second_key
                ):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_wifi_tx_cal_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'TX_POWER'
                    key_name_test_process2 = 'Measure Process\tTX_POWER Reading '
                    key_name_test_process3 = 'TX_POWER'

                elif re.match(
                        r'^(QC_WLAN_2\.4GHz_80211[na]_RADIATED_RX_C\d+_(H|M|L)CH_EQ|'
                        r'QC_WLAN_5\.0GHz_80211[na]_RADIATED_RX_C\d+_(H|M|L)CH(\d*?)_-?\d+)',
                        second_key
                ):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     rx_radiated_calibrate,
                     folder_path) = cleaner.get_wifi_rx_cal_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'RSSI_ANT'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'RSSI_ANT'

                elif re.match(r'^QC_GPS_RAD_CARRIER_TO_NOISE_GEN\d+_(WR|L\d+_EQ)', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     rx_radiated_calibrate,
                     folder_path) = cleaner.get_gps_rx_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'GPS_SIGNAL_RX'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'GPS_SIGNAL_RX'

                elif re.match(r'^QC_BT_RAD_MEAS_CW_POW_(H|M|L)CH\d+_PRO', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_bluetooth_tx_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'BLUETOOTH_POWER'
                    key_name_test_process2 = 'Measure Process\tTX_POWER Reading '
                    key_name_test_process3 = 'BLUETOOTH_POWER'

                elif re.match(r'^QC_LTE_BC\d+_QRRFR_TX_POWER_(H|M|L)CH_\d+_V\d+', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     route_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_lte_tx_log_info(second_key, second_value, file_dir)

                    # 3-1.解析 route_container
                    route_container_parse = cleaner.parse_lte_route_info(route_container, second_key)

                    key_name_test_process1 = 'MTK_MMRF_LTE'
                    key_name_test_process2 = 'Measure Process\tTX_POWER Reading '
                    key_name_test_process3 = 'MTK_MMRF_LTE'

                elif re.match(r'^QC_LTE_BC\d+_QRRFR_ACTION_V\d+_RX_C\d+_(H|M|L)CH_\d+', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     route_container,
                     exception_error_container,
                     rx_radiated_calibrate,
                     folder_path) = cleaner.get_lte_rx_log_info(second_key, second_value, file_dir)

                    # 3-1.解析 route_container
                    route_container_parse = cleaner.get_lte_route_info(route_container, second_key)

                    key_name_test_process1 = 'MTK_MMRF_LTE'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'MTK_MMRF_LTE'
                    key_name_test_process4 = 'PREV_CAL'

                    # 4.解析
                    # 4-0.解析 exception_error_container的数据
                    if (re.match(r'^QC_LTE_BC\d+_QRRFR_ACTION_V\d+_RX_C\d+_(M|L)CH_\d+', second_key)
                            and exception_error_container
                            and len(exception_error_container) > 1):
                        exception_error_container_parse = cleaner.get_lte_rx_cal_exception_info2(
                            exception_error_container)

                    key_name_test_process1 = 'MTK_MMRF_LTE'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'MTK_MMRF_LTE'
                    key_name_test_process4 = 'PREV_CAL'

                elif re.match(r'^CAPSWTICH_TURBORCHARGE_\w+_\d+W', second_key):
                    target_pattern = first_key
                    (eval_and_log_results_container,
                     exception_error_container,
                     folder_path) = cleaner.get_basic_band_log_info(second_key, second_value, file_dir)

                    key_name_test_process1 = 'CAPSWTICH_TURBORCHARGE'
                    key_name_test_process2 = 'CAPSWTICH_TURBORCHARGE'
                    key_name_test_process3 = 'CAPSWTICH_TURBORCHARGE'

                elif re.match(r'^QC_NS_N\d+_.+?_V\d+_RX_C\d+_(H|M|L)CH_\d+', second_key):
                    target_pattern = first_key
                    (test_process_container,
                     eval_and_log_results_container,
                     satisifed_container,
                     route_container,
                     exception_error_container,
                     tx_radiated_calibrate,
                     folder_path) = cleaner.get_ns_rx_log_info_for_qc(second_key, second_value, file_dir)

                    key_name_test_process1 = 'NS_RX'
                    key_name_test_process2 = 'Measure Process\tSIGNAL_LEVEL Reading '
                    key_name_test_process3 = 'NS_RX'

                # 4-0. Parse the data in exception_error_container
                if len(exception_error_container) > 1:
                    exception_error_container_parse = cleaner.parse_exception_errors(exception_error_container)

                if '_CAL' not in second_key:
                    json_file_path, save_path = generate_json_file_without_using_cal_data(cleaner,
                                                                                          eval_and_log_results_container,
                                                                                          exception_error_container,
                                                                                          exception_error_container_parse,
                                                                                          folder_path,
                                                                                          jsoner,
                                                                                          loop_index,
                                                                                          route_container_parse,
                                                                                          satisifed_container,
                                                                                          save_path,
                                                                                          second_key,
                                                                                          test_process_container,
                                                                                          language,
                                                                                          show_state='FAILED',
                                                                                          platform='Qualcomm',
                                                                                          is_ai=is_ai)

                if '_CAL' in second_key:
                    json_file_path, save_path = generate_json_file_using_cal_data(cleaner,
                                                                                  eval_and_log_results_container,
                                                                                  exception_error_container,
                                                                                  exception_error_container_parse,
                                                                                  folder_path,
                                                                                  json_file_path,
                                                                                  jsoner,
                                                                                  key_name_test_process1,
                                                                                  key_name_test_process2,
                                                                                  key_name_test_process3,
                                                                                  key_name_test_process4,
                                                                                  loop_index,
                                                                                  route_container_parse,
                                                                                  satisifed_container,
                                                                                  save_path,
                                                                                  second_key,
                                                                                  test_process_container,
                                                                                  language='en',
                                                                                  show_state='all',
                                                                                  platform='MTK',
                                                                                  is_ai=is_ai)

        else:
            print(f"  第一层值: {first_value}")
    return save_path, json_file_path


def execute_abnormal_log_of_basic_band(cleaner,
                                       file_dir,
                                       jsoner,
                                       language,
                                       grouped_dict,
                                       base_band_test_item,
                                       show_state='FAILED',
                                       is_ai=False):
    # 初始化 容器，变量
    folder_path = ''
    loop_index = 0
    json_file_path = ''
    json_content = ''
    # 遍历 第一层的key，正则表达式
    for first_key, first_value in grouped_dict.items():
        print(f"第一层键: {first_key}")
        # 检查第一层值是否为字典
        if isinstance(first_value, dict):
            # 遍历 第二层：key是测试项名称，value是每一行记录
            for second_key, second_value in first_value.items():
                print(f"  第二层键: {second_key}")
                print(f"  第二层值: {second_value}")

                # # 初始化 容器，变量
                # eval_and_log_results_container = []
                # exception_error_container = []

                # 记录循环的index，后面用来表示chart图片的index。
                loop_index = loop_index + 1

                # TODO:这里加载clean_filter_data_entity.json正则表达式文件
                # # TODO:这里手动添加正则表达式被替代。
                # # 3.获取原始数据
                # # eval_and_log_results_container 测试结果的数据容器
                # # exception_error_container 测试异常数据的数据容器
                # # folder_path
                # if re.match(r'^(CAPSWTICH_TURBORCHARGE_\w+_\d+W|'
                #             r'^SPKINFOPROGRAMMING_READ|'
                #             r'^ANDROID_GET_BATTERY_LEVEL|'
                #             r'^ANDROID_MAGNETOMETER|'
                #             r'QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW_[0-9A-Z]{2}_[0-9A-Z]{4})',
                #             second_key.upper().replace(' ', '_')):
                #     target_pattern = first_key
                #     (eval_and_log_results_container,
                #      exception_error_container,
                #      folder_path) = cleaner.get_basic_band_log_info(second_key, second_value, file_dir)
                def load_patterns_from_json(json_path):
                    """从JSON文件加载模式列表"""
                    try:
                        # 读取JSON文件内容
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # 提取BasicBandPatterns下的L2AR_BASIC_BAND模式列表
                        return data.get('Patterns', {}).get('BasicBandPatterns', {}).get(base_band_test_item, [])

                    except FileNotFoundError:
                        print(f"错误: 找不到文件 {json_path}")
                        return []
                    except json.JSONDecodeError:
                        print(f"错误: {json_path} 不是有效的JSON文件")
                        return []
                    except Exception as e:
                        print(f"加载模式时发生错误: {str(e)}")
                        return []

                def match_pattern_from_json(second_key, json_relative_path='config/clean_filter_data_entity.json'):
                    """
                    从JSON配置文件加载模式并与处理后的键进行匹配

                    参数:
                        second_key: 需要匹配的原始键
                        json_relative_path: JSON配置文件的相对路径，默认值为'config/clean_filter_data_entity.json'

                    返回:
                        如果匹配成功返回元组(processed_key, combined_regex)，否则返回(None, combined_regex或None)
                    """
                    try:
                        json_path = None
                        # 初始化组合正则表达式变量
                        combined_regex = None
                        # 拼接得到正确的JSON文件路径
                        if sys.platform.startswith('linux'):
                            # Linux系统使用指定路径
                            json_path = '/opt/xiejun4/pro_PathFinder/config/clean_filter_data_entity.json'
                        else:
                            # Windows系统保持原有路径不变
                            current_dir = os.path.dirname(__file__)
                            json_path = os.path.join(current_dir, json_relative_path)

                        # 加载JSON中的模式
                        patterns = load_patterns_from_json(json_path)

                        # 构建正则表达式（将所有模式组合成一个正则表达式）
                        if patterns:
                            # 提取所有正则表达式模式，并移除子模式中可能存在的^锚点
                            all_patterns = []
                            for pattern in patterns:  # 直接遍历列表中的每个模式
                                # 移除每个模式中的^（避免组合后冲突），同时保留模式其他部分
                                cleaned_pattern = pattern.lstrip('^')
                                all_patterns.append(cleaned_pattern)

                            # 组合所有模式为一个正则表达式，只在整体添加^和$锚点
                            # 使用非捕获组(?:...)减少分组数量，提高效率
                            pattern_regex = '|'.join([f'(?:{p})' for p in all_patterns])
                            combined_regex = f'^({pattern_regex})$'  # 确保完全匹配

                            # 处理键并进行匹配
                            try:
                                processed_key = second_key.upper().replace(' ', '_')
                                # 验证正则表达式有效性
                                re.compile(combined_regex)
                                # 执行匹配
                                match = re.match(combined_regex, processed_key)
                            except re.error as e:
                                print(f"正则表达式错误: {str(e)}")
                                print(f"有问题的正则表达式: {combined_regex}")
                                return (None, combined_regex)
                            except Exception as e:
                                print(f"处理键或匹配过程中发生错误: {str(e)}")
                                print(f"处理的键: {second_key}")
                                return (None, combined_regex)

                            if match:
                                print(f"匹配成功: {processed_key}")
                                # 找到具体匹配的模式
                                try:
                                    matched_pattern = next(
                                        p for p in all_patterns
                                        if re.match(f'^{p}$', processed_key)  # 这里单独给每个模式加锚点验证
                                    )
                                    print(f"匹配的模式: {matched_pattern}")
                                except StopIteration:
                                    print(f"匹配成功，但未找到具体对应的模式: {processed_key}")
                                return (processed_key, combined_regex)
                            else:
                                print(f"不匹配: {processed_key}")
                                print(f"使用的正则表达式: {combined_regex}")
                                return (None, combined_regex)
                        else:
                            print("没有加载到任何模式，无法进行匹配")
                            return (None, combined_regex)

                    except Exception as e:
                        print(f"加载配置文件或执行匹配过程中发生错误: {str(e)}")
                        return (None, None)

                # 调用函数并获取结果和正则表达式
                result, combined_regex = match_pattern_from_json(second_key, json_relative_path='config/clean_filter_data_entity.json')
                if result is None:
                    return None

                # 3.获取原始数据
                # target_pattern = first_key
                (eval_and_log_results_container,
                 exception_error_container,
                 folder_path) = cleaner.get_basic_band_log_info(second_key, second_value, file_dir)

                def filter_invalid_exception_data(data):
                    """
                    过滤无效的异常数据：当存在2个或多个包含* FAILED *的项时，移除包含_STATUS的行

                    参数:
                    data (list): 原始数据列表，通常是eval_and_log_results_container

                    返回:
                    list: 过滤后的数据集
                    """
                    # 统计包含 * FAILED * 的行数
                    failed_count = sum(1 for item in data if '* FAILED *' in item)

                    # 根据失败项数量进行过滤
                    if failed_count >= 2:
                        filtered_data = [item for item in data if '_STATUS' not in item]
                    else:
                        filtered_data = data  # 保持原数据不变

                    # 打印处理结果
                    print("处理前数据行数:", len(data))
                    print("失败项数量:", failed_count)
                    print("处理后数据行数:", len(filtered_data))
                    print("\n处理后的数据:")
                    for item in filtered_data:
                        print(item)

                    return filtered_data

                eval_and_log_results_container = filter_invalid_exception_data(eval_and_log_results_container)

                # 4-0. Parse the data in eval_and_log_results
                eval_and_log_results_container_parse = cleaner.parse_test_result_for_basic_band(
                    cleaner.parse_eval_and_log_results_for_basic_band(eval_and_log_results_container))

                # 4-0. Parse the data in exception_error_container
                if len(exception_error_container) > 1:
                    exception_error_container_parse = cleaner.parse_exception_errors_for_basic_band(exception_error_container)

                # 4-5.解析 测试目的和测试项说明
                # parser = BasicBand_TestPurposeAndItems_parser()
                parser = BasicBand_TestPurposeAndItems_parser()
                try:
                    # 根据show_state决定是否需要过滤
                    if show_state.upper() in ["PASSED", "FAILED"]:
                        # 过滤出指定状态的子字典，同时排除test_item含"_RESULT"且low_limit和up_limit均为0的情况
                        filtered_results = {}
                        for key, sub_dict in eval_and_log_results_container_parse.items():
                            # 1. 检查state是否匹配目标状态（忽略大小写）
                            state_match = sub_dict.get('state', '').upper() == show_state.upper()
                            # 2. 检查是否需要排除：test_item含"_RESULT" 且 low_limit=0 且 up_limit=0
                            need_exclude = (
                                    "_RESULT" in sub_dict.get('test_item', '')
                                    and sub_dict.get('low_limit', 0) == 0
                                    and sub_dict.get('up_limit', 0) == 0
                            )
                            # 3. 仅保留状态匹配且不需要排除的子字典
                            if state_match and not need_exclude:
                                filtered_results[key] = sub_dict
                    else:
                        # show_state为"all"或其他值时，保留所有结果
                        filtered_results = eval_and_log_results_container_parse.copy()

                    # 遍历结果进行处理
                    for key, sub_dict in filtered_results.items():
                        # 取出test_item的值作为param
                        param = sub_dict.get('test_item', '').upper().replace(' ', '_')
                        # 如果test_item为空则跳过
                        if not param:
                            continue

                        result = parser.parse_test_parameters(param)

                        if not is_ai:
                            # 将中英文测试目的赋值给meaning字段和indicator字段
                            if language == "zh":
                                sub_dict['meaning'] = result["test_purpose_zh"]
                                print(f"已更新 {key} 的meaning字段: {sub_dict['meaning']}")
                                # 在每个测试项后添加换行符，提高可读性
                                sub_dict['indicator'] = ';\n'.join(result["test_items_zh"])

                            elif language == "en":
                                sub_dict['meaning'] = result["test_purpose_en"]
                                print(f"已更新 {key} 的meaning字段: {sub_dict['meaning']}")
                                # 在每个测试项后添加换行符，提高可读性
                                sub_dict['indicator'] = ';\n'.join(result["test_items_en"])
                        else:
                            # TODO: this is place for ai function
                            # 测试目的和测试项说明
                            if os.name == 'posix':  # Linux
                                interpreter_path = '/usr/local/bin/python311/bin/python3'
                            else:  # windows
                                interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'

                            function_name = 'debug_basic_api'
                            test_language = '中文' if language == 'zh' else '英文'
                            test_item = second_key
                            is_filter_think = True
                            test_query = (f"使用通俗易懂的 {test_language} 语言解释说明：{test_item},"
                                          f"这里的 CAP_SWITCH 是电容开关，TURBO_CHARGER 是快充，CAPSWTICH 是电容开关的简写，TURBORCHARGE 是快充的简写，"
                                          f"这里的 SPK_INFO_PROGAMMING 是扬声器信息编程，SPK 代表扬声器，INFO 是信息，PROGAMMING 是编程，"
                                          f"这里的 BATTERY_LEVELS 是电池电量等级，BATTERY 是电池，LEVELS 是等级（复数表示多个等级），"
                                          f"这里的 ANDROID_MAGNETOMETER 是安卓磁力计，ANDROID 是安卓系统，MAGNETOMETER 是测量磁场的磁力计设备，"
                                          f"这里的 QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW 中，QC 是质量控制，USIM 是通用用户识别模块，MECHANICAL_SWITCH 是机械开关，REMOVED 是移除，RAW 是原始（指原始测试数据 / 结果），"
                                          f"这里的 ANT_CAP_SENSOR_ASM_RESULT_SX9375_8CH_YWQ 中，ANT 是天线，CAP_SENSOR 是电容传感器，ASM_RESULT 是组装结果，SX9375 是电容传感器芯片型号，8CH 是 8 通道，YWQ 是特定标识（如项目 / 部件标识），"
                                          f"这里的 ONLINE_MODE 是在线模式，指设备处于连接网络或在线工作的模式，"
                                          f"先将：{test_item} 各部分含义解析汇总成有序或无序列表，"
                                          f"然后：使用通俗易懂的语言描述，描述内容缩写为 50 字左右，"
                                          f"最后：按照 MarkDown 的格式输出给我。")

                            # 调用外部函数可能产生的异常
                            if os.name == 'posix':
                                result = run_ai_api_test_name_describe_for_linux(interpreter_path, function_name, test_query, test_item, test_language, is_filter_think)
                            else:
                                result = run_ai_api_test_name_describe_for_windows(interpreter_path, function_name, test_query, test_item, test_language, is_filter_think)

                            sub_dict['meaning'] = result
                            sub_dict['indicator'] = result

                            # 处理结果可能为空或格式异常的情况
                            if not result:
                                raise ValueError("AI 解析返回结果为空")

                    # 用处理后的结果替换原字典
                    eval_and_log_results_container_parse = filtered_results

                except ValueError as e:
                    print(f"参数解析错误: {e}")

                # 4-6.生成错误分析与建议"
                for result_key, result_dict in eval_and_log_results_container_parse.items():
                    print(f"\n----- {result_key} 内容 -----")
                    print(f"result_dict:{result_dict}")

                    if not is_ai:
                        issue_suggestion = generate_issue_from_container(language,
                                                                         result_dict,
                                                                         platform='Generic',
                                                                         test_item_desc=second_key.upper().replace(' ', '_'),
                                                                         combined_regex=combined_regex)

                        result_dict['implied_problem_possibility'] = f"{issue_suggestion}"
                    else:
                        # TODO: this is place for ai function
                        if os.name == 'posix':  # Linux
                            interpreter_path = '/usr/local/bin/python311/bin/python3'
                        else:  # windows
                            interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'
                        function_name = 'debug_failure_analysis'
                        test_language = language
                        test_name = second_key

                        # 将测试数据转成AI接口需要的测试数据格式
                        def convert_data_items(data_items):
                            # 确保输入可以是单个字典或字典列表
                            if isinstance(data_items, dict):
                                data_items = [data_items]

                            sub_items = []
                            for item in data_items:
                                # 提取各项信息
                                item_name = item.get('Item', '未知项')
                                state = item.get('state', '未知状态').strip('* ').upper()
                                data = item.get('data', '无数据')
                                unit = item.get('unit', '')
                                lowlimit = item.get('lowlimit', '无下限')
                                uplimit = item.get('uplimit', '无上限')
                                position_cn = item.get('position_cn', '位置未知')

                                # 组合成更详细的描述格式
                                detail = (f"{item_name} - {state}，测量值: {data} {unit}，"
                                          f"范围: {lowlimit}-{uplimit} {unit}，结果{position_cn}")
                                sub_items.append(detail)

                            return sub_items

                        data_items = result_dict[first_key][second_key + '_FAILED'].get('data_items', [])
                        test_items = convert_data_items(data_items)
                        test_status = 'FAILED'
                        test_query = (f"这里的 CAP_SWITCH 是电容开关，TURBO_CHARGER 是快充，CAPSWTICH 是电容开关的简写，TURBORCHARGE 是快充的简写，"
                                      f"这里的 SPK_INFO_PROGAMMING 是扬声器信息编程，SPK 代表扬声器，INFO 是信息，PROGAMMING 是编程，"
                                      f"这里的 BATTERY_LEVELS 是电池电量等级，BATTERY 是电池，LEVELS 是等级（复数表示多个等级），"
                                      f"这里的 ANDROID_MAGNETOMETER 是安卓磁力计，ANDROID 是安卓系统，MAGNETOMETER 是测量磁场的磁力计设备，"
                                      f"这里的 QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW 中，QC 是质量控制，USIM 是通用用户识别模块，MECHANICAL_SWITCH 是机械开关，REMOVED 是移除，RAW 是原始（指原始测试数据 / 结果），"
                                      f"这里的 ANT_CAP_SENSOR_ASM_RESULT_SX9375_8CH_YWQ 中，ANT 是天线，CAP_SENSOR 是电容传感器，ASM_RESULT 是组装结果，SX9375 是电容传感器芯片型号，8CH 是 8 通道，YWQ 是特定标识（如项目 / 部件标识），"
                                      f"这里的 ONLINE_MODE 是在线模式，指设备处于连接网络或在线工作的模式，")
                        is_filter_think = True
                        test_log_details = None
                        # 调用外部函数可能产生的异常
                        if os.name == 'posix':  # Linux
                            failure_reasons_suggestion = run_ai_api_failed_log_analysis_suggest_for_linux(interpreter_path, function_name,
                                                                                                          test_name, test_status,
                                                                                                          test_items, test_log_details,
                                                                                                          test_language, test_query,
                                                                                                          is_filter_think)

                        else:
                            failure_reasons_suggestion = run_ai_api_failed_log_analysis_suggest_for_windows(interpreter_path, function_name,
                                                                                                            test_name, test_status,
                                                                                                            test_items, test_log_details,
                                                                                                            test_language, test_query,
                                                                                                            is_filter_think)
                        result_dict['implied_problem_possibility'] = f"{failure_reasons_suggestion}"

                # 4-7.------------------- 生成绘制折线图，保存绘制折线图，将绘制折线图转换为base64数据并保存到文本 -------------------
                chart_container = cleaner.chart_generate_and_save3_for_basic_band(
                    eval_and_log_results_container_parse,
                    folder_path,
                    show_image=False)

                # 4-8. 解析 图片名称和图片内容
                json_file_name, json_base64 = cleaner.chart_get_base64_read_file(chart_container['chart_content'])
                for result_key, result_dict in eval_and_log_results_container_parse.items():
                    result_dict['chart_name'] = chart_container['chart_name']
                    result_dict['chart_content'] = chart_container['chart_content']
                    result_dict['chart_content'] = json_base64

                # 5.----------------------- json 文件处理 -------------------------
                # 5-1.转换 将 json文件 转换为 report类对象
                report = jsoner.convert_json_to_object3(
                    file_path=jsoner.json_template_file if loop_index == 1 else json_file_path,
                    is_clear=(loop_index == 1))
                print(report)

                def check_overall_state(eval_and_log_results_container_parse):
                    """
                    检查所有测试项的状态，返回整体结果

                    参数:
                        eval_and_log_results_container_parse: 包含多个测试结果的字典容器

                    返回:
                        str: 如果所有测试项状态都是'PASSED'，返回'PASSED'；
                             如果有任何一个测试项状态是'FAILED'，返回'FAILED'
                    """
                    try:
                        # 遍历容器中的每个测试结果
                        for result_key, result_data in eval_and_log_results_container_parse.items():
                            # 获取状态并去除可能的空白字符
                            state = result_data.get('state', '').strip().upper()  # 转为大写，处理可能的大小写不一致

                            # 检查是否有失败的测试项
                            if state == 'FAILED':
                                return 'FAILED'

                        # 如果所有测试项都通过
                        return 'PASSED'

                    except Exception as e:
                        print(f"检查测试状态时出错: {str(e)}")
                        # 出错时可以根据实际需求返回适当的默认值或抛出异常
                        return 'UNKNOWN'  # 未知状态

                # 5-2.更新 Status_Indicators 对象
                report = jsoner.update_status_indicators4(
                    report,
                    second_key.upper().replace(' ', '_'),
                    test_state=check_overall_state(eval_and_log_results_container_parse),
                    is_clear=(loop_index == 1))

                # 5-3.新增 TestProjectResult 对象
                result_dict_index = 0
                for result_key, result_dict in eval_and_log_results_container_parse.items():
                    result_dict_index += 1
                    # 根据索引设置is_clear的值：第一个元素为True，后续为False
                    report = jsoner.process_test_project_result2(report,
                                                                 result_dict,
                                                                 is_clear=(result_dict_index == 1) and (loop_index == 1))

                # 5-4.保存 json文件
                json_file_path = jsoner.save_json(report, jsoner.json_template_file)
                json_content = json_file_path
        else:
            print(f"  第一层值: {first_value}")

    return json_content, json_file_path


def generate_json_file_common_data(cleaner,
                                   eval_and_log_results_container,
                                   exception_error_container,
                                   exception_error_container_parse,
                                   folder_path,
                                   json_file_path,
                                   jsoner,
                                   key_name_test_process1,
                                   key_name_test_process2,
                                   key_name_test_process3,
                                   key_name_test_process4,
                                   loop_index,
                                   route_container_parse,
                                   satisifed_container,
                                   save_path,
                                   second_key,
                                   test_process_container,
                                   language='en',
                                   show_state='all',
                                   platform='MTK',
                                   is_ai=False):
    # 4-1.解析 eval_and_log_results_container的数据
    parsed_eval_and_log_results_cal_container = cleaner.parse_test_result_for_mtk_common(eval_and_log_results_container)

    # # 4-2.解析 test_process_container的数据

    # 4-3.解析 数据范围
    # 提取 parsed_test_process_cal_container 中键为数字的值
    lst_values = cleaner.convert_dict_to_list_for_mtk_common(parsed_eval_and_log_results_cal_container)
    # 从 'TX_POWER' 子字典中获取 low_limit 和 up_limit
    test_result = parsed_eval_and_log_results_cal_container.get('test_result', {})
    low_limit = float(test_result.get('low_limit', 0))
    up_limit = float(test_result.get('up_limit', 0))
    if language == 'en':
        judgment_result = cleaner.parse_judge_value_range3(lst_values,
                                                           low_limit,
                                                           up_limit,
                                                           0.5,
                                                           'en')
        print(f"数据范围: {judgment_result}")
    else:
        judgment_result = cleaner.parse_judge_value_range3(lst_values,
                                                           low_limit,
                                                           up_limit,
                                                           0.5,
                                                           'zh')
        print(f"数据范围: {judgment_result}")

    # 4-4.解析 稳定性
    if language == 'en':
        trend_analysis_en, stability_status_en = cleaner.parse_stability(
            satisifed_container, parsed_eval_and_log_results_cal_container['test_result']['state'],
            language='en')
        print(f"稳定性状态（英文）: {stability_status_en}")
        print(f"趋势分析（英文）: {stability_status_en}")
        parsed_eval_and_log_results_cal_container['test_result']['stability'] = stability_status_en
        parsed_eval_and_log_results_cal_container['test_result']['trend_analysis'] = trend_analysis_en

    else:
        trend_analysis_zh, stability_status_zh = cleaner.parse_stability(
            satisifed_container, parsed_eval_and_log_results_cal_container['test_result']['state'],
            language='zh')
        print(f"稳定性状态（中文）: {stability_status_zh}")
        print(f"趋势分析（英文）: {trend_analysis_zh}")
        parsed_eval_and_log_results_cal_container['test_result']['stability'] = stability_status_zh
        parsed_eval_and_log_results_cal_container['test_result']['trend_analysis'] = trend_analysis_zh

    # 4-5.解析 测试目的和测试项说明
    try:
        result = cleaner.parse_mtk_meta_trackid_from_md_nvram(parsed_eval_and_log_results_cal_container['test_result']['test_item'])
        # 英文的测试目的和测试项说明
        if language == 'en':
            parsed_eval_and_log_results_cal_container['test_result']['meaning'] = result["test_purpose_en"]
            test_items_en_str = '; '.join(result["test_items_en"])
            parsed_eval_and_log_results_cal_container['test_result']['indicator'] = test_items_en_str
        else:
            parsed_eval_and_log_results_cal_container['test_result']['meaning'] = result["test_purpose_zh"]
            test_items_zh_str = '; '.join(result["test_items_zh"])
            parsed_eval_and_log_results_cal_container['test_result']['indicator'] = test_items_zh_str

    except ValueError as e:
        print(f"参数解析错误: {e}")

    # 4-6.解析 异常日志的原因和排查"
    try:
        if language == 'en':
            issue_suggestion_en = generate_issue_analysis_mtk_meta_trackid_from_md_nvram(language, parsed_eval_and_log_results_cal_container['test_result'])
            parsed_eval_and_log_results_cal_container['test_result']['implied_problem_possibility'] = f"{issue_suggestion_en}"
        else:
            issue_suggestion_zh = generate_issue_analysis_mtk_meta_trackid_from_md_nvram(language, parsed_eval_and_log_results_cal_container['test_result'])
            parsed_eval_and_log_results_cal_container['test_result']['implied_problem_possibility'] = f"{issue_suggestion_zh}"

    except ValueError as e:
        print(f"参数解析错误: {e}")

    # 4-7.------------------- 生成绘制折线图，保存绘制折线图，将绘制折线图转换为base64数据并保存到文本 -------------------
    test_index = loop_index
    chart_container = cleaner.chart_generate_generate_and_save_for_mtk_common(
        parsed_eval_and_log_results_cal_container,
        folder_path,
        test_index,
        False)

    # 4-8. 解析 图片名称和图片内容
    parsed_eval_and_log_results_cal_container['test_result']['chart_name'] = chart_container['chart_name']
    json_file_name, json_base64 = cleaner.chart_get_base64_read_file(chart_container['chart_content'])
    parsed_eval_and_log_results_cal_container['test_result']['chart_content'] = json_base64
    print("调试：这里为了能看一下生成的图片。")

    # 5.----------------------- json 文件处理 -------------------------
    failed_loop_index = 0
    if show_state == "all" or parsed_eval_and_log_results_cal_container[key_name_test_process1]['state'] == show_state:
        failed_loop_index = failed_loop_index + 1
        if failed_loop_index == 1:
            _is_clear = True
            json_file_path = jsoner.json_template_file
        else:
            _is_clear = False
            json_file_path = save_path

        # 5-1.转换 将 json文件 转换为 report类对象
        report = jsoner.convert_json_to_object3(json_file_path, is_clear=_is_clear)
        print(report)

        # 5-2.更新 Status_Indicators 对象
        report = jsoner.update_status_indicators3(
            report,
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['test_item'],
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['state'],
            is_clear=_is_clear)

        # 5-3.新增 TestProjectResult 对象
        report = jsoner.process_test_project_result2(report,
                                                     parsed_eval_and_log_results_cal_container[key_name_test_process1],
                                                     is_clear=_is_clear)

        # 5-4.保存 json文件
        save_path = jsoner.save_json(report, json_file_path)

    # if loop_index == 1:
    #     # 5-1.转换 将 json文件 转换为 report类对象
    #     json_file_path = jsoner.json_template_file
    #     report = jsoner.convert_json_to_object3(json_file_path)
    #     print(report)
    #
    #     # 5-2.更新 Status_Indicators 对象
    #     report = jsoner.update_status_indicators3(
    #         report,
    #         parsed_eval_and_log_results_cal_container['test_result']['test_item'],
    #         parsed_eval_and_log_results_cal_container['test_result']['state'])
    #
    #     # 5-3.新增 TestProjectResult 对象
    #     report = jsoner.process_test_project_result2(
    #         report, parsed_eval_and_log_results_cal_container['test_result'])
    #
    #     # 5-4.保存 json文件
    #     save_path = jsoner.save_json(report, json_file_path)
    # else:
    #     # TODO:这里添加哪些测试项与跟FALSE测试项相关的代码，然后将其输出。
    #     # 当show_state为"all"时全部显示
    #     # 当show_state为"pass"或"failed"时只显示对应状态
    #     if (show_state == "all" or
    #             parsed_eval_and_log_results_cal_container['test_result']['state'] == show_state):
    #         json_file_path = save_path
    #         report = jsoner.convert_json_to_object3(json_file_path, is_clear=False)
    #         print(report)
    #
    #         report = jsoner.update_status_indicators3(
    #             report,
    #             parsed_eval_and_log_results_cal_container['test_result']['test_item'],
    #             parsed_eval_and_log_results_cal_container['test_result']['state'],
    #             is_clear=False)
    #
    #         report = jsoner.process_test_project_result2(report,
    #                                                      parsed_eval_and_log_results_cal_container['test_result'],
    #                                                      is_clear=False)
    #
    #         save_path = jsoner.save_json(report, json_file_path, is_clear=False)
    #
    #     json_file_path = save_path

    return save_path, save_path


def generate_json_file_using_cal_data(cleaner,
                                      eval_and_log_results_container,
                                      exception_error_container,
                                      exception_error_container_parse,
                                      folder_path,
                                      json_file_path,
                                      jsoner,
                                      key_name_test_process1,
                                      key_name_test_process2,
                                      key_name_test_process3,
                                      key_name_test_process4,
                                      loop_index,
                                      route_container_parse,
                                      satisifed_container,
                                      save_path,
                                      second_key,
                                      test_process_container,
                                      language='en',
                                      show_state='all',
                                      platform='MTK',
                                      is_ai=False):
    if (re.match(r'^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_MCH\d+_EP', second_key)
            and exception_error_container
            and len(exception_error_container) > 1):
        # 4-1.解析 eval_and_log_results_container的数据
        parsed_eval_and_log_results_cal_container = (
            cleaner.parse_test_result_lte_rx_error_cal2(eval_and_log_results_container))
        key_name_test_process1 = next(iter(parsed_eval_and_log_results_cal_container))
        key_name_test_process2 = next(iter(parsed_eval_and_log_results_cal_container))
        key_name_test_process3 = next(iter(parsed_eval_and_log_results_cal_container))
        # parsed_eval_and_log_results_cal_container = (
        #     cleaner.parse_test_result_lte_rx_error_cal2(eval_and_log_results_container,
        #                                                key_name_test_process1))
        # parsed_eval_and_log_results_cal_container[key_name_test_process1]['low_limit'] = (
        #     parsed_eval_and_log_results_cal_container)[key_name_test_process4]['low_limit']
        # parsed_eval_and_log_results_cal_container[key_name_test_process1]['up_limit'] = (
        #     parsed_eval_and_log_results_cal_container)[key_name_test_process4]['up_limit']

    else:
        # 4-1.解析 eval_and_log_results_container的数据
        parsed_eval_and_log_results_cal_container = (
            cleaner.parse_test_result_cal(eval_and_log_results_container,
                                          key_name_test_process1))

    # 4-2.解析 test_process_container的数据
    parsed_test_process_cal_container, parsed_eval_and_log_results_cal_container = (
        cleaner.parse_test_process_cal(test_process_container,
                                       parsed_eval_and_log_results_cal_container,
                                       folder_path,
                                       key_name_test_process1))

    # 4-3.解析 数据范围
    # 提取 parsed_test_process_cal_container 中键为数字的值
    lst_values = cleaner.convert_dict_to_list(parsed_test_process_cal_container)
    # 从 'TX_POWER' 子字典中获取 low_limit 和 up_limit
    tx_power_info = parsed_eval_and_log_results_cal_container.get(key_name_test_process1, {})
    low_limit = float(tx_power_info.get('low_limit', 0))
    up_limit = float(tx_power_info.get('up_limit', 0))
    if language == 'en':
        judgment_result = cleaner.parse_judge_value_range3(lst_values,
                                                           low_limit,
                                                           up_limit,
                                                           0.5,
                                                           'en')
        print(f"数据范围: {judgment_result}")
    else:
        judgment_result = cleaner.parse_judge_value_range3(lst_values,
                                                           low_limit,
                                                           up_limit,
                                                           0.5,
                                                           'zh')
        print(f"数据范围: {judgment_result}")

    # 4-4.解析 稳定性
    stability_status_zh = ''
    stability_status_en = ''
    if language == 'en':
        stability_status_en, implied_problem_possibility_en = cleaner.parse_stability(
            satisifed_container, parsed_eval_and_log_results_cal_container[key_name_test_process3]['state'],
            language='en')
        print(f"稳定性状态（中文）: {stability_status_zh}")
    else:
        stability_status_zh, implied_problem_possibility_zh = cleaner.parse_stability(
            satisifed_container, parsed_eval_and_log_results_cal_container[key_name_test_process3]['state'],
            language='zh')
        print(f"稳定性状态（英文）: {stability_status_en}")

    # 4-5.解析 测试目的和测试项说明
    try:
        result = []
        # "MTK_WLAN_2.4G_C0_TX_POWER_MCH07_ANT_CW"
        param = parsed_eval_and_log_results_cal_container[key_name_test_process1]['test_item']

        if ('MTK_WLAN2.4G_TX' in second_key or 'MTK_WLAN5G_TX' in second_key) and '_CAL' in second_key:
            result = cleaner.parse_wifi_tx_test_purpose2items_cal(second_key)
        elif ('MTK_WLAN2.4G_RX' in second_key or 'MTK_WLAN5G_RX' in second_key) and '_CAL' in second_key:
            result = cleaner.parse_wifi_rx_test_purpose2items_cal(second_key)
        elif (re.match(r'MTK_GPS_RX_V\d+_L\d+_-\d+DB', second_key)
              and '_CAL' in second_key):
            result = cleaner.parse_gps_rx_test_description2(second_key)
        elif (re.match(r'MTK_BLUETOOTH_TX_POWER_V\d+_CH\d+', second_key)
              and '_CAL' in second_key):
            result = cleaner.parse_bluetooth_tx_test_description(second_key)
        elif (re.match(r'MTK_MMRF_LTE_BC\d+_TX_\d+DB_V\d+_MCH\d+', second_key)
              and '_CAL' in second_key):
            result = cleaner.parse_lte_tx_test_description(second_key)
        elif (re.match(r'^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_MCH\d+_EP', second_key)
              and '_CAL' in second_key):
            result = cleaner.parse_lte_rx_test_description(second_key)

        # 英文的测试目的和测试项说明
        if language == 'en':
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['meaning'] = result["test_purpose_en"]
            test_items_en_str = '; '.join(result["test_items_en"])
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['indicator'] = test_items_en_str
        else:
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['meaning'] = result["test_purpose_zh"]
            test_items_zh_str = '; '.join(result["test_items_zh"])
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['indicator'] = test_items_zh_str

    except ValueError as e:
        print(f"参数解析错误: {e}")

    # 4-6.解析 "趋势分析": "值集中在中位区（稳定）"
    try:
        # "隐含问题可能性": f"低,{异常错误信息}"
        parsed_eval_and_log_results_cal_container[key_name_test_process1]['trend_analysis'] = f'{judgment_result}'
        if (re.match(r'^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_MCH\d+_EP', second_key)
                and '_CAL' in second_key
                and exception_error_container
                and len(exception_error_container) > 1):
            # exception_error = cleaner.parse_lte_rx_cal_exception_error_dict_to_string(
            #     exception_error_container_parse)
            exception_error = parsed_eval_and_log_results_cal_container[key_name_test_process1]['test_data']
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['test_data'] = float('-999')

            if language == 'zh':
                issue_suggestion_zh = generate_issue_from_container(language, parsed_eval_and_log_results_cal_container[key_name_test_process1])
                parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = f"{issue_suggestion_zh}"
                # parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = (f"{exception_error}", f"{issue_suggestion_zh}")
            else:
                issue_suggestion_en = generate_issue_from_container(language, parsed_eval_and_log_results_cal_container[key_name_test_process1])
                parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = f"{issue_suggestion_en}"
                # parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = (f"{exception_error}", f"{issue_suggestion_en}")

        elif exception_error_container and len(exception_error_container) > 1:
            if language == 'zh':
                issue_suggestion_zh = generate_issue_from_container(language, parsed_eval_and_log_results_cal_container[key_name_test_process1])
                parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = f"{issue_suggestion_zh}"
            else:
                issue_suggestion_en = generate_issue_from_container(language, parsed_eval_and_log_results_cal_container[key_name_test_process1])
                parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = f"{issue_suggestion_en}"
        else:
            if language == 'zh':
                issue_suggestion_zh = generate_issue_from_container(language, parsed_eval_and_log_results_cal_container[key_name_test_process1])
                parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = f"{issue_suggestion_zh}"
            else:
                issue_suggestion_en = generate_issue_from_container(language, parsed_eval_and_log_results_cal_container[key_name_test_process1])
                parsed_eval_and_log_results_cal_container[key_name_test_process1]['implied_problem_possibility'] = f"{issue_suggestion_en}"

    except ValueError as e:
        print(f"参数解析错误: {e}")

    # 4-7.------------------- 生成绘制折线图，保存绘制折线图，将绘制折线图转换为base64数据并保存到文本 -------------------
    parsed_test_process_cal_container_chart = cleaner.parse_merge_and_modify_dicts_cal2(
        parsed_test_process_cal_container,
        key_name_test_process2)
    test_index = loop_index
    chart_container = {}
    if not route_container_parse:
        chart_container = cleaner.chart_generate_and_save2(
            parsed_eval_and_log_results_cal_container[key_name_test_process1],
            parsed_test_process_cal_container_chart,
            folder_path,
            test_index,
            False)
    else:
        chart_container = cleaner.chart_generate_and_save3(
            parsed_eval_and_log_results_cal_container[key_name_test_process1],
            parsed_test_process_cal_container_chart,
            route_container_parse,
            folder_path,
            test_index,
            False)

    # 4-8. 解析 图片名称和图片内容
    parsed_eval_and_log_results_cal_container[key_name_test_process1]['chart_name'] = chart_container[
        'chart_name']
    json_file_name, json_base64 = cleaner.chart_get_base64_read_file(chart_container['chart_content'])
    parsed_eval_and_log_results_cal_container[key_name_test_process1]['chart_content'] = json_base64
    print("调试：这里为了能看一下生成的图片。")

    # 5.----------------------- json 文件处理 -------------------------
    failed_loop_index = 0
    if show_state == "all" or parsed_eval_and_log_results_cal_container[key_name_test_process1]['state'] == show_state:
        failed_loop_index = failed_loop_index + 1
        if failed_loop_index == 1:
            _is_clear = True
            json_file_path = jsoner.json_template_file
        else:
            _is_clear = False
            json_file_path = save_path

        # 5-1.转换 将 json文件 转换为 report类对象
        report = jsoner.convert_json_to_object3(json_file_path, is_clear=_is_clear)
        print(report)

        # 5-2.更新 Status_Indicators 对象
        report = jsoner.update_status_indicators3(
            report,
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['test_item'],
            parsed_eval_and_log_results_cal_container[key_name_test_process1]['state'],
            is_clear=_is_clear)

        # 5-3.新增 TestProjectResult 对象
        report = jsoner.process_test_project_result2(report,
                                                     parsed_eval_and_log_results_cal_container[key_name_test_process1],
                                                     is_clear=_is_clear)

        # 5-4.保存 json文件
        save_path = jsoner.save_json(report, json_file_path)

    # if loop_index == 1:
    #     # 5-1.转换 将 json文件 转换为 report类对象
    #     json_file_path = jsoner.json_template_file
    #     report = jsoner.convert_json_to_object3(json_file_path)
    #     print(report)
    #
    #     # 5-2.更新 Status_Indicators 对象
    #     report = jsoner.update_status_indicators3(
    #         report,
    #         parsed_eval_and_log_results_cal_container[key_name_test_process1]['test_item'],
    #         parsed_eval_and_log_results_cal_container[key_name_test_process1]['state'])
    #
    #     # 5-3.新增 TestProjectResult 对象
    #     report = jsoner.process_test_project_result2(report,
    #                                                  parsed_eval_and_log_results_cal_container[key_name_test_process1])
    #
    #     # 5-4.保存 json文件
    #     save_path = jsoner.save_json(report, json_file_path)
    # else:
    #     # TODO:这里添加哪些测试项与跟FALSE测试项相关的代码，然后将其输出。
    #     # 当show_state为"all"时全部显示
    #     # 当show_state为"pass"或"failed"时只显示对应状态
    #     if (show_state == "all" or
    #             parsed_eval_and_log_results_cal_container[key_name_test_process1]['state'] == show_state):
    #         json_file_path = save_path
    #         report = jsoner.convert_json_to_object3(json_file_path, is_clear=False)
    #         print(report)
    #
    #         report = jsoner.update_status_indicators3(
    #             report,
    #             parsed_eval_and_log_results_cal_container[key_name_test_process1]['test_item'],
    #             parsed_eval_and_log_results_cal_container[key_name_test_process1]['state'],
    #             is_clear=False)
    #
    #         report = jsoner.process_test_project_result2(report,
    #                                                      parsed_eval_and_log_results_cal_container[key_name_test_process1],
    #                                                      is_clear=False)
    #
    #         save_path = jsoner.save_json(report, json_file_path, is_clear=False)
    #
    #     json_file_path = save_path

    return save_path, save_path


def generate_json_file_without_using_cal_data(cleaner,
                                              eval_and_log_results_container,
                                              exception_error_container,
                                              exception_error_container_parse,
                                              folder_path,
                                              jsoner,
                                              loop_index,
                                              route_container_parse,
                                              satisifed_container,
                                              save_path,
                                              second_key,
                                              test_process_container,
                                              language='en',
                                              show_state='all',
                                              platform='MTK',
                                              is_ai=False):
    # 4-1.解析 eval_and_log_results_container的数据
    parsed_eval_and_log_results_container = cleaner.parse_test_result(
        eval_and_log_results_container)

    # 4-2.解析 test_process_container的数据
    # 如果列表只有一个元素且为'# test_process'，则不执行解析
    if not (len(test_process_container) == 1 and test_process_container[0] == '# test_process'):
        parsed_test_process_container, parsed_eval_and_log_results_container = (
            cleaner.parse_test_process(test_process_container,
                                       parsed_eval_and_log_results_container,
                                       folder_path))
        values = list(parsed_test_process_container.values())
    else:
        # 添加指定的子字典到test_process_container
        test_process_container.clear()  # 清空原有元素
        test_process_container.append({
            'title_name': '# test_process',
            'Measure Process\tEnd Test Item measure process': '-9999'
        })

        # 初始化目标字典
        parsed_test_process_container = {
            'title_name': 'test_process',
            'Measure Process\tEnd Test Item measure process': '-9999'
        }

        values = '-9999'

    # 4-3.解析 数据范围
    low_limit = float(parsed_eval_and_log_results_container['low_limit'])
    up_limit = float(parsed_eval_and_log_results_container['up_limit'])

    judgment_result = cleaner.parse_judge_value_range(values,
                                                      low_limit,
                                                      up_limit,
                                                      0.5,
                                                      language)
    print(f"数据范围: {judgment_result}")

    # 4-4.解析 稳定性
    stability_status_zh = ''
    implied_problem_possibility_zh = ''
    stability_status_en = ''
    implied_problem_possibility_en = ''
    test_items_zh_str = ''
    test_items_en_str = ''
    if language == 'zh':
        stability_status_zh, implied_problem_possibility_zh = cleaner.parse_stability(
            satisifed_container,
            parsed_eval_and_log_results_container['state'],
            language)
        print(f"稳定性状态（中文）: {stability_status_zh}")
    else:
        stability_status_en, implied_problem_possibility_en = cleaner.parse_stability(
            satisifed_container,
            parsed_eval_and_log_results_container['state'],
            language)
        print(f"稳定性状态（英文）: {stability_status_en}")

    # 4-5.解析 测试目的和测试项说明
    result = []
    param = parsed_eval_and_log_results_container['test_item']
    if is_ai:
        if (loop_index == 1) or (exception_error_container and len(exception_error_container) > 1):
            try:
                # 测试目的和测试项说明
                if os.name == 'posix':  # Linux
                    interpreter_path = '/usr/local/bin/python311/bin/python3'
                else:  # windows
                    interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'

                function_name = 'debug_basic_api'
                test_language = '中文' if language == 'zh' else '英文'
                test_item = param
                is_filter_think = True
                test_query = (f"使用通俗易懂的{test_language}语言解释说明：{test_item},"
                              f"这里的测试项包含QC的是高通，包含MTK的是联发科，"
                              f"这里的测试项是WLAN，Bluetooth，GPS，LTE，NR的测试项，"
                              f"这里的测试项是Tx是发射，RX是接受，"
                              f"MCH：M是中频，L是低频，H是高频，CH是通道，CH后面的数字是通道号，最后的一段内容是产品名称，"
                              f"先将各部分含义解析汇总成有序或无序列表，"
                              f"然后将其通俗易懂的语言，其内容缩写为50字左右，"
                              f"然后按照MarkDown的格式输出给我。")

                # 调用外部函数可能产生的异常
                if os.name == 'posix':
                    result = run_ai_api_test_name_describe_for_linux(interpreter_path, function_name, test_query, test_item, test_language, is_filter_think)
                else:
                    result = run_ai_api_test_name_describe_for_windows(interpreter_path, function_name, test_query, test_item, test_language, is_filter_think)

                # 处理结果可能为空或格式异常的情况
                if not result:
                    raise ValueError("AI 解析返回结果为空")

                # 字符串处理可能产生的异常
                formatted_result = result.replace('；', ';\n')
                parsed_eval_and_log_results_container['meaning'] = formatted_result
                parsed_eval_and_log_results_container['indicator'] = formatted_result
            except subprocess.CalledProcessError as e:
                print(f"外部脚本执行失败: {e.stderr}")
                parsed_eval_and_log_results_container['meaning'] = f"执行失败: 外部命令返回错误"
                parsed_eval_and_log_results_container['indicator'] = f"执行失败: 外部命令返回错误"
    else:
        try:
            if 'MTK_WLAN2.4G_TX' in second_key or 'MTK_WLAN5G_TX' in second_key:
                result = cleaner.parse_wifi_tx_test_purpose2items(param)

            elif 'MTK_WLAN2.4G_RX' in second_key or 'MTK_WLAN5G_RX' in second_key:
                result = cleaner.parse_wifi_rx_test_description_select(param)

            elif re.match(r'MTK_GPS_RX_V\d+_L\d+_-\d+DB', second_key):
                result = cleaner.parse_gps_rx_test_description2(second_key)

            elif re.match(r'^(MTK_BLUETOOTH_TX_POWER_V\d+_CH\d+|'
                          r'MTK_BLUETOOTH_TX_POWER_V\d+_CH\d+_X)', second_key):
                result = cleaner.parse_bluetooth_tx_test_description(second_key)

            elif re.match(r'(MTK_MMRF_LTE_BC\d+_TX_\d+DB_V\d+_(H|M|L)CH\d+|'
                          r'^MTK_MMRF_LTE_BC\\d+_TX_\\d+DB_V\\d+_(H|M|L)CH\\d+_ANT_CW)', second_key):
                result = cleaner.parse_lte_tx_test_description(second_key)

            elif re.match(r'(MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_(H|M|L)CH\d+_(EP|ROW)|'
                          r'MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_(H|M|L)CH\d+)', second_key):
                result = cleaner.parse_lte_rx_test_description(second_key)

            elif re.match(r'(^MTK_MMRF_NR\d+G_NS\d+_RX_C\d+_V\d+_RSSI_(H|M|L)CH\d+|'
                          r'^MTK_MMRF_NR\d+G_NS\d+_RX_C\d+_V\d+_RSSI_(H|M|L)CH\d+_ANT_CW)', second_key):
                result = cleaner.parse_ns_rx_test_description_for_mtk(second_key)

            elif re.match(r'^(QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RADIATED_TX_C\d+_(H|M|L)CH_P2K_(TRUE|FALSE)|'
                          r'QC_WLAN_5\.0GHz_\d+[a-zA-Z]_RADIATED_TX_C\d+_(H|M|L)CH(\d*?)_P2K_(TRUE|FALSE))',
                          second_key
                          ):
                result = cleaner.parse_wifi_tx_test_purpose2items_for_qc(second_key)

            elif re.match(r'^(QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RADIATED_RX_C\d+_(H|M|L)CH_EQ|'
                          r'QC_WLAN_5\.0GHz_\d+[a-zA-Z]_RADIATED_RX_C\d+_(H|M|L)CH(\d*?)_-?\d+|'
                          r'QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RADIATED_RX_C\d+_(H|M|L)CH_EQ|'
                          r'QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RAD_RX_C\d+_CAL_POWER_(H|M|L)CH)',
                          second_key
                          ):
                # 处理匹配到的逻辑
                result = cleaner.parse_wifi_rx_test_description3_for_qc(second_key)

            elif re.match(r'^QC_GPS_RAD_CARRIER_TO_NOISE_GEN\d+_(WR|L\d+_EQ)', second_key):
                result = cleaner.parse_gps_rx_test_description2_for_qc(second_key)

            elif re.match(r'^QC_BT_RAD_MEAS_CW_POW_(H|M|L)CH\d+_PRO', second_key):
                result = cleaner.parse_bluetooth_tx_test_description_for_qc(second_key)

            elif re.match(r'^QC_LTE_BC\d+_QRRFR_TX_POWER_(H|M|L)CH_\d+_V\d+', second_key):
                result = cleaner.parse_lte_tx_test_description_for_qc(second_key)

            elif re.match(r'^QC_LTE_BC\d+_QRRFR_ACTION_V\d+_RX_C\d+_(H|M|L)CH_\d+', second_key):
                result = cleaner.parse_lte_rx_test_description_for_qc(second_key)

            elif re.match(r'^QC_NS_N\d+_.+?_V\d+_RX_C\d+_(H|M|H|L)CH_\d+', second_key):
                result = cleaner.parse_ns_rx_test_description_for_qc(second_key)

            if language == "zh":
                parsed_eval_and_log_results_container['meaning'] = result["test_purpose_zh"]
                # 在每个测试项后添加换行符，提高可读性
                test_items_zh_str = ';\n'.join(result["test_items_zh"])
                parsed_eval_and_log_results_container['indicator'] = test_items_zh_str
            else:
                parsed_eval_and_log_results_container['meaning'] = result["test_purpose_en"]
                # 在每个测试项后添加换行符，提高可读性
                test_items_en_str = ';\n'.join(result["test_items_en"])
                parsed_eval_and_log_results_container['indicator'] = test_items_en_str
        except ValueError as e:
            print(f"参数解析错误: {e}")

    # 4-6.解析 "趋势分析": "值集中在中位区（稳定）",
    # "隐含问题可能性": f"低,{异常错误信息}",
    def convert_data_items(data_item):
        # 提取各项信息
        test_item = data_item.get('test_item', '未知测试项')
        state = data_item.get('state', '未知状态')
        test_data = data_item.get('test_data', '无数据')
        unit = data_item.get('unit', '')
        low_limit = data_item.get('low_limit', '无下限')
        up_limit = data_item.get('up_limit', '无上限')
        trend = data_item.get('trend_analysis', '无趋势分析')
        meaning = data_item.get('meaning', '无说明信息')

        # 拼接成完整描述
        result = [
            f"测试项: {test_item}",
            f"测试状态: {state}",
            f"测试数据: {test_data} {unit} (正常范围: {low_limit}-{up_limit} {unit})",
            f"趋势分析: {trend}",
            f"项目说明:\n{meaning}"  # 合并为一项，通过换行分隔标题和内容
        ]

        # 先合并为字符串，再放入列表中返回
        return ["\n".join(result)]

    if language == "zh":
        parsed_eval_and_log_results_container['trend_analysis'] = f'{judgment_result}({implied_problem_possibility_zh})'
        if exception_error_container and len(exception_error_container) > 1:
            chinese_result = cleaner.translate_exception_dict(exception_error_container_parse, language)
            if is_ai:
                if os.name == 'posix':  # Linux
                    interpreter_path = '/usr/local/bin/python311/bin/python3'
                else:  # windows
                    interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'
                function_name = 'debug_failure_analysis'
                test_language = language
                test_name = second_key
                # 将测试数据转成AI接口需要的测试数据格式
                test_items = convert_data_items(parsed_eval_and_log_results_container)
                test_status = 'FAILED'
                test_query = (f"这里的测试项包含QC的是高通，包含MTK的是联发科，"
                              f"这里的测试项是WLAN，Bluetooth，GPS，LTE，NR的测试项，"
                              f"这里的测试项是Tx是发射，RX是接受，"
                              f"MCH：M是中频，L是低频，H是高频，CH是通道，CH后面的数字是通道号，最后的一段内容是产品名称，")
                is_filter_think = True
                test_log_details = None
                # 调用外部函数可能产生的异常
                if os.name == 'posix':  # Linux
                    issue_suggestion_zh = run_ai_api_failed_log_analysis_suggest_for_linux(interpreter_path, function_name,
                                                                                           test_name, test_status,
                                                                                           test_items, test_log_details,
                                                                                           test_language, test_query,
                                                                                           is_filter_think)

                else:
                    issue_suggestion_zh = run_ai_api_failed_log_analysis_suggest_for_windows(interpreter_path, function_name,
                                                                                             test_name, test_status,
                                                                                             test_items, test_log_details,
                                                                                             test_language, test_query,
                                                                                             is_filter_think)

                parsed_eval_and_log_results_container['implied_problem_possibility'] = issue_suggestion_zh
            else:
                issue_suggestion_zh = generate_issue_from_container(language,
                                                                    parsed_eval_and_log_results_container,
                                                                    platform=platform)
                parsed_eval_and_log_results_container['implied_problem_possibility'] = f"{issue_suggestion_zh}"
                # parsed_eval_and_log_results_container['implied_problem_possibility'] = f"# {chinese_result['Exception error']}\n {issue_suggestion_zh}"
        else:
            pass
            # # just for debug
            # issue_suggestion_zh = generate_issue_from_container(language, parsed_eval_and_log_results_container,platform)
            # parsed_eval_and_log_results_container['implied_problem_possibility'] = f"{issue_suggestion_zh}"
    else:
        parsed_eval_and_log_results_container['trend_analysis'] = f'{judgment_result}({implied_problem_possibility_en})'
        if exception_error_container and len(exception_error_container) > 1:
            english_result = cleaner.translate_exception_dict(exception_error_container_parse, language)
            if is_ai:
                if os.name == 'posix':  # Linux
                    interpreter_path = '/usr/local/bin/python311/bin/python3'
                else:  # windows
                    interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'
                function_name = 'debug_failure_analysis'
                test_language = language
                test_name = second_key
                # 将测试数据转成AI接口需要的测试数据格式
                test_items = convert_data_items(parsed_eval_and_log_results_container)
                test_status = 'FAILED'
                test_query = (f"这里的测试项包含QC的是高通，包含MTK的是联发科，"
                              f"这里的测试项是WLAN，Bluetooth，GPS，LTE，NR的测试项，"
                              f"这里的测试项是Tx是发射，RX是接受，"
                              f"MCH：M是中频，L是低频，H是高频，CH是通道，CH后面的数字是通道号，最后的一段内容是产品名称，")
                is_filter_think = True
                test_log_details = None
                # 调用外部函数可能产生的异常
                if os.name == 'posix':  # Linux
                    issue_suggestion_en = run_ai_api_failed_log_analysis_suggest_for_linux(interpreter_path, function_name,
                                                                                           test_name, test_status,
                                                                                           test_items, test_log_details,
                                                                                           test_language, test_query,
                                                                                           is_filter_think)
                else:
                    issue_suggestion_en = run_ai_api_failed_log_analysis_suggest_for_windows(interpreter_path, function_name, test_name,
                                                                                             test_status, test_items, test_log_details,
                                                                                             test_language, test_query, is_filter_think)

                parsed_eval_and_log_results_container['implied_problem_possibility'] = issue_suggestion_en
            else:
                issue_suggestion_en = generate_issue_from_container(language,
                                                                    parsed_eval_and_log_results_container,
                                                                    platform=platform)
                parsed_eval_and_log_results_container['implied_problem_possibility'] = f"# {issue_suggestion_en}"
                # parsed_eval_and_log_results_container['implied_problem_possibility'] = f"# {english_result['Exception error']}\n {issue_suggestion_en}"
        else:
            pass
            # # just for debug
            # issue_suggestion_en = generate_issue_from_container(language, parsed_eval_and_log_results_container,platform)
            # parsed_eval_and_log_results_container['implied_problem_possibility'] = f"{issue_suggestion_en}"

    # 4-7.------------------- 生成绘制折线图，保存绘制折线图，将绘制折线图转换为base64数据并保存到文本 -------------------
    test_index = loop_index
    chart_container = {}
    if not route_container_parse:
        chart_container = cleaner.chart_generate_and_save2(
            parsed_eval_and_log_results_container,
            parsed_test_process_container,
            folder_path,
            test_index,
            show_image=False)
    else:
        chart_container = cleaner.chart_generate_and_save3(
            parsed_eval_and_log_results_container,
            parsed_test_process_container,
            route_container_parse,
            folder_path,
            test_index,
            show_image=False)

    # 4-8. 解析 图片名称和图片内容
    parsed_eval_and_log_results_container['chart_name'] = chart_container['chart_name']
    json_file_name, json_base64 = cleaner.chart_get_base64_read_file(chart_container['chart_content'])
    # json_file_name, json_base64 = cleaner.chart_get_base64_read_image(chart_container['chart_content'])
    parsed_eval_and_log_results_container['chart_content'] = json_base64
    print("调试：这里为了能看一下生成的图片。")

    # 5.----------------------- json 文件处理 -------------------------
    # TODO:这里添加哪些测试项与跟FALSE测试项相关的代码，然后将其输出。
    # 当show_state为"all"时全部显示
    # 当show_state为"pass"或"failed"时只显示对应状态
    failed_loop_index = 0
    if show_state == "all" or parsed_eval_and_log_results_container['state'] == show_state:
        failed_loop_index = failed_loop_index + 1
        if failed_loop_index == 1:
            _is_clear = True
            json_file_path = jsoner.json_template_file
        else:
            _is_clear = False
            json_file_path = save_path

        # 5-1.转换 将 json文件 转换为 report类对象
        report = jsoner.convert_json_to_object3(json_file_path, is_clear=_is_clear)
        print(report)

        # 5-2.更新 Status_Indicators 对象
        report = jsoner.update_status_indicators3(
            report,
            parsed_eval_and_log_results_container['test_item'],
            parsed_eval_and_log_results_container['state'],
            is_clear=_is_clear)

        # 5-3.新增 TestProjectResult 对象
        report = jsoner.process_test_project_result2(report,
                                                     parsed_eval_and_log_results_container,
                                                     is_clear=_is_clear)

        # 5-4.保存 json文件
        save_path = jsoner.save_json(report, json_file_path, is_clear=_is_clear)

    # 2025-9-18 被替代
    # if loop_index == 1:
    #     # 5-1.转换 将 json文件 转换为 report类对象
    #     json_file_path = jsoner.json_template_file
    #     report = jsoner.convert_json_to_object3(json_file_path)
    #     print(report)
    #
    #     # 5-2.更新 Status_Indicators 对象
    #     report = jsoner.update_status_indicators3(
    #         report,
    #         parsed_eval_and_log_results_container['test_item'],
    #         parsed_eval_and_log_results_container['state'])
    #
    #     # 5-3.新增 TestProjectResult 对象
    #     report = jsoner.process_test_project_result2(report,
    #                                                  parsed_eval_and_log_results_container)
    #
    #     # 5-4.保存 json文件
    #     save_path = jsoner.save_json(report, json_file_path)
    # else:
    #     # TODO:这里添加哪些测试项与跟FALSE测试项相关的代码，然后将其输出。
    #     # 当show_state为"all"时全部显示
    #     # 当show_state为"pass"或"failed"时只显示对应状态
    #     if show_state == "all" or parsed_eval_and_log_results_container['state'] == show_state:
    #         json_file_path = save_path
    #         report = jsoner.convert_json_to_object3(json_file_path, is_clear=False)
    #         print(report)
    #
    #         report = jsoner.update_status_indicators3(
    #             report,
    #             parsed_eval_and_log_results_container['test_item'],
    #             parsed_eval_and_log_results_container['state'],
    #             is_clear=False)
    #
    #         report = jsoner.process_test_project_result2(report,
    #                                                      parsed_eval_and_log_results_container,
    #                                                      is_clear=False)
    #
    #         save_path = jsoner.save_json(report, json_file_path, is_clear=False)
    #
    #     json_file_path = save_path

    return save_path, save_path


def execute_abnormal_log_of_main_processing_logic(cleaner, file_dir, jsoner, language, output_file_path,
                                                  site, platform, base_band_test_item, is_ai=False):
    """
    Process log file based on site and platform type

    Parameters:
    cleaner: Cleaner object for log processing
    file_dir (str): Directory containing the log file
    jsoner: JSON helper object
    language: Language setting
    output_file_path (str): Path to the output log file
    site (str): Site type
    platform (str): Platform type

    Returns:
    dict: JSON content of processed log data
    """

    # Delete .zip and .log_zip files in uploads directory
    def cleanup_uploads_directory():
        if os.name == 'nt':  # Windows
            directory_path = r".\\uploads"
        else:  # Linux
            directory_path = r'/opt/xiejun4/pro_PathFinder/uploads/'
        return unzip_otplus_helper_delete_zip_files(directory_path)

    # Process patterns for given test types and platform
    def get_platform_patterns(platform_key, platform_name, test_types):
        patterns = []
        pattern_names = {}

        for test_type in test_types:
            test_patterns = cleaner.get_patterns(TestSites.L2AR, platform_key, test_type)
            test_name = test_type.upper()  # Convert TestTypes enum value to string
            print(f"{platform_name} {test_name} Test Regex Patterns:", test_patterns)

            patterns.append(test_patterns)
            pattern_names[id(test_patterns)] = f"{platform_name.lower()}_{test_name}"

        return patterns, pattern_names

    # Iterate through patterns and process first match
    def get_patterns_grouped_dic(patterns_list, pattern_names, platform_name):
        grouped_dict = None
        json_content = None
        json_file_path = None

        for patterns_list_item in patterns_list:
            if not patterns_list_item:
                continue

            patterns, grouped_dict = cleaner.group_log_file_content(output_file_path, patterns_list_item)
            if not grouped_dict:
                print("The current document content does not match the regular expression.")
            else:
                pattern_name = pattern_names.get(id(patterns_list_item), "unknown")
                print(f"Successfully matched {pattern_name} patterns in the document.")

                has_matches = False
                for test_item, records in grouped_dict.items():
                    if records:
                        has_matches = True
                        print(f"  Found {len(records)} records for test item: {test_item}")

                if not has_matches:
                    print("  No records found in any test items.")
                else:
                    break  # Exit after first successful match

        return grouped_dict, pattern_name

    def get_patterns_grouped_dic2(patterns_list, pattern_names, platform_name, index=0):
        grouped_dict = None
        json_content = None
        json_file_path = None

        for patterns_list_item in patterns_list:
            if not patterns_list[index]:
                continue

            patterns, grouped_dict = cleaner.group_log_file_content(output_file_path, patterns_list[index])
            if not grouped_dict:
                print("The current document content does not match the regular expression.")
            else:
                pattern_name = pattern_names.get(id(patterns_list[index]), "unknown")
                print(f"Successfully matched {pattern_name} patterns in the document.")

                has_matches = False
                for test_item, records in grouped_dict.items():
                    if records:
                        has_matches = True
                        print(f"  Found {len(records)} records for test item: {test_item}")

                if not has_matches:
                    print("  No records found in any test items.")
                else:
                    break  # Exit after first successful match

        return grouped_dict, pattern_name

    # Main processing logic
    json_content = None
    json_file_path = None
    second_key_index = 0
    test_item_count = [0]
    if site == 'L2AR Site':
        if platform == 'MTK Platform' and base_band_test_item == 'Other Test Type':
            print("Processing L2AR Site with MTK Platform")
            platform_key = Platforms.MTK[0]
            platform_name = "MTK"
            file_dir = os.path.dirname(file_dir)
            test_types = [TestTypes.COMPREHENSIVE_TEST, TestTypes.CALIBRATION]
            mtk_patterns, pattern_names = get_platform_patterns(platform_key, platform_name, test_types)
            grouped_dict, pattern_name = get_patterns_grouped_dic(mtk_patterns, pattern_names, platform_name)
            json_content, json_file_path = execute_abnormal_log_of_wcn_lte_of_mtk(cleaner, file_dir, jsoner, language, grouped_dict, is_ai)

        elif platform == 'Qualcomm Platform' and base_band_test_item == 'Other Test Type':
            print("Processing L2AR Site with Qualcomm Platform")
            platform_key = Platforms.Qualcomm[0]
            platform_name = "Qualcomm"
            file_dir = os.path.dirname(file_dir)
            test_types = [TestTypes.COMPREHENSIVE_TEST, TestTypes.CALIBRATION]
            qualcomm_patterns, pattern_names = get_platform_patterns(platform_key, platform_name, test_types)
            grouped_dict, pattern_name = get_patterns_grouped_dic(qualcomm_patterns, pattern_names, platform_name)
            json_content, json_file_path = execute_abnormal_log_of_wcn_lte_of_qc(cleaner, file_dir, jsoner, language, grouped_dict, is_ai)

        elif platform == 'Generic Platform' and base_band_test_item != 'Other Test Type':
            print("Processing L2AR_Basic_Band")
            platform_key = Platforms.GENERIC_Basic_Band[0]
            platform_name = "GENERIC_Basic_Band"
            file_dir = os.path.dirname(file_dir)
            test_types = [base_band_test_item]
            basic_patterns, basic_names = get_platform_patterns(platform_key, platform_name, test_types)
            grouped_dict, pattern_name = get_patterns_grouped_dic(basic_patterns, basic_names, platform_name)
            json_content, json_file_path = execute_abnormal_log_of_basic_band(cleaner,
                                                                              file_dir,
                                                                              jsoner,
                                                                              language,
                                                                              grouped_dict,
                                                                              base_band_test_item,
                                                                              show_state='FAILED',
                                                                              is_ai=False)

        elif platform == 'Generic Platform' and base_band_test_item == 'Other Test Type':
            print("Processing L2AR Site with Generic Platform")
            platform_key = Platforms.GENERIC[0]
            platform_name = "Generic"

            # Only process audio test types for Generic platform
            test_types = [TestTypes.SPEAKER, TestTypes.MIC, TestTypes.EAR]
            generic_patterns, pattern_names = get_platform_patterns(platform_key, platform_name, test_types)

            json_content = None
            json_file_path = None
            result_json_content = None
            result_json_file_path = None
            pattern_index = -1

            # 遍历generic_patterns列表中的每个元素
            for pattern in generic_patterns:
                pattern_index = pattern_index + 1
                print(f"当前pattern: {pattern}, pattern_index: {pattern_index}")

                grouped_dict, pattern_name = get_patterns_grouped_dic2(generic_patterns,
                                                                       pattern_names,
                                                                       platform_name,
                                                                       pattern_index)

                if pattern_name == "generic_SPEAKER":
                    json_content, json_file_path = execute_abnormal_log_of_generic_audio(cleaner, grouped_dict, jsoner, test_item_count, language, pattern_name, is_ai)
                    # 检查是否获取到有效结果
                    if json_content is not None and json_file_path is not None:
                        result_json_content = json_content
                        result_json_file_path = json_file_path

                elif pattern_name == "generic_MIC":
                    json_content, json_file_path = execute_abnormal_log_of_generic_audio(cleaner, grouped_dict, jsoner, test_item_count, language, pattern_name, is_ai)
                    # 检查是否获取到有效结果
                    if json_content is not None and json_file_path is not None:
                        result_json_content = json_content
                        result_json_file_path = json_file_path

                elif pattern_name == "generic_EAR":
                    json_content, json_file_path = execute_abnormal_log_of_generic_audio(cleaner, grouped_dict, jsoner, test_item_count, language, pattern_name, is_ai)
                    # 检查是否获取到有效结果
                    if json_content is not None and json_file_path is not None:
                        result_json_content = json_content
                        result_json_file_path = json_file_path

            # 如果有任何一组不为空，返回它们
            if result_json_content is not None and result_json_file_path is not None:
                json_content = result_json_content
                json_file_path = result_json_file_path

        else:
            print(f"Unsupported platform: {platform}")
            return ''

        # Cleanup uploads directory
        res = cleanup_uploads_directory()
        print(res)

        # Return JSON content
        if json_content is None:
            print(f"log file: log info of {output_file_path} is empty.")
            return ''
        else:
            if json_file_path:
                print(f"log file: {output_file_path} has been processed.")
                json_content = jsoner.read_json_file(json_file_path)
            return json_content
    else:
        print(f"Unsupported site: {site}")
        return ''


def l2ar_process_log_file(zip_path, language='en', is_ai=False):
    # 1.加载check site and platform, base_band_test_item规则配置
    # 2.check site and platform, base_band_test_item
    site, platform, base_band_test_item = check_file_info(zip_path, _file_info_rules=load_file_info_rules())
    print(f"Site: {site}")
    print(f"Platform: {platform}")
    print(f"base_band_test_item: {base_band_test_item}")

    if site == 'Non-L2AR Site':
        return ''

    # 0.实例化 L2AR的数据清理与过滤类
    cleaner = DataCleaningAndFiltering.L2AR.DataCleaner()
    # 0.实例化 L2AR的Json工具类
    jsoner = JsonDataUtil.L2AR()

    # -------------------- unzip_otplus 调试 -------------------------
    # 复制 xx.log_zip文件，然后重命名 xx.log_zip文件为 xx.zip。
    res = unzip_otplus_helper_rename_log_zip(zip_path)
    print(f'返回值：{res[0]} \n信息：{res[1]}')

    # 创建Path对象并获取父目录
    path_obj = Path(zip_path)
    directory = path_obj.parent
    print(f"目录路径: {directory}")

    # 解压 log_zip文件
    try:
        zip_path_rename = res[2]
    except IndexError:
        print(f"error: result list is not exist element of index 2. zip_path:{zip_path}")
        zip_path_rename = None

    if os.name == 'nt':  # Windows 系统
        config = {
            "zip_file_path": zip_path_rename,
            "folder_in_zip": "prod/log",
            "dest_path": f"{directory}\\extracted_logs",
            "overwrite": True
        }
    else:  # Linux 系统
        config = {
            "zip_file_path": zip_path_rename,
            "folder_in_zip": "prod/log",
            "dest_path": f"{directory}/extracted_logs",
            "overwrite": True
        }

    success, msg = unzip_otplus_helper_unzip_file(**config)
    print(f"\n{'成功' if success else '失败'}: {msg}")
    filter_results = []
    if success:
        keywords = {"_startup", "resourceHistory.xml.txt", ".txt", ".xml"}
        filter_results = unzip_otplus_helper_filter_files2(config["dest_path"], keywords)

        print("\n过滤后保留的文件:")
        for file in filter_results.filtered_files:
            print(file)

    # 0.解析文件信息：获取文件目录，文件名，文件扩展名，不带扩展名的文件名
    file_path, file_dir, file_name, file_ext, file_name_without_ext = cleaner.extract_file_info(
        filter_results.filtered_files[0])

    # 0.清除 log文件中的时间戳和一些无效内容
    if os.name == 'nt':  # Windows 系统
        input_file_path = f'{file_dir}\\{file_name}'
        output_file_path = f'{file_dir}\\{file_name_without_ext}_filter{file_ext}'
    else:  # Linux 系统
        input_file_path = f'{file_dir}/{file_name}'
        output_file_path = f'{file_dir}/{file_name_without_ext}_filter{file_ext}'

    res = cleaner.remove_timestamp2log_level(input_file_path, output_file_path)
    if not res:
        return ''

    json_content = execute_abnormal_log_of_main_processing_logic(cleaner, output_file_path, jsoner, language,
                                                                 output_file_path, site, platform, base_band_test_item, is_ai=is_ai)

    return json_content


if __name__ == "__main__":

    # # debug:pass
    # if os.name =='posix': # Linux
    #     log_file = r"/opt/xiejun4/pro_PathFinder/functions/log/uwsgi/app.log"
    # else: # Windows
    #     log_file = r".\functions\log\uwsgi\app.log"
    #
    # unzip_otplus_helper_rotate_log_file(log_file)

    # # debug:pass
    # if os.name =='posix': # Linux
    #     directory_to_clean = "/opt/xiejun4/pro_PathFinder/uploads/"
    # else: # Windows
    #     directory_to_clean = ".\\uploads"
    #
    # unzip_otplus_helper_delete_zip_files(directory_to_clean)

    if os.name == 'posix':  # Linux
        log_zip_path = '/opt/xiejun4/pro_PathFinder/uploads/machuan_LAR02_TRACKID_fail.log_zip'
    else:  # windows
        log_zip_path = os.path.join(os.path.dirname(__file__),
                                    'uploads',
                                    'NexTestLogs_L2AR_EQUATOR25_INDIA_L2_AR_NPI-EQUATOR25-BE-LAR02_Failed_QC_WLAN_5.0GHz_80211n_RADIATED_TX_C1_HCH156_P2K_TRUE_NEQI270105_2025-08-10_T18-19-37~11.log_zip')
        # log_zip_path = r'D:\PythonProject\pro_PathFinder\uploads\NexTestLogs_L2ARNORM_FUJI25_JAPAN_L2_AR_NORM_BE05-LAR02_Failed_MTK_MMRF_LTE_BC01_RX_C1_RSSI_V9_MCH300_EP_CAL_NF0M4H0120_2025-06-17_T10-47-22_0.log_zip'
        # log_zip_path = r'D:\PythonProject\pro_PathFinder\uploads\NexTestLogs_L2AR_KANSAS25_NA_L2_AR_BE02-LAR08_Failed_AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200_ZT42242JLL_2025-06-28_T22-55-00~23.log_zip'
        # log_zip_path = r'D:\PythonProject\pro_PathFinder\uploads\machuan_L2AR_MTK_pass.log_zip'
        # AR的 mic
        # log_zip_path = r'D:\PythonProject\pro_PathFinder\uploads\NexTestLogs_L2AR_KANSAS25_NA_L2_AR_BE01-LAR10_Failed_AUDIO_SAMPLE_MIC_2_CONTIGUOUS_SPKR2_300-5200_ZT422449TC_2025-06-28_T22-57-28~1359.log_zip'
        # log_zip_path = r'D:\PythonProject\pro_PathFinder\uploads\NexTestLogs_L2AR_URUS25_SUPER_L2_AR_NPI-URUS25-BE-LAR01_Failed_AUDIO_L2AR_ALERT_LEFT_11100_8KHz_TO_140Hz_MIC1left_URUS_N0UR0A0102_2025-07-08_T16-54-56_1.log_zip'
        # AR的 ear
        # log_zip_path = r'D:\PythonProject\pro_PathFinder\uploads\NexTestLogs_L2AR_PORTO25_POWER_PRC_L2_AR_NPI-PORTO25-BE-LAR01_Failed_AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_N6PC270177_2025-07-17_T09-36-02_25.log_zip'
        # AR的 speaker
        # log_zip_path = r'D:\PythonProject\pro_PathFinder\uploads\NexTestLogs_L2AR_FUJI25_JAPAN_L2_AR_NPI-FUJI25-BE-LAR01_Failed_AUDIO_SAMPLE_MIC_1_FFT_44100_4K-16K_SPKR1_MILOS_NF0J490147_2025-06-04_T08-57-36_0.log_zip'

    json_content = l2ar_process_log_file(log_zip_path, language='en', is_ai=False)
    # time.sleep(1)  # 等待1秒，让线程有时间完成并释放资源
    # gc.collect()  # 强制垃圾回收

    if json_content is not None:
        print(json_content)
    else:
        print("无法获取有效的JSON内容")

    # interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'
    # function_name = 'debug_basic_api'
    # test_language = "中文"
    # test_item = "WLAN_QC_TX_MCH1_PORTO_EQ"
    # is_filter_think = True
    # test_query = (f"使用{test_language}解释说明：{test_item},"
    #               f"这里的测试项包含QC的是高通，包含MTK的是联发科，"
    #               f"这里的测试项是WLAN，Bluetooth，GPS，LTE，NR的测试项，"
    #               f"这里的测试项是Tx是发射，RX是接受，"
    #               f"MCH：M是中频，L是低频，H是高频，CH是通道，CH后面的数字是通道号，最后的一段内容是产品名称，"
    #               f"输出内容（要求：1.必须输出## 1. 测试项分解和## 2. 简要描述；2.按照MarkDown的格式输出）："
    #               f"## 1. 测试项分解（要求：1.将各部分含义解析汇总成有序或无序列表），"
    #               f"## 2. 简要描述（要求：1.通俗易懂的语言描述，长度30字左右）。"
    #               )
    #
    # # result_meaning = debug_basic_api(test_query,test_item,test_language,is_filter_think)
    # result_meaning = run_ai_api_test_name_describe_for_windows(interpreter_path, function_name, test_query, test_item, test_language, is_filter_think)
    #
    # interpreter_path = r'C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe'
    # function_name = 'debug_failure_analysis'
    # test_language = "zh"
    # test_name = "WLAN_QC_TX_MCH1_PORTO_EQ"
    # # 将测试数据转成AI接口需要的测试数据格式
    # # 提取各项信息
    # test_item = 'WLAN_QC_TX_MCH1_PORTO_EQ'
    # state = 'FAILED'
    # test_data = '-10'
    # unit = "dBm"
    # low_limit = "10"
    # up_limit = "100"
    # trend = "偏下限"
    # meaning = result_meaning
    # # 拼接成完整描述
    # result = [
    #     f"测试项: {test_item}",
    #     f"测试状态: {state}",
    #     f"测试数据: {test_data} {unit} (正常范围: {low_limit}-{up_limit} {unit})",
    #     f"趋势分析: {trend}",
    #     f"项目说明:\n{meaning}"  # 合并为一项，通过换行分隔标题和内容
    # ]
    # # 先合并为字符串，再放入列表中返回
    # test_items=["\n".join(result)]
    # test_status = 'FAILED'
    # test_query = (f"这里的测试项包含QC的是高通，包含MTK的是联发科，"
    #               f"这里的测试项是WLAN，Bluetooth，GPS，LTE，NR的测试项，"
    #               f"这里的测试项是Tx是发射，RX是接受，"
    #               f"MCH：M是中频，L是低频，H是高频，CH是通道，CH后面的数字是通道号，最后的一段内容是产品名称，")
    # is_filter_think = True
    # test_log_details = None
    # # 调用外部函数可能产生的异常
    # # issue_suggestion_zh = debug_failure_analysis(test_name, test_status, test_items,test_log_details, test_language, test_query, is_filter_think)
    # issue_suggestion_zh = run_ai_api_failed_log_analysis_suggest_for_windows(interpreter_path, function_name,
    #                                                              test_name, test_status, test_items, test_log_details, test_language, test_query, is_filter_think)
