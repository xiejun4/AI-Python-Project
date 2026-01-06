import time
import re
import sys

# 判断当前操作系统
if sys.platform.startswith('win'):
    # Windows系统的导入路径
    from functions.chat import (
        get_ai_analysis,
        get_ai_analysis_stream,
        get_test_description,
        get_failure_analysis
    )
elif sys.platform.startswith('linux'):
    # Linux系统的导入路径
    from chat import (
        get_ai_analysis,
        get_ai_analysis_stream,
        get_test_description,
        get_failure_analysis
    )
else:
    # 其他操作系统可以抛出异常或做相应处理
    raise OSError(f"不支持的操作系统: {sys.platform}")

def extract_think_content(content, start_marker="<think>", end_marker="</think>"):
    """
    优先过滤AI返回内容中特定标记之间的内容，仅当两个冒号之间内容超过30字符时插入换行符

    参数:
        content (str): AI返回的原始内容
        start_marker (str): 起始标记，默认为"</think>"
        end_marker (str): 结束标记，默认为"</think>"

    返回:
        str: 处理后的内容
    """
    if not content or not start_marker or not end_marker:
        return content

    # 1. 优先过滤标记之间的内容（修复正则匹配逻辑）
    # 使用贪婪模式确保所有标记对都被处理，添加前后边界避免部分匹配
    pattern = r'(?s)' + re.escape(start_marker) + r'.*?' + re.escape(end_marker)
    filtered_content = re.sub(pattern, '', content)

    # 调试用：检查标记是否被正确过滤
    # print("过滤标记后内容：", filtered_content)

    # 2. 处理过滤后内容中的冒号
    colon_matches = list(re.finditer(r'：', filtered_content))
    colon_positions = [m.start() for m in colon_matches]

    def handle_colon(match):
        current_pos = match.start()
        try:
            idx = colon_positions.index(current_pos)
            if idx + 1 < len(colon_positions):
                next_colon_pos = colon_positions[idx + 1]
                content_between = filtered_content[current_pos + 1: next_colon_pos]
                cleaned_length = len(content_between.strip())
                if cleaned_length > 30:
                    return "：\n"
        except (ValueError, IndexError):
            pass
        return "："

    colon_processed = re.sub(r'：', handle_colon, filtered_content)
    punctuated_content = re.sub(r'。', r'。\n', colon_processed)

    # 3. 清理多余空行
    return re.sub(r'\n+', '\n', punctuated_content).strip()

def process_formatted_content(content):
    """对提取的Markdown内容进行基本格式化处理"""
    # 处理空内容
    if not content:
        return ""
    # 去除每行首尾多余空格，保留内部格式
    lines = [line.strip() for line in content.split('\n')]
    # 过滤空行（可选，根据需求调整）
    lines = [line for line in lines if line]
    return '\n'.join(lines)

def extract_markdown_content(content):
    """
    提取内容中```markdown 和 ```之间的内容，不处理其他标记
    提取后会对内容进行基本的格式化处理

    参数:
        content (str): 原始内容

    返回:
        str: 提取并格式化后的Markdown内容，如果未找到则返回原始内容
    """
    if not content:
        return content

    # 优化正则：允许markdown标记后有空格或换行，使用非贪婪匹配
    markdown_pattern = r'```markdown\s*(.*?)\s*```'
    # 使用DOTALL让.匹配换行符，IGNORECASE忽略大小写（防止Markdown大写）
    markdown_match = re.search(markdown_pattern, content, re.DOTALL | re.IGNORECASE)

    if markdown_match:
        # 提取Markdown代码块内容
        markdown_content = markdown_match.group(1)
        # 应用格式化处理
        return process_formatted_content(markdown_content)
    else:
        # 如果没有找到Markdown代码块，返回原始内容
        return content

def extract_test_items_content(content):
    """
    提取字符串中## 1. 测试项分解和## 2. 简要描述的内容

    参数:
        content (str): 原始字符串内容

    返回:
        dict: 包含两个部分内容的字典，键为标题，值为对应内容
    """
    if not content:
        return {"## 1. 测试项分解": "", "## 2. 简要描述": ""}

    # 正则模式：匹配两个标题及其内容，直到下一个标题或字符串结束
    pattern = r'(## 1\. 测试项分解\n)(.*?)(?=## |$)(## 2\. 简要描述\n)(.*?)(?=## |$)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        # 提取各个部分内容并处理空白
        section1_title = match.group(1).strip()
        section1_content = match.group(2).strip()
        section2_title = match.group(3).strip()
        section2_content = match.group(4).strip()

        return {
            section1_title: section1_content,
            section2_title: section2_content
        }
    else:
        # 如果未找到对应部分，返回空内容
        return {"## 1. 测试项分解": "", "## 2. 简要描述": ""}


