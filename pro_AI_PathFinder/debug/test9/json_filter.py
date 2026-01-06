import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# 定义子项的自定义类型
@dataclass
class SubItem:
    line_number: Optional[int] = None
    timestamp: Optional[str] = None
    measure_description: Optional[str] = None
    low_limit: Optional[str] = None
    high_limit: Optional[str] = None
    result: Optional[str] = None
    units: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    meas_code: Optional[str] = None


# 定义主项的自定义类型
@dataclass
class TestLogItem:
    log_type: Optional[str] = None
    test_name: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    duration_ms: Optional[float] = None
    end_time: Optional[str] = None
    log_details: List[str] = None
    sub_items: List[SubItem] = None

    def __post_init__(self):
        # 确保列表属性初始化
        if self.log_details is None:
            self.log_details = []
        if self.sub_items is None:
            self.sub_items = []


# def filter_test_failures(json_file_path: str) -> List[TestLogItem]:
#     """
#     从指定JSON文件中过滤出log_type='测试项'且status='失败'的内容，
#     并返回自定义TestLogItem类型的列表
#
#     参数:
#         json_file_path: JSON文件的路径
#
#     返回:
#         符合条件的TestLogItem对象列表，如果文件不存在或解析错误则返回空列表
#     """
#     try:
#         # 读取JSON文件内容
#         with open(json_file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#
#         # 确保数据是列表类型
#         if not isinstance(data, list):
#             print("JSON数据格式不正确，应为列表类型")
#             return []
#
#         # 过滤符合条件的条目并转换为自定义类型
#         filtered_items: List[TestLogItem] = []
#         for item in data:
#             # 检查是否包含必要的键并符合过滤条件
#             if 'log_type' in item and 'status' in item:
#                 if item['log_type'] == '测试项' and item['status'] == '失败':
#                     # 处理子项
#                     sub_items = []
#                     if 'sub_items' in item and isinstance(item['sub_items'], list):
#                         for sub in item['sub_items']:
#                             sub_item = SubItem(
#                                 line_number=sub.get('line_number'),
#                                 timestamp=sub.get('timestamp'),
#                                 measure_description=sub.get('measure_description'),
#                                 low_limit=sub.get('low_limit'),
#                                 high_limit=sub.get('high_limit'),
#                                 result=sub.get('result'),
#                                 units=sub.get('units'),
#                                 status=sub.get('status'),
#                                 message=sub.get('message'),
#                                 meas_code=sub.get('meas_code')
#                             )
#                             sub_items.append(sub_item)
#
#                     # 创建主项对象
#                     test_item = TestLogItem(
#                         log_type=item.get('log_type'),
#                         test_name=item.get('test_name'),
#                         status=item.get('status'),
#                         start_time=item.get('start_time'),
#                         start_line=item.get('start_line'),
#                         end_line=item.get('end_line'),
#                         duration_ms=item.get('duration_ms'),
#                         end_time=item.get('end_time'),
#                         log_details=item.get('log_details', []),
#                         sub_items=sub_items
#                     )
#
#                     filtered_items.append(test_item)
#
#         print(f"共找到 {len(filtered_items)} 个符合条件的测试项失败记录")
#         return filtered_items
#
#     except FileNotFoundError:
#         print(f"错误: 文件 '{json_file_path}' 不存在")
#         return []
#     except json.JSONDecodeError:
#         print(f"错误: 文件 '{json_file_path}' 不是有效的JSON格式")
#         return []
#     except Exception as e:
#         print(f"处理文件时发生错误: {str(e)}")
#         return []
#
#
# def do_json_filter_process(json_path="logs.json"):
#     # 替换为你的JSON文件路径
#     failures = filter_test_failures(json_path)
#
#     # 打印过滤结果
#     for i, failure in enumerate(failures, 1):
#         print(f"\n第 {i} 个失败的测试项:")
#         print(f"测试名称: {failure.test_name}")
#         print(f"开始时间: {failure.start_time}")
#         print(f"状态: {failure.status}")
#         print(f"开始行号: {failure.start_line}")
#         print(f"结束行号: {failure.end_line}")
#         print(f"子项数量: {len(failure.sub_items)}")
#         print(f"日志详情数量: {len(failure.log_details)}")
#
#     return failures
#
#
# def load_finder_from_file(finder_file_path: str) -> Dict[str, Any]:
#     """从指定路径加载finder JSON文件"""
#     try:
#         with open(finder_file_path, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"错误: 找不到finder文件 - {finder_file_path}")
#         return {}
#     except json.JSONDecodeError:
#         print(f"错误: finder文件不是有效的JSON格式 - {finder_file_path}")
#         return {}
#     except Exception as e:
#         print(f"加载finder文件时发生错误: {str(e)}")
#         return {}
#
#
# def find_matching_info(failures: List[TestLogItem], finder: Dict[str, Any]) -> List[Dict[str, Any]]:
#     """
#     遍历失败的测试项，从finder中查找匹配的信息
#
#     参数:
#         failures: 失败的测试项列表
#         finder: 包含测试项信息的查找字典
#
#     返回:
#         匹配结果列表，每个结果包含测试项和对应的finder信息
#     """
#     matching_results = []
#
#     # 遍历所有失败的测试项
#     for failure in failures:
#         if not failure.test_name:
#             continue  # 跳过没有测试名称的项
#
#         # 遍历finder中的所有测试组
#         for test_group, group_data in finder.items():
#             # 遍历测试组中的所有参数类别（如"时间戳"）
#             for param_category, param_items in group_data.items():
#                 # 遍历每个参数类别下的具体测试项信息
#                 for item_info in param_items:
#                     # 检查是否包含正则表达式列表
#                     if "List of Regular Expressions" in item_info:
#                         patterns = item_info["List of Regular Expressions"]
#
#                         # 尝试用每个正则表达式匹配测试项名称
#                         for pattern in patterns:
#                             if re.match(pattern, failure.test_name):
#                                 # 找到匹配项，添加到结果列表
#                                 matching_results.append({
#                                     "test_item": failure,
#                                     "finder_info": item_info,
#                                     "test_group": test_group,
#                                     "param_category": param_category
#                                 })
#                                 break  # 找到匹配的正则表达式后停止尝试其他模式
#
#     return matching_results
#
#
# def do_find_matching_info_process(failures, finder_file_path=r"C:\Users\xiejun4\Desktop\pro_PathFinder\debug\test9\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json"):
#     # # 指定finder JSON文件路径
#     # finder_file_path = r"C:\Users\xiejun4\Desktop\pro_PathFinder\debug\test9\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json"
#
#     # 加载finder数据
#     finder = load_finder_from_file(finder_file_path)
#     if not finder:
#         print("无法加载finder数据，程序退出")
#         exit(1)
#
#     # 查找匹配信息
#     results = find_matching_info(failures, finder)
#
#     # 打印匹配结果
#     print(f"找到 {len(results)} 个匹配项:")
#     for i, result in enumerate(results, 1):
#         print(f"\n匹配项 {i}:")
#         print(f"测试组: {result['test_group']}")
#         print(f"参数类别: {result['param_category']}")
#         print(f"测试项名称: {result['test_item'].test_name}")
#         print(f"匹配的测试项模板: {result['finder_info']['TEST ITEMS']}")
#         print(f"测试详情: {result['finder_info']['Test detail information']}")
#
#     return results

