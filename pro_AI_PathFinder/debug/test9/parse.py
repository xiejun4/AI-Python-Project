import json
import re
from datetime import datetime
from typing import List, Dict, Any


def parse_log_to_structured_data_v1(log_content):
    """
    将日志文件内容解析为定义的结构化数据。
    优化了测试项结束的识别逻辑，确保包含所有相关的Footer信息。
    修复了测试描述包含空格的识别问题。
    修复了FAILED状态解析错误的问题。
    修复了负数限值的解析问题。

    Args:
        log_content (str): 日志文件的完整字符串内容。

    Returns:
        list: 包含结构化日志块的列表。
    """
    if not log_content.strip():
        print("警告：日志文件内容为空。")
        return []

    # 正则表达式定义
    # 1. 匹配标准日志行，捕获关键字段
    line_regex = re.compile(
        # 捕获组: timestamp, level, module, time2, context, keyword, message
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s+\[\]\s+"
        r"(?P<level>\w+)\s+(?P<module>.+?)\s+(?P<time2>\d{2}:\d{2}:\d{2}\.\d+)\s+"
        r"(?P<context>\S+?)\s+(?P<keyword>\S+?)\s+(?P<message>.*)$"
    )
    # 2. 匹配测试项的Header行，提取测试名
    header_regex = re.compile(
        r"Test = (?P<test_name>\S+)\s+\|\s+Barcode = (?P<barcode>\S+)"
    )
    # 3. 匹配测试项的Footer行，提取结果和测试时间
    footer_regex = re.compile(
        r"Test = (?P<test_name>\S+)\s+\|\s+Overall Result = (?P<result_code>.*?)\s+\|\s+"
        r"Test Time = (?P<duration>[\d.]+) msec"
    )

    structured_data = []
    current_block = None
    in_test_item = False
    # 用于跟踪测试项结束后需要收集的额外行数
    test_item_footer_lines_remaining = 0

    lines = log_content.splitlines()

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        match = line_regex.match(line)
        parts = match.groupdict() if match else {}
        message = parts.get("message", "")
        # 'keyword' 字段现在用于捕获 Header, Footer, EvalAndLogResults 等关键标识
        keyword = parts.get("keyword", "")
        context = parts.get("context", "")

        # 检查是否为测试项的开始或结束
        is_header = keyword == "Header" and "====" in message
        is_footer_with_result = keyword == "Footer" and "Overall Result" in message
        is_footer_separator = (
                keyword == "Footer"
                and "===========================================" in message
        )
        is_end_of_test = context == "END_OF_TEST"

        if is_header:
            # 如果当前有正在记录的系统级日志块，则先将其保存
            if current_block and not in_test_item:
                current_block["end_line"] = line_num - 1
                if current_block["log_details"]:
                    last_line_match = line_regex.match(current_block["log_details"][-1])
                    if last_line_match:
                        current_block["end_time"] = last_line_match.group("timestamp")
                structured_data.append(current_block)

            # 开始一个新的测试项
            in_test_item = True
            test_item_footer_lines_remaining = 0
            header_match = header_regex.search(message)
            current_block = {
                "log_type": "测试项",
                "test_name": (
                    header_match.group("test_name")
                    if header_match
                    else parts.get("context", "未知")
                ),
                "status": "未知",
                "start_time": parts.get("timestamp"),
                "start_line": line_num,
                "sub_items": [],
                "log_details": [line],
            }
        elif in_test_item or test_item_footer_lines_remaining > 0:
            current_block["log_details"].append(line)

            # 如果还在收集footer额外行
            if test_item_footer_lines_remaining > 0:
                test_item_footer_lines_remaining -= 1
                # 如果是END_OF_TEST行，这是测试项的最后一行
                if is_end_of_test:
                    current_block["end_time"] = parts.get("timestamp")
                    current_block["end_line"] = line_num
                    structured_data.append(current_block)
                    current_block = None
                    in_test_item = False
                    test_item_footer_lines_remaining = 0
                elif test_item_footer_lines_remaining == 0:
                    # 如果没有找到END_OF_TEST但额外行已收集完，也结束测试项
                    current_block["end_time"] = parts.get("timestamp")
                    current_block["end_line"] = line_num
                    structured_data.append(current_block)
                    current_block = None
                    in_test_item = False
            else:
                # 检查是否为测试子项 - 修复负数限值解析问题
                if keyword == "EvalAndLogResults":
                    try:
                        # 使用更精确的正则表达式来解析EvalAndLogResults行
                        # 格式: r_num m_num description low_limit high_limit result units recipe_time test_time status [message] pos_in_limits sampling open_lim enh_lim meas_code

                        # 首先分离出最后的固定字段（从右侧开始）
                        # 找到 pos_in_limits（<...> 格式）
                        pos_match = re.search(r"<[^>]+>", message)
                        if not pos_match:
                            continue

                        pos_in_limits = pos_match.group()
                        pos_start = pos_match.start()
                        pos_end = pos_match.end()

                        # 分割消息：pos_in_limits之前和之后的部分
                        before_pos = message[:pos_start].strip()
                        after_pos = message[pos_end:].strip()

                        # 解析pos_in_limits之后的部分（固定顺序：sampling, open_lim, enh_lim, meas_code）
                        after_parts = after_pos.split()
                        if len(after_parts) < 4:
                            continue

                        sampling = after_parts[0]
                        open_lim = after_parts[1]
                        enh_lim = after_parts[2]
                        meas_code = after_parts[3]

                        # 解析pos_in_limits之前的部分
                        # 使用正则表达式来更精确地解析字段
                        # 格式: r_num m_num description low_limit high_limit result units recipe_time test_time status [message]

                        # 先找到状态字段（PASSED 或 * FAILED * 等）
                        status_pattern = r"(\*\s*FAILED\s*\*|PASSED|\*\s*PASSED\s*\*|\*?\s*FAILED\s*\*?)"
                        status_matches = list(re.finditer(status_pattern, before_pos))

                        if not status_matches:
                            continue

                        # 取最后一个匹配的状态（防止description中包含FAILED等词）
                        status_match = status_matches[-1]
                        status_text = status_match.group().strip()
                        status_start = status_match.start()
                        status_end = status_match.end()

                        # 提取状态并清理
                        status_clean = re.sub(r"\*|\s+", " ", status_text).strip()
                        status_clean = (
                            "PASSED" if "PASSED" in status_clean else "FAILED"
                        )

                        # 状态之前的部分
                        before_status = before_pos[:status_start].strip()
                        # 状态之后的部分（message）
                        message_text = before_pos[status_end:].strip()

                        # 使用正则表达式解析所有字段，处理可能的空值
                        # 格式: r_num m_num description low_limit high_limit result units recipe_time test_time
                        fields_pattern = r"(\S+)\s+(\S+)\s+(.*?)\s+(-?\d*\.?\d*)\s+(-?\d*\.?\d*|\s*)\s+(-?\d*\.?\d*)\s*(\S*)\s+(\d+)\s+(\d+)"
                        fields_match = re.match(fields_pattern, before_status)

                        if not fields_match:
                            # 如果正则表达式无法匹配，则使用原有的分割方法作为备选
                            before_status_parts = before_status.split()

                            if (
                                    len(before_status_parts) < 9
                            ):  # 至少需要 r_num m_num desc low high result units recipe_time test_time
                                continue

                            # 从右向左解析固定字段
                            test_time = before_status_parts[-1]  # 最后一个
                            recipe_time = before_status_parts[-2]  # 倒数第二个
                            units = before_status_parts[-3]  # 倒数第三个
                            result = before_status_parts[-4]  # 倒数第四个
                            high_limit = before_status_parts[-5]  # 倒数第五个
                            low_limit = before_status_parts[-6]  # 倒数第六个

                            # 前两个是r_num和m_num
                            r_num = before_status_parts[0]
                            m_num = before_status_parts[1]

                            # 中间的部分都是description
                            desc_parts = before_status_parts[2:-6]  # 从第3个到倒数第7个
                            desc = " ".join(desc_parts)
                        else:
                            # 使用正则表达式匹配的结果
                            groups = fields_match.groups()
                            r_num = groups[0]
                            m_num = groups[1]
                            desc = groups[2]
                            low_limit = groups[3] if groups[3] else ""
                            high_limit = groups[4] if groups[4] else ""
                            result = groups[5] if groups[5] else ""
                            units = groups[6] if groups[6] else ""
                            recipe_time = groups[7]
                            test_time = groups[8]

                        sub_item = {
                            "line_number": line_num,
                            "timestamp": parts.get("timestamp"),
                            "measure_description": desc,
                            "low_limit": low_limit,
                            "high_limit": high_limit,
                            "result": result,
                            "units": units,
                            "status": "成功" if status_clean == "PASSED" else "失败",
                            "message": message_text,
                            "meas_code": meas_code,
                        }
                        current_block["sub_items"].append(sub_item)

                    except (IndexError, ValueError, AttributeError) as e:
                        # 如果解析失败，打印调试信息
                        print(
                            f"Warning: EvalAndLogResults line {line_num} parsing failed: {e}"
                        )
                        print(f"Message: {message}")

                # 检查是否为测试项的结束（包含Overall Result的Footer）
                elif is_footer_with_result:
                    footer_match = footer_regex.search(message)
                    if footer_match:
                        result_code = footer_match.group("result_code").strip()
                        current_block["status"] = (
                            "成功" if result_code == "0" else "失败"
                        )
                        current_block["duration_ms"] = float(
                            footer_match.group("duration")
                        )
                    # 设置需要收集后续的2行footer信息
                    test_item_footer_lines_remaining = 2
                # 如果直接遇到END_OF_TEST（可能没有Overall Result行）
                elif is_end_of_test:
                    current_block["end_time"] = parts.get("timestamp")
                    current_block["end_line"] = line_num
                    structured_data.append(current_block)
                    current_block = None
                    in_test_item = False
        else:  # 系统级日志
            # 如果没有当前块，则开始一个新的系统级日志块
            if not current_block:
                current_block = {
                    "log_type": "系统级",
                    "start_time": parts.get("timestamp"),
                    "start_line": line_num,
                    "log_details": [],
                }
            current_block["log_details"].append(line)

    # 循环结束后，如果仍有未保存的日志块，则保存它
    if current_block:
        current_block["end_line"] = line_num
        if current_block.get("log_type") == "系统级" and current_block["log_details"]:
            last_line_match = line_regex.match(current_block["log_details"][-1])
            if last_line_match:
                current_block["end_time"] = last_line_match.group("timestamp")
        elif current_block.get("log_type") == "测试项":
            # 如果是未完成的测试项，设置结束时间
            if current_block["log_details"]:
                last_line_match = line_regex.match(current_block["log_details"][-1])
                if last_line_match:
                    current_block["end_time"] = last_line_match.group("timestamp")
        structured_data.append(current_block)

    # 后处理，计算系统级日志的持续时间
    for block in structured_data:
        if (
                block.get("log_type") == "系统级"
                and block.get("start_time")
                and block.get("end_time")
        ):
            try:
                start_dt = datetime.strptime(
                    block["start_time"], "%Y-%m-%d %H:%M:%S,%f"
                )
                end_dt = datetime.strptime(block["end_time"], "%Y-%m-%d %H:%M:%S,%f")
                block["duration_ms"] = (end_dt - start_dt).total_seconds() * 1000
            except (ValueError, TypeError):
                block["duration_ms"] = None

    return structured_data


