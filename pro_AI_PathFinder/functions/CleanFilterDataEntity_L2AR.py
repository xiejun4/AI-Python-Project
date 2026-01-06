"""

正则表达式的类对象

"""
class TestSites:
    """
    该类用于存放所有的测试站点名称。
    如果有新的测试站点，可以在这个类下面以静态属性的形式添加，例如：
    NEW_SITE = 'NewSiteName'
    """
    L2AR = 'L2AR'

class Platforms:
    """
    该类用于存放所有的芯片平台名称及描述。
    如果有新的芯片平台，可以在这个类下面以静态属性的形式添加，格式为：
    NEW_PLATFORM = ('NewPlatformName', '平台详细描述')
    """
    # 联发科芯片平台
    MTK = ('MTK','MediaTek 联发科芯片平台')
    # 高通芯片平台
    Qualcomm = ('Qualcomm','Qualcomm 高通芯片平台')
    # 通用平台（无特定芯片平台）
    GENERIC = ('Generic','通用平台，不特定于任何芯片厂商')
    GENERIC_Basic_Band = ('Generic_Basic_Band', '通用平台，不特定于任何芯片厂商的基带')

class TestTypes:
    """
    该类用于存放所有的测试类型名称。
    如果有新的测试类型，可以在这个类下面以静态属性的形式添加，例如：
    NEW_TEST_TYPE = 'NewTestTypeName'
    """
    # 综合测试
    COMPREHENSIVE_TEST = 'Comprehensive Test'
    # 校准测试
    CALIBRATION = 'Calibration'
    # 扬声器测试
    SPEAKER = 'Speaker'
    # 麦克风测试
    MIC = 'Mic'
    # 耳测（Earphone Auto Response）
    EAR = 'EAR'
    # 基带
    BASIC_BAND ='BASIC_BAND'

class MTKPatterns:
    """
    该类用于存放 MTK 芯片平台的所有正则表达式。
    如果有新的针对 MTK 平台的测试类型及其对应的正则表达式，可以在这个类下面以静态属性的形式添加，例如：
    NEW_TEST_TYPE = [
        r'^NewPatternForMTK$'
    ]
    """
    COMPREHENSIVE_TEST = [
        r'^MTK_WLAN\d+\.\d+G_TX_C\d+_HQA_\d+DB_(M|L)CH\d+',
        r'^MTK_WLAN\d+\.\d+G_RX_C\d+_HQA_RSSI_(M|L)CH\d+',
        r'^MTK_WLAN\d+G_TX_HQA_C\d+_\d+DB_CH\d+',
        r'^MTK_WLAN\d+G_RX_C\d+_HQA_CH\d+',
        r'^MTK_GPS_RX_V\d+_L\d+_-\d+DB',
        r'^MTK_BLUETOOTH_TX_POWER_V\d+_CH\d+',
        r'^MTK_MMRF_LTE_BC\d+_TX_\d+DB_V\d+_(M|L)CH\d+',
        r'^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_(M|L)CH\d+_EP'
    ]
    CALIBRATION = [
        r'^MTK_WLAN\d+\.\d+G_TX_C\d+_HQA_\d+DB_(M|L)CH\d+_CAL',
        r'^MTK_WLAN\d+\.\d+G_RX_C\d+_HQA_RSSI_(M|L)CH\d+_CAL',
        r'^MTK_WLAN\d+G_TX_HQA_C\d+_\d+DB_CH\d+_CAL',
        r'^MTK_WLAN\d+G_RX_C\d+_HQA_CH\d+_CAL',
        r'^MTK_GPS_RX_V\d+_L\d+_-\d+DB_CAL',
        r'^MTK_BLUETOOTH_TX_POWER_V\d+_CH\d+_CAL',
        r'^MTK_MMRF_LTE_BC\d+_TX_\d+DB_V\d+_(M|L)CH\d+_CAL',
        r'^MTK_MMRF_LTE_BC\d+_RX_C\d+_RSSI_V\d+_(M|L)CH\d+_EP_CAL'
    ]

