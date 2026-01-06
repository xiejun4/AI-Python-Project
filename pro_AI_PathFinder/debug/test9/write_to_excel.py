import json
import sys
import os


def check_libraries():
    """检查必要的库是否可用"""
    print("检查库...")
    try:
        import pandas as pd
        print("pandas 库可用")
    except ImportError as e:
        print(f"pandas 库不可用: {e}")
        return False

    try:
        from openpyxl import Workbook
        print("openpyxl 库可用")
    except ImportError as e:
        print(f"openpyxl 库不可用: {e}")
        return False

    return True


# 读取 JSON 文件
def read_json_file(file_path):
    print(f"尝试读取文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功读取 JSON 文件: {file_path}")
        return data
    except Exception as e:
        print(f"读取 JSON 文件时出错: {e}")
        return None


# 将 JSON 数据转换为列表
def json_to_list(data):
    print("转换 JSON 数据为列表...")
    rows = []

    for test_group, key_parts in data.items():
        for key_part, items in key_parts.items():
            for item in items:
                # 创建一个包含所有字段的字典
                row = {
                    "Test Group": test_group,
                    "Key parts": key_part,
                    "TEST ITEMS": item.get("TEST ITEMS", ""),
                    "Method": item.get("Method", ""),
                    "Test detail information": item.get("Test detail information", ""),
                    "Dependency": item.get("Dependency", ""),
                    "Principle": item.get("Principle", ""),
                    "Impact": item.get("Impact", ""),
                    "Risk": item.get("Risk", ""),
                    "Owner": item.get("Owner", ""),
                    "List of Regular Expressions": ", ".join(item.get("List of Regular Expressions", [])),
                    "AI Prompt - 测试项解释": item.get("AI Prompt", {}).get("测试项解释", ""),
                    "AI Prompt - 异常日志分析与建议": item.get("AI Prompt", {}).get("异常日志分析与建议", "")
                }
                rows.append(row)

    print(f"转换了 {len(rows)} 行数据")
    return rows


# 将列表写入 Excel 文件
def write_list_to_excel(rows, excel_file_path):
    print(f"尝试写入 Excel 文件: {excel_file_path}")
    try:
        import pandas as pd
        # 创建 DataFrame
        df = pd.DataFrame(rows)

        # 写入 Excel 文件
        df.to_excel(excel_file_path, index=False, engine='openpyxl')
        print(f"成功写入 Excel 文件: {excel_file_path}")
    except Exception as e:
        print(f"写入 Excel 文件时出错: {e}")
        import traceback
        traceback.print_exc()


# 主函数
def do_write_json_to_excel(station):
    print("开始执行脚本...")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python 版本: {sys.version}")

    # 检查必要的库
    if not check_libraries():
        print("缺少必要的库，请安装 pandas 和 openpyxl")
        sys.exit(1)

    json_file_path = rf'.\debug\test9\docs\{station}_grouped_output_with_properties.json'
    excel_file_path = rf'.\debug\test9\docs\{station}_new.xlsx'

    print(f"JSON 文件路径: {json_file_path}")
    print(f"Excel 文件路径: {excel_file_path}")

    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"JSON 文件不存在: {json_file_path}")
        sys.exit(1)

    # 读取 JSON 数据
    data = read_json_file(json_file_path)
    if data is None:
        print("无法读取 JSON 数据")
        sys.exit(1)

    # 将 JSON 数据转换为列表
    rows = json_to_list(data)
    if not rows:
        print("没有数据可写入")
        sys.exit(1)

    # 确保输出目录存在
    output_dir = os.path.dirname(excel_file_path)
    if not os.path.exists(output_dir):
        print(f"创建输出目录: {output_dir}")
        os.makedirs(output_dir)

    # 将列表写入 Excel 文件
    write_list_to_excel(rows, excel_file_path)

    print(f'已成功将 JSON 数据写入 {excel_file_path}')


if __name__ == '__main__':
    do_write_json_to_excel()
