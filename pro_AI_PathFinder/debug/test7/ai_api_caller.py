import requests
import json


def call_ai_api():
    # 接口URL
    url = "http://10.114.208.143:11434/v1/chat/completions"

    # 请求头，对应curl中的-H参数
    headers = {
        "Content-Type": "application/json"
    }

    # 请求数据，对应curl中的-d参数
    data = {
        "model": "crisp-im/Qwen3-30B-A3B-Instruct-2507-UD-Q4_K_XL",
        "messages": [
            {"role": "user", "content": "你好，介绍一下你自己"}
        ],
        "max_tokens": 256
    }

    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # 检查请求是否成功
        response.raise_for_status()

        # 解析并返回结果
        result = response.json()
        print("接口返回结果：")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 提取AI的回答内容
        if "choices" in result and len(result["choices"]) > 0:
            ai_response = result["choices"][0]["message"]["content"]
            print("\nAI回答：")
            print(ai_response)

        return result

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误：{e}")
        return None


if __name__ == "__main__":
    call_ai_api()
