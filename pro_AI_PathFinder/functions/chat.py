import json
import sys
sys.path.append(r'/usr/local/bin/python311/lib/python3.11/site-packages/')
import requests
import time
import re
# flask packages module path
sys.path.append(r'/usr/local/bin/python311/lib/python3.11/site-packages/')
import urllib3
from urllib3.exceptions import InsecureRequestWarning
# 如果你想禁用SSL证书验证警告，可以这样做
urllib3.disable_warnings(InsecureRequestWarning)




try:
    import sseclient
except ImportError:
    print("警告: sseclient 模块未安装。请运行: pip install sseclient-py")
    sseclient = None

# API_URL = "http://10.179.21.53:16071/v1/chat-messages"
API_URL = "https://10.114.132.81/ai-v1/chat-messages"

API_KEY = "app-e1l0NGAUTqn8pseCZQmn0FGe"


def get_ai_analysis_stream(query, conversation_id="", user_id="user-123"):
    """
    流式调用AI接口获取分析结果

    Args:
        query (str): 查询内容
        conversation_id (str): 对话ID，默认为空
        user_id (str): 用户ID

    Yields:
        str: 流式AI分析结果片段
    """
    if sseclient is None:
        yield "错误: sseclient 模块未安装，请运行 'pip install sseclient-py'"
        return
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    data = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "conversation_id": conversation_id,
        "user": user_id,
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers, stream=True, verify=False)

        if response.status_code != 200:
            yield f"请求失败: {response.status_code} - {response.text}"
            return

        client = sseclient.SSEClient(response)
        
        for event in client.events():
            if event.event == "error":
                yield f"流式错误: {event.data}"
                return

            try:
                event_data = event.data
                if not event_data or event_data == "[DONE]":
                    break

                msg = json.loads(event_data)
                event_type = msg.get("event", "")
                
                if event_type in ["message", "agent_message"]:
                    answer = msg.get("answer", "")
                    if answer:
                        yield answer
                elif event_type == "message_replace":
                    answer = msg.get("answer", "")
                    if answer:
                        yield f"__REPLACE__{answer}"
                elif event_type == "message_end":
                    break

            except json.JSONDecodeError:
                continue
            except Exception as e:
                yield f"解析响应失败: {str(e)}"
                return

    except requests.exceptions.RequestException as e:
        yield f"网络请求失败: {str(e)}"
    except Exception as e:
        yield f"未知错误: {str(e)}"


def get_ai_analysis(query, conversation_id="", user_id="user-123"):
    """
    调用AI接口获取分析结果

    Args:
        query (str): 查询内容
        conversation_id (str): 对话ID，默认为空
        user_id (str): 用户ID

    Returns:
        str: AI分析结果，如果失败返回错误信息
    """
    if sseclient is None:
        return "错误: sseclient 模块未安装，请运行 'pip install sseclient-py'"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    data = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "conversation_id": conversation_id,
        "user": user_id,
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers, stream=True, verify=False)

        if response.status_code != 200:
            return f"请求失败: {response.status_code} - {response.text}"

        # 收集完整的响应内容
        full_response = ""
        client = sseclient.SSEClient(response)
        event_count = 0

        for event in client.events():
            event_count += 1

            if event.event == "error":
                return f"流式错误: {event.data}"

            try:
                event_data = event.data
                if not event_data or event_data == "[DONE]":
                    break

                msg = json.loads(event_data)

                # 根据消息类型处理不同的响应
                event_type = msg.get("event", "")
                if event_type == "message":
                    answer = msg.get("answer", "")
                    full_response += answer
                elif event_type == "agent_message":
                    # 处理agent_message事件类型
                    answer = msg.get("answer", "")
                    full_response += answer
                elif event_type == "message_end":
                    break
                elif event_type == "message_replace":
                    # 有些API可能使用message_replace事件
                    answer = msg.get("answer", "")
                    full_response = answer  # 替换而不是追加
                elif event_type == "agent_thought":
                    # 跳过思考过程，不处理
                    continue

            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {event_data[:100]}...")
                continue
            except Exception as e:
                return f"解析响应失败: {str(e)}"

        # 可选：启用调试模式时打印信息
        # print(f"总共处理了 {event_count} 个事件，最终响应长度: {len(full_response)}")

        # 保留完整响应内容，包括think标签
        if full_response:
            full_response = full_response.strip()

        return (
            full_response
            if full_response
            else f"未获取到有效响应 (处理了{event_count}个事件)"
        )

    except requests.exceptions.RequestException as e:
        return f"网络请求失败: {str(e)}"
    except Exception as e:
        return f"未知错误: {str(e)}"


