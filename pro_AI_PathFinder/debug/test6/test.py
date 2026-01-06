# import re
#
# # 使用修复后的正则表达式
# pattern = r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+[A-Z]+)_(?P<version>V\d+)_(?P<product>[A-Z]+)$'
#
# # 测试字符串（所有字符串相同）
# test_strings = [
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS",
#     "AUDIO_L2AR_ALERT_LEFT_11100_16KHZ_TO_7KHZ_MIC1LEFT_V2_URUS"
# ]
#
# # 进行匹配测试
# for i, s in enumerate(test_strings, 1):
#     match = re.match(pattern, s)
#     if match:
#         print(f"字符串 {i} 匹配成功:")
#         print(f"  direction: {match.group('direction')}")
#         print(f"  id: {match.group('id')}")
#         print(f"  start_freq: {match.group('start_freq')}")
#         print(f"  end_freq: {match.group('end_freq')}")
#         print(f"  mic_id: {match.group('mic_id')}")
#         print(f"  version: {match.group('version')}")
#         print(f"  product: {match.group('product')}\n")
#     else:
#         print(f"字符串 {i} 匹配失败\n")

import re


def test_ear_regex_matching():
    # 待匹配的目标字符串
    test_string = "AUDIO_L2AR_EAR_25000_8KHz_TO_140Hz_MIC1_PORTO_EQ"

    # EAR设备相关的正则表达式列表
    EAR_TEST = [
        # 1. 带异步模式和产品名的完整模式
        r'^AUDIO_L2AR_EAR_(?P<id>\d+)_(?P<start_freq>\d+K?Hz)_TO_(?P<end_freq>\d+K?Hz)_MIC(?P<mic_id>\d+)_(?P<product>[A-Za-z]+)_ASYNC_(?P<async_mode>START|WAIT)$',
        # 2. 带产品名但无异步模式
        r'^AUDIO_L2AR_EAR_(?P<id>\d+)_(?P<start_freq>\d+K?Hz)_TO_(?P<end_freq>\d+K?Hz)_MIC(?P<mic_id>\d+)_(?P<product>[A-Za-z]+)$',
        # 3. 带EQ模式和产品名
        r'^AUDIO_L2AR_EAR_(?P<id>\d+)_(?P<start_freq>\d+K?Hz)_TO_(?P<end_freq>\d+K?Hz)_MIC(?P<mic_id>\d+)_(?P<product>[A-Za-z]+)_EQ$',
        # 4. 仅带MIC ID，无其他附加信息
        r'^AUDIO_L2AR_EAR_(?P<id>\d+)_(?P<start_freq>\d+K?Hz)_TO_(?P<end_freq>\d+K?Hz)_MIC(?P<mic_id>\d+)$'
    ]

    print(f"测试字符串: {test_string}\n")
    matched = False

    for i, pattern in enumerate(EAR_TEST, 1):
        print(f"----- 检查模式 {i} -----")
        print(f"正则表达式: {pattern}")

        # 执行匹配
        match = re.match(pattern, test_string)

        if match:
            print("\n✅ 匹配成功!")
            print("提取的参数:")
            for group_name, value in match.groupdict().items():
                print(f"  {group_name}: {value}")
            matched = True
            break
        else:
            print("❌ 匹配失败\n")

    if not matched:
        print("❌ 所有模式均匹配失败")


if __name__ == "__main__":
    test_ear_regex_matching()