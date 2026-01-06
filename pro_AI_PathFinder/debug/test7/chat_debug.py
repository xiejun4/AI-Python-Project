import time
from chat import (
    get_ai_analysis,
    get_ai_analysis_stream,
    get_test_description,
    get_failure_analysis)


def debug_basic_api():
    """测试基本API调用功能"""
    print("=== 测试基本API调用 ===")
    test_query = "请简要介绍你自己的功能"

    try:
        start_time = time.time()
        result = get_ai_analysis(test_query)
        end_time = time.time()

        print(f"调用耗时: {end_time - start_time:.2f}秒")
        print(f"返回结果长度: {len(result)}字符")
        print("返回结果预览:")
        print(result[:500] + ("..." if len(result) > 500 else ""))

    except Exception as e:
        print(f"基本API调用出错: {str(e)}")


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


def debug_failure_analysis():
    """测试失败分析功能"""
    print("\n=== 测试失败分析功能 ===")
    test_name = "支付流程验证测试"
    test_status = "失败"
    duration_ms = 1500
    sub_items = [
        "验证支付金额 - 成功",
        "验证支付方式 - 成功",
        "处理支付请求 - 失败",
        "生成支付凭证 - 未执行"
    ]
    log_details = [
        "INFO: 开始处理支付请求",
        "DEBUG: 连接支付网关",
        "ERROR: 支付网关响应超时",
        "WARN: 尝试重试支付请求",
        "ERROR: 第二次尝试仍超时",
        "INFO: 记录失败状态"
    ]

    try:
        start_time = time.time()
        analysis = get_failure_analysis(
            test_name, test_status, duration_ms, sub_items, log_details
        )
        end_time = time.time()

        print(f"调用耗时: {end_time - start_time:.2f}秒")
        print(f"测试项 '{test_name}' 的失败分析:")
        print(analysis)

    except Exception as e:
        print(f"失败分析功能出错: {str(e)}")


def debug_conversation():
    """测试多轮对话功能"""
    print("\n=== 测试多轮对话功能 ===")
    conversation_id = f"test-conv-{int(time.time())}"
    print(f"使用对话ID: {conversation_id}")

    queries = [
        "我有一个关于用户登录的测试失败了",
        "这个测试的名字是用户密码验证测试",
        "它失败的原因可能是什么？"
    ]

    try:
        for i, query in enumerate(queries):
            print(f"\n--- 第{i + 1}轮查询 ---")
            print(f"查询内容: {query}")

            start_time = time.time()
            result = get_ai_analysis(query, conversation_id=conversation_id)
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
    debug_basic_api()
    debug_stream_api()
    debug_test_description()
    debug_failure_analysis()
    debug_conversation()

    print("\n===== 调试完成 =====")


if __name__ == "__main__":
    main()