def get_test_description(test_name):
    """
    获取测试项的AI描述

    Args:
        test_name (str): 测试名称

    Returns:
        str: 测试项描述
    """
    query = f"""请简要描述这个测试项的功能和目的：
测试名称: {test_name}

请用1-2句话简洁地说明这个测试项的作用。"""

    return get_ai_analysis(query)


def get_failure_analysis(
    test_name, test_status, duration_ms, sub_items=None, log_details=None, language='zh', test_query=''
):
    """
    获取失败测试项的AI分析建议

    Args:
        test_name (str): 测试名称
        test_status (str): 测试状态
        duration_ms (float): 持续时间
        sub_items (list): 测试子项列表
        log_details (list): 日志详情

    Returns:
        str: 分析建议
    """
    if test_status == "PASS":
        return "测试通过，无需分析。"

    if language == 'zh':
        language = '中文'
    else:
        language = '英文'

    # 构建分析上下文
    context = f"""测试项失败分析：
测试名称: {test_name}
测试状态: {test_status}
执行时间: {duration_ms}ms"""

    if sub_items:
        context += f"\n测试子项数量: {len(sub_items)}"
        # 添加前几个子项作为参考
        for i, item in enumerate(sub_items[:3]):
            context += f"\n子项{i+1}: {item}"

    if log_details:
        context += f"\n相关日志片段: {' '.join(log_details[-5:])}"  # 最后5行日志

    query = f"""{context}

请结合用户的提示词:[{test_query}]来分析这个失败的测试项，并提供：
1. 可能的失败原因
2. 建议的解决方案
3. 预防措施

要求：请使用{language}回答，内容简洁，以MarkDown输出，不要输出表格，
1. 可能的失败原因（内容不要超过3条）
2. 建议的解决方案（内容不要超过3条）
3. 预防措施（内容不要超过3条）
。"""

    return get_ai_analysis(query)


def filter_ai_content2(content, start_marker="<think>", end_marker="</think>"):
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
            filtered = filter_ai_content2(result)
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

# 使用示例
# debug_basic_api("请简要介绍你自己的功能")
# debug_basic_api("另一个测试查询内容")


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
            test_name, test_status, duration_ms, sub_items, log_details
        )
        end_time = time.time()

        print(f"调用耗时: {end_time - start_time:.2f}秒")
        print(f"测试项 '{test_name}' 的失败分析:")
        print(analysis)

        if is_filter:
            # 过滤标记内容
            filtered = filter_ai_content2(analysis)
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
    language = "中文"
    test_item = "AUDIO_L2AR_EAR_10000_8KHz_TO_140Hz_MIC1_PORTO_EQ"
    test_query = (f"使用通俗易懂的{language}语言解释说明：{test_item},"
                  f"其中L2AR这样的是第二代音频测试站，"
                  f"其中4500这样的是采样率，最后面的像PORTO_EQ是手机或平板的产品名称，"
                  f"先将各部分含义解析汇总成有序或无序列表，"
                  f"然后将其通俗易懂的语言，其内容缩写为50字左右，"
                  f"然后按照MarkDown的格式输出给我。")
    debug_basic_api(test_query=test_query, test_item=test_item, language=language, is_filter_think=True)
    # debug_stream_api()
    # debug_test_description()
    # debug_failure_analysis()
    # debug_conversation()

    print("\n===== 调试完成 =====")


if __name__ == "__main__":
    main()