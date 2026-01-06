import pandas as pd
import os
import openpyxl
from typing import Optional


class ExcelReader:
    def __init__(self, file_path):
        """
        初始化Excel读取器
        :param file_path: Excel文件路径
        """
        self.file_path = file_path
        self.data = None

    def read_excel(self):
        """
        读取Excel文件内容
        :return: DataFrame
        """
        try:
            # 读取Excel文件
            self.data = pd.read_excel(self.file_path, header=0)
            return self.data
        except Exception as e:
            print(f"读取Excel文件时发生错误: {e}")
            return None

    def get_column_names(self):
        """
        获取第一行的列标题
        :return: 列标题列表
        """
        if self.data is not None:
            return self.data.columns.tolist()
        else:
            print("请先读取Excel文件")
            return []

    def get_data_by_column(self, column_name):
        """
        根据列名获取数据
        :param column_name: 列名
        :return: 列数据
        """
        if self.data is not None:
            if column_name in self.data.columns:
                return self.data[column_name]
            else:
                print(f"列 '{column_name}' 不存在")
                return None
        else:
            print("请先读取Excel文件")
            return None

    def display_data(self, num_rows=5):
        """
        显示前几行数据
        :param num_rows: 显示的行数
        """
        if self.data is not None:
            print(self.data.head(num_rows))
        else:
            print("请先读取Excel文件")

    def to_json(self, orient='records', force_ascii=False):
        """
        将DataFrame转换为JSON格式
        :param orient: JSON格式 orientation
        :param force_ascii: 是否强制ASCII编码
        :return: JSON字符串
        """
        if self.data is not None:
            return self.data.to_json(orient=orient, force_ascii=force_ascii)
        else:
            print("请先读取Excel文件")
            return None

    def save_json_to_file(self, file_path, orient='records', force_ascii=False, indent=2):
        """
        将DataFrame转换为JSON格式并保存到文件
        :param file_path: 保存文件路径
        :param orient: JSON格式 orientation
        :param force_ascii: 是否强制ASCII编码
        :param indent: JSON缩进空格数
        """
        if self.data is not None:
            try:
                json_data = self.data.to_json(orient=orient, force_ascii=force_ascii)
                # 格式化JSON数据
                import json
                formatted_json = json.dumps(json.loads(json_data), ensure_ascii=False, indent=indent)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_json)
                print(f"JSON数据已保存到 {file_path}")
            except Exception as e:
                print(f"保存JSON文件时发生错误: {e}")
        else:
            print("请先读取Excel文件")


def do_excel_reader_v1(station='JOTSLIM+L2VISION'):
    # Excel文件路径
    excel_file_path = rf".\docs\{station}.xlsx"

    # 创建Excel读取器实例
    reader = ExcelReader(excel_file_path)

    # 读取Excel文件
    data = reader.read_excel()
    if data is not None:
        print("Excel文件读取成功")

        # 显示前5行数据
        print("\n前5行数据:")
        reader.display_data()

        # 获取列标题
        columns = reader.get_column_names()
        print("\n列标题:")
        print(columns)

        # 根据列名获取数据
        if 'Test Group' in columns:
            test_group_data = reader.get_data_by_column('Test Group')
            print("\n'Test Group' 列数据:")
            print(test_group_data)

        # 转换为JSON格式
        json_data = reader.to_json()
        if json_data:
            print("\nJSON格式数据:")
            print(json_data[:500] + "..." if len(json_data) > 500 else json_data)

        # 保存JSON到文件
        reader.save_json_to_file(rf".\\docs\\{station}_output.json")
    else:
        print("Excel文件读取失败")