class QualcommPatterns:
    """
    该类用于存放高通芯片平台的所有正则表达式。
    如果有新的针对高通平台的测试类型及其对应的正则表达式，可以在这个类下面以静态属性的形式添加，例如：
    NEW_TEST_TYPE = [
        r'^NewPatternForQualcomm$'
    ]
    """
    COMPREHENSIVE_TEST = [
        # 蓝牙相关模式
        r'^QC_BT_RAD_MEAS_CW_POW_(M|L)CH\d+_PRO',

        # GPS相关模式
        r'^QC_GPS_RAD_CARRIER_TO_NOISE_GEN\d+_(WR|L\d+_EQ)',

        # WLAN 5.0GHz相关模式
        r'^QC_WLAN_5\.0GHz_80211[na]_RADIATED_TX_C\d+_(M|L)CH(\d*?)_P2K_(TRUE|FALSE)',
        r'^QC_WLAN_5\.0GHz_80211[na]_RADIATED_RX_C\d+_(M|L)CH(\d*?)_-?\d+',

        # WLAN 2.4GHz相关模式
        r'^QC_WLAN_2\.4GHz_80211[na]_RADIATED_TX_C\d+_(M|L)CH_P2K_(TRUE|FALSE)',
        r'^QC_WLAN_2\.4GHz_80211[na]_RADIATED_RX_C\d+_(M|L)CH_EQ',

        # LTE相关模式
        r'^QC_LTE_BC\d+_QRRFR_TX_POWER_(M|L)CH_\d+_V\d+',
        r'^QC_LTE_BC\d+_QRRFR_ACTION_V\d+_RX_C\d+_(M|L)CH_\d+',

        # NS相关模式
        r'^QC_NS_N\d+_.+?_V\d+_RX_C\d+_(M|H|L)CH_\d+'
    ]
    CALIBRATION = [
        # 蓝牙相关模式
        r'^QC_BT_RAD_MEAS_CW_POW_(M|L)CH\d+_PRO_CAL',

        # GPS相关模式
        r'^QC_GPS_RAD_CARRIER_TO_NOISE_GEN\d+_(WR|L\d+_EQ)_CAL',

        # WLAN 5.0GHz相关模式
        r'^QC_WLAN_5\.0GHz_80211[na]_RADIATED_TX_C\d+_(M|L)CH(\d*?)_P2K_(TRUE|FALSE)_CAL',
        r'^QC_WLAN_5\.0GHz_80211[na]_RADIATED_RX_C\d+_(M|L)CH(\d*?)_-?\d+_CAL',

        # WLAN 2.4GHz相关模式
        r'^QC_WLAN_2\.4GHz_80211[na]_RADIATED_TX_C\d+_(M|L)CH_P2K_(TRUE|FALSE)_CAL',
        r'^QC_WLAN_2\.4GHz_80211[na]_RADIATED_RX_C\d+_(M|L)CH_EQ_CAL',

        # LTE相关模式
        r'^QC_LTE_BC\d+_QRRFR_TX_POWER_(M|L)CH_\d+_V\d+_CAL',
        r'^QC_LTE_BC\d+_QRRFR_ACTION_V\d+_RX_C\d+_(M|L)CH_\d+_CAL'
    ]

