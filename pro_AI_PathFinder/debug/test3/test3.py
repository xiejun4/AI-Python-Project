# 使用原始字符串定义（推荐）
first_key = r'AUDIO_L2AR_ALERT_[A-Za-z]+_\\d+_\\d+(?:KHz)?_TO_\\d+(?:KHz)?_MIC[\\w_]+(?:_ASYNC_(?:START|WAIT))?.*FAILED'

# 正确替换原始字符串中的双反斜杠
fixed_key = first_key.replace('\\\\', '\\')

print("替换前:", first_key)   # 显示带有\\d的原始字符串
print("替换后:", fixed_key)   # 显示带有\d的正确正则表达式

# 验证正则表达式
import re
test_string = "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_FAILED"
pattern = re.compile(fixed_key)
print("匹配结果:", bool(pattern.match(test_string)))  # 应输出True