def filter_test_log_items(json_file_path: str, log_type: str, status: Optional[str] = None) -> List[TestLogItem]:
    """
    从指定JSON文件中过滤出指定log_type的内容，可选地指定status过滤条件，
    并返回自定义TestLogItem类型的列表

    参数:
        json_file_path: JSON文件的路径
        log_type: 要过滤的日志类型（如'测试项'、'系统级'）
        status: 可选，要过滤的状态（如'失败'、'成功'）

    返回:
        符合条件的TestLogItem对象列表，如果文件不存在或解析错误则返回空列表
    """
    try:
        # 读取JSON文件内容
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 确保数据是列表类型
        if not isinstance(data, list):
            print("JSON数据格式不正确，应为列表类型")
            return []

        # 过滤符合条件的条目并转换为自定义类型
        filtered_items: List[TestLogItem] = []
        for item in data:
            # 检查是否包含必要的键并符合过滤条件
            if 'log_type' in item and item['log_type'] == log_type:
                # 如果指定了状态过滤，则检查状态是否匹配
                if status is not None:
                    if 'status' not in item or item['status'] != status:
                        continue  # 状态不匹配，跳过
                else:
                    # 如果没有指定状态过滤，即使没有status字段也保留
                    pass

                # 处理子项
                sub_items = []
                if 'sub_items' in item and isinstance(item['sub_items'], list):
                    for sub in item['sub_items']:
                        sub_item = SubItem(
                            line_number=sub.get('line_number'),
                            timestamp=sub.get('timestamp'),
                            measure_description=sub.get('measure_description'),
                            low_limit=sub.get('low_limit'),
                            high_limit=sub.get('high_limit'),
                            result=sub.get('result'),
                            units=sub.get('units'),
                            status=sub.get('status'),
                            message=sub.get('message'),
                            meas_code=sub.get('meas_code')
                        )
                        sub_items.append(sub_item)

                # 创建主项对象
                test_item = TestLogItem(
                    log_type=item.get('log_type'),
                    test_name=item.get('test_name'),
                    status=item.get('status'),
                    start_time=item.get('start_time'),
                    start_line=item.get('start_line'),
                    end_line=item.get('end_line'),
                    duration_ms=item.get('duration_ms'),
                    end_time=item.get('end_time'),
                    log_details=item.get('log_details', []),
                    sub_items=sub_items
                )

                filtered_items.append(test_item)

        print(f"共找到 {len(filtered_items)} 个符合条件的{log_type}记录")
        if status:
            print(f"状态筛选条件: {status}")
        return filtered_items

    except FileNotFoundError:
        print(f"错误: 文件 '{json_file_path}' 不存在")
        return []
    except json.JSONDecodeError:
        print(f"错误: 文件 '{json_file_path}' 不是有效的JSON格式")
        return []
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}")
        return []