def do_excel_reader(station: str = 'JOTSLIM+L2VISION') -> Optional[dict]:
    """
    读取Excel文件并处理数据，使用绝对路径确保文件可访问

    参数:
        station: 工作站名称，用于构建文件名

    返回:
        读取的数据，如果失败则返回None
    """
    try:
        # 获取当前脚本所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 构建docs目录的绝对路径
        docs_dir = os.path.join(current_dir, 'docs')

        # 如果docs目录不存在，则创建
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            print(f"已创建docs目录: {docs_dir}")

        # 构建Excel文件的绝对路径
        excel_file_name = f"{station}.xlsx"
        excel_file_path = os.path.join(docs_dir, excel_file_name)

        # 打印文件路径以便调试
        print(f"正在读取Excel文件: {excel_file_path}")

        # 检查文件是否存在
        if not os.path.exists(excel_file_path):
            print(f"错误: Excel文件不存在 - {excel_file_path}")
            return None

        # 检查文件是否可读取
        if not os.access(excel_file_path, os.R_OK):
            print(f"错误: 没有权限读取Excel文件 - {excel_file_path}")
            return None

        # 检查文件大小是否为0
        if os.path.getsize(excel_file_path) == 0:
            print(f"错误: Excel文件为空 - {excel_file_path}")
            return None

        # 创建Excel读取器实例
        reader = ExcelReader(excel_file_path)

        # 读取Excel文件
        print("开始读取Excel文件...")
        data = reader.read_excel()

        if data is None:
            print("错误: read_excel()返回None，读取失败")
            # 检查ExcelReader内部可能的错误信息
            if hasattr(reader, 'error_message'):
                print(f"读取错误详情: {reader.error_message}")
            return None

        print("Excel文件读取成功")

        # 后续处理逻辑...
        # 显示前5行数据
        print("\n前5行数据:")
        reader.display_data()

        # 获取列标题
        columns = reader.get_column_names()
        print("\n列标题:")
        print(columns)

        # 根据列名获取数据
        if 'Test Group' in columns:
            test_group_data = reader.get_data_by_column('Test Group')
            print("\n'Test Group' 列数据:")
            print(test_group_data[:5] if len(test_group_data) > 5 else test_group_data)

        # 转换为JSON格式
        json_data = reader.to_json()
        if json_data:
            print("\nJSON格式数据 (前500字符):")
            print(json_data[:500] + "..." if len(json_data) > 500 else json_data)

        # 构建输出JSON文件的绝对路径
        json_file_name = f"{station}_output.json"
        json_file_path = os.path.join(docs_dir, json_file_name)

        # 保存JSON到文件
        reader.save_json_to_file(json_file_path)
        print(f"\nJSON文件已保存至: {json_file_path}")

        return data

    except Exception as e:
        print(f"处理Excel文件时发生错误: {str(e)}")
        # 打印详细的异常信息，包括堆栈跟踪
        import traceback
        print(f"异常详情: {traceback.format_exc()}")
        return None


def temp():
    # 创建Excel读取器实例前添加详细的文件检查
    file_path = r"C:\\Users\\xiejun4\\Desktop\\pro_PathFinder\\debug\\test9\\docs\\Audio(AR&ACT)+ANT.xlsx"

    # 详细检查文件状态
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件不存在 - {file_path}")
            return None

        # 检查是否是文件（不是目录）
        if not os.path.isfile(file_path):
            print(f"错误：路径指向的不是文件 - {file_path}")
            return None

        # 检查文件是否可读取
        if not os.access(file_path, os.R_OK):
            print(f"错误：没有文件读取权限 - {file_path}")
            return None

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        print(f"文件大小：{file_size} 字节")
        if file_size == 0:
            print(f"错误：文件为空 - {file_path}")
            return None

        # 尝试打开文件（验证文件是否损坏）
        try:
            with open(file_path, 'rb') as f:
                # 读取前1024字节验证文件可打开
                f.read(1024)
            print("文件可以正常打开")
        except Exception as e:
            print(f"错误：无法打开文件 - {str(e)}")
            return None

        # 创建Excel读取器实例
        reader = ExcelReader(file_path)

        # 读取Excel文件
        print("开始读取Excel文件...")
        data = reader.read_excel()

        if data is None:
            print("错误: read_excel()返回None，读取失败")
            # 检查ExcelReader内部可能的错误信息
            if hasattr(reader, 'error_message'):
                print(f"读取错误详情: {reader.error_message}")
            # 检查是否有其他错误信息属性
            elif hasattr(reader, 'last_error'):
                print(f"读取错误详情: {reader.last_error}")
            return None

        print("Excel文件读取成功")
        return data

    except Exception as e:
        print(f"处理过程中发生异常: {str(e)}")
        import traceback
        print(f"异常堆栈: {traceback.format_exc()}")
        return None


# 使用示例
if __name__ == "__main__":
    do_excel_reader()

    # temp()
