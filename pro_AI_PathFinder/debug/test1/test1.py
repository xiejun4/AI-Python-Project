import re

# 进一步简化的正则表达式，确保匹配所有目标字符串
pattern = r'AUDIO_L2AR_ALERT_[A-Za-z]+_\d+_\d+(?:KHz)?_TO_\d+(?:KHz)?_MIC[\w_]+(?:_ASYNC_(?:START|WAIT))?'

# 测试数据
log_lines = [
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	Header	==========================================================================================================================================================================",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	Header	Test = AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START  |  Barcode = N6PC270177  |  Time start = 7/17/2025 9:35:38 AM",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	AsyncTesting	Creating test 'AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO' thread to run this test asynchronously...",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	AsyncTesting	Adding test 'AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO' to the async test thread pool.",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	AsyncTesting	Starting test 'AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO' thread to run this test asynchronously...",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	Header	===========================================================================================================================================================================================================================================",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	EvalAndLogResults	102	244	AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	0	0	0	P/F	2	30269	PASSED		<-----------------------|#|--------------------->	Off	False	False	AUDRIGSS",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	Header	Test = AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO  |  Barcode = N6PC270177  |  Time start = 7/17/2025 9:35:38 AM",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	before analyzer start",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	AssignInputDevice	Input Device assigned to Cube pro Analog In 1/2",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	GetModelData	Unit model data: AUDIO_FAMILY = 'PORTO25'",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	AudioBenchMicSensitivityFactor49.801946	AudioBenchPathCorrectionFactor3500",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	StartAnalyzer	starting analysisThread",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	Footer	Test = AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START  |  Overall Result = 0  |  Test Time = 0 msec",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO_ASYNC_START	Footer	==========================================================================================================================================================================",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	StartAnalyzer	analysisThread started",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	StartAnalyzer	open input stream",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	PortAudio	Opening PortAudio stream (callback)...",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	PortAudio	PortAudio stream (callback) opened.",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	after analyzer start",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	MeasureNoiseLevel	Noise Readings",
    "AUDIO_L2AR_ALERT_RIGHT_14600_16KHz_TO_7KHz_MIC2_PORTO	GetConsecutiveFrames	Capturing Frames."
]

# 应用正则表达式并展示匹配结果
print(f"使用正则表达式: {pattern}\n")
match_count = 0
for i, line in enumerate(log_lines, 1):
    # 查找行中是否包含匹配的模式
    match = re.search(pattern, line)
    if match:
        match_count += 1
        print(f"行 {i} 匹配成功: {match.group()}")
        print(f"行内容预览: {line[:80]}...")
        print("-" * 80)
    else:
        print(f"行 {i} 未匹配: {line[:50]}...")

print(f"\n匹配总结: 共 {match_count} 行匹配成功，{len(log_lines) - match_count} 行未匹配")