def do_json_filter_process(json_path=r".\logs\extracted_logs\parsed_log_output_fixed.json",
                           log_type="测试项",
                           status="失败"):
    """处理JSON过滤的流程函数"""
    # 调用通用过滤函数
    filtered_items = filter_test_log_items(json_path, log_type, status)

    # 打印过滤结果
    for i, item in enumerate(filtered_items, 1):
        print(f"\n第 {i} 个{log_type}记录:")
        print(f"名称: {item.test_name or 'N/A'}")
        print(f"开始时间: {item.start_time or 'N/A'}")
        print(f"状态: {item.status or 'N/A'}")
        print(f"开始行号: {item.start_line or 'N/A'}")
        print(f"结束行号: {item.end_line or 'N/A'}")
        print(f"子项数量: {len(item.sub_items)}")
        print(f"日志详情数量: {len(item.log_details)}")

    return filtered_items


def load_finder_from_file(finder_file_path: str) -> Dict[str, Any]:
    """从指定路径加载finder JSON文件"""
    try:
        with open(finder_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到finder文件 - {finder_file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"错误: finder文件不是有效的JSON格式 - {finder_file_path}")
        return {}
    except Exception as e:
        print(f"加载finder文件时发生错误: {str(e)}")
        return {}


def find_matching_info(failures: List[TestLogItem], finder: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    遍历失败的测试项，从finder中查找匹配的信息

    参数:
        failures: 失败的测试项列表
        finder: 包含测试项信息的查找字典

    返回:
        匹配结果列表，每个结果包含测试项和对应的finder信息
    """
    matching_results = []

    # 遍历所有失败的测试项
    for failure in failures:
        if not failure.test_name:
            continue  # 跳过没有测试名称的项

        # 遍历finder中的所有测试组
        for test_group, group_data in finder.items():
            # 遍历测试组中的所有参数类别（如"时间戳"）
            for param_category, param_items in group_data.items():
                # 遍历每个参数类别下的具体测试项信息
                for item_info in param_items:
                    # 检查是否包含正则表达式列表
                    if "List of Regular Expressions" in item_info:
                        patterns = item_info["List of Regular Expressions"]

                        # 尝试用每个正则表达式匹配测试项名称
                        for pattern in patterns:
                            if re.match(pattern, failure.test_name):
                                # 找到匹配项，添加到结果列表
                                matching_results.append({
                                    "test_item": failure,
                                    "finder_info": item_info,
                                    "test_group": test_group,
                                    "param_category": param_category
                                })
                                break  # 找到匹配的正则表达式后停止尝试其他模式

    return matching_results

def find_matching_info_single(failure: TestLogItem, finder: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从单个测试项中，从finder中查找匹配的信息

    参数:
        failure: 单个失败的测试项
        finder: 包含测试项信息的查找字典

    返回:
        匹配结果列表，每个结果包含测试项和对应的finder信息
    """
    matching_results = []
    
    if not failure.test_name:
        return matching_results  # 没有测试名称，直接返回空列表

    # 遍历finder中的所有测试组
    for test_group, group_data in finder.items():
        # 遍历测试组中的所有参数类别（如"时间戳"）
        for param_category, param_items in group_data.items():
            # 遍历每个参数类别下的具体测试项信息
            for item_info in param_items:
                # 检查是否包含正则表达式列表
                if "List of Regular Expressions" in item_info:
                    patterns = item_info["List of Regular Expressions"]

                    # 尝试用每个正则表达式匹配测试项名称
                    for pattern in patterns:
                        if re.match(pattern, failure.test_name):
                            # 找到匹配项，添加到结果列表
                            matching_results.append({
                                "test_item": failure,
                                "finder_info": item_info,
                                "test_group": test_group,
                                "param_category": param_category
                            })
                            break  # 找到匹配的正则表达式后停止尝试其他模式

    return matching_results


def do_find_matching_info_process(failure: TestLogItem,
                                  finder_file_path=r"debug\test9\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json"):
    # # 指定finder JSON文件路径
    # finder_file_path = r"C:\Users\xiejun4\Desktop\pro_PathFinder\debug\test9\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json"

    # 加载finder数据
    finder = load_finder_from_file(finder_file_path)
    if not finder:
        print("无法加载finder数据，程序退出")
        exit(1)

    # 假设failures已定义
    # failures = [TestLogItem(...), ...]

    # 查找匹配信息
    # results = find_matching_info(failures, finder)
    results = find_matching_info_single(failure, finder)

    # 打印匹配结果
    print(f"找到 {len(results)} 个匹配项:")
    for i, result in enumerate(results, 1):
        print(f"\n匹配项 {i}:")
        print(f"测试组: {result['test_group']}")
        print(f"参数类别: {result['param_category']}")
        print(f"测试项名称: {result['test_item'].test_name}")
        print(f"匹配的测试项模板: {result['finder_info']['TEST ITEMS']}")
        print(f"测试详情: {result['finder_info']['Test detail information']}")

    return results


# 使用示例
if __name__ == "__main__":
    # failures = do_json_filter_process()
    # results = do_find_matching_info_process(failures,
    #                               finder_file_path=r".\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json")

    # 过滤系统级日志（不指定状态）
    print("=== 系统级日志 ===")
    system_items = do_json_filter_process(
        json_path=r".\logs\extracted_logs\parsed_log_output_fixed.json",
        log_type="系统级",
        status=None  # 系统级日志可能没有status字段，所以不指定
    )

    results = do_find_matching_info_process(system_items,
                                            finder_file_path=r".\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json")


    # 过滤失败的测试项（保持原有功能）
    print("\n=== 失败的测试项 ===")
    failed_tests = do_json_filter_process(
        json_path=r".\logs\extracted_logs\parsed_log_output_fixed.json",
        log_type="测试项",
        status="失败"
    )

    results = do_find_matching_info_process(failed_tests,
                                            finder_file_path=r".\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json")


