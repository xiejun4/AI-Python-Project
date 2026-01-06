from typing import List, Dict
from dataclasses import dataclass, field, asdict, replace

"""

L2AR的数据实体

"""


@dataclass
class StatusIndicatorItem:
    item: str
    state: str
    color: str
    show: str


@dataclass
class StatusIndicators:
    """更新后的状态指示器类，包含一个测试项列表"""
    Status_Indicators: List[StatusIndicatorItem]


# @dataclass
# class KeyConclusionSummary:
#     WCN_Status: str
#     LTE_status: str


@dataclass
class GlobalOverview:
    Status_Indicators: StatusIndicators
    # Key_Conclusion_Summary: KeyConclusionSummary


@dataclass
class TestProjectResult:
    Test_Project: str
    Meaning: str
    Indicator: str
    Test_Value: str
    Range: str
    Test_Result: str
    Trend_Analysis: str
    Implied_Problem_Possibility: str
    Chart_Name: str
    Chart_Content: str


@dataclass
class TestAnalysis:
    Test_Project_Results: List[TestProjectResult]
    # Analysis_Logic_Chain: str


@dataclass
class ModularTestResultsDisplay:
    Test_Analysis: TestAnalysis


# @dataclass
# class OptimizationSuggestionsOrSolutions:
#     Emergency_Plan: str
#     Radical_Solution: str


@dataclass
class Report:
    Report_Theme: str
    Global_Overview: GlobalOverview
    Modular_Test_Results_Display: ModularTestResultsDisplay
    # Optimization_Suggestions_or_Solutions: OptimizationSuggestionsOrSolutions