def process_formatted_content(content):
    """处理内容格式化的辅助函数"""
    # 处理冒号
    colon_matches = list(re.finditer(r'：', content))
    colon_positions = [m.start() for m in colon_matches]

    def handle_colon(match):
        current_pos = match.start()
        try:
            idx = colon_positions.index(current_pos)
            if idx + 1 < len(colon_positions):
                next_colon_pos = colon_positions[idx + 1]
                content_between = content[current_pos + 1: next_colon_pos]
                cleaned_length = len(content_between.strip())
                if cleaned_length > 30:
                    return "：\n"
        except (ValueError, IndexError):
            pass
        return "："

    colon_processed = re.sub(r'：', handle_colon, content)
    punctuated_content = re.sub(r'。', r'。\n', colon_processed)

    # 清理多余空行
    return re.sub(r'\n+', '\n', punctuated_content).strip()
def debug_basic_api(test_query, test_item, language='zh', is_filter_think=False):
    """测试基本API调用功能，返回指定结构的字典"""
    print("=== 测试基本API调用 ===")
    # 保留传入的test_item参数，移除硬编码
    if language == 'zh':
        language = '中文'
    else:
        language = '英文'

    test_query = test_query
    # test_query = (f"使用通俗易懂的{language}语言解释说明：{test_item},"
    #               f"其中L2AR这样的是第二代音频测试站，"
    #               f"其中4500这样的是采样率，最后面的像PORTO_EQ是手机或平板的产品名称，"
    #               f"先将各部分含义解析汇总成有序或无序列表，"
    #               f"然后将其通俗易懂的语言，其内容缩写为50字左右，"
    #               f"然后按照MarkDown的格式输出给我。")

    try:
        start_time = time.time()
        result = get_ai_analysis(test_query)  # 假设该函数已定义
        end_time = time.time()

        print(f"调用耗时: {end_time - start_time:.2f}秒")
        print(f"返回结果长度: {len(result)}字符")
        print("返回结果预览:")
        print(result[:5000] + ("..." if len(result) > 5000 else ""))

        if is_filter_think:
            # 过滤标记内容
            filtered = extract_think_content(result)
            print("过滤后结果：")
            print(filtered)
        else:
            filtered = result

        # 构建并返回指定结构的字典
        return {
            'test_purpose_zh': filtered,
            'test_items_zh': filtered,
            'test_purpose_en': filtered,
            'test_items_en': filtered
        }

    except Exception as e:
        error_msg = f"基本API调用出错: {str(e)}"
        print(error_msg)
        # 出错时仍返回字典结构，便于统一处理
        return {
            'test_purpose_zh': error_msg,
            'test_items_zh': [],
            'test_purpose_en': error_msg,
            'test_items_en': []
        }


def debug_stream_api():
    """测试流式API调用功能"""
    print("\n=== 测试流式API调用 ===")
    test_query = "请详细解释一个简单的数学问题，比如1+1为什么等于2"

    try:
        start_time = time.time()
        print("流式返回结果:")
        print("-" * 50)

        chunk_count = 0
        full_response = ""

        for chunk in get_ai_analysis_stream(test_query):
            chunk_count += 1
            full_response += chunk
            print(f"[片段{chunk_count}] {chunk}")

        end_time = time.time()
        print("-" * 50)
        print(f"流式调用完成，共接收{chunk_count}个片段，耗时{end_time - start_time:.2f}秒")
        print(f"完整结果长度: {len(full_response)}字符")

    except Exception as e:
        print(f"流式API调用出错: {str(e)}")


def debug_test_description():
    """测试测试项描述功能"""
    print("\n=== 测试测试项描述功能 ===")
    test_name = "用户登录验证测试"

    try:
        start_time = time.time()
        description = get_test_description(test_name)
        end_time = time.time()

        print(f"调用耗时: {end_time - start_time:.2f}秒")
        print(f"测试项 '{test_name}' 的描述:")
        print(description)

    except Exception as e:
        print(f"测试项描述功能出错: {str(e)}")