class GenericPatterns:
    """
    该类用于存放SPEAKER设备相关的正则表达式。
    """
    SPEAKER_TEST = [
        # **SPEAKER**:
        # AUDIO_L2AR_ALERT_LEFT_7545_7100_TO_140Hz_MIC1
        # AUDIO_L2AR_ALERT_LEFT_7545_7100_TO_140Hz_MIC1_KANSA
        # AUDIO_L2AR_ALERT_LEFT_7545_7100_TO_140Hz_MIC1_KANSA_ASYNC_START
        # AUDIO_L2AR_ALERT_LEFT_7545_7100_TO_140Hz_MIC1_KANSA_ASYNC_WAIT
        # AUDIO_L2AR_ALERT_LEFT_7975_8KHz_TO_140Hz_MIC1LEFT_MILOS-5300_ASYNC_START
        # AUDIO_L2AR_ALERT_LEFT_7975_8KHz_TO_140Hz_MIC1LEFT_MILOS-5300_ASYNC_WAIT
        # AUDIO_L2AR_ALERT_LEFT2_12865_7100_TO_1000Hz_MIC1-KANSA_ASYNC_START
        # AUDIO_L2AR_ALERT_LEFT2_12865_7100_TO_1000Hz_MIC1-KANSA_ASYNC_WAIT
        # AUDIO_L2AR_ALERT_LEFT_11100_8KHz_TO_140Hz_MIC1left_URUS


        # 正则表达式说明：
        # ^
        # 匹配字符串的开始位置，确保从整个字符串的最开头开始匹配。
        # AUDIO_L2AR_ALERT_LEFT
        # 匹配固定前缀 “AUDIO_L2AR_ALERT_LEFT”，这是所有字符串共有的起始部分。
        # \d?
        # 匹配可选的一个数字（\d表示数字，?表示 “0 次或 1 次”）。
        # 对应示例中的 “LEFT”（无数字）或 “LEFT2”（有数字 2）。
        # _\d+
        # 匹配一个下划线（_）加一个或多个数字（\d+）。
        # 对应示例中的 “_7545”“_7975”“_12865” 等数字部分。
        # _(?:\d+K?Hz|\d+)
        # 匹配频率相关的部分，用非捕获分组(?:...)包裹（仅用于分组，不单独捕获内容）：
        # \d+K?Hz：匹配 “数字 + 可选的 K+Hz”（如 “8KHz”“140Hz”）；
        # |：表示 “或”；
        # \d+：匹配纯数字（如 “7100”）。
        # 对应示例中的 “_7100”“_8KHz” 等。
        # _TO_\d+Hz
        # 匹配固定的 “TO” 加数字加 “Hz”。
        # 对应示例中的 “_TO_140Hz”“_TO_1000Hz” 等。
        # _MIC[\w-]+
        # 匹配 “_MIC” 加一个或多个字母、数字、下划线或连字符（[\w-]+，\w等价于[A-Za-z0-9_]）。
        # 对应示例中的 “_MIC1”“_MIC1LEFT”“_MIC1-KANSA” 等。
        # (?:_[\w-]+)?
        # 匹配可选的设备 / 名称部分，用非捕获分组(?:...)包裹，末尾的?表示 “0 次或 1 次”：
        # 内部为 “_+ 字母 / 数字 / 下划线 / 连字符”。
        # 对应示例中可选的 “_KANSA”“_MILOS-5300”，也可省略（如最短的 “AUDIO_L2AR_ALERT_LEFT_7545_7100_TO_140Hz_MIC1” 就没有这部分）。
        # (?:_ASYNC_(?:START|WAIT))?
        # 匹配可选的异步操作结尾，用非捕获分组包裹，末尾的?表示 “0 次或 1 次”：
        # 内部先匹配固定的 “ASYNC”，再用(?:START|WAIT)匹配 “START” 或 “WAIT”。
        # 对应示例中可选的 “_ASYNC_START”“_ASYNC_WAIT”，也可省略（如 “AUDIO_L2AR_ALERT_LEFT_7545_7100_TO_140Hz_MIC1”“..._MIC1_KANSA” 就没有这部分）。
        # $
        # 匹配字符串的结束位置，确保整个字符串都被完整匹配，避免多余字符。
        # r'^AUDIO_L2AR_ALERT_LEFT\d?_\d+_(?:\d+K?Hz|\d+)_TO_\d+Hz_MIC[\w-]+(?:_[\w-]+)?(?:_ASYNC_(?:START|WAIT))?'
        r'^AUDIO_L2AR_ALERT_[A-Za-z]+\d?_\d+_(?:\d+K?Hz|\d+)_TO_\d+Hz_MIC[\w-]+(?:_[\w-]+)?(?:_ASYNC_(?:START|WAIT))?',
        r'AUDIO_L2AR_ALERT_[A-Za-z]+_\d+_\d+(?:KHz)?_TO_\d+(?:KHz)?_MIC[\w_]+(?:_ASYNC_(?:START|WAIT))?'
    ]

    """
    该类用于存放MIC设备相关的正则表达式。
    """
    MIC_TEST = [
        # **MIC**:
        # AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200_ASYNC_START
        # AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200_ASYNC_WAIT 手机MIC录音测试
        #
        r'AUDIO_SAMPLE_MIC_\d+_CONTIGUOUS_SPKR\d+_\d+-\d+(?:_ASYNC_(START|WAIT))?',
        r'^AUDIO_SAMPLE_MIC_\d+_(FFT|DFT)_\d+_\d+K-\d+K_SPKR\d+(?:_[A-Za-z0-9-]+)?(?:_ASYNC_(START|WAIT))?',
        r'^AUDIO_MIC\d+_SPKR\d+_\d+-\d+K\d+Hz_VS_SEAL_.+'
    ]

    """
    该类用于存放EAR设备相关的正则表达式。
    """
    EAR_TEST = [
        # 1. 带异步模式和产品名的完整模式
        # 匹配格式: AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>_<产品名>_ASYNC_<异步模式>
        # 示例: AUDIO_L2AR_EAR_14705_140Hz_TO_7100Hz_MIC1_KANSA_ASYNC_START
        # 捕获组顺序:
        #   1: 数字ID(如14705)
        #   2: 起始频率(支持Hz/KHz单位，如140Hz)
        #   3: 结束频率(支持Hz/KHz单位，如7100Hz)
        #   4: 麦克风ID(数字，如1)
        #   5: 产品名称(如KANSA)
        #   6: 异步模式(固定值START或WAIT)
        r'^AUDIO_L2AR_EAR_(\d+)_(\d+K?Hz)_TO_(\d+K?Hz)_MIC(\d+)_([A-Za-z]+)_ASYNC_(START|WAIT)',

        # 2. 带产品名但无异步模式
        # 匹配格式: AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>_<产品名>
        # 示例: AUDIO_L2AR_EAR_14705_140Hz_TO_7100Hz_MIC1_KANSA
        # 捕获组顺序:
        #   1: 数字ID(如14705)
        #   2: 起始频率(支持Hz/KHz单位，如140Hz)
        #   3: 结束频率(支持Hz/KHz单位，如7100Hz)
        #   4: 麦克风ID(数字，如1)
        #   5: 产品名称(如KANSA)
        r'^AUDIO_L2AR_EAR_(\d+)_(\d+K?Hz)_TO_(\d+K?Hz)_MIC(\d+)_([A-Za-z]+)',

        # # 3. 带EQ模式和产品名
        # # 匹配格式: AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>_<产品名>_EQ
        # # 示例: AUDIO_L2AR_EAR_25000_8KHz_TO_140Hz_MIC1_PORTO_EQ
        # # 捕获组顺序:
        # #   1: 数字ID(如25000)
        # #   2: 起始频率(支持Hz/KHz单位，如8KHz)
        # #   3: 结束频率(支持Hz/KHz单位，如140Hz)
        # #   4: 麦克风ID(数字，如1)
        # #   5: 产品名称(如PORTO)
        # r'^AUDIO_L2AR_EAR_(\d+)_(\d+K?Hz)_TO_(\d+K?Hz)_MIC(\d+)_([A-Za-z]+)_EQ$',
        #
        # # 4. 仅带MIC ID，无其他附加信息
        # # 匹配格式: AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>
        # # 示例: AUDIO_L2AR_EAR_14705_140Hz_TO_7100Hz_MIC1、AUDIO_L2AR_EAR_14705_140Hz_TO_7100Hz_MIC2
        # # 捕获组顺序:
        # #   1: 数字ID(如14705)
        # #   2: 起始频率(支持Hz/KHz单位，如140Hz)
        # #   3: 结束频率(支持Hz/KHz单位，如7100Hz)
        # #   4: 麦克风ID(数字，如1、2)
        # r'^AUDIO_L2AR_EAR_(\d+)_(\d+K?Hz)_TO_(\d+K?Hz)_MIC(\d+)$'
    ]