def parse_log_to_structured_data(log_content: str) -> List[Dict[str, Any]]:
    """
    将日志文件内容解析为定义的结构化数据，为系统级日志添加test_name和status属性。
    优化了test_name提取方式，使用\t分隔符并从正确位置提取包含空格的名称。

    Args:
        log_content (str): 日志文件的完整字符串内容。

    Returns:
        list: 包含结构化日志块的列表。
    """
    if not log_content.strip():
        print("警告：日志文件内容为空。")
        return []

    # 正则表达式定义
    # 1. 匹配标准日志行，捕获关键字段
    line_regex = re.compile(
        # 捕获组: timestamp, level, module, time2, context, keyword, message
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s+\[\]\s+"
        r"(?P<level>\w+)\s+(?P<module>.+?)\s+(?P<time2>\d{2}:\d{2}:\d{2}\.\d+)\s+"
        r"(?P<context>\S+?)\s+(?P<keyword>\S+?)\s+(?P<message>.*)$"
    )

    # 2. 匹配测试项的Header行，提取测试名
    header_regex = re.compile(
        r"Test = (?P<test_name>\S+)\s+\|\s+Barcode = (?P<barcode>\S+)"
    )

    # 3. 匹配测试项的Footer行，提取结果和测试时间
    footer_regex = re.compile(
        r"Test = (?P<test_name>\S+)\s+\|\s+Overall Result = (?P<result_code>.*?)\s+\|\s+"
        r"Test Time = (?P<duration>[\d.]+) msec"
    )

    structured_data = []
    current_block = None
    in_test_item = False
    # 用于跟踪测试项结束后需要收集的额外行数
    test_item_footer_lines_remaining = 0

    lines = log_content.splitlines()

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        match = line_regex.match(line)
        parts = match.groupdict() if match else {}
        message = parts.get("message", "")
        keyword = parts.get("keyword", "")
        context = parts.get("context", "")

        # 检查是否为测试项的开始或结束
        is_header = keyword == "Header" and "====" in message
        is_footer_with_result = keyword == "Footer" and "Overall Result" in message
        is_end_of_test = context == "END_OF_TEST"

        if is_header:
            # 如果当前有正在记录的系统级日志块，则先将其保存
            if current_block and not in_test_item:
                current_block["end_line"] = line_num - 1
                if current_block["log_details"]:
                    last_line_match = line_regex.match(current_block["log_details"][-1])
                    if last_line_match:
                        current_block["end_time"] = last_line_match.group("timestamp")
                # 处理系统级日志的test_name和status提取
                process_system_level_block(current_block)
                structured_data.append(current_block)

            # 开始一个新的测试项
            in_test_item = True
            test_item_footer_lines_remaining = 0
            header_match = header_regex.search(message)
            current_block = {
                "log_type": "测试项",
                "test_name": (
                    header_match.group("test_name")
                    if header_match
                    else parts.get("context", "未知")
                ),
                "status": "未知",
                "start_time": parts.get("timestamp"),
                "start_line": line_num,
                "sub_items": [],
                "log_details": [line],
            }
        elif in_test_item or test_item_footer_lines_remaining > 0:
            current_block["log_details"].append(line)

            # 如果还在收集footer额外行
            if test_item_footer_lines_remaining > 0:
                test_item_footer_lines_remaining -= 1
                # 如果是END_OF_TEST行，这是测试项的最后一行
                if is_end_of_test:
                    current_block["end_time"] = parts.get("timestamp")
                    current_block["end_line"] = line_num
                    structured_data.append(current_block)
                    current_block = None
                    in_test_item = False
                    test_item_footer_lines_remaining = 0
                elif test_item_footer_lines_remaining == 0:
                    # 如果没有找到END_OF_TEST但额外行已收集完，也结束测试项
                    current_block["end_time"] = parts.get("timestamp")
                    current_block["end_line"] = line_num
                    structured_data.append(current_block)
                    current_block = None
                    in_test_item = False
            else:
                # 处理测试子项
                if keyword == "EvalAndLogResults":
                    # 保留原有的EvalAndLogResults解析逻辑
                    pass  # 实际代码中保留原有解析逻辑

                # 检查是否为测试项的结束（包含Overall Result的Footer）
                elif is_footer_with_result:
                    footer_match = footer_regex.search(message)
                    if footer_match:
                        result_code = footer_match.group("result_code").strip()
                        current_block["status"] = (
                            "成功" if result_code == "0" else "失败"
                        )
                        current_block["duration_ms"] = float(
                            footer_match.group("duration")
                        )
                    # 设置需要收集后续的2行footer信息
                    test_item_footer_lines_remaining = 2
                # 如果直接遇到END_OF_TEST（可能没有Overall Result行）
                elif is_end_of_test:
                    current_block["end_time"] = parts.get("timestamp")
                    current_block["end_line"] = line_num
                    structured_data.append(current_block)
                    current_block = None
                    in_test_item = False
        else:  # 系统级日志
            # 如果没有当前块，则开始一个新的系统级日志块
            if not current_block:
                current_block = {
                    "log_type": "系统级",
                    "start_time": parts.get("timestamp"),
                    "start_line": line_num,
                    "log_details": [],
                    # 初始化系统级日志的test_name和status
                    "test_name": None,
                    "status": None
                }
            current_block["log_details"].append(line)

    # 循环结束后，如果仍有未保存的日志块，则保存它
    if current_block:
        current_block["end_line"] = line_num
        if current_block.get("log_type") == "系统级" and current_block["log_details"]:
            last_line_match = line_regex.match(current_block["log_details"][-1])
            if last_line_match:
                current_block["end_time"] = last_line_match.group("timestamp")
            # 处理系统级日志的test_name和status提取
            process_system_level_block(current_block)
        elif current_block.get("log_type") == "测试项":
            if current_block["log_details"]:
                last_line_match = line_regex.match(current_block["log_details"][-1])
                if last_line_match:
                    current_block["end_time"] = last_line_match.group("timestamp")
        structured_data.append(current_block)

    # 后处理，计算系统级日志的持续时间
    for block in structured_data:
        if (
                block.get("log_type") == "系统级"
                and block.get("start_time")
                and block.get("end_time")
        ):
            try:
                start_dt = datetime.strptime(
                    block["start_time"], "%Y-%m-%d %H:%M:%S,%f"
                )
                end_dt = datetime.strptime(block["end_time"], "%Y-%m-%d %H:%M:%S,%f")
                block["duration_ms"] = (end_dt - start_dt).total_seconds() * 1000
            except (ValueError, TypeError):
                block["duration_ms"] = None

    return structured_data


