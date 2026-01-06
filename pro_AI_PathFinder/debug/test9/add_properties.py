import json
import re
from typing import Dict, Any

# 读取 grouped_output.json 文件
def read_grouped_output(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# 为每个子节点添加 List of Regular Expressions 和 AI Prompt 属性
def add_properties_v1(data):
    for test_group, key_parts in data.items():
        for key_part, items in key_parts.items():
            for item in items:
                # 添加默认的正则表达式，将数字替换为变量
                test_item = item.get("TEST ITEMS", "")
                # 将数字替换为\d+的正则表达式
                import re
                regex_with_variables = re.sub(r'\d+', r'\\d+', test_item)
                default_regex = f".*{regex_with_variables}.*" if regex_with_variables else ".*"
                item["List of Regular Expressions"] = [default_regex]

                # 添加AI提示词，将字段翻译成中文后用逗号连接
                test_group_cn = "测试组"
                key_parts_cn = "关键参数"
                test_items_cn = "测试项"
                method_cn = "方法"
                test_detail_info_cn = "测试详细信息"

                # 构建解释测试项内容
                explanation_content = f"{test_group_cn}: {item.get('Test Group', '')}, "
                explanation_content += f"{key_parts_cn}: {item.get('Key parts', '')}, "
                explanation_content += f"{test_items_cn}: {test_item}, "
                explanation_content += f"{method_cn}: {item.get('Method', '')}, "
                explanation_content += f"{test_detail_info_cn}: {item.get('Test detail information', '')}."

                # 构建异常分析与建议内容
                analysis_content = f"{test_group_cn}: {item.get('Test Group', '')}, "
                analysis_content += f"{key_parts_cn}: {item.get('Key parts', '')}, "
                analysis_content += f"{test_items_cn}: {test_item}, "
                analysis_content += f"{method_cn}: {item.get('Method', '')}, "
                analysis_content += f"{test_detail_info_cn}: {item.get('Test detail information', '')}."

                # 更新AI Prompt结构
                item["AI Prompt"] = {
                    "测试项解释": f"请参考以下内容：{explanation_content}，\n"
                                  "用简洁的语言解释测试项的意思，\n"
                                  "数字控制在50字左右，\n"
                                  "内容已Markdown格式输出。",
                    "异常日志分析与建议": f"请参考以下内容：{analysis_content}，\n"
                                          "用简洁的语言分析异常日志的意思，要求输出：\n"
                                          "1. 可能的失败原因\n"
                                          "2. 建议的解决方案\n"
                                          "3. 预防措施。\n"
                                          "数字控制在150字左右，\n"
                                          "不要使用表格，\n"
                                          "采用有序或无序列表，\n"
                                          "内容已Markdown格式输出。"
                }
    return data


def add_properties(data: Dict[str, Any]) -> Dict[str, Any]:
    for test_group, key_parts in data.items():
        for key_part, items in key_parts.items():
            for item in items:
                # 添加默认的正则表达式，将数字替换为变量
                test_item = item.get("TEST ITEMS", "")
                # 将数字替换为\d+的正则表达式
                regex_with_variables = re.sub(r'\d+', r'\\d+', test_item)
                default_regex = f".*{regex_with_variables}.*" if regex_with_variables else ".*"
                item["List of Regular Expressions"] = [default_regex]

                # 添加AI提示词，将字段翻译成中文后用逗号连接
                test_group_cn = "测试组"
                key_parts_cn = "关键参数"
                test_items_cn = "测试项"
                method_cn = "方法"
                test_detail_info_cn = "测试详细信息"

                # 构建解释测试项内容
                explanation_content = f"{test_group_cn}: {item.get('Test Group', '')}, "
                explanation_content += f"{key_parts_cn}: {item.get('Key parts', '')}, "
                explanation_content += f"{test_items_cn}: {test_item}, "
                explanation_content += f"{method_cn}: {item.get('Method', '')}, "
                explanation_content += f"{test_detail_info_cn}: {item.get('Test detail information', '')}."

                # 构建异常分析与建议内容
                analysis_content = f"{test_group_cn}: {item.get('Test Group', '')}, "
                analysis_content += f"{key_parts_cn}: {item.get('Key parts', '')}, "
                analysis_content += f"{test_items_cn}: {test_item}, "
                analysis_content += f"{method_cn}: {item.get('Method', '')}, "
                analysis_content += f"{test_detail_info_cn}: {item.get('Test detail information', '')}."

                # 更新AI Prompt结构
                item["AI Prompt"] = {
                    "测试项解释": f"请参考以下内容：{explanation_content}，\n"
                                  "用简洁的语言解释测试项的意思，\n"
                                  "数字控制在50字左右，\n"
                                  "内容已Markdown格式输出。",
                    "异常日志分析与建议": f"请参考以下内容：{analysis_content}，\n"
                                          "用简洁的语言分析异常日志的意思，要求输出：\n"
                                          "1. 可能的失败原因\n"
                                          "2. 建议的解决方案\n"
                                          "3. 预防措施。\n"
                                          "数字控制在150字左右，\n"
                                          "不要使用表格，\n"
                                          "采用有序或无序列表，\n"
                                          "内容已Markdown格式输出。"
                }

                # 添加analysis_suggest字段，包含默认分析建议框架
                item["analysis_suggest"] = {
                    "异常日志": [],
                    "可能的失败原因": [],
                    "建议的解决方案": [],
                    "预防措施": []
                }

                # 根据测试项信息生成基础分析建议（示例逻辑）
                test_detail = str(item.get('Test detail information', '')).lower()

                # 示例：基于测试详情添加可能的分析
                if 'adb' in test_detail:
                    item["analysis_suggest"]["可能的失败原因"].append("ADB连接问题或设备无响应")
                    item["analysis_suggest"]["建议的解决方案"].append("检查USB连接或重新启动ADB服务")
                    item["analysis_suggest"]["预防措施"].append("确保设备驱动正常安装")

                if 'time' in test_detail:
                    item["analysis_suggest"]["可能的失败原因"].append("时间同步问题或超时")
                    item["analysis_suggest"]["建议的解决方案"].append("检查网络时间同步或调整超时设置")

                if 'error' in test_detail:
                    item["analysis_suggest"]["可能的失败原因"].append("系统错误或配置问题")
                    item["analysis_suggest"]["建议的解决方案"].append("查看详细错误日志定位问题")
                    item["analysis_suggest"]["预防措施"].append("定期检查系统健康状态")

    return data


# 保存修改后的数据到文件
def save_grouped_output(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 主函数
def do_add_properties(station):
    input_file = rf".\debug\test9\docs\{station}_grouped_output.json"
    output_file = rf".\debug\test9\docs\{station}_grouped_output_with_properties.json"

    # 读取数据
    data = read_grouped_output(input_file)

    # 添加属性
    data = add_properties(data)

    # 保存数据
    save_grouped_output(data, output_file)
    print(f"已成功为 {input_file} 中的每个子节点添加属性，并保存到 {output_file}")


if __name__ == "__main__":
    do_add_properties()