def debug_failure_analysis(param_test_name,
                           param_test_status,
                           param_sub_items,
                           param_log_details=None,
                           language='zh',
                           test_query='',
                           is_filter=False):
    """测试失败分析功能"""
    print("\n=== 测试失败分析功能 ===")
    test_name = param_test_name
    test_status = param_test_status
    duration_ms = 1500
    sub_items = param_sub_items
    # sub_items = [
    #     "验证支付金额 - 成功",
    #     "验证支付方式 - 成功",
    #     "处理支付请求 - 失败",
    #     "生成支付凭证 - 未执行"
    # ]
    # 设置默认值为空列表
    if param_log_details is None:
        param_log_details = []
    log_details = param_log_details
    # log_details = [
    #     "INFO: 开始处理支付请求",
    #     "DEBUG: 连接支付网关",
    #     "ERROR: 支付网关响应超时",
    #     "WARN: 尝试重试支付请求",
    #     "ERROR: 第二次尝试仍超时",
    #     "INFO: 记录失败状态"
    # ]

    try:
        start_time = time.time()
        analysis = get_failure_analysis(
            test_name, test_status, duration_ms, sub_items, log_details,language, test_query
        )

        end_time = time.time()

        print(f"调用耗时: {end_time - start_time:.2f}秒")
        print(f"测试项 '{test_name}' 的失败分析:")
        print(analysis)

        if is_filter:
            # 过滤标记内容
            filtered = extract_think_content(analysis)
            print("过滤后结果：")
            print(filtered)
            return filtered
        else:
            return analysis

    except Exception as e:
        print(f"失败分析功能出错: {str(e)}")


def debug_conversation():
    """测试多轮对话功能"""
    print("\n=== 测试多轮对话功能 ===")
    conversation_id = f"test-conv-{int(time.time())}"
    print(f"使用对话ID: {conversation_id}")

    str_temp = "使用通俗易懂的语言解释这个字符串的意思："

    queries = [
        f"{str_temp}^MTK_WLAN\\d+\\.\\d+G_TX_C\\d+_HQA_\\d+DB_(M|L)CH\\d+",
        f"{str_temp}^MTK_WLAN\\d+\\.\\d+G_RX_C\\d+_HQA_RSSI_(M|L)CH\\d+",
        f"{str_temp}^MTK_WLAN\\d+G_TX_HQA_C\\d+_\\d+DB_CH\\d+",
        f"{str_temp}^MTK_WLAN\\d+G_RX_C\\d+_HQA_CH\\d+",
        f"{str_temp}^MTK_GPS_RX_V\\d+_L\\d+_-\\d+DB",
        f"{str_temp}^MTK_BLUETOOTH_TX_POWER_V\\d+_CH\\d+",
        f"{str_temp}^MTK_MMRF_LTE_BC\\d+_TX_\\d+DB_V\\d+_(M|L)CH\\d+",
        f"{str_temp}^MTK_MMRF_LTE_BC\\d+_RX_C\\d+_RSSI_V\\d+_(M|L)CH\\d+_EP"
    ]

    try:
        for i, query in enumerate(queries):
            print(f"\n--- 第{i + 1}轮查询 ---")
            print(f"查询内容: {query}")

            start_time = time.time()
            # result = get_ai_analysis(query, conversation_id=conversation_id)
            result = get_ai_analysis(query, conversation_id='')
            end_time = time.time()

            print(f"耗时: {end_time - start_time:.2f}秒")
            print("响应:")
            print(result)

    except Exception as e:
        print(f"多轮对话测试出错: {str(e)}")


def main():
    """调试主函数"""
    print("===== AI API 调试工具 =====")
    print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 运行所有调试测试
    language = "zh"
    test_item = "AUDIO_L2AR_EAR_10000_8KHz_TO_140Hz_MIC1_PORTO_EQ"
    test_query = (f"使用通俗易懂的{language}语言解释说明：{test_item},"
                  f"其中L2AR这样的是第二代音频测试站，"
                  f"其中4500这样的是采样率，最后面的像PORTO_EQ是手机或平板的产品名称，"
                  f"先将各部分含义解析汇总成有序或无序列表，"
                  f"然后将其通俗易懂的语言，其内容缩写为50字左右，"
                  f"然后按照MarkDown的格式输出给我。")
    result_datas =  debug_basic_api(test_query=test_query, test_item=test_item, language=language, is_filter_think=False)
    # debug_stream_api()
    # debug_test_description()
    # debug_failure_analysis()
    # debug_conversation()

    print("\n===== 调试完成 =====")

if __name__ == "__main__":
    main()