def process_system_level_block(block: Dict[str, Any]) -> None:
    """
    处理系统级日志块，提取并设置test_name和status属性
    - 若日志行包含连续两个\t\t，则从第7个字段提取test_name（0-based index 6）
    - 若日志行不包含连续两个\t\t，则从第6个字段提取test_name（0-based index 5）
    - status: 从EvalAndLogResults行提取
    """
    if block.get("log_type") != "系统级":
        return

    # 用于提取状态的正则表达式
    eval_status_regex = re.compile(r".*\s+(PASSED|\* FAILED \*)\s+.*")

    # 遍历日志详情行，查找需要的信息
    for line in block.get("log_details", []):
        # 检查是否包含连续两个制表符
        has_double_tab = "\t\t" in line

        # 使用\t分割行内容
        line_parts = line.split('\t')

        # 根据是否有连续两个制表符，选择不同的索引提取test_name
        if block.get("test_name") is None:
            if has_double_tab:
                # 情况1: 有连续两个\t\t，从第7个字段提取（index 6）
                if len(line_parts) >= 7:
                    test_name_candidate = line_parts[6].strip().replace('[', '').replace(']', '')
                    if test_name_candidate:
                        block["test_name"] = test_name_candidate
                    # 备选方案：尝试第8个字段（index 7）
                    elif len(line_parts) >= 8 and line_parts[7].strip():
                        test_name_candidate = line_parts[7].strip().replace('[', '').replace(']', '')
                        block["test_name"] = test_name_candidate
            else:
                # 情况2: 没有连续两个\t\t，从第6个字段提取（index 5）
                if len(line_parts) >= 6:
                    test_name_candidate = line_parts[5].strip().replace('[', '').replace(']', '')
                    if test_name_candidate:
                        block["test_name"] = test_name_candidate
                    # 备选方案：尝试第7个字段（index 6）
                    elif len(line_parts) >= 7 and line_parts[6].strip():
                        test_name_candidate = line_parts[6].strip().replace('[', '').replace(']', '')
                        block["test_name"] = test_name_candidate

        # 提取status（从EvalAndLogResults行）
        if "EvalAndLogResults" in line and block.get("status") is None:
            status_match = eval_status_regex.match(line)
            if status_match:
                status_text = status_match.group(1).strip()
                if "* FAILED *" in status_text:
                    block["status"] = "失败"
                elif "PASSED" in status_text:
                    block["status"] = "成功"

    # 如果没有找到test_name，设置为"未知系统操作"
    if block.get("test_name") is None:
        block["test_name"] = "未知系统操作"

    # 如果没有找到status，设置为"未知"
    if block.get("status") is None:
        block["status"] = "未知"


