import re

# 完全匹配的正则表达式
pattern = r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Z]+)$'

# 测试字符串
test_string = "AUDIO_L2AR_ALERT_RIGHT_14600_16KHZ_TO_7KHZ_MIC2_PORTO"

# 执行匹配
match = re.match(pattern, test_string)

if match:
    print("匹配成功！")
    print("提取的分组：")
    print(f"方向(direction): {match.group('direction')}")  # RIGHT
    print(f"ID(id): {match.group('id')}")                  # 14600
    print(f"起始频率(start_freq): {match.group('start_freq')}")  # 16KHZ
    print(f"结束频率(end_freq): {match.group('end_freq')}")      # 7KHZ
    print(f"MIC ID(mic_id): {match.group('mic_id')}")      # 2
    print(f"产品(product): {match.group('product')}")      # PORTO
else:
    print("匹配失败")