# 汇总所有正则表达式模式
REGEX_PATTERNS_For_Status_Indicators = {
    'wifi_2_4g_tx': [
        r'MTK_WLAN_\d+\.\d+G_C\d+_TX_POWER_(H|M|L)CH\d+_ANT_CW',
        r"WLAN_TX_WLAN_80211_(?P<band>2_4G)"
        r"_(?P<antenna_type>PRIMARY|SECONDARY|TERTIARY)"
        r"_CH_(?P<channel>\d+)",
        r"_(?P<cal_type>NEW_CAL|OLD_CAL|CUSTOM_CAL)",
        r'^QC_WLAN_2\.4GHz_80211[na]_RADIATED_TX_C\d+_(H|M|L)CH_P2K_(TRUE|FALSE)'
    ],
    'wifi_2_4g_rx': [
        r'MTK_WLAN_\d+\.\d+G_C\d+_(H|M|L)CH\d+_RSSI_ANT_CW',
        r"MTK_WLAN_(?P<band>\d+\.\d+G)_CH(?P<channel>\d+)_RSSI",
        r"WLAN_RX_WLAN_80211_(?P<band>2_4G)"
        r"_(?P<antenna_type>PRIMARY|SECONDARY|TERTIARY)"
        r"_CH_(?P<channel>\d+)"
        r"_(?P<cal_type>NEW_CAL|OLD_CAL|CUSTOM_CAL)",
        r'^QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RADIATED_RX_C\d+_(H|M|L)CH_EQ',
        r'^QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RAD_RX_C\d+_CAL_POWER_(H|M|L)CH'
    ],
    'wifi_5g_tx': [
        r'MTK_WLAN_\d+G_C\d+_TX_POWER_(H|M|L)CH\d+_ANT_CW',
        r"WLAN_TX_WLAN_80211_(?P<band>5G|5G_160M)_(?P<antenna_type>PRIMARY|SECONDARY|TERTIARY)_CH_(?P<channel>\d+)_(?P<cal_type>NEW_CAL|OLD_CAL|CUSTOM_CAL)",
        r"MTK_WLAN_(?P<band>\d+\.?\d*G)_C(?P<channel>\d+)_TX_POWER_(?P<mode>(H|M|L)CH\d+)_(?:ANT_)?(?P<test_type>\w+)",
        r'^QC_WLAN_5\.0GHz_80211[na]_RADIATED_TX_C\d+_(H|M|L)CH(\d*?)_P2K_(TRUE|FALSE)',
        r'^QC_WLAN_\d+\.\d+GHz_\d+[a-zA-Z]_RAD_TX_C\d_CAL_(H|M|L)CH_ANT_CW',
        r'^QC_WLAN_\d+\.\d+GHz_\d+[a-zA-Z]_RAD_TX_C\d_CAL_(H|M|L)CH_CW'

    ],
    'wifi_5g_rx': [
        r'MTK_WLAN_\d+\.\d+G_C\d+_(H|M|L)CH\d+_RSSI_ANT',
        r'MTK_WLAN_\d+\.\d+G_C\d+_CH\d+_RSSI_ANT',
        r"WLAN_RX_WLAN_80211_(?P<band>2_4G|5G|5G_160M|6G)"
        r"_(?P<antenna_type>PRIMARY|SECONDARY|TERTIARY)"
        r"_CH_(?P<channel>\d+)"
        r"_(?P<cal_type>NEW_CAL|OLD_CAL|CUSTOM_CAL)",
        r'^QC_WLAN_5\.0GHz_80211[na]_RADIATED_RX_C\d+_(H|M|L)CH(\d*?)_-?\d+',
        r'^QC_WLAN_\d+\.\d+GHz_\d+[a-zA-Z]_RAD_RX_C\d_CAL_(H|M|L)CH_ANT_CW',
        r'^QC_WLAN_\d+\.\d+GHz_\d+[a-zA-Z]_RAD_RX_C\d_CAL_(H|M|L)CH_CW',
        r'^QC_WLAN_\d+\.\d+GHz_\d+[a-zA-Z]_RAD_RX_C\d+_CAL_POWER_(H|M|L)CH(\d+)$'
    ],
    'bluetooth_tx': [
        r'MTK_BLUETOOTH_POWER',
        r'BLUETOOTH_TX',
        r'BT_RAD_MEAS_CW_POW_CH_(\d*?)',
        r'MTK_BLUETOOTH_CH(\d*?)_STATUS'
    ],
    'gps_rx': [
        r'MTK_GPS_SIGNAL_RX',
        r'MTK_GPS_SIGNAL',
        r'GPS_RX',
        r'QC_GPS(?:_L\d)?_CARRIER_TO_NOISE_ANT_CW',
    ],
    'lte_tx': [
        r'LTE_BC\d+_TX',
        r'LTE_(TDD|FDD)_TX',
        r'^QC_LTE_BC\d+_QRRFR_TX_POWER_(H|M|L)CH_\d+_V\d+',
    ],
    'lte_rx': [
        r'LTE_BC\d+_RX',
        r'(?=.*LTE)(?=.*RX)(?=.*RSSI).+',
        r'^QC_LTE_BC\d+_QRRFR_ACTION_V\d+_RX_C\d+_(H|M|L)CH_\d+'
    ],
    'basic_band': [
        r"^CAPSWTICH_TURBORCHARGE_\w+_\d+W",
        r"^SPKINFOPROGRAMMING_READ",
        r"^SPK_INFO_PROGAMMING",
        r'^ANDROID_GET_BATTERY_LEVEL',
        r'^GET_BATTERY_CHARGE_LEVEL_STATUS',
        r'^ANDROID_MAGNETOMETER',
        r'^MAGNETOMETER_PRESENSE_APK_STATUS',
        r'^QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW_[0-9A-Z]{2}_[0-9A-Z]{4}',
        r'^MECH_SWITCH_STATE_SIM_REMOVED',
        r'^INCLINOMETER_MEASURE_A\\+G'
        r'^ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS'
    ],
    # TODO：这里添加各个测试项的正则表达式表
    'ns_rx': [
        # ^ 表示字符串开始
        # $ 表示字符串结束
        # \d+ 匹配一个或多个数字
        # .+? 匹配任意字符（非贪婪模式）
        # 下划线 _ 直接匹配下划线字符
        r'^QC_NS_N\d+_RX_RSSI_C\d+_(M|H|L)CH_\d+',
        r'^QC_NS_N\d+_RX_RSSI_C\d+_(M|H|L)CH_\d+_ANT_CW',
        r'^MTK_NR\d+G_N\d+_C\d+_RX_RAD_RSSI_(H|M|L)CH\d+',
        r'^MTK_NR\d+G_N\d+_C\d+_RX_RAD_RSSI_(H|M|L)CH\d+_ANT_CW'
    ],

    'mtk_common': [
        "^MTK_META_TRACKID_READ_FROM_MD_NVRAM",
        "^MTK_META_READ_TRACKID_FROM_MD_NVRAM"
    ]

}