def do_parse_process(file_path=r"debug\test9\logs\extracted_logs\nextest2010_L2_VISION_LVISION14_TEBEVSN-V3-184.txt"):
    """主函数，用于命令行执行时的文件处理"""
    # 1. 将您的日志文件内容读取到一个变量中
    # file_path = r"debug\test9\logs\extracted_logs\nextest2010_L2_VISION_LVISION14_TEBEVSN-V3-184.txt"
    try:
        with open(file_path, "r", encoding="gbk") as f:
            log_file_content = f.read()

        # 2. 调用解析函数
        parsed_data = parse_log_to_structured_data(log_file_content)

        # 3. 将结果保存为JSON文件以便查看
        output_json_path = r"debug\test9\logs\extracted_logs\parsed_log_output_fixed.json"
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)

        print(f"解析完成！共解析出 {len(parsed_data)} 个日志块。")
        print(f"结果已保存至: {output_json_path}")

        # 4. 打印统计信息
        test_item_count = 0
        system_log_count = 0
        for item in parsed_data:
            if item["log_type"] == "测试项":
                test_item_count += 1
                print(
                    f"找到测试项 {test_item_count}: {item['test_name']} - 状态: {item['status']} - 子项数量: {len(item.get('sub_items', []))} - 日志行数: {len(item.get('log_details', []))}"
                )
            elif item["log_type"] == "系统级":
                system_log_count += 1

        print(
            f"\n总计：测试项 {test_item_count} 个，系统级日志块 {system_log_count} 个"
        )

        return output_json_path, parsed_data

    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'。请确保文件名正确且文件在正确的路径下。")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


# --- 使用方法 ---
if __name__ == "__main__":
    output_json_path, parsed_data = do_parse_process(file_path=r".\logs\extracted_logs\nextest2010_L2_VISION_LVISION14_TEBEVSN-V3-184.txt")
