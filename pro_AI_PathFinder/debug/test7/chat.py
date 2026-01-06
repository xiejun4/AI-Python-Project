import json

import requests

try:
    import sseclient
except ImportError:
    print("警告: sseclient 模块未安装。请运行: pip install sseclient-py")
    sseclient = None

API_URL = "http://10.179.21.53:16071/v1/chat-messages"
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
        response = requests.post(API_URL, json=data, headers=headers, stream=True)

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
        response = requests.post(API_URL, json=data, headers=headers, stream=True)

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
    test_name, test_status, duration_ms, sub_items=None, log_details=None
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
    if test_status == "成功":
        return "测试通过，无需分析。"

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

请分析这个失败的测试项，并提供：
1. 可能的失败原因
2. 建议的解决方案
3. 预防措施

请简洁明了地回答。"""

    return get_ai_analysis(query)