# TODO：这里添加正则表达式列表
class BasicBandPatterns:

    L2AR_BASIC_BAND = [
        # 正则表达式说明：
        # ^ 表示字符串开始
        # CAPSWTICH 匹配电容式开关标识（允许原始拼写）
        # TURBORCHARGE 匹配涡轮增压充电技术标识
        # \w+ 匹配任意产品名称（字母、数字、下划线）
        # \d+W 匹配数字+W格式的功率标识（如30W、65W等）
        # $ 表示字符串结束
        r"^CAPSWTICH_TURBORCHARGE_\w+_\d+W",
        r'^GET_BATTERY_CHARGE_LEVEL_STATUS',

        # SPKinfoprogramming_READ 匹配SPK信息程序读取开关标识
        r"^SPKinfoprogramming_READ",
        r"^SPK_INFO_PROGAMMING",

        # ANDROID_GET_BATTERY_LEVEL
        r'^ANDROID_GET_BATTERY_LEVEL',
        
        r'^ANDROID_MAGNETOMETER',
        r'^MAGNETOMETER_PRESENSE_APK_STATUS',
        
        r'^QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW_[0-9A-Z]{2}_[0-9A-Z]{4}',
        r'^MECH_SWITCH_STATE_SIM_REMOVED'
    ]
