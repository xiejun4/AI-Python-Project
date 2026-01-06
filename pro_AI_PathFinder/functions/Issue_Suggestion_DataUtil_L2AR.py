# 主要改进内容
# 为每种测试类型创建专用函数：
# 新增了针对不同测试类型的专用函数：
# wlan_rx_issue_suggestion: WLAN 接收信号强度异常
# gps_rx_issue_suggestion: GPS 接收信号异常
# bluetooth_tx_issue_suggestion: 蓝牙发射功率异常
# lte_tx_issue_suggestion: LTE 发射功率异常
# lte_rx_issue_suggestion: LTE 接收信号强度异常
# 使用工厂模式选择合适的函数：
# 创建了 suggestion_generator_map 字典，将测试类型和模式映射到对应的问题与建议生成函数
# 通过组合 test_type 和 test_mode 生成键值，动态选择合适的函数
# 如果没有匹配的函数，则使用默认的 wlan_tx_issue_suggestion 函数
# 优化参数处理：
# 为每个函数添加了适当的文档字符串
# 根据不同测试类型的特点，调整了函数参数的描述和默认值
# 可扩展性：
# 未来需要添加新的测试类型时，只需：
# 创建新的问题与建议生成函数
# 在 suggestion_generator_map 字典中添加对应的映射
# 无需修改核心逻辑，大大降低了维护成本
import re


def wlan_tx_issue_suggestion_v1(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: 2.4G, 5G等)",
        channel_id="请输入通道标识(如: C0, C1等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh'
):
    """
    根据测试参数生成WLAN发射功率问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: 2.4G, 5G等)
        channel_id: 通道标识 (如: C0, C1等)
        power_value: 发射功率数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述
        issue_description = f"""
{test_item_desc}{problem_desc}简易排查方案
一、核心问题
{test_type} {freq_range} {channel_id} 通道发射功率 {power_value} dBm，
{deviation} {standard_value} dBm 标准，需快速排查测试设备连接、硬件及软件问题。
二、产线快速排查步骤
（一）测试设备检查
综测仪：确认屏幕显示 “ {freq_range} {channel_id} ”；检查与设备线缆接口，重插松动接口。
程控电源：查看指示灯是否正常；检查输出线有无破损，破损即换线。
（二）硬件连接检查
工装夹具：擦除接触点氧化发黑处；拧紧夹具螺丝，确保固定稳固。
射频链路：换掉有折痕、破损的电缆；旋紧射频头松动连接处。
（三）被测设备处理
整机外观：拆开后盖（允许时），隔离元件脱落、烧焦的设备；插紧天线与模块松动排线。
软件检查：进工厂测试工具查 {test_type} 功率，非 {standard_value} dBm 即上报；重启设备复测，仍超标则标记待处理。
"""
    elif language == 'en':
        # 英文描述
        issue_description = f"""
{test_item_desc}{problem_desc}Simple Troubleshooting Guide
I. Core Issue
The transmission power of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Quick troubleshooting of test equipment connections, hardware, and software issues is required.
II. Quick Troubleshooting Steps for Production Line
(1) Test Equipment Check
Spectrum Analyzer: Confirm that the screen displays "{freq_range} {channel_id}"; Check the cable interface with the device and reinsert any loose connections.
Programmable Power Supply: Check if the indicator light is normal; Inspect the output cable for any damage and replace if necessary.
(2) Hardware Connection Check
Fixture: Clean any oxidized or blackened contact points; Tighten the fixture screws to ensure a secure fit.
RF Link: Replace any cables with creases or damage; Tighten any loose RF connector joints.
(3) Device Under Test (DUT) Handling
Device Appearance: Open the back cover (if allowed) to isolate devices with detached or burnt components; Secure any loose antenna or module cables.
Software Check: Check the {test_type} power using the factory test tool. Report any values not equal to {standard_value} dBm; Restart the device and retest. Mark for further processing if the issue persists.
"""
    else:
        # 默认返回中文
        return wlan_tx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
                                        test_item_desc, problem_desc, language='zh')

    return issue_description.strip()


def wlan_tx_issue_suggestion(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: 2.4G, 5G等)",
        channel_id="请输入通道标识(如: C0, C1等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, Primary, Diversity)"  # 新增：天线类型参数
):
    """
    根据测试参数生成WLAN发射功率问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: 2.4G, 5G等)
        channel_id: 通道标识 (如: C0, C1等)
        power_value: 发射功率数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, Primary, Diversity)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示、天线专项检查、校准验证步骤
        issue_description = f"""
{test_item_desc}{problem_desc}简易排查方案
一、核心问题
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道发射功率 {power_value} dBm，
{deviation} {standard_value} dBm 标准，需快速排查测试设备连接、硬件及软件问题。
二、产线快速排查步骤
（一）测试设备检查
综测仪：确认屏幕显示 “ {freq_range} {channel_id} ”；检查与设备线缆接口，重插松动接口。
程控电源：查看指示灯是否正常；检查输出线有无破损，破损即换线。
（二）硬件连接检查
工装夹具：擦除接触点氧化发黑处；拧紧夹具螺丝，确保固定稳固。
射频链路：换掉有折痕、破损的电缆；旋紧射频头松动连接处。
{antenna_type}天线检查：确认天线与模块排线连接牢固，无松动/脱落；检查天线座有无氧化，氧化处用酒精棉擦拭清洁。
（三）被测设备处理
整机外观：拆开后盖（允许时），隔离元件脱落、烧焦的设备；插紧天线与模块松动排线。
软件检查：进工厂测试工具查 {test_type} {antenna_type}天线 {channel_id} 功率，非 {standard_value} dBm 即上报；重启设备复测，仍超标则标记待处理。
校准验证：若复测仍异常，重新执行 {test_item_desc} 校准流程（CAL），确认校准数据写入成功；校准后仍不达标则判定硬件故障。
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型、天线检查、校准验证逻辑
        issue_description = f"""
{test_item_desc}{problem_desc}Simple Troubleshooting Guide
I. Core Issue
The transmission power of {test_type} ({freq_range}) {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Quick troubleshooting of test equipment connections, hardware, and software issues is required.
II. Quick Troubleshooting Steps for Production Line
(1) Test Equipment Check
Spectrum Analyzer: Confirm that the screen displays "{freq_range} {channel_id}"; Check the cable interface with the device and reinsert any loose connections.
Programmable Power Supply: Check if the indicator light is normal; Inspect the output cable for any damage and replace if necessary.
(2) Hardware Connection Check
Fixture: Clean any oxidized or blackened contact points; Tighten the fixture screws to ensure a secure fit.
RF Link: Replace any cables with creases or damage; Tighten any loose RF connector joints.
{antenna_type} Antenna Check: Ensure the antenna-to-module cable is securely connected without looseness/falling off; Check the antenna base for oxidation and clean oxidized areas with alcohol wipes.
(3) Device Under Test (DUT) Handling
Device Appearance: Open the back cover (if allowed) to isolate devices with detached or burnt components; Secure any loose antenna or module cables.
Software Check: Check the {test_type} {antenna_type} Antenna {channel_id} power using the factory test tool. Report any values not equal to {standard_value} dBm; Restart the device and retest. Mark for further processing if the issue persists.
Calibration Verification: If the issue persists after retesting, re-execute the {test_item_desc} calibration process (CAL) and confirm successful calibration data writing; If calibration fails to resolve the issue, it is determined as a hardware fault.
"""
    else:
        # 默认返回中文，需传递新增的antenna_type参数
        return wlan_tx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 补充传递天线类型参数
        )

    return issue_description.strip()


def wlan_rx_issue_suggestion_v1(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: 2.4G, 5G等)",
        channel_id="请输入通道标识(如: C0, C1等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh'
):
    """
    根据测试参数生成WLAN接收信号强度问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: 2.4G, 5G等)
        channel_id: 通道标识 (如: C0, C1等)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}简易排查方案
一、核心问题定位
{test_type} {freq_range} {channel_id} 通道接收信号强度 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需重点关注以下方面：

二、临时处理建议
1. 若RSSI偏差>3dBm：检查测试设备连接及信号源
2. 若RSSI波动过大：检查测试环境干扰情况

三、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/RSSI采样值）
"""
    elif language == 'en':
        # 英文描述
        issue_description = f"""

Test Item Description: {test_item_desc}

{problem_desc}Simple Troubleshooting Guide
I. Core Problem Identification
The received signal strength of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Focus on the following aspects:

II. Immediate Handling Suggestions
1. If RSSI deviation >3dBm: Check test equipment connections and signal source
2. If RSSI fluctuates excessively: Check for environmental interference

III. Problem Reporting Guidelines
Please include the following data with the problem ticket:
1. Complete test logs (with timestamps/RSSI samples)
"""
    else:
        # 默认返回中文
        return wlan_rx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
                                        test_item_desc, problem_desc, language='zh')

    return issue_description.strip()


def wlan_rx_issue_suggestion(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: 2.4G, 5G等)",
        channel_id="请输入通道标识(如: C0, C1等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, Primary, Diversity)"  # 新增：天线类型参数
):
    """
    根据测试参数生成WLAN接收信号强度问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: 2.4G, 5G等)
        channel_id: 通道标识 (如: C0, C1等)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, Primary, Diversity)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示，补充天线相关排查点
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}简易排查方案
一、核心问题定位
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道接收信号强度 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需重点关注以下方面：

二、临时处理建议
1. 若RSSI偏差>3dBm：
   - 检查{antenna_type}天线与模块排线连接是否松动，重新插拔并固定
   - 确认测试设备（如信号发生器）与{antenna_type}天线的射频链路无破损
2. 若RSSI波动过大：
   - 检查测试环境是否存在同频段干扰（如其他WLAN设备）
   - 清洁{antenna_type}天线座接触点氧化层，确保信号传输稳定

三、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/RSSI采样值、{antenna_type}天线标识）
2. 天线外观及连接状态照片（重点标注接触点）
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型及相关排查逻辑
        issue_description = f"""

Test Item Description: {test_item_desc}

{problem_desc}Simple Troubleshooting Guide
I. Core Problem Identification
The received signal strength of {test_type} ({freq_range}) {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Focus on the following aspects:

II. Immediate Handling Suggestions
1. If RSSI deviation >3dBm:
   - Check if the {antenna_type} Antenna-to-module cable connection is loose, reinsert and secure it
   - Confirm that the RF link between test equipment (e.g., signal generator) and {antenna_type} Antenna is intact
2. If RSSI fluctuates excessively:
   - Check for co-frequency interference in the test environment (e.g., other WLAN devices)
   - Clean the oxidation layer on the {antenna_type} Antenna base contact points to ensure stable signal transmission

III. Problem Reporting Guidelines
Please include the following data with the problem ticket:
1. Complete test logs (with timestamps/RSSI samples, {antenna_type} Antenna identifier)
2. Photos of Antenna appearance and connection status (highlight contact points)
"""
    else:
        # 默认返回中文，补充传递天线类型参数
        return wlan_rx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 传递新增的天线类型参数
        )

    return issue_description.strip()


def gps_rx_issue_suggestion_v1(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: L1, L5等)",
        channel_id="请输入通道标识(如: GPS-1, GPS-2等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh'
):
    """
    根据测试参数生成GPS接收信号问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: L1, L5等)
        channel_id: 通道标识 (如: GPS-1, GPS-2等)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {channel_id} 通道接收信号强度 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）测试环境验证
1. GPS信号模拟器核查：
   - 确认RF输出功率为-110dBm@1575.42MHz
   - 确认RF线缆衰减值（≤0.5dB）

2. 频谱分析仪检查：
   - 确认频谱仪参考电平设置为-100dBm
   - 验证RBW/VBW设置（100kHz/300kHz）
   - 检查GPS信号频谱纯度（杂散≤-40dBc）

三、临时处理建议
1. 若信号捕获失败：检查GPS模拟器RF输出连接
2. 若跟踪不稳定：检查测试环境多径干扰

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/CN0值/跟踪状态）
"""
    elif language == 'en':
        # 英文描述
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The received signal strength of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Test Environment Verification
1. GPS Signal Simulator Check:
   - Confirm RF output power is -110dBm@1575.42MHz
   - Check RF cable attenuation (≤0.5dB)

2. Spectrum Analyzer Verification:
   - Confirm spectrum analyzer reference level is set to -100dBm
   - Verify RBW/VBW settings (100kHz/300kHz)
   - Check GPS signal spectral purity (spurious ≤-40dBc)

III. Immediate Mitigation Suggestions
1. For signal acquisition failure: Check GPS simulator RF output connection
2. For unstable tracking: Check for multipath interference in test environment

IV. Issue Reporting Guidelines
Please include the following data with problem tickets:
1. Complete test logs (with timestamps/CN0 values/tracking status)
"""
    else:
        # 默认返回中文
        return gps_rx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
                                       test_item_desc, problem_desc, language='zh')

    return issue_description.strip()


def gps_rx_issue_suggestion(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: L1, L5等)",
        channel_id="请输入通道标识(如: GPS-1, GPS-2等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, Primary, Diversity)"  # 新增：天线类型参数
):
    """
    根据测试参数生成GPS接收信号问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: L1, L5等)
        channel_id: 通道标识 (如: GPS-1, GPS-2等)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, Primary, Diversity)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示，补充天线相关排查点
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道接收信号强度 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）天线与硬件链路核查
1. {antenna_type}天线专项检查：
   - 确认天线与GPS模块排线连接无松动，重新插拔并固定卡扣
   - 检查天线馈线阻抗匹配（标准50Ω），替换阻抗异常的馈线
   - 清洁天线座接触点氧化层（用酒精棉擦拭，避免残留）

2. 测试环境验证
   - GPS信号模拟器核查：确认RF输出功率为-110dBm@1575.42MHz，且与{antenna_type}天线射频链路无衰减异常
   - 频谱分析仪检查：确认频谱仪参考电平设置为-100dBm，验证{antenna_type}天线接收端信号频谱纯度（杂散≤-40dBc）

（二）设备参数配置检查
1. 确认GPS模块工作模式（冷启动/热启动），优先采用热启动复测
2. 核查{antenna_type}天线对应的接收通道增益配置（标准值：20dB），偏差超1dB需重新校准

三、临时处理建议
1. 若信号捕获失败：
   - 检查{antenna_type}天线与模拟器RF接口连接，更换损坏的射频头
   - 重启GPS模拟器并重新加载星座数据（确保卫星数量≥8颗）
2. 若跟踪不稳定：
   - 检查测试环境多径干扰（远离金属反射物、高频设备）
   - 重新定位{antenna_type}天线摆放角度（建议水平放置，无遮挡）

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/CN0值/跟踪状态、{antenna_type}天线标识）
2. 天线外观、连接状态及馈线阻抗测试报告（重点标注接触点、阻抗值）
3. GPS模块通道增益配置截图
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型及相关排查逻辑
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The received signal strength of {test_type} ({freq_range}) {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Antenna and Hardware Link Verification
1. {antenna_type} Antenna Special Check:
   - Confirm the antenna-to-GPS module cable connection is secure, reinsert and fasten the buckle
   - Check antenna feeder impedance matching (standard 50Ω), replace feeders with abnormal impedance
   - Clean the oxidation layer on the antenna base contact points (wipe with alcohol pad, no residue)

2. Test Environment Verification
   - GPS Signal Simulator Check: Confirm RF output power is -110dBm@1575.42MHz, and no abnormal attenuation in the RF link with {antenna_type} Antenna
   - Spectrum Analyzer Verification: Confirm spectrum analyzer reference level is set to -100dBm, verify signal spectral purity at {antenna_type} Antenna receiving end (spurious ≤-40dBc)

(2) Device Parameter Configuration Check
1. Confirm GPS module working mode (cold start/warm start), prefer warm start for retesting
2. Verify the receive channel gain configuration of {antenna_type} Antenna (standard value: 20dB), re-calibrate if deviation exceeds 1dB

III. Immediate Mitigation Suggestions
1. For signal acquisition failure:
   - Check the RF interface connection between {antenna_type} Antenna and simulator, replace damaged RF connectors
   - Restart the GPS simulator and reload constellation data (ensure satellite count ≥8)
2. For unstable tracking:
   - Check for multipath interference in the test environment (keep away from metal reflectors and high-frequency devices)
   - Reposition {antenna_type} Antenna placement angle (horizontal placement recommended, no obstruction)

IV. Issue Reporting Guidelines
Please include the following data with problem tickets:
1. Complete test logs (with timestamps/CN0 values/tracking status, {antenna_type} Antenna identifier)
2. Antenna appearance, connection status and feeder impedance test report (highlight contact points and impedance values)
3. Screenshot of GPS module channel gain configuration
"""
    else:
        # 默认返回中文，补充传递天线类型参数
        return gps_rx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 传递新增的天线类型参数
        )

    return issue_description.strip()


# def bluetooth_tx_issue_suggestion(
#         test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
#         freq_range="请输入频率范围(如: 2.4G等)",
#         channel_id="请输入通道标识(如: BT-1, BT-2等)",
#         power_value="请输入发射功率数值(dBm)",
#         deviation="请输入偏差情况(如: 偏大, 偏小等)",
#         standard_value="请输入标准数值(dBm)",
#         test_item_desc="{{测试项描述}}",
#         problem_desc="{{问题描述}}",
#         language='zh'
# ):
#     """
#     根据测试参数生成蓝牙发射功率问题描述和排查建议
#
#     参数:
#         test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
#         freq_range: 频率范围 (如: 2.4G等)
#         channel_id: 通道标识 (如: BT-1, BT-2等)
#         power_value: 发射功率数值 (dBm)
#         deviation: 偏差变量 (如: 偏大, 偏小等)
#         standard_value: 标准数值 (dBm)
#         test_item_desc: 测试项描述，默认为"{{测试项描述}}"
#         problem_desc: 问题描述，默认为"{{问题描述}}"
#         language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
#
#     返回:
#         格式化的问题描述和排查建议
#     """
#     if language == 'zh':
#         # 中文描述
#         issue_description = f"""
# 测试项描述：{test_item_desc}
#
# {problem_desc}分层排查方案
# 一、核心问题定位
# {test_type} {freq_range} {channel_id} 通道发射功率 {power_value} dBm，
# {deviation} {standard_value} dBm 标准值，需按以下维度排查：
#
# 二、分层排查策略
# （一）测试环境验证
# 1. 综测仪核查：
#    - 确认测试模式为"Bluetooth BR/EDR"
#    - 检查RF输入线缆接口，重插/更换测试线
#    - 验证测量带宽设置为1MHz
#    - 确认参考电平设置为-20dBm
#
# 2. 频谱分析仪检查：
#    - 确认中心频率为2480MHz
#    - 验证RBW/VBW设置（300kHz/3MHz）
#    - 检查杂散辐射（≤-30dBm/MHz）
#
# 三、临时处理建议
# 1. 若功率偏差>1dBm：检查综测仪RF输入连接
# 2. 若调制质量异常：检查测试环境干扰源
#
# 四、问题上报指引
# 请随问题单提供以下数据：
# 1. 完整测试日志（含时间戳/功率值/EVM值）
# """
#     elif language == 'en':
#         # 英文描述
#         issue_description = f"""
#
# Test Item Description: {test_item_desc}
#
# {problem_desc}Hierarchical Troubleshooting Guide
# I. Root Cause Localization
# The transmission power of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
# which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:
#
# II. Layered Diagnostic Strategy
# (1) Test Environment Verification
# 1. Test Set Check:
#    - Confirm test mode is "Bluetooth BR/EDR"
#    - Check RF input cable connections
#    - Verify measurement bandwidth is set to 1MHz
#    - Confirm reference level is set to -20dBm
#
# 2. Spectrum Analyzer Check:
#    - Confirm center frequency is 2480MHz
#    - Verify RBW/VBW settings (300kHz/3MHz)
#    - Check spurious emissions (≤-30dBm/MHz)
#
# 三、临时处理建议
# 1. For power deviation >1dBm: Check test set RF input connection
# 2. For abnormal modulation quality: Check for environmental interference sources
#
# 四、问题上报指引
# 请随问题单提供以下数据：
# 1. Complete test logs (with timestamps/power values/EVM values)
# """
#     else:
#         # 默认返回中文
#         return bluetooth_tx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
#                                              test_item_desc, problem_desc, language='zh')
#
#     return issue_description.strip()
#
def bluetooth_tx_issue_suggestion(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: 2.4G等)",
        channel_id="请输入通道标识(如: BT-1, BT-2等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, Primary, Diversity)"  # 新增：天线类型参数
):
    """
    根据测试参数生成蓝牙发射功率问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: 2.4G等)
        channel_id: 通道标识 (如: BT-1, BT-2等)
        power_value: 发射功率数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, Primary, Diversity)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示，补充天线相关排查点
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道发射功率 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）天线与硬件链路核查
1. {antenna_type}天线专项检查：
   - 确认蓝牙模块与天线的U.FL/IPEX连接器连接牢固，重新插拔测试
   - 检查天线阻抗匹配（标准50Ω），替换阻抗异常的柔性天线
   - 验证天线增益参数（标准0dBi~2dBi），与设计规格书比对

2. 测试环境验证
   - 综测仪核查：确认工作模式为"Bluetooth BR/EDR"，RF端口衰减补偿正确
   - 频谱分析仪检查：在2402-2480MHz频段内，验证{antenna_type}天线发射端杂散辐射（≤-30dBm/MHz）

（二）设备参数配置检查
1. 确认蓝牙模块发射功率等级设置（Class 1: 0dBm~20dBm, Class 2: -6dBm~4dBm）
2. 核查{antenna_type}天线对应的射频通道功率校准数据，偏差超1dB需重新校准
3. 检查蓝牙协议栈版本与功率控制算法匹配性（重点验证BLE与BR/EDR模式差异）

三、临时处理建议
1. 若功率偏差>1dBm：
   - 检查{antenna_type}天线与测试仪表的RF接口连接，更换损坏的射频转接头
   - 通过AT指令重新配置发射功率等级并保存
2. 若连接稳定性差：
   - 检查测试环境2.4GHz频段干扰（Wi-Fi信道重叠、微波炉等强干扰源）
   - 调整{antenna_type}天线摆放位置，远离金属遮挡物

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/功率值/调制指数/误码率、{antenna_type}天线标识）
2. 天线外观照片、连接器状态及阻抗测试报告
3. 蓝牙模块功率控制寄存器配置截图
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型及相关排查逻辑
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The transmission power of {test_type} ({freq_range}) {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Antenna and Hardware Link Verification
1. {antenna_type} Antenna Special Check:
   - Confirm U.FL/IPEX connector between Bluetooth module and antenna is secure, reinsert and test
   - Check antenna impedance matching (standard 50Ω), replace flexible antennas with abnormal impedance
   - Verify antenna gain parameters (standard 0dBi~2dBi), compare with design specifications

2. Test Environment Verification
   - Test Set Check: Confirm operating mode is "Bluetooth BR/EDR", RF port attenuation compensation is correct
   - Spectrum Analyzer Check: Verify spurious emissions at {antenna_type} Antenna transmitting end (≤-30dBm/MHz) within 2402-2480MHz band

(2) Device Parameter Configuration Check
1. Confirm Bluetooth module transmit power class setting (Class 1: 0dBm~20dBm, Class 2: -6dBm~4dBm)
2. Verify RF channel power calibration data for {antenna_type} Antenna, re-calibrate if deviation exceeds 1dB
3. Check compatibility between Bluetooth stack version and power control algorithm (focus on BLE vs BR/EDR mode differences)

III. Temporary Handling Suggestions
1. For power deviation >1dBm:
   - Check RF interface connection between {antenna_type} Antenna and test instruments, replace damaged RF adapters
   - Reconfigure transmit power level via AT commands and save
2. For poor connection stability:
   - Check 2.4GHz band interference in test environment (Wi-Fi channel overlap, microwave ovens and other strong interferers)
   - Adjust {antenna_type} Antenna position, keep away from metal obstructions

IV. Problem Reporting Guidelines
Please provide the following data along with the problem report:
1. Complete test logs (including timestamps/power values/modulation index/bit error rate, {antenna_type} Antenna identifier)
2. Antenna appearance photos, connector status and impedance test report
3. Screenshot of Bluetooth module power control register configuration
"""
    else:
        # 默认返回中文，补充传递天线类型参数
        return bluetooth_tx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 传递新增的天线类型参数
        )

    return issue_description.strip()


def lte_tx_issue_suggestion_v1(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: B1, B3等)",
        channel_id="请输入通道标识(如: LTE-1, LTE-2等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh'
):
    """
    根据测试参数生成LTE发射功率问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: B1, B3等)
        channel_id: 通道标识 (如: LTE-1, LTE-2等)
        power_value: 发射功率数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {channel_id} 通道发射功率 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）测试环境验证
1. 信号源核查：
   - 确认RF输出频率为20525.0MHz
   - 验证调制方式为QPSK/16QAM/64QAM
   - 确认功率设置为20dBm
   - 检查RF线缆衰减值（≤0.5dB）

2. 频谱分析仪检查：
   - 确认中心频率为20525.0MHz
   - 验证RBW/VBW设置（100kHz/300kHz）
   - 检查ACLR（邻道泄漏比）符合3GPP要求
   - 验证SEM（频谱发射模板）符合规范

三、临时处理建议
1. 若功率偏差>1dBm：检查信号源RF输出连接
2. 若调制精度异常：检查基带配置参数

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/功率值/EVM值/ACLR值）
"""
    elif language == 'en':
        # 英文描述
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The transmission power of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Test Environment Verification
1. Signal Generator Check:
   - Confirm RF output frequency is 20525.0MHz
   - Verify modulation scheme is QPSK/16QAM/64QAM
   - Confirm power setting is 20dBm
   - Check RF cable attenuation (≤0.5dB)

2. Spectrum Analyzer Check:
   - Confirm center frequency is 20525.0MHz
   - Verify RBW/VBW settings (100kHz/300kHz)
   - Check ACLR (Adjacent Channel Leakage Ratio) meets 3GPP requirements
   - Verify SEM (Spectrum Emission Mask) compliance

III. Temporary Handling Suggestions
1. For power deviation >1dBm: Check the RF output connection of the signal generator.
2. For abnormal modulation accuracy: Check the baseband configuration parameters.

IV. Problem Reporting Guidelines
Please provide the following data along with the problem report:
1. Complete test logs (including timestamps, power values, EVM values, and ACLR values).
"""
    else:
        # 默认返回中文
        return lte_tx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
                                       test_item_desc, problem_desc, language='zh')

    return issue_description.strip()


def lte_tx_issue_suggestion(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: B1, B3等)",
        channel_id="请输入通道标识(如: LTE-1, LTE-2等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, Primary, Diversity)"  # 新增：天线类型参数
):
    """
    根据测试参数生成LTE发射功率问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: B1, B3等)
        channel_id: 通道标识 (如: LTE-1, LTE-2等)
        power_value: 发射功率数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, Primary, Diversity)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示，补充天线相关排查点
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道发射功率 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）天线与硬件链路核查
1. {antenna_type}天线专项检查：
   - 确认天线与射频模块连接端口紧固，重新插拔并测试
   - 检查天线馈线损耗（标准≤0.8dB），替换损耗超标的馈线
   - 清洁天线连接器接触点（使用专用清洁剂，确保无氧化层）

2. 测试环境验证
   - 信号源核查：确认RF输出频率为{freq_range}频段中心频率，功率设置符合3GPP规范
   - 频谱分析仪检查：确认中心频率、RBW/VBW设置正确，验证{antenna_type}天线发射端ACLR指标

（二）设备参数配置检查
1. 确认LTE模块工作带宽配置（10MHz/20MHz）与测试要求一致
2. 核查{antenna_type}天线对应的发射通道功率校准参数，偏差超0.5dB需重新校准
3. 检查PA（功率放大器）工作状态，确保无过温保护或异常降功率

三、临时处理建议
1. 若功率偏差>1dBm：
   - 检查{antenna_type}天线与测试仪表的RF接口连接，更换损坏的射频头
   - 重新进行功率校准并保存参数
2. 若调制精度异常：
   - 检查基带IQ配置参数，重启模块后重试
   - 确认{antenna_type}天线极化方向与测试天线一致

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/功率值/EVM值/ACLR值、{antenna_type}天线标识）
2. 天线外观、连接状态及馈线损耗测试报告
3. LTE模块功率放大器工作参数截图
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型及相关排查逻辑
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The transmission power of {test_type} ({freq_range}) {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Antenna and Hardware Link Verification
1. {antenna_type} Antenna Special Check:
   - Confirm the antenna-to-RF module connection port is secure, reinsert and test
   - Check antenna feeder loss (standard ≤0.8dB), replace feeders with excessive loss
   - Clean antenna connector contact points (use dedicated cleaner, ensure no oxide layer)

2. Test Environment Verification
   - Signal Source Check: Confirm RF output frequency is the center frequency of {freq_range} band, power settings comply with 3GPP specifications
   - Spectrum Analyzer Check: Confirm center frequency and RBW/VBW settings are correct, verify ACLR limit at {antenna_type} Antenna transmitting end

(2) Device Parameter Configuration Check
1. Confirm LTE module working bandwidth configuration (10MHz/20MHz) matches test requirements
2. Verify the transmit channel power calibration parameters of {antenna_type} Antenna, re-calibrate if deviation exceeds 0.5dB
3. Check PA (Power Amplifier) working status, ensure no over-temperature protection or abnormal power reduction

III. Temporary Handling Suggestions
1. For power deviation >1dBm:
   - Check the RF interface connection between {antenna_type} Antenna and test instruments, replace damaged RF connectors
   - Re-calibrate power and save parameters
2. For abnormal modulation accuracy:
   - Check baseband IQ configuration parameters, restart module and retry
   - Confirm {antenna_type} Antenna polarization direction matches test antenna

IV. Problem Reporting Guidelines
Please provide the following data along with the problem report:
1. Complete test logs (including timestamps/power values/EVM values/ACLR values, {antenna_type} Antenna identifier)
2. Antenna appearance, connection status and feeder loss test report
3. Screenshot of LTE module power amplifier working parameters
"""
    else:
        # 默认返回中文，补充传递天线类型参数
        return lte_tx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 传递新增的天线类型参数
        )

    return issue_description.strip()


def lte_tx_issue_suggestion_add_more_fields(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: B1, B3等)",
        channel_id="请输入通道标识(如: LTE-1, LTE-2等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        # 新增参数（与调用方匹配，添加默认值保证兼容性）
        antenna_type=None,
        band_channel=None,
        mch_channel=None,
        antenna_flag=None
):
    """
    根据测试参数生成LTE发射功率问题描述和排查建议，新增对天线类型、子频段等参数的支持

    参数:
        原有参数略（保持不变）
        antenna_type: 天线类型（主集/分集）
        band_channel: 子频段信息（如BC01）
        mch_channel: 中心频率信道（如MCH300）
        antenna_flag: 天线配置标识（ANT）
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    # 处理中心频率计算（基于MCH信道，默认使用LTE Band4上行起始频率）
    center_freq = "未知"
    if mch_channel and mch_channel.startswith("MCH"):
        try:
            ch_num = int(''.join(filter(str.isdigit, mch_channel)))
            center_freq = f"{1710 + 0.1 * ch_num} MHz"  # 基于Band4上行公式
        except:
            center_freq = f"{mch_channel}对应频率"

    if language == 'zh':
        # 中文描述（整合新增参数信息）
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type}系统{band_channel or '未知'}子频段下，
{antenna_type or '未知'}天线（{channel_id}物理通道）发射功率为{power_value} dBm，
{deviation}标准值{standard_value} dBm。
中心频率信道：{mch_channel or '未指定'}（对应频率：{center_freq}）
{'' if not antenna_flag else '【天线配置标记：需重点检查发射链路匹配】'}

二、分层排查策略
（一）测试环境验证
1. 信号源核查：
   - 确认RF输出频率与{center_freq}一致
   - 验证子频段配置与{band_channel or '目标频段'}匹配
   - 确认功率设置为{standard_value}±0.5 dBm
   - 检查RF线缆衰减值（≤0.5dB，{antenna_type == '分集' and '分集发射链路需额外匹配校准' or ''}）

2. 频谱分析仪检查：
   - 中心频率设置为{center_freq}
   - 验证RBW/VBW设置（LTE发射测试推荐：1MHz/3MHz）
   - 检查{band_channel or '当前频段'}内ACLR（邻道泄漏比）≤-45dBc
   - 验证SEM（频谱发射模板）符合3GPP TS 36.101规范

（二）设备硬件排查
1. 天线链路检查：
   - {antenna_type == '主集' and '主集发射天线' or '分集发射天线'}驻波比测试（VSWR≤1.5）
   - 发射端到天线端口的功率损耗测试（≤1.5dB）
   - {'' if not antenna_flag else '发射天线相位一致性校准数据复核'}

2. 射频通道验证：
   - {channel_id}物理通道发射功率平坦度测试（带宽内偏差≤±0.5dB）
   - PA（功率放大器）工作点检查（确保在饱和功率以下3dB工作）
   - 通道滤波器带外抑制测试（对邻道抑制≥50dB）

三、临时处理建议
1. 若功率偏差>1dBm：
   - 优先校准{channel_id}通道的PA增益参数
   - 检查{antenna_type or '对应'}天线与发射前端的阻抗匹配

2. 若ACLR/SEM不达标：
   - 调整{band_channel and band_channel or '当前'}子频段的功率回退值（建议回退2dB）
   - 检查基带调制信号的EVM（误差向量幅度）≤8%

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/功率值/EVM值/ACLR值/SEM曲线）
2. {mch_channel or '中心频率'}的频谱模板测试报告
3. {antenna_type or '天线'}发射链路的S21参数（传输损耗）测试数据
"""
    elif language == 'en':
        # 英文描述（整合新增参数信息）
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
In {test_type} system {band_channel or 'unknown'} sub-band,
{antenna_type or 'unknown'} antenna ({channel_id} physical channel) transmit power is {power_value} dBm,
which is {deviation} the standard value {standard_value} dBm.
Center frequency channel: {mch_channel or 'unspecified'} (corresponding frequency: {center_freq})
{'' if not antenna_flag else '[Antenna Configuration Flag: Focus on transmit link matching]'}

II. Layered Diagnostic Strategy
(1) Test Environment Verification
1. Signal Generator Check:
   - Confirm RF output frequency matches {center_freq}
   - Verify sub-band configuration matches {band_channel or 'target band'}
   - Confirm power setting is {standard_value}±0.5 dBm
   - Check RF cable attenuation (≤0.5dB, {antenna_type == 'Diversity' and 'Diversity transmit link requires additional matching calibration' or ''})

2. Spectrum Analyzer Check:
   - Center frequency set to {center_freq}
   - Verify RBW/VBW settings (LTE TX test recommended: 1MHz/3MHz)
   - Check ACLR (Adjacent Channel Leakage Ratio) ≤-45dBc in {band_channel or 'current band'}
   - Verify SEM (Spectrum Emission Mask) compliance with 3GPP TS 36.101

(2) Device Hardware Inspection
1. Antenna Link Check:
   - {antenna_type == 'Primary' and 'Primary transmit antenna' or 'Diversity transmit antenna'} VSWR test (VSWR≤1.5)
   - Power loss test from transmitter to antenna port (≤1.5dB)
   - {'' if not antenna_flag else 'Transmit antenna phase consistency calibration data review'}

2. RF Channel Verification:
   - {channel_id} physical channel transmit power flatness test (in-band deviation ≤±0.5dB)
   - PA (Power Amplifier) operating point check (ensure 3dB below saturation power)
   - Channel filter out-of-band rejection test (≥50dB for adjacent channels)

III. Temporary Handling Suggestions
1. For power deviation >1dBm:
   - Prioritize calibrating PA gain parameters of {channel_id} channel
   - Check impedance matching between {antenna_type or 'corresponding'} antenna and transmit front-end

2. For ACLR/SEM non-compliance:
   - Adjust power back-off value for {band_channel and band_channel or 'current'} sub-band (2dB recommended)
   - Check EVM (Error Vector Magnitude) of baseband modulated signal ≤8%

IV. Problem Reporting Guidelines
Please provide the following data along with the problem report:
1. Complete test logs (including timestamps, power values, EVM values, ACLR values, SEM curves)
2. Spectrum mask test report for {mch_channel or 'center frequency'}
3. S21 parameter (transmission loss) test data of {antenna_type or 'antenna'} transmit link
"""
    else:
        # 默认返回中文
        return lte_tx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type,
            band_channel=band_channel,
            mch_channel=mch_channel,
            antenna_flag=antenna_flag
        )

    return issue_description.strip()


# def lte_rx_issue_suggestion(
#         test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
#         freq_range="请输入频率范围(如: B1, B3等)",
#         channel_id="请输入通道标识(如: LTE-1, LTE-2等)",
#         power_value="请输入接收信号强度数值(dBm)",
#         deviation="请输入偏差情况(如: 偏大, 偏小等)",
#         standard_value="请输入标准数值(dBm)",
#         test_item_desc="{{测试项描述}}",
#         problem_desc="{{问题描述}}",
#         language='zh'
# ):
#     """
#     根据测试参数生成LTE接收信号强度问题描述和排查建议
#
#     参数:
#         test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
#         freq_range: 频率范围 (如: B1, B3等)
#         channel_id: 通道标识 (如: LTE-1, LTE-2等)
#         power_value: 接收信号强度数值 (dBm)
#         deviation: 偏差变量 (如: 偏大, 偏小等)
#         standard_value: 标准数值 (dBm)
#         test_item_desc: 测试项描述，默认为"{{测试项描述}}"
#         problem_desc: 问题描述，默认为"{{问题描述}}"
#         language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
#
#     返回:
#         格式化的问题描述和排查建议
#     """
#     if language == 'zh':
#         # 中文描述
#         issue_description = f"""
# 测试项描述：{test_item_desc}
#
# {problem_desc}分层排查方案
# 一、核心问题定位
# {test_type} {freq_range} {channel_id} 通道接收信号强度 {power_value} dBm，
# {deviation} {standard_value} dBm 标准值，需按以下维度排查：
#
# 二、分层排查策略
# （一）测试环境验证
# 1. 信号源核查：
#    - 确认RF输出频率为1575.0MHz
#    - 验证调制方式为QPSK
#    - 确认信号强度为-105dBm
#    - 检查RF线缆衰减值（≤0.5dB）
#
# 2. 频谱分析仪检查：
#    - 确认中心频率为1575.0MHz
#    - 验证RBW/VBW设置（100kHz/300kHz）
#    - 检查信号质量（EVM≤17%）
#
# 三、临时处理建议
# 1. 若RSSI偏差>2dBm：检查信号源RF输出连接
# 2. 若误包率异常：检查测试环境干扰源
#
# 四、问题上报指引
# 请随问题单提供以下数据：
# 1. 完整测试日志（含时间戳/RSSI值/BLER值/EVM值）
# """
#     elif language == 'en':
#         # 英文描述
#         issue_description = f"""
# Test Item Description: {test_item_desc}
#
# {problem_desc}Hierarchical Troubleshooting Guide
# I. Root Cause Localization
# The received signal strength of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
# which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:
#
# II. Layered Diagnostic Strategy
# (1) Test Environment Verification
# 1. Signal Source Check:
#    - Confirm RF output frequency is 1575.0MHz
#    - Verify modulation scheme is QPSK
#    - Confirm signal strength is -105dBm
#    - Check RF cable attenuation (≤0.5dB)
#
# 2. Spectrum Analyzer Check:
#    - Confirm center frequency is 1575.0MHz
#    - Verify RBW/VBW settings (100kHz/300kHz)
#    - Check signal quality (EVM≤17%)
#
# III. Temporary Handling Recommendations
# 1. For RSSI deviation >2dBm: Check the RF output connection of the signal source.
# 2. For abnormal packet error rate: Check for environmental interference sources.
#
# IV. Problem Reporting Guidelines
# Please include the following data with your problem report:
# 1. Complete test logs (including timestamps, RSSI values, BLER values, and EVM values).
# """
#     else:
#         # 默认返回中文
#         return lte_rx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
#                                        test_item_desc, problem_desc, language='zh')
#
#     return issue_description.strip()
def lte_rx_issue_suggestion(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: B1, B3等)",
        channel_id="请输入通道标识(如: LTE-1, LTE-2等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, Primary, Diversity)"  # 新增：天线类型参数
):
    """
    根据测试参数生成LTE接收信号强度问题描述和排查建议

    参数:
        test_type: 测试制式 (如: WLAN, Bluetooth, GPS等)
        freq_range: 频率范围 (如: B1, B3等)
        channel_id: 通道标识 (如: LTE-1, LTE-2等)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, Primary, Diversity)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示，补充天线相关排查点
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道接收信号强度 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）天线与硬件链路核查
1. {antenna_type}天线专项检查：
   - 确认天线与射频前端模块连接紧固，重新插拔测试
   - 检查天线馈线损耗（标准≤0.8dB），替换损耗超标的馈线
   - 验证天线驻波比（VSWR≤1.5），确保符合3GPP规范要求

2. 测试环境验证
   - 信号源核查：确认RF输出频率为{freq_range}频段中心频率，功率设置符合测试规范
   - 频谱分析仪检查：验证{antenna_type}天线接收端信号频谱纯度，邻道干扰≤-45dBc

（二）设备参数配置检查
1. 确认LTE模块接收带宽配置（10MHz/20MHz）与测试要求一致
2. 核查{antenna_type}天线对应的接收通道增益（标准值：25dB±1dB）
3. 检查接收端LNA（低噪声放大器）工作状态，确保增益稳定

三、临时处理建议
1. 若RSSI偏差>2dBm：
   - 检查{antenna_type}天线与测试仪表的RF接口连接，更换损坏的射频头
   - 重新校准接收通道增益并保存参数
2. 若误包率异常：
   - 检查测试环境同频段干扰（其他LTE信号、雷达信号等）
   - 调整{antenna_type}天线方向，优化接收角度

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/RSSI值/BLER值/EVM值、{antenna_type}天线标识）
2. 天线外观、连接状态及驻波比测试报告
3. LTE模块接收通道增益配置截图
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型及相关排查逻辑
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The received signal strength of {test_type} ({freq_range}) {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Antenna and Hardware Link Verification
1. {antenna_type} Antenna Special Check:
   - Confirm the connection between antenna and RF front-end module is secure, reinsert and test
   - Check antenna feeder loss (standard ≤0.8dB), replace feeders with excessive loss
   - Verify antenna VSWR (Voltage Standing Wave Ratio ≤1.5), ensure compliance with 3GPP specifications

2. Test Environment Verification
   - Signal Source Check: Confirm RF output frequency is the center frequency of {freq_range} band, power settings comply with test specifications
   - Spectrum Analyzer Check: Verify signal spectral purity at {antenna_type} Antenna receiving end, adjacent channel interference ≤-45dBc

(2) Device Parameter Configuration Check
1. Confirm LTE module receiving bandwidth configuration (10MHz/20MHz) matches test requirements
2. Verify the receive channel gain of {antenna_type} Antenna (standard value: 25dB±1dB)
3. Check the working status of receiver LNA (Low Noise Amplifier) to ensure stable gain

III. Temporary Handling Recommendations
1. For RSSI deviation >2dBm:
   - Check the RF interface connection between {antenna_type} Antenna and test instruments, replace damaged RF connectors
   - Re-calibrate receive channel gain and save parameters
2. For abnormal packet error rate:
   - Check for co-channel interference in test environment (other LTE signals, radar signals, etc.)
   - Adjust {antenna_type} Antenna direction to optimize receiving angle

IV. Problem Reporting Guidelines
Please include the following data with your problem report:
1. Complete test logs (including timestamps/RSSI values/BLER values/EVM values, {antenna_type} Antenna identifier)
2. Antenna appearance, connection status and VSWR test report
3. Screenshot of LTE module receive channel gain configuration
"""
    else:
        # 默认返回中文，补充传递天线类型参数
        return lte_rx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 传递新增的天线类型参数
        )

    return issue_description.strip()


def nr5g_rx_issue_suggestion(
        test_type="请输入测试制式(如: NR5G, NR6G等)",
        freq_range="请输入频率范围(如: n77, n78等)",
        channel_id="请输入通道标识(如: C0, C1等)",
        mch_channel="请输入中心频率信道(如: MCH650000)",
        mch_type="请输入信道类型(如: 低, 中, 高)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        nr_generation="NR5G",
        language='zh'
):
    """
    根据测试参数生成NR5G接收信号强度问题描述和排查建议

    参数:
        test_type: 测试制式 (如: NR5G, NR6G等)
        freq_range: 频率范围 (如: n77, n78等)
        channel_id: 通道标识 (如: C0, C1等)
        mch_channel: 中心频率信道 (如: MCH650000)
        mch_type: 信道类型 (如: 低, 中, 高)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        nr_generation: NR世代 (如: NR5G, NR6G)
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述
        issue_description = f"""
测试项描述：{test_item_desc}

{nr_generation}接收信号异常分层排查方案
一、核心问题定位
{test_type} {freq_range} {mch_type}信道（{mch_channel}）{channel_id}通道接收信号强度为 {power_value} dBm，
{deviation}标准值 {standard_value} dBm，需按以下维度排查：

二、分层排查策略
（一）测试环境验证
1. 信号源核查：
   - 确认RF输出频率在3300-4200MHz范围（n77频段）
   - 验证调制方式（QPSK/16QAM/64QAM/256QAM）
   - 确认信号强度符合-110dBm弱信号场景要求
   - 检查波束赋形参数（水平±60°，垂直±30°）

2. 频谱分析仪检查：
   - 确认中心频率与{mch_channel}匹配
   - 验证RBW/VBW设置（30kHz/100kHz）
   - 检查信号质量（EVM≤12% @ 256QAM）
   - 确认带宽配置（100MHz/200MHz）

（二）设备配置检查
1. MIMO配置验证：
   - 确认{nr_generation}终端支持的空间层数
   - 检查天线端口映射关系（SRS/SU-MIMO）
   - 验证预编码矩阵索引（PMI）配置

2. 协议栈参数检查：
   - 确认RRC连接状态（Connected/Idle）
   - 检查测量间隙配置（Measurement Gap）
   - 验证HARQ重传机制（最大重传次数≤8）

三、临时处理建议
1. 若RSSI偏差>1.5dBm：重新校准波束赋形方向
2. 若BLER异常：检查上下行定时同步（±1.5μs）
3. 若MIMO层失配：重新配置空间复用层数

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/RSSI值/BLER值/EVM值）
2. 波束赋形增益扫描结果（水平/垂直方向图）
3. MIMO层间一致性测试报告
4. 3GPP TS 38.101协议一致性测试记录
"""
    elif language == 'en':
        # 英文描述
        issue_description = f"""
Test Item Description: {test_item_desc}

{nr_generation} Received Signal Anomaly Hierarchical Troubleshooting Guide
I. Root Cause Localization
The received signal strength of {channel_id} channel in {test_type} {freq_range} {mch_type} channel ({mch_channel}) is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Test Environment Verification
1. Signal Source Check:
   - Confirm RF output frequency is within 3300-4200MHz (n77 band)
   - Verify modulation scheme (QPSK/16QAM/64QAM/256QAM)
   - Confirm signal strength meets -110dBm weak signal scenario requirements
   - Check beamforming parameters (azimuth ±60°, elevation ±30°)

2. Spectrum Analyzer Check:
   - Confirm center frequency matches {mch_channel}
   - Verify RBW/VBW settings (30kHz/100kHz)
   - Check signal quality (EVM≤12% @ 256QAM)
   - Confirm bandwidth configuration (100MHz/200MHz)

(2) Device Configuration Check
1. MIMO Configuration Verification:
   - Confirm number of spatial layers supported by {nr_generation} UE
   - Check antenna port mapping (SRS/SU-MIMO)
   - Verify Precoding Matrix Index (PMI) configuration

2. Protocol Stack Parameter Check:
   - Confirm RRC connection status (Connected/Idle)
   - Check measurement gap configuration
   - Verify HARQ retransmission mechanism (max retries ≤8)

III. Temporary Handling Recommendations
1. For RSSI deviation >1.5dBm: Recalibrate beamforming direction
2. For abnormal BLER: Check uplink/downlink timing synchronization (±1.5μs)
3. For MIMO layer mismatch: Reconfigure spatial multiplexing layers

IV. Problem Reporting Guidelines
Please include the following data with your problem report:
1. Complete test logs (including timestamps, RSSI values, BLER values, EVM values)
2. Beamforming gain scan results (azimuth/elevation patterns)
3. MIMO inter-layer consistency test report
4. 3GPP TS 38.101 protocol conformance test records
"""
    else:
        # 默认返回中文
        return nr5g_rx_issue_suggestion(
            test_type, freq_range, channel_id, mch_channel, mch_type,
            power_value, deviation, standard_value, test_item_desc,
            nr_generation, language='zh'
        )

    return issue_description.strip()


def lte_rx_issue_suggestion_add_more_fields(
        test_type="请输入测试制式(如: WLAN, Bluetooth, GPS等)",
        freq_range="请输入频率范围(如: B1, B3等)",
        channel_id="请输入通道标识(如: LTE-1, LTE-2等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        # 新增参数（与调用方匹配，添加默认值保证兼容性）
        antenna_type=None,
        band_channel=None,
        mch_channel=None,
        rssi_indicator=None,
        antenna_flag=None
):
    """
    根据测试参数生成LTE接收信号强度问题描述和排查建议，新增对天线类型、子频段等参数的支持

    参数:
        原有参数略（保持不变）
        antenna_type: 天线类型（主集/分集）
        band_channel: 子频段信息（如BC01）
        mch_channel: 中心频率信道（如MCH300）
        rssi_indicator: 信号强度标识（RSSI）
        antenna_flag: 天线配置标识（ANT）
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    # 处理中心频率计算（基于MCH信道，默认使用LTE Band4下行起始频率）
    center_freq = "未知"
    if mch_channel and mch_channel.startswith("MCH"):
        try:
            ch_num = int(''.join(filter(str.isdigit, mch_channel)))
            center_freq = f"{2110 + 0.1 * ch_num} MHz"  # 基于Band4下行公式
        except:
            center_freq = f"{mch_channel}对应频率"

    if language == 'zh':
        # 中文描述（整合新增参数信息）
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type}系统{band_channel or '未知'}子频段下，
{antenna_type or '未知'}天线（{channel_id}物理通道）接收信号强度为{power_value} dBm，
{deviation}标准值{standard_value} dBm。
{'' if not rssi_indicator else '【信号强度专项监测】'}
中心频率信道：{mch_channel or '未指定'}（对应频率：{center_freq}）
{'' if not antenna_flag else '【天线配置标记：需重点检查天线连接链路】'}

二、分层排查策略
（一）测试环境验证
1. 信号源核查：
   - 确认RF输出频率与{center_freq}一致
   - 验证子频段配置与{band_channel or '目标频段'}匹配
   - 确认信号强度基准值（建议设置为{standard_value}±1 dBm）
   - 检查RF线缆衰减值（≤0.5dB，{antenna_type == '分集' and '分集天线链路需额外校准' or ''}）

2. 频谱分析仪检查：
   - 中心频率设置为{center_freq}
   - 验证RBW/VBW设置（LTE推荐：180kHz/600kHz）
   - 检查{band_channel or '当前频段'}内干扰信号（峰值≤-110dBm）

（二）设备硬件排查
1. 天线链路检查：
   - {antenna_type == '主集' and '主集天线' or '分集天线'}接口紧固性验证
   - 天线增益测试（建议≥2dBi，分集天线隔离度≥15dB）
   - {'' if not antenna_flag else '天线校准数据复核（查阅校准日志）'}

2. 射频通道验证：
   - {channel_id}物理通道增益一致性测试（与其他通道偏差≤1dB）
   - 通道滤波器带宽检查（需覆盖{band_channel or '目标子频段'}频率范围）

三、临时处理建议
1. 若RSSI偏差>2dBm：
   - 优先检查{antenna_type or '对应'}天线与射频前端的连接
   - 重新校准{channel_id}通道的接收增益

2. 若存在频段内干扰：
   - 切换至{band_channel and band_channel.replace('01', '02') or '相邻'}子频段测试
   - 启用带外干扰抑制功能

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/{rssi_indicator or 'RSSI'}值/通道增益/干扰谱图）
2. {mch_channel or '中心频率'}的频谱扫描结果
3. {antenna_type or '天线'}链路的S参数测试报告
"""
    elif language == 'en':
        # 英文描述（整合新增参数信息）
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
In {test_type} system {band_channel or 'unknown'} sub-band,
{antenna_type or 'unknown'} antenna ({channel_id} physical channel) received signal strength is {power_value} dBm,
which is {deviation} the standard value {standard_value} dBm.
{'' if not rssi_indicator else '[Signal Strength Special Monitoring]'}
Center frequency channel: {mch_channel or 'unspecified'} (corresponding frequency: {center_freq})
{'' if not antenna_flag else '[Antenna Configuration Flag: Focus on antenna link inspection]'}

II. Layered Diagnostic Strategy
(1) Test Environment Verification
1. Signal Source Check:
   - Confirm RF output frequency matches {center_freq}
   - Verify sub-band configuration matches {band_channel or 'target band'}
   - Confirm signal strength reference value (recommended: {standard_value}±1 dBm)
   - Check RF cable attenuation (≤0.5dB, {antenna_type == 'Diversity' and 'Diversity antenna link requires extra calibration' or ''})

2. Spectrum Analyzer Check:
   - Center frequency set to {center_freq}
   - Verify RBW/VBW settings (LTE recommended: 180kHz/600kHz)
   - Check interference in {band_channel or 'current band'} (peak ≤-110dBm)

(2) Device Hardware Inspection
1. Antenna Link Check:
   - {antenna_type == 'Primary' and 'Primary antenna' or 'Diversity antenna'} interface tightness verification
   - Antenna gain test (recommended ≥2dBi, diversity antenna isolation ≥15dB)
   - {'' if not antenna_flag else 'Antenna calibration data review (check calibration logs)'}

2. RF Channel Verification:
   - {channel_id} physical channel gain consistency test (deviation ≤1dB from other channels)
   - Channel filter bandwidth check (must cover {band_channel or 'target sub-band'} frequency range)

III. Temporary Handling Recommendations
1. For RSSI deviation >2dBm:
   - Prioritize checking connection between {antenna_type or 'corresponding'} antenna and RF front-end
   - Recalibrate receive gain of {channel_id} channel

2. For in-band interference:
   - Switch to {band_channel and band_channel.replace('01', '02') or 'adjacent'} sub-band for testing
   - Enable out-of-band interference suppression

IV. Problem Reporting Guidelines
Please include the following data with your problem report:
1. Complete test logs (including timestamp/{rssi_indicator or 'RSSI'} value/channel gain/interference spectrum)
2. Spectrum scan results of {mch_channel or 'center frequency'}
3. S-parameter test report of {antenna_type or 'antenna'} link
"""
    else:
        # 默认返回中文
        return lte_rx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type,
            band_channel=band_channel,
            mch_channel=mch_channel,
            rssi_indicator=rssi_indicator,
            antenna_flag=antenna_flag
        )

    return issue_description.strip()


def nr_tx_issue_suggestion_v1(
        test_type="请输入测试制式(如: NR, LTE, WLAN等)",
        freq_range="请输入频率范围(如: N78, N41等)",
        channel_id="请输入通道标识(如: NR-1, NR-2等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh'
):
    """
    根据测试参数生成5G NR发射功率问题描述和排查建议

    参数:
        test_type: 测试制式 (如: NR, LTE, WLAN等)
        freq_range: 频率范围 (如: N78, N41等)
        channel_id: 通道标识 (如: NR-1, NR-2等)
        power_value: 发射功率数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {channel_id} 通道发射功率 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）测试环境验证
1. 信号源核查：
   - 确认RF输出频率符合3GPP TS 38.101规范
   - 验证调制方式为QPSK/16QAM/64QAM/256QAM
   - 确认功率设置符合频段要求（FR1: ≤23dBm, FR2: ≤18dBm）
   - 检查RF线缆衰减值（≤0.3dB）

2. 频谱分析仪检查：
   - 确认中心频率与测试频段匹配
   - 验证RBW/VBW设置（1MHz/3MHz）
   - 检查ACLR（邻道泄漏比）和SRS（探测参考信号）
   - 验证EVM（误差向量幅度）≤8%（64QAM）

三、临时处理建议
1. 若功率偏差>0.8dBm：检查信号源与DUT连接
2. 若调制精度异常：检查波束赋形参数配置
3. 若频段切换异常：验证NR频段组合（EN-DC配置）

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/功率值/EVM值/SINR值）
2. 频段信息和带宽配置（如N78-100MHz）
3. 波束配置参数和MIMO模式
"""
    elif language == 'en':
        # 英文描述
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The transmission power of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Test Environment Verification
1. Signal Generator Check:
   - Confirm RF output frequency complies with 3GPP TS 38.101
   - Verify modulation scheme is QPSK/16QAM/64QAM/256QAM
   - Confirm power setting meets frequency band requirements (FR1: ≤23dBm, FR2: ≤18dBm)
   - Check RF cable attenuation (≤0.3dB)

2. Spectrum Analyzer Check:
   - Confirm center frequency matches test band
   - Verify RBW/VBW settings (1MHz/3MHz)
   - Check ACLR (Adjacent Channel Leakage Ratio) and SRS (Sounding Reference Signal)
   - Verify EVM (Error Vector Magnitude) ≤8% (64QAM)

III. Temporary Handling Suggestions
1. For power deviation >0.8dBm: Check signal generator to DUT connection
2. For abnormal modulation accuracy: Check beamforming parameters
3. For band switching issues: Verify NR band combination (EN-DC configuration)

IV. Problem Reporting Guidelines
Please provide the following data along with the problem report:
1. Complete test logs (including timestamps, power values, EVM values, SINR values)
2. Band information and bandwidth configuration (e.g., N78-100MHz)
3. Beam configuration parameters and MIMO mode
"""
    else:
        # 默认返回中文
        return nr_tx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
                                      test_item_desc, problem_desc, language='zh')

    return issue_description.strip()


def nr_tx_issue_suggestion(
        test_type="请输入测试制式(如: NR, LTE, WLAN等)",
        freq_range="请输入频率范围(如: N78, N41等)",
        channel_id="请输入通道标识(如: NR-1, NR-2等)",
        power_value="请输入发射功率数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, 毫米波, Sub-6G)"  # 新增：天线类型参数
):
    """
    根据测试参数生成5G NR发射功率问题描述和排查建议

    参数:
        test_type: 测试制式 (如: NR, LTE, WLAN等)
        freq_range: 频率范围 (如: N78, N41等)
        channel_id: 通道标识 (如: NR-1, NR-2等)
        power_value: 发射功率数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, 毫米波, Sub-6G)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示，补充发射相关排查点
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道发射功率 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）天线与发射链路核查
1. {antenna_type}天线发射性能检查：
   - 确认天线发射端口与PA（功率放大器）连接可靠性
   - 检查发射链路损耗（Sub-6G≤0.8dB，毫米波≤1.5dB）
   - 验证天线发射效率（Sub-6G≥85%，毫米波≥70%）
   - 毫米波天线额外检查：T/R组件发射增益一致性（±0.5dB）

2. 测试环境验证
   - 信号源核查：确认RF输出频率符合3GPP TS 38.101规范
   - 验证调制方式为QPSK/16QAM/64QAM/256QAM
   - 确认功率设置符合频段要求（FR1: ≤23dBm, FR2: ≤18dBm）
   - 检查RF线缆衰减值（≤0.3dB）

（二）发射参数配置检查
1. 功率控制参数验证：
   - 确认{antenna_type}天线对应的TPC（发射功率控制）命令配置
   - 检查功率余量报告（PHR）设置及上报周期
   - 验证上行功率控制算法（开环/闭环）参数

2. 频谱特性检查：
   - 确认中心频率与测试频段匹配
   - 验证RBW/VBW设置（1MHz/3MHz）
   - 检查ACLR（邻道泄漏比）和SRS（探测参考信号）功率
   - 验证EVM（误差向量幅度）≤8%（64QAM）

三、临时处理建议
1. 若功率偏差>0.8dBm：
   - 检查{antenna_type}天线与功率放大器连接，重新校准发射通道
   - 验证PA偏置电压是否在标准范围内（3.3V±0.1V）
2. 若调制精度异常：
   - 检查波束赋形参数配置，优化预编码矩阵
   - 重新校准{antenna_type}天线的IQ不平衡
3. 若频段切换异常：
   - 验证NR频段组合（EN-DC配置）
   - 检查{antenna_type}天线在频段切换时的匹配电路

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/功率值/EVM值/SINR值、{antenna_type}天线标识）
2. 频段信息和带宽配置（如N78-100MHz）
3. 波束配置参数和MIMO模式
4. {antenna_type}天线发射功率校准记录及PA工作状态日志
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型及相关排查逻辑
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The transmission power of {test_type} {freq_range} {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Antenna and Transmission Link Verification
1. {antenna_type} Antenna Transmission Performance Check:
   - Confirm connection reliability between antenna transmit port and PA (Power Amplifier)
   - Check transmission link loss (Sub-6G ≤0.8dB, mmWave ≤1.5dB)
   - Verify antenna transmission efficiency (Sub-6G ≥85%, mmWave ≥70%)
   - Additional checks for mmWave antennas: T/R module transmit gain consistency (±0.5dB)

2. Test Environment Verification
   - Signal Generator Check: Confirm RF output frequency complies with 3GPP TS 38.101
   - Verify modulation scheme is QPSK/16QAM/64QAM/256QAM
   - Confirm power setting meets frequency band requirements (FR1: ≤23dBm, FR2: ≤18dBm)
   - Check RF cable attenuation (≤0.3dB)

(2) Transmission Parameter Configuration Check
1. Power Control Parameter Verification:
   - Confirm TPC (Transmit Power Control) command configuration for {antenna_type} Antenna
   - Check Power Headroom Report (PHR) settings and reporting period
   - Verify uplink power control algorithm (open-loop/closed-loop) parameters

2. Spectral Characteristics Check:
   - Confirm center frequency matches test band
   - Verify RBW/VBW settings (1MHz/3MHz)
   - Check ACLR (Adjacent Channel Leakage Ratio) and SRS (Sounding Reference Signal) power
   - Verify EVM (Error Vector Magnitude) ≤8% (64QAM)

III. Temporary Handling Suggestions
1. For power deviation >0.8dBm:
   - Check {antenna_type} Antenna connection to power amplifier, recalibrate transmit channel
   - Verify PA bias voltage is within standard range (3.3V±0.1V)
2. For abnormal modulation accuracy:
   - Check beamforming parameter configuration, optimize precoding matrix
   - Recalibrate IQ imbalance of {antenna_type} Antenna
3. For band switching issues:
   - Verify NR band combination (EN-DC configuration)
   - Check matching circuit of {antenna_type} Antenna during band switching

IV. Problem Reporting Guidelines
Please provide the following data along with the problem report:
1. Complete test logs (including timestamps, power values, EVM values, SINR values, {antenna_type} Antenna identifier)
2. Band information and bandwidth configuration (e.g., N78-100MHz)
3. Beam configuration parameters and MIMO mode
4. {antenna_type} Antenna transmit power calibration records and PA working status logs
"""
    else:
        # 默认返回中文，传递新增的天线类型参数
        return nr_tx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 传递新增参数
        )

    return issue_description.strip()


def nr_rx_issue_suggestion_v1(
        test_type="请输入测试制式(如: NR, LTE, WLAN等)",
        freq_range="请输入频率范围(如: N78, N41等)",
        channel_id="请输入通道标识(如: NR-1, NR-2等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh'
):
    """
    根据测试参数生成5G NR接收信号强度问题描述和排查建议

    参数:
        test_type: 测试制式 (如: NR, LTE, WLAN等)
        freq_range: 频率范围 (如: N78, N41等)
        channel_id: 通道标识 (如: NR-1, NR-2等)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {channel_id} 通道接收信号强度 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）测试环境验证
1. 信号源核查：
   - 确认RF输出频率符合3GPP TS 38.101规范
   - 验证调制方式为QPSK/16QAM/64QAM/256QAM
   - 确认信号强度符合灵敏度要求（FR1: ≤-95dBm, FR2: ≤-85dBm）
   - 检查RF线缆衰减值（≤0.3dB）

2. 接收性能检查：
   - 确认中心频率与测试频段匹配
   - 验证RBW/VBW设置（1MHz/3MHz）
   - 检查SINR（信号与干扰加噪声比）≥-3dB
   - 验证吞吐量达标率（≥95%）

三、临时处理建议
1. 若RSSI偏差>1.5dBm：检查信号源与DUT连接
2. 若误块率（BLER）>10%：检查测试环境干扰
3. 若波束同步异常：重新校准波束管理参数

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/RSSI值/BLER值/SINR值）
2. 频段信息和带宽配置（如N78-100MHz）
3. 接收波束配置和MIMO层数
"""
    elif language == 'en':
        # 英文描述
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The received signal strength of {channel_id} channel in {test_type} ({freq_range}) is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Test Environment Verification
1. Signal Source Check:
   - Confirm RF output frequency complies with 3GPP TS 38.101
   - Verify modulation scheme is QPSK/16QAM/64QAM/256QAM
   - Confirm signal strength meets sensitivity requirements (FR1: ≤-95dBm, FR2: ≤-85dBm)
   - Check RF cable attenuation (≤0.3dB)

2. Reception Performance Check:
   - Confirm center frequency matches test band
   - Verify RBW/VBW settings (1MHz/3MHz)
   - Check SINR (Signal to Interference plus Noise Ratio) ≥-3dB
   - Verify throughput compliance rate (≥95%)

III. Temporary Handling Recommendations
1. For RSSI deviation >1.5dBm: Check signal source to DUT connection
2. For Block Error Rate (BLER) >10%: Check for test environment interference
3. For beam synchronization issues: Recalibrate beam management parameters

IV. Problem Reporting Guidelines
Please include the following data with your problem report:
1. Complete test logs (including timestamps, RSSI values, BLER values, SINR values)
2. Band information and bandwidth configuration (e.g., N78-100MHz)
3. Receive beam configuration and MIMO layers
"""
    else:
        # 默认返回中文
        return nr_rx_issue_suggestion(test_type, freq_range, channel_id, power_value, deviation, standard_value,
                                      test_item_desc, problem_desc, language='zh')

    return issue_description.strip()


def nr_rx_issue_suggestion(
        test_type="请输入测试制式(如: NR, LTE, WLAN等)",
        freq_range="请输入频率范围(如: N78, N41等)",
        channel_id="请输入通道标识(如: NR-1, NR-2等)",
        power_value="请输入接收信号强度数值(dBm)",
        deviation="请输入偏差情况(如: 偏大, 偏小等)",
        standard_value="请输入标准数值(dBm)",
        test_item_desc="{{测试项描述}}",
        problem_desc="{{问题描述}}",
        language='zh',
        antenna_type="请输入天线类型(如: 主集, 分集, 毫米波, Sub-6G)"  # 新增：天线类型参数
):
    """
    根据测试参数生成5G NR接收信号强度问题描述和排查建议

    参数:
        test_type: 测试制式 (如: NR, LTE, WLAN等)
        freq_range: 频率范围 (如: N78, N41等)
        channel_id: 通道标识 (如: NR-1, NR-2等)
        power_value: 接收信号强度数值 (dBm)
        deviation: 偏差变量 (如: 偏大, 偏小等)
        standard_value: 标准数值 (dBm)
        test_item_desc: 测试项描述，默认为"{{测试项描述}}"
        problem_desc: 问题描述，默认为"{{问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        antenna_type: 天线类型 (如: 主集, 分集, 毫米波, Sub-6G)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：新增天线类型展示，补充接收相关排查点
        issue_description = f"""
测试项描述：{test_item_desc}

{problem_desc}分层排查方案
一、核心问题定位
{test_type} {freq_range} {antenna_type}天线 {channel_id} 通道接收信号强度 {power_value} dBm，
{deviation} {standard_value} dBm 标准值，需按以下维度排查：

二、分层排查策略
（一）天线与接收链路核查
1. {antenna_type}天线接收性能检查：
   - 确认天线接收端口与LNA（低噪声放大器）连接可靠性
   - 检查接收链路损耗（Sub-6G≤1.0dB，毫米波≤2.0dB）
   - 验证天线接收灵敏度（Sub-6G≤-95dBm，毫米波≤-85dBm）
   - 毫米波天线额外检查：相控阵波束接收增益波动（≤±1dB）

2. 测试环境验证
   - 信号源核查：确认RF输出频率符合3GPP TS 38.101规范
   - 验证调制方式为QPSK/16QAM/64QAM/256QAM
   - 检查多径衰落模拟参数（多普勒频移/时延扩展）
   - 确认RF线缆衰减值（≤0.3dB）

（二）接收参数配置检查
1. 接收增益控制验证：
   - 确认{antenna_type}天线对应的LNA增益配置（25-30dB）
   - 检查AGC（自动增益控制）响应时间（≤100μs）
   - 验证噪声系数（NF≤3dB @ 室温）

2. 波束与MIMO配置检查：
   - 确认接收波束赋形参数（水平±60°，垂直±30°）
   - 检查{antenna_type}天线对应的MIMO层数配置
   - 验证SRS（探测参考信号）周期与资源配置
   - 检查接收分集合并算法有效性

三、临时处理建议
1. 若RSSI偏差>1.5dBm：
   - 检查{antenna_type}天线与接收模块连接，重新校准接收通道
   - 验证LNA偏置电压（2.8V±0.1V）及工作温度（-40~85℃）
2. 若误块率（BLER）>10%：
   - 优化{antenna_type}天线方向，降低多径干扰影响
   - 检查测试环境同频干扰（≤-80dBm）
3. 若波束同步异常：
   - 重新执行波束扫描与赋形校准
   - 检查{antenna_type}天线的T/R组件相位一致性

四、问题上报指引
请随问题单提供以下数据：
1. 完整测试日志（含时间戳/RSSI值/BLER值/SINR值、{antenna_type}天线标识）
2. 频段信息和带宽配置（如N78-100MHz）
3. 接收波束配置和MIMO层数报告
4. {antenna_type}天线接收灵敏度校准记录及LNA工作状态日志
"""
    elif language == 'en':
        # 英文描述：对应新增天线类型及相关排查逻辑
        issue_description = f"""
Test Item Description: {test_item_desc}

{problem_desc}Hierarchical Troubleshooting Guide
I. Root Cause Localization
The received signal strength of {test_type} {freq_range} {antenna_type} Antenna {channel_id} channel is {power_value} dBm,
which is {deviation} the standard value of {standard_value} dBm. Troubleshoot according to the following dimensions:

II. Layered Diagnostic Strategy
(1) Antenna and Receive Link Verification
1. {antenna_type} Antenna Reception Performance Check:
   - Confirm connection reliability between antenna receive port and LNA (Low Noise Amplifier)
   - Check receive link loss (Sub-6G ≤1.0dB, mmWave ≤2.0dB)
   - Verify antenna receive sensitivity (Sub-6G ≤-95dBm, mmWave ≤-85dBm)
   - Additional checks for mmWave antennas: Phased array beam receive gain fluctuation (≤±1dB)

2. Test Environment Verification
   - Signal Source Check: Confirm RF output frequency complies with 3GPP TS 38.101
   - Verify modulation scheme is QPSK/16QAM/64QAM/256QAM
   - Check multipath fading simulation parameters (Doppler shift/delay spread)
   - Confirm RF cable attenuation (≤0.3dB)

(2) Receive Parameter Configuration Check
1. Receive Gain Control Verification:
   - Confirm LNA gain configuration for {antenna_type} Antenna (25-30dB)
   - Check AGC (Automatic Gain Control) response time (≤100μs)
   - Verify Noise Figure (NF ≤3dB @ room temperature)

2. Beam and MIMO Configuration Check:
   - Confirm receive beamforming parameters (azimuth ±60°, elevation ±30°)
   - Check MIMO layer configuration for {antenna_type} Antenna
   - Verify SRS (Sounding Reference Signal) period and resource configuration
   - Check effectiveness of receive diversity combining algorithm

III. Temporary Handling Recommendations
1. For RSSI deviation >1.5dBm:
   - Check {antenna_type} Antenna connection to receive module, recalibrate receive channel
   - Verify LNA bias voltage (2.8V±0.1V) and operating temperature (-40~85℃)
2. For Block Error Rate (BLER) >10%:
   - Optimize {antenna_type} Antenna orientation to reduce multipath interference
   - Check test environment co-channel interference (≤-80dBm)
3. For beam synchronization issues:
   - Re-execute beam scanning and forming calibration
   - Check phase consistency of {antenna_type} Antenna T/R components

IV. Problem Reporting Guidelines
Please include the following data with your problem report:
1. Complete test logs (including timestamps, RSSI values, BLER values, SINR values, {antenna_type} Antenna identifier)
2. Band information and bandwidth configuration (e.g., N78-100MHz)
3. Receive beam configuration and MIMO layers report
4. {antenna_type} Antenna receive sensitivity calibration records and LNA working status logs
"""
    else:
        # 默认返回中文，传递新增的天线类型参数
        return nr_rx_issue_suggestion(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            antenna_type=antenna_type  # 传递新增参数
        )

    return issue_description.strip()


# MTK的 分析与建议函数
def generate_issue_from_container_for_mtk_v1(language, parsed_eval_and_log_results_container):
    """
    从测试结果容器生成问题描述和排查建议

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']

    # 动态解析test_type, freq_range和channel_id
    # 假设test_item格式为: "MTK_WLAN_2.4G_C0_TX_POWER_LCH01_ANT_CW"
    parts = test_item.split('_')

    # 初始化默认值
    test_type = "WLAN"
    freq_range = "2.4G"
    channel_id = "C0"
    test_mode = "TX"  # 默认发射模式

    # 动态解析
    for i, part in enumerate(parts):
        if part == "WLAN" or part == "Bluetooth" or part == "GPS" or part == "LTE":
            test_type = part
        elif (part.endswith("G") or part.endswith("GHz")) and (part.startswith("2.4") or part.startswith("5") or part.startswith("5.0")):
            freq_range = part
        elif part.startswith("C") and len(part) > 1 and part[1:].isdigit():
            channel_id = part
        elif part == "TX" or part == "TX_POWER":
            test_mode = "TX"
        elif part == "RX" or part == "RSSI":
            test_mode = "RX"

    # 测试数据值
    power_value = str(parsed_eval_and_log_results_container['test_data'])

    # 取上下限的平均值作为标准值
    standard_value = str(
        (parsed_eval_and_log_results_container['low_limit'] + parsed_eval_and_log_results_container['up_limit']) / 2)

    # 计算偏差情况
    test_value = parsed_eval_and_log_results_container['test_data']
    mid_value = (parsed_eval_and_log_results_container['low_limit'] + parsed_eval_and_log_results_container[
        'up_limit']) / 2

    if test_value > mid_value:
        deviation = "偏大"
        deviation_en = "higher than"
    else:
        deviation = "偏小"
        deviation_en = "lower than"

    # 根据语言选择合适的描述
    if language == 'zh':
        # 中文描述
        test_item_desc = parsed_eval_and_log_results_container['meaning'] + " - "

        # 使用字典映射来确定问题描述，更加灵活
        problem_desc_map = {
            "WLAN_TX": "WLAN发射功率异常 - ",
            "WLAN_RX": "WLAN接收信号强度异常 - ",
            "LTE_TX": "LTE发射功率异常 - ",
            "LTE_RX": "LTE接收信号强度异常 - ",
            "GPS_RX": "GPS接收信号异常 - ",
            "BLUETOOTH_TX": "蓝牙发射功率异常 - ",
        }

        # 生成键值
        key = f"{test_type}_{test_mode}"

        # 获取问题描述，如果没有匹配则使用默认值
        problem_desc = problem_desc_map.get(key, "发射功率异常 - ")

        deviation_text = deviation
    else:
        # 英文描述
        test_item_desc = f"Verification of antenna CW transmission power (continuous wave mode) for channel {channel_id} in {freq_range} band under LCH01 mode - "

        # 使用字典映射来确定问题描述，更加灵活
        problem_desc_map = {
            "WLAN_TX": "WLAN Transmission Power Anomaly - ",
            "WLAN_RX": "WLAN Received Signal Strength Anomaly - ",
            "LTE_TX": "LTE Transmission Power Anomaly - ",
            "LTE_RX": "LTE Received Signal Strength Anomaly - ",
            "GPS_RX": "GPS Signal Reception Anomaly - ",
            "BLUETOOTH_TX": "Bluetooth Transmission Power Anomaly - ",
        }

        # 生成键值
        key = f"{test_type}_{test_mode}"

        # 获取问题描述，如果没有匹配则使用默认值
        problem_desc = problem_desc_map.get(key, "Transmission Power Anomaly - ")

        deviation_text = deviation_en

    # 使用工厂模式选择合适的问题与建议生成函数
    suggestion_generator_map = {
        "WLAN_TX": wlan_tx_issue_suggestion,
        "WLAN_RX": wlan_rx_issue_suggestion,
        "LTE_TX": lte_tx_issue_suggestion,
        "LTE_RX": lte_rx_issue_suggestion,
        "GPS_RX": gps_rx_issue_suggestion,
        "BLUETOOTH_TX": bluetooth_tx_issue_suggestion,
    }

    # 生成键值
    generator_key = f"{test_type}_{test_mode}"

    # 获取对应的问题与建议生成函数，如果没有匹配则使用默认函数
    suggestion_generator = suggestion_generator_map.get(generator_key, wlan_tx_issue_suggestion)

    # 生成问题与建议
    result = suggestion_generator(
        test_type=test_type,
        freq_range=freq_range,
        channel_id=channel_id,
        power_value=power_value,
        deviation=deviation_text,
        standard_value=standard_value,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc,
        language=language
    )

    return result


def generate_issue_from_container_for_mtk_v2(language, parsed_eval_and_log_results_container):
    """
    从测试结果容器生成Markdown格式的问题描述和排查建议

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        Markdown格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']

    # 动态解析test_type, freq_range和channel_id
    # 假设test_item格式为: "MTK_WLAN_2.4G_C0_TX_POWER_LCH01_ANT_CW"
    parts = test_item.split('_')

    # 初始化默认值
    test_type = "WLAN"
    freq_range = "2.4G"
    channel_id = "C0"
    test_mode = "TX"  # 默认发射模式

    # 动态解析
    for i, part in enumerate(parts):
        if part == "WLAN" or part == "Bluetooth" or part == "GPS" or part == "LTE":
            test_type = part
        elif (part.endswith("G") or part.endswith("GHz")) and (
                part.startswith("2.4") or part.startswith("5") or part.startswith("5.0")):
            freq_range = part
        elif part.startswith("C") and len(part) > 1 and part[1:].isdigit():
            channel_id = part
        elif part == "TX" or part == "TX_POWER":
            test_mode = "TX"
        elif part == "RX" or part == "RSSI":
            test_mode = "RX"

    # 测试数据值
    power_value = str(parsed_eval_and_log_results_container['test_data'])

    # 取上下限的平均值作为标准值
    standard_value = str(
        (parsed_eval_and_log_results_container['low_limit'] + parsed_eval_and_log_results_container['up_limit']) / 2)

    # 计算偏差情况
    test_value = parsed_eval_and_log_results_container['test_data']
    mid_value = (parsed_eval_and_log_results_container['low_limit'] + parsed_eval_and_log_results_container[
        'up_limit']) / 2

    if test_value > mid_value:
        deviation = "偏大"
        deviation_en = "higher than"
    else:
        deviation = "偏小"
        deviation_en = "lower than"

    # 生成Markdown格式描述文本
    if language == 'zh':
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)

        # 主标题使用##级别
        problem_desc_map = {
            "WLAN_TX": f"## WLAN发射功率异常",
            "WLAN_RX": f"## WLAN接收信号强度异常",
            "LTE_TX": f"## LTE发射功率异常",
            "LTE_RX": f"## LTE接收信号强度异常",
            "GPS_RX": f"## GPS接收信号异常",
            "BLUETOOTH_TX": f"## 蓝牙发射功率异常",
        }

        # 测试详情使用列表形式
        details = f"""
### 测试详情
- 测试项: {test_item_desc}
- 测试类型: {test_type}
- 频率范围: {freq_range}
- 信道: {channel_id}
- 测试模式: {test_mode}
- 实测值: {power_value}
- 标准值: {standard_value}
- 偏差情况: {deviation}
"""
        deviation_text = deviation
    else:
        # 英文版本Markdown格式
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)
        problem_desc_map = {
            "WLAN_TX": f"## WLAN Transmission Power Anomaly",
            "WLAN_RX": f"## WLAN Received Signal Strength Anomaly",
            "LTE_TX": f"## LTE Transmission Power Anomaly",
            "LTE_RX": f"## LTE Received Signal Strength Anomaly",
            "GPS_RX": f"## GPS Signal Reception Anomaly",
            "BLUETOOTH_TX": f"## Bluetooth Transmission Power Anomaly",
        }

        details = f"""
### Test Details
- Test Item: {test_item}
- Test Type: {test_type}
- Frequency Range: {freq_range}
- Channel: {channel_id}
- Test Mode: {test_mode}
- Measured Value: {power_value}
- Standard Value: {standard_value}
- Deviation: {deviation_en}
"""
        deviation_text = deviation_en

    # 使用工厂模式选择合适的问题与建议生成函数
    suggestion_generator_map = {
        "WLAN_TX": wlan_tx_issue_suggestion,
        "WLAN_RX": wlan_rx_issue_suggestion,
        "LTE_TX": lte_tx_issue_suggestion,
        "LTE_RX": lte_rx_issue_suggestion,
        "GPS_RX": gps_rx_issue_suggestion,
        "BLUETOOTH_TX": bluetooth_tx_issue_suggestion,
    }

    # 生成键值
    generator_key = f"{test_type}_{test_mode}"

    # 获取对应的问题与建议生成函数，如果没有匹配则使用默认函数
    suggestion_generator = suggestion_generator_map.get(generator_key, wlan_tx_issue_suggestion)

    # 生成建议部分（确保建议也是Markdown格式）
    suggestions = suggestion_generator(
        test_type=test_type,
        freq_range=freq_range,
        channel_id=channel_id,
        power_value=power_value,
        deviation=deviation_text,
        standard_value=standard_value,
        test_item_desc=test_item_desc,
        language=language
    )

    # 组合所有部分为完整的Markdown内容
    markdown_content = f"{problem_desc_map.get(generator_key, '## Test Anomaly')}\n"
    markdown_content += f"{details}\n"
    markdown_content += "### 排查建议\n" if language == 'zh' else "### Troubleshooting Suggestions\n"
    markdown_content += suggestions

    return markdown_content


def generate_issue_from_container_for_mtk_v3(language, parsed_eval_and_log_results_container):
    """
    从测试结果容器生成Markdown格式的问题描述和排查建议

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        Markdown格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']

    # 动态解析test_type, freq_range, channel_id, antenna_type（新增天线类型解析）
    parts = test_item.split('_')

    # 初始化默认值
    test_type = "WLAN"
    freq_range = "2.4G"
    channel_id = ""  # 初始化为未知，避免默认值误导
    antenna_type = ""  # 新增：天线类型（主集/分集）
    test_mode = "TX"  # 默认发射模式
    band_channel = ''
    mch_channel = ''
    antenna_flag = ''
    rssi_indicator = ''

    # # 动态解析核心逻辑（新增天线类型和信道标识解析）
    # for i, part in enumerate(parts):
    #     # 解析测试类型（WLAN/Bluetooth/GPS/LTE）
    #     if part in ["WLAN", "Bluetooth", "GPS", "LTE"]:
    #         test_type = part
    #     # 解析频率范围（2.4G/5G/5.0G等）
    #     elif (part.endswith(("G", "GHz")) and
    #           part.startswith(("2.4", "5", "5.0"))):
    #         freq_range = part
    #     # 解析天线类型（主集：C0/PRIMARY；分集：C1/DIVERSITY）
    #     elif part == "C0" or part == "PRIMARY":
    #         antenna_type = "主集" if language == 'zh' else "Primary"
    #     elif part == "C1" or part == "DIVERSITY":
    #         antenna_type = "分集" if language == 'zh' else "Diversity"
    #     # 解析信道（CH_7/CH7格式）
    #     elif part.startswith("CH"):
    #         # 处理CH_7（带下划线）和CH7（不带下划线）两种格式
    #         channel_clean = part.replace("CH_", "CH")  # 统一格式为CH+数字
    #         # 提取数字部分作为信道编号
    #         channel_num = ''.join(filter(str.isdigit, channel_clean))
    #         channel_id = f"CH{channel_num}" if channel_num else "未知"
    #     # 解析测试模式（TX/RX）
    #     elif part in ["TX", "TX_POWER"]:
    #         test_mode = "TX"
    #     elif part in ["RX", "RSSI"]:
    #         test_mode = "RX"
    #     # 补充：若存在"WLAN_80211_2_4G"格式，修正频率范围
    #     elif i > 1 and parts[i-2] == "WLAN" and parts[i-1] == "80211" and part == "2_4G":
    #         freq_range = "2.4G"

    # 测试数据值
    # 动态解析核心逻辑（新增天线类型、信道标识、BC子频段、MCH信道等解析）
    for i, part in enumerate(parts):
        # 解析测试类型（WLAN/Bluetooth/GPS/LTE）
        if part in ["WLAN", "Bluetooth", "BLUETOOTH", "GPS", "LTE", "NR5G"]:
            test_type = part
        # 解析频率范围（2.4G/5G/5.0G等）
        elif (part.endswith(("G", "GHz")) and
              part.startswith(("2.4", "5", "5.0"))):
            freq_range = part
        # 解析天线类型（主集：C0/PRIMARY；分集：C1/DIVERSITY）
        elif part == "C0" or part == "PRIMARY":
            antenna_type = "主集" if language == 'zh' else "Primary"
        elif part == "C1" or part == "DIVERSITY":
            antenna_type = "分集" if language == 'zh' else "Diversity"
        # 解析信道（CH_7/CH7格式）
        elif part.startswith("CH"):
            # 处理CH_7（带下划线）和CH7（不带下划线）两种格式
            channel_clean = part.replace("CH_", "CH")  # 统一格式为CH+数字
            # 提取数字部分作为信道编号
            channel_num = ''.join(filter(str.isdigit, channel_clean))
            channel_id = f"CH{channel_num}" if channel_num else "未知"
        # 解析LTE Band子频段（BCxx格式，如BC01、BC04）
        elif part.startswith("BC"):
            # 提取BC后的数字部分，如BC01 -> Band Channel 01
            bc_num = ''.join(filter(str.isdigit, part))
            band_channel = f"BC{bc_num}" if bc_num else part  # 保留原始格式
        # 解析中心频率与信道号（MCHxxx格式，如MCH300）
        elif part.startswith("MCH"):
            # 提取MCH后的数字部分，对应EARFCN或自定义信道号
            mch_num = ''.join(filter(str.isdigit, part))
            mch_channel = f"MCH{mch_num}" if mch_num else part
        # 解析测试模式（TX/RX）及RSSI参数
        elif part in ["TX", "TX_POWER"]:
            test_mode = "TX"
        elif part in ["RX", "RSSI"]:
            test_mode = "RX"
            # 标记存在RSSI测量（接收信号强度指示）
            if part == "RSSI":
                rssi_indicator = "RSSI"
        # 解析天线标识（ANT）
        elif part == "ANT":
            antenna_flag = "ANT"  # 标记与天线相关配置
        # 补充：若存在"WLAN_80211_2_4G"格式，修正频率范围
        elif i > 1 and parts[i - 2] == "WLAN" and parts[i - 1] == "80211" and part == "2_4G":
            freq_range = "2.4G"

    power_value = str(parsed_eval_and_log_results_container['test_data'])

    # 取上下限的平均值作为标准值
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    standard_value = str((low_limit + up_limit) / 2)

    # 计算偏差情况
    test_value = parsed_eval_and_log_results_container['test_data']
    mid_value = (low_limit + up_limit) / 2
    if test_value > mid_value:
        deviation = "偏大"
        deviation_en = "higher than"
    else:
        deviation = "偏小"
        deviation_en = "lower than"

    # 生成Markdown格式描述文本
    if language == 'zh':
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)
        # 主标题映射
        problem_desc_map = {
            "WLAN_TX": "## WLAN发射功率异常",
            "WLAN_RX": "## WLAN接收信号强度异常",
            "LTE_TX": "## LTE发射功率异常",
            "LTE_RX": "## LTE接收信号强度异常",
            "GPS_RX": "## GPS接收信号异常",
            "BLUETOOTH_TX": "## 蓝牙发射功率异常",
        }
        # 测试详情（新增子频段、中心频率信道等信息展示）
        details = f"""
        ### 测试详情
        - 测试项: {test_item_desc}
        - 测试类型: {test_type}
        - 频率范围: {freq_range}
        - 子频段 (BC): {band_channel if 'band_channel' in locals() else '未指定'}
        - 中心频率信道 (MCH): {mch_channel if 'mch_channel' in locals() else '未指定'}
        - 天线类型: {antenna_type if 'antenna_type' in locals() else '未指定'}
        - 天线配置: {antenna_flag if 'antenna_flag' in locals() else '无'}
        - 物理通道: {channel_id if 'channel_id' in locals() else '未指定'}
        - 测试模式: {test_mode}
        - 信号强度指示: {rssi_indicator if 'rssi_indicator' in locals() else '无'}
        - 实测值: {power_value}
        - 标准值: {standard_value}
        - 偏差情况: {deviation}
        """
        deviation_text = deviation
    else:
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)
        # 英文主标题映射
        problem_desc_map = {
            "WLAN_TX": "## WLAN Transmission Power Anomaly",
            "WLAN_RX": "## WLAN Received Signal Strength Anomaly",
            "LTE_TX": "## LTE Transmission Power Anomaly",
            "LTE_RX": "## LTE Received Signal Strength Anomaly",
            "GPS_RX": "## GPS Signal Reception Anomaly",
            "BLUETOOTH_TX": "## Bluetooth Transmission Power Anomaly",
        }
        # 英文测试详情（新增天线类型展示）
        details = f"""
### Test Details
- Test Item: {test_item_desc}
- Test Type: {test_type}
- Frequency Range: {freq_range}
- Antenna Type: {antenna_type}
- Channel: {channel_id}
- Test Mode: {test_mode}
- Measured Value: {power_value}
- Standard Value: {standard_value}
- Deviation: {deviation_en}
"""
        deviation_text = deviation_en

    # 建议生成函数映射（假设以下函数已提前定义）
    suggestion_generator_map = {
        "WLAN_TX": wlan_tx_issue_suggestion,
        "WLAN_RX": wlan_rx_issue_suggestion,
        "LTE_TX": lte_tx_issue_suggestion,
        "LTE_TX_MORE": lte_tx_issue_suggestion_add_more_fields,
        "LTE_RX": lte_rx_issue_suggestion,
        "LTE_RX_MORE": lte_rx_issue_suggestion_add_more_fields,
        "GPS_RX": gps_rx_issue_suggestion,
        "BLUETOOTH_TX": bluetooth_tx_issue_suggestion,
    }

    # 生成建议函数键值
    if ('band_channel' in locals() and band_channel and  # 等效于 band_channel is not None and band_channel != ''
            'mch_channel' in locals() and mch_channel and
            'rssi_indicator' in locals() and rssi_indicator and
            'antenna_flag' in locals() and antenna_flag):

        generator_key = f"{test_type}_{test_mode}_MORE"
        # 获取对应建议生成函数，默认使用WLAN_TX的建议函数
        suggestion_generator = suggestion_generator_map.get(generator_key, wlan_tx_issue_suggestion)
    else:
        generator_key = f"{test_type}_{test_mode}"
        # 获取对应建议生成函数，默认使用WLAN_TX的建议函数
        suggestion_generator = suggestion_generator_map.get(generator_key, wlan_tx_issue_suggestion)

    if "LTE_RX_MORE" in generator_key or "_MORE" in generator_key:
        # 生成排查建议（传入新增的天线类型、子频段、中心频率信道等参数）
        suggestions = suggestion_generator(
            test_type=test_type,
            freq_range=freq_range,
            antenna_type=antenna_type,
            channel_id=channel_id,
            band_channel=band_channel if 'band_channel' in locals() else None,  # 新增：子频段信息
            mch_channel=mch_channel if 'mch_channel' in locals() else None,  # 新增：中心频率信道
            rssi_indicator=rssi_indicator if 'rssi_indicator' in locals() else None,  # 新增：信号强度标识
            antenna_flag=antenna_flag if 'antenna_flag' in locals() else None,  # 新增：天线配置标识
            power_value=power_value,
            deviation=deviation_text,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            language=language
        )

    else:
        # 生成排查建议（传入新增的天线类型参数）
        suggestions = suggestion_generator(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation_text,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            language=language
        )

    # 组合完整Markdown内容
    markdown_content = f"{problem_desc_map.get(generator_key, '## Test Anomaly')}\n"
    markdown_content += f"{details}\n"
    markdown_content += "### 排查建议\n" if language == 'zh' else "### Troubleshooting Suggestions\n"
    markdown_content += suggestions

    return markdown_content


def generate_issue_from_container_for_mtk(language, parsed_eval_and_log_results_container):
    """
    从测试结果容器生成Markdown格式的问题描述和排查建议

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        Markdown格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']

    # 动态解析各参数
    parts = test_item.split('_')

    # 初始化默认值
    test_type = "WLAN"
    freq_range = "2.4G"
    channel_id = ""
    antenna_type = ""
    test_mode = "TX"
    band_channel = ''
    mch_channel = ''  # 统一存储MCH/LCH/HCH完整信道标识
    mch_num = ''  # 统一存储信道数字部分
    mch_type = ''  # 存储信道类型：low/middle/high
    antenna_flag = ''
    rssi_indicator = ''
    nr_generation = ''
    nr_band = ''
    version = ''

    # 动态解析核心逻辑（新增MCH/LCH/HCH统一解析）
    for i, part in enumerate(parts):
        # 解析测试类型
        if part in ["WLAN", "Bluetooth", "BLUETOOTH", "GPS", "LTE", "NR5G"]:
            test_type = part
            if part.startswith("NR"):
                nr_generation = part

        # 解析NR频段
        elif part.startswith("NS"):
            nr_band = part

        # 解析版本号
        elif part.startswith("V") and part[1:].isdigit():
            version = part

        # 解析频率范围
        elif (part.endswith(("G", "GHz")) and
              part.startswith(("2.4", "5", "5.0", "3.3", "4.2"))):
            freq_range = part

        # 解析天线类型
        elif part == "C0" or part == "PRIMARY":
            antenna_type = "主集" if language == 'zh' else "Primary"
        elif part == "C1" or part == "DIVERSITY":
            antenna_type = "分集" if language == 'zh' else "Diversity"

        # 解析信道（CH开头）
        elif part.startswith("CH"):
            channel_clean = part.replace("CH_", "CH")
            channel_num = ''.join(filter(str.isdigit, channel_clean))
            channel_id = f"CH{channel_num}" if channel_num else "未知"

        # 解析LTE Band子频段
        elif part.startswith("BC"):
            bc_num = ''.join(filter(str.isdigit, part))
            band_channel = f"BC{bc_num}" if bc_num else part

        # 解析MCH/LCH/HCH（统一处理，提取类型和数字）
        elif part.startswith(("MCH", "LCH", "HCH")):
            # 提取前缀（M/L/H）确定类型
            ch_prefix = part[0]  # 取第一个字符（M/L/H）
            # 映射类型（low/middle/high）
            if ch_prefix == "M":
                mch_type = "middle" if language == 'en' else "中"
            elif ch_prefix == "L":
                mch_type = "low" if language == 'en' else "低"
            elif ch_prefix == "H":
                mch_type = "high" if language == 'en' else "高"

            # 提取数字部分（去除前缀后的数字）
            mch_num = ''.join(filter(str.isdigit, part[3:]))  # part[3:]去除"MCH"/"LCH"/"HCH"
            # 完整信道标识（保留原始格式）
            mch_channel = part

        # 解析测试模式及RSSI参数
        elif part in ["TX", "TX_POWER"]:
            test_mode = "TX"
        elif part in ["RX", "RSSI"]:
            test_mode = "RX"
            if part == "RSSI":
                rssi_indicator = "RSSI"

        # 解析天线标识
        elif part == "ANT":
            antenna_flag = "ANT"

        # 补充频率范围修正
        elif i > 1 and parts[i - 2] == "WLAN" and parts[i - 1] == "80211" and part == "2_4G":
            freq_range = "2.4G"

    power_value = str(parsed_eval_and_log_results_container['test_data'])

    # 取上下限的平均值作为标准值
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    standard_value = str((low_limit + up_limit) / 2)

    # 计算偏差情况
    test_value = parsed_eval_and_log_results_container['test_data']
    mid_value = (low_limit + up_limit) / 2
    if test_value > mid_value:
        deviation = "偏大"
        deviation_en = "higher than"
    else:
        deviation = "偏小"
        deviation_en = "lower than"

    # 生成Markdown格式描述文本
    if language == 'zh':
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)
        problem_desc_map = {
            "WLAN_TX": "## WLAN发射功率异常",
            "WLAN_RX": "## WLAN接收信号强度异常",
            "LTE_TX": "## LTE发射功率异常",
            "LTE_RX": "## LTE接收信号强度异常",
            "NR5G_TX": "## NR5G发射功率异常",
            "NR5G_RX": "## NR5G接收信号强度异常",
            "GPS_RX": "## GPS接收信号异常",
            "BLUETOOTH_TX": "## 蓝牙发射功率异常",
        }
        # 测试详情（新增信道类型描述）
        details = f"""
        ### 测试详情
        - 测试项: {test_item_desc}
        - 测试类型: {test_type}
        - 频率范围: {freq_range}
        - 世代: {nr_generation if nr_generation else '未指定'}
        - 频段: {nr_band if nr_band else band_channel if band_channel else '未指定'}
        - 版本: {version if version else '未指定'}
        - 信道类型: {mch_type}信道（{mch_channel}）
        - 信道编号: {mch_num if mch_num else '未指定'}
        - 中心频率信道: {mch_channel if mch_channel else '未指定'}
        - 天线类型: {antenna_type if antenna_type else '未指定'}
        - 天线配置: {antenna_flag if antenna_flag else '无'}
        - 物理通道: {channel_id if channel_id else '未指定'}
        - 测试模式: {test_mode}
        - 信号强度指示: {rssi_indicator if rssi_indicator else '无'}
        - 实测值: {power_value}
        - 标准值: {standard_value}
        - 偏差情况: {deviation}
        """
        deviation_text = deviation
    else:
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)
        problem_desc_map = {
            "WLAN_TX": "## WLAN Transmission Power Anomaly",
            "WLAN_RX": "## WLAN Received Signal Strength Anomaly",
            "LTE_TX": "## LTE Transmission Power Anomaly",
            "LTE_RX": "## LTE Received Signal Strength Anomaly",
            "NR5G_TX": "## NR5G Transmission Power Anomaly",
            "NR5G_RX": "## NR5G Received Signal Strength Anomaly",
            "GPS_RX": "## GPS Signal Reception Anomaly",
            "BLUETOOTH_TX": "## Bluetooth Transmission Power Anomaly",
        }
        # 英文测试详情
        details = f"""
### Test Details
- Test Item: {test_item_desc}
- Test Type: {test_type}
- Frequency Range: {freq_range}
- Generation: {nr_generation if nr_generation else 'Not specified'}
- Band: {nr_band if nr_band else band_channel if band_channel else 'Not specified'}
- Version: {version if version else 'Not specified'}
- Channel Type: {mch_type} channel ({mch_channel})
- Channel Number: {mch_num if mch_num else 'Not specified'}
- Center Frequency Channel: {mch_channel if mch_channel else 'Not specified'}
- Antenna Type: {antenna_type if antenna_type else 'Not specified'}
- Channel: {channel_id if channel_id else 'Not specified'}
- Test Mode: {test_mode}
- Measured Value: {power_value}
- Standard Value: {standard_value}
- Deviation: {deviation_en}
"""
        deviation_text = deviation_en

    # 建议生成函数映射
    suggestion_generator_map = {
        "WLAN_TX": wlan_tx_issue_suggestion,
        "WLAN_RX": wlan_rx_issue_suggestion,
        "LTE_TX": lte_tx_issue_suggestion,
        "LTE_TX_MORE": lte_tx_issue_suggestion_add_more_fields,
        "LTE_RX": lte_rx_issue_suggestion,
        "LTE_RX_MORE": lte_rx_issue_suggestion_add_more_fields,
        "NR5G_RX": nr5g_rx_issue_suggestion,
        "GPS_RX": gps_rx_issue_suggestion,
        "BLUETOOTH_TX": bluetooth_tx_issue_suggestion,
    }

    # 生成建议函数键值
    if (band_channel or nr_band) and mch_channel and rssi_indicator and antenna_flag:
        generator_key = f"{test_type}_{test_mode}_MORE"
        suggestion_generator = suggestion_generator_map.get(generator_key, wlan_tx_issue_suggestion)
    else:
        generator_key = f"{test_type}_{test_mode}"
        suggestion_generator = suggestion_generator_map.get(generator_key, wlan_tx_issue_suggestion)

    # 生成排查建议
    if "LTE_RX_MORE" in generator_key or "_MORE" in generator_key:
        # 生成排查建议（传入新增的天线类型、子频段、中心频率信道等参数）
        suggestions = suggestion_generator(
            test_type=test_type,
            freq_range=freq_range,
            antenna_type=antenna_type,
            channel_id=channel_id,
            band_channel=band_channel if 'band_channel' in locals() else None,  # 新增：子频段信息
            mch_channel=mch_channel if 'mch_channel' in locals() else None,  # 新增：中心频率信道
            rssi_indicator=rssi_indicator if 'rssi_indicator' in locals() else None,  # 新增：信号强度标识
            antenna_flag=antenna_flag if 'antenna_flag' in locals() else None,  # 新增：天线配置标识
            power_value=power_value,
            deviation=deviation_text,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            language=language
        )
    if 'NR5G_RX' in generator_key:
        suggestions = suggestion_generator(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            mch_channel=mch_channel,  # 传递完整信道标识
            mch_type=mch_type,  # 传递信道类型
            power_value=power_value,
            deviation=deviation_text,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            nr_generation=nr_generation,
            language=language
        )
    else:
        # 生成排查建议（传入新增的天线类型参数）
        suggestions = suggestion_generator(
            test_type=test_type,
            freq_range=freq_range,
            channel_id=channel_id,
            power_value=power_value,
            deviation=deviation_text,
            standard_value=standard_value,
            test_item_desc=test_item_desc,
            language=language
        )

    # 组合完整Markdown内容
    markdown_content = f"{problem_desc_map.get(generator_key, '## Test Anomaly')}\n"
    markdown_content += f"{details}\n"
    markdown_content += "### 排查建议\n" if language == 'zh' else "### Troubleshooting Suggestions\n"
    markdown_content += suggestions

    return markdown_content


# 高通的 分析与建议函数
def generate_issue_from_container_for_qc_v1(language, parsed_eval_and_log_results_container):
    """
    从高通测试结果容器生成问题描述和排查建议

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    parts = test_item.split('_')

    # 初始化解析参数
    test_type = "UNKNOWN"
    freq_range = "UNKNOWN"
    channel_id = "C0"
    test_mode = "TX"  # 默认发射模式
    band_class = ""  # 用于LTE频段分类

    # 解析测试类型
    for part in parts:
        if part == "BT":
            test_type = "BLUETOOTH"
        elif part == "GPS":
            test_type = "GPS"
        elif part == "WLAN":
            test_type = "WLAN"
        elif part == "LTE":
            test_type = "LTE"

    # 解析频率范围
    for part in parts:
        if "GHz" in part:
            freq_range = part
        elif test_type == "LTE" and part.startswith("BC"):
            band_class = part
            freq_range = f"BC{part[2:]}"  # LTE频段表示为BC01, BC03等

    # 解析信道ID
    for part in parts:
        if part.startswith("C") and len(part) > 1 and part[1:].isdigit():
            channel_id = part

    # 解析测试模式（TX/RX）
    for part in parts:
        if part in ["TX", "TX_POWER"]:
            test_mode = "TX"
        elif part in ["RX", "RSSI"]:
            test_mode = "RX"
    # GPS默认是接收模式
    if test_type == "GPS":
        test_mode = "RX"

    # 提取测试数据
    power_value = str(parsed_eval_and_log_results_container['test_data'])
    mid_value = (parsed_eval_and_log_results_container['low_limit'] +
                 parsed_eval_and_log_results_container['up_limit']) / 2
    standard_value = str(mid_value)

    # 判断偏差方向
    test_value = parsed_eval_and_log_results_container['test_data']
    if test_value > mid_value:
        deviation = "偏大"
        deviation_en = "higher than"
    else:
        deviation = "偏小"
        deviation_en = "lower than"

    # 生成描述文本
    if language == 'zh':
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item) + " - "

        problem_desc_map = {
            "WLAN_TX": "WLAN发射功率异常 - ",
            "WLAN_RX": "WLAN接收信号异常 - ",
            "LTE_TX": f"LTE {freq_range}发射功率异常 - ",
            "LTE_RX": f"LTE {freq_range}接收信号异常 - ",
            "GPS_RX": "GPS载噪比异常 - ",
            "BLUETOOTH_TX": "蓝牙发射功率异常 - "
        }
        deviation_text = deviation
    else:
        test_item_desc = f"QC {test_type} test {test_item} - "

        problem_desc_map = {
            "WLAN_TX": "WLAN TX Power Anomaly - ",
            "WLAN_RX": "WLAN RX Signal Anomaly - ",
            "LTE_TX": f"LTE {freq_range} TX Power Anomaly - ",
            "LTE_RX": f"LTE {freq_range} RX Signal Anomaly - ",
            "GPS_RX": "GPS Carrier-to-Noise Anomaly - ",
            "BLUETOOTH_TX": "Bluetooth TX Power Anomaly - "
        }
        deviation_text = deviation_en

    # 选择问题生成器
    generator_key = f"{test_type}_{test_mode}"
    suggestion_generator_map = {
        "WLAN_TX": wlan_tx_issue_suggestion,
        "WLAN_RX": wlan_rx_issue_suggestion,
        "LTE_TX": lte_tx_issue_suggestion,
        "LTE_RX": lte_rx_issue_suggestion,
        "GPS_RX": gps_rx_issue_suggestion,
        "BLUETOOTH_TX": bluetooth_tx_issue_suggestion,
    }
    suggestion_generator = suggestion_generator_map.get(generator_key,
                                                        lambda **kwargs: "No suggestion available")

    # 生成结果
    return suggestion_generator(
        test_type=test_type,
        freq_range=freq_range,
        channel_id=channel_id,
        power_value=power_value,
        deviation=deviation_text,
        standard_value=standard_value,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc_map.get(generator_key, "Test Anomaly - "),
        language=language
    )


def generate_issue_from_container_for_qc_v2(language, parsed_eval_and_log_results_container):
    """
    从高通测试结果容器生成问题描述和排查建议，支持5G NR等多种测试类型

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    parts = test_item.split('_')

    # 初始化解析参数
    test_type = "UNKNOWN"
    freq_range = "UNKNOWN"
    channel_id = "C0"
    test_mode = "TX"  # 默认发射模式
    band_class = ""  # 用于频段分类
    specific_freq = ""  # 具体频率值

    # 解析测试类型（新增NR支持）
    for part in parts:
        if part == "BT":
            test_type = "BLUETOOTH"
        elif part == "GPS":
            test_type = "GPS"
        elif part == "WLAN":
            test_type = "WLAN"
        elif part == "LTE":
            test_type = "LTE"
        # 识别5G NR类型（如N78, N41等）
        elif part.startswith("N") and len(part) > 1 and part[1:].isdigit():
            test_type = "NR"

    # 解析频率范围（增强NR支持）
    for part in parts:
        # 处理带单位的频率
        if "GHz" in part or "MHz" in part or "kHz" in part:
            freq_range = part
            specific_freq = part
        # 处理LTE频段
        elif test_type == "LTE" and part.startswith("BC"):
            band_class = part
            freq_range = f"BC{part[2:]}"
        # 处理NR频段（如N78）
        elif test_type == "NR" and part.startswith("N") and len(part) > 1 and part[1:].isdigit():
            freq_range = part
        # 处理具体频率数值（如636667）
        elif part.isdigit() and len(part) >= 5:  # 假设频率数值至少5位
            specific_freq = part
            # 组合频段和具体频率
            if freq_range != "UNKNOWN":
                freq_range = f"{freq_range} ({specific_freq})"
            else:
                freq_range = specific_freq

    # 解析信道ID
    for part in parts:
        if part.startswith("C") and len(part) > 1 and part[1:].isdigit():
            channel_id = part

    # 解析测试模式（TX/RX）
    for part in parts:
        if part in ["TX", "TX_POWER"]:
            test_mode = "TX"
        elif part in ["RX", "RSSI"]:
            test_mode = "RX"
    # GPS默认是接收模式
    if test_type == "GPS":
        test_mode = "RX"

    # 提取测试数据
    power_value = str(parsed_eval_and_log_results_container['test_data'])
    mid_value = (parsed_eval_and_log_results_container['low_limit'] +
                 parsed_eval_and_log_results_container['up_limit']) / 2
    standard_value = str(mid_value)

    # 判断偏差方向
    test_value = parsed_eval_and_log_results_container['test_data']
    if test_value > mid_value:
        deviation = "偏大"
        deviation_en = "higher than"
    else:
        deviation = "偏小"
        deviation_en = "lower than"

    # 生成描述文本
    if language == 'zh':
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item) + " - "

        problem_desc_map = {
            "WLAN_TX": "WLAN发射功率异常 - ",
            "WLAN_RX": "WLAN接收信号异常 - ",
            "LTE_TX": f"LTE {freq_range}发射功率异常 - ",
            "LTE_RX": f"LTE {freq_range}接收信号异常 - ",
            "GPS_RX": "GPS载噪比异常 - ",
            "BLUETOOTH_TX": "蓝牙发射功率异常 - ",
            # 新增NR相关描述
            "NR_TX": f"5G NR {freq_range}发射功率异常 - ",
            "NR_RX": f"5G NR {freq_range}接收信号异常 - "
        }
        deviation_text = deviation
    else:
        test_item_desc = f"QC {test_type} test {test_item} - "

        problem_desc_map = {
            "WLAN_TX": "WLAN TX Power Anomaly - ",
            "WLAN_RX": "WLAN RX Signal Anomaly - ",
            "LTE_TX": f"LTE {freq_range} TX Power Anomaly - ",
            "LTE_RX": f"LTE {freq_range} RX Signal Anomaly - ",
            "GPS_RX": "GPS Carrier-to-Noise Anomaly - ",
            "BLUETOOTH_TX": "Bluetooth TX Power Anomaly - ",
            # 新增NR相关描述
            "NR_TX": f"5G NR {freq_range} TX Power Anomaly - ",
            "NR_RX": f"5G NR {freq_range} RX Signal Anomaly - "
        }
        deviation_text = deviation_en

    # 选择问题生成器
    generator_key = f"{test_type}_{test_mode}"
    suggestion_generator_map = {
        "WLAN_TX": wlan_tx_issue_suggestion,
        "WLAN_RX": wlan_rx_issue_suggestion,
        "LTE_TX": lte_tx_issue_suggestion,
        "LTE_RX": lte_rx_issue_suggestion,
        "GPS_RX": gps_rx_issue_suggestion,
        "BLUETOOTH_TX": bluetooth_tx_issue_suggestion,
        # 新增NR相关建议生成器
        "NR_TX": nr_tx_issue_suggestion,
        "NR_RX": nr_rx_issue_suggestion,
    }
    suggestion_generator = suggestion_generator_map.get(generator_key,
                                                        lambda **kwargs: "No suggestion available")

    # 生成结果
    return suggestion_generator(
        test_type=test_type,
        freq_range=freq_range,
        channel_id=channel_id,
        power_value=power_value,
        deviation=deviation_text,
        standard_value=standard_value,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc_map.get(generator_key, "Test Anomaly - "),
        language=language
    )


def generate_issue_from_container_for_qc(language, parsed_eval_and_log_results_container):
    """
    从高通测试结果容器生成Markdown格式的问题描述和排查建议，支持5G NR等多种测试类型

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        Markdown格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    parts = test_item.split('_')

    # 初始化解析参数
    test_type = "UNKNOWN"
    freq_range = "UNKNOWN"
    channel_id = "C0"
    test_mode = "TX"  # 默认发射模式
    band_class = ""  # 用于频段分类
    specific_freq = ""  # 具体频率值
    antenna_type = ""  # 天线类型

    # 解析测试类型（新增NR支持）
    for part in parts:
        if part == "BT":
            test_type = "BLUETOOTH"
        elif part == "GPS":
            test_type = "GPS"
        elif part == "WLAN":
            test_type = "WLAN"
        elif part == "LTE":
            test_type = "LTE"
        # 识别5G NR类型（如N78, N41等）
        elif part.startswith("N") and len(part) > 1 and part[1:].isdigit():
            test_type = "NR"

    # 解析频率范围（增强NR支持）
    for part in parts:
        # 处理带单位的频率
        if "GHz" in part or "MHz" in part or "kHz" in part:
            freq_range = part
            specific_freq = part
        # 处理LTE频段
        elif test_type == "LTE" and part.startswith("BC"):
            band_class = part
            freq_range = f"BC{part[2:]}"
        # 处理NR频段（如N78）
        elif test_type == "NR" and part.startswith("N") and len(part) > 1 and part[1:].isdigit():
            freq_range = part
        # 处理具体频率数值（如636667）
        elif part.isdigit() and len(part) >= 5:  # 假设频率数值至少5位
            specific_freq = part
            # 组合频段和具体频率
            if freq_range != "UNKNOWN":
                freq_range = f"{freq_range} ({specific_freq})"
            else:
                freq_range = specific_freq

    # 解析信道ID和天线类型
    for part in parts:
        if part.startswith("C") and len(part) > 1 and part[1:].isdigit():
            channel_id = part

            # 根据channel_id判断天线类型，并根据language返回对应语言描述
            if channel_id == "C0":
                if language == "zh":
                    antenna_type = "天线主集"
                else:  # 默认英文
                    antenna_type = "Primary"
            elif channel_id == "C1":
                if language == "zh":
                    antenna_type = "天线分集"
                else:  # 默认英文
                    antenna_type = "Diversity"

    # 解析测试模式（TX/RX）
    for part in parts:
        if part in ["TX", "TX_POWER"]:
            test_mode = "TX"
        elif part in ["RX", "RSSI"]:
            test_mode = "RX"

    # GPS默认是接收模式
    if test_type == "GPS":
        test_mode = "RX"

    # 问题描述默认字段名
    if language == 'zh':
        problem_desc = "问题描述："
    elif language == 'en':
        problem_desc = "issues desc: "

    # 提取测试数据
    power_value = str(parsed_eval_and_log_results_container['test_data'])
    mid_value = (parsed_eval_and_log_results_container['low_limit'] +
                 parsed_eval_and_log_results_container['up_limit']) / 2
    standard_value = str(mid_value)

    # 判断偏差方向
    test_value = parsed_eval_and_log_results_container['test_data']
    if test_value > mid_value:
        deviation = "偏大"
        deviation_en = "higher than"
    else:
        deviation = "偏小"
        deviation_en = "lower than"

    # 生成Markdown格式描述文本
    if language == 'zh':
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)

        # 主标题使用##级别
        problem_desc_map = {
            "WLAN_TX": f"## WLAN发射功率异常",
            "WLAN_RX": f"## WLAN接收信号异常",
            "LTE_TX": f"## LTE {freq_range}发射功率异常",
            "LTE_RX": f"## LTE {freq_range}接收信号异常",
            "GPS_RX": f"## GPS载噪比异常",
            "BLUETOOTH_TX": f"## 蓝牙发射功率异常",
            "NR_TX": f"## 5G NR {freq_range}发射功率异常",
            "NR_RX": f"## 5G NR {freq_range}接收信号异常"
        }

        # 测试详情使用列表形式
        details = f"""
### 测试详情
- 测试项: {test_item_desc}
- 频率范围: {freq_range}
- 信道: {channel_id}
- 测试模式: {test_mode}
- 实测值: {power_value}
- 标准值: {standard_value}
- 偏差情况: {deviation}
"""
        deviation_text = deviation
    else:
        test_item_desc = parsed_eval_and_log_results_container.get('meaning', test_item)
        # 英文版本Markdown格式
        problem_desc_map = {
            "WLAN_TX": f"## WLAN TX Power Anomaly",
            "WLAN_RX": f"## WLAN RX Signal Anomaly",
            "LTE_TX": f"## LTE {freq_range} TX Power Anomaly",
            "LTE_RX": f"## LTE {freq_range} RX Signal Anomaly",
            "GPS_RX": f"## GPS Carrier-to-Noise Anomaly",
            "BLUETOOTH_TX": f"## Bluetooth TX Power Anomaly",
            "NR_TX": f"## 5G NR {freq_range} TX Power Anomaly",
            "NR_RX": f"## 5G NR {freq_range} RX Signal Anomaly"
        }

        details = f"""
### Test Details
- Test Item: {test_item}
- Frequency Range: {freq_range}
- Channel: {channel_id}
- Test Mode: {test_mode}
- Measured Value: {power_value}
- Standard Value: {standard_value}
- Deviation: {deviation_en}
"""
        deviation_text = deviation_en

    # 选择问题生成器
    generator_key = f"{test_type}_{test_mode}"
    suggestion_generator_map = {
        "WLAN_TX": wlan_tx_issue_suggestion,
        "WLAN_RX": wlan_rx_issue_suggestion,
        "LTE_TX": lte_tx_issue_suggestion,
        "LTE_RX": lte_rx_issue_suggestion,
        "GPS_RX": gps_rx_issue_suggestion,
        "BLUETOOTH_TX": bluetooth_tx_issue_suggestion,
        "NR_TX": nr_tx_issue_suggestion,
        "NR_RX": nr_rx_issue_suggestion,
    }
    suggestion_generator = suggestion_generator_map.get(generator_key,
                                                        lambda **kwargs: "No suggestion available")

    # 生成建议部分（确保建议也是Markdown格式）
    suggestions = suggestion_generator(
        test_type=test_type,
        freq_range=freq_range,
        channel_id=channel_id,
        power_value=power_value,
        deviation=deviation_text,
        standard_value=standard_value,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc,
        language=language,
        antenna_type=antenna_type
    )

    # 组合所有部分为完整的Markdown内容
    markdown_content = f"{problem_desc_map.get(generator_key, '## Test Anomaly')}\n"
    markdown_content += f"{details}\n"
    markdown_content += "### 排查建议\n" if language == 'zh' else "### Troubleshooting Suggestions\n"
    markdown_content += suggestions

    return markdown_content


# 基带部分的异常分析与建议

# 1.格式说明
# 1.Markdown 结构优化：
#   @ 使用###和####创建标题层级，使内容结构更清晰
#   @ 采用列表 (-) 展示关键参数，提高可读性
#   @ 使用引用块 (>) 突出显示排查建议
# 2.重要信息突出：
#   @ 测试值、标准范围和状态使用**加粗**突出显示
#   @ 指标说明和排查建议使用**加粗标题**引导，明确区分不同内容块
# 3.格式一致性：
# @ 中英文输出保持相同的 Markdown 结构
# @ 统一换行和缩进，确保生成的文档格式整洁

# 电容开关快充相关的 分析与建议函数
def generate_issue_for_basic_band_CAP_SWITCH_TURBO_CHARGER(language, parsed_eval_and_log_results_container):
    """
    从基础频段测试结果容器生成Markdown格式的问题描述和排查建议

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        Markdown格式化的问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    test_data = parsed_eval_and_log_results_container['test_data']
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    unit = parsed_eval_and_log_results_container['unit']
    meaning = parsed_eval_and_log_results_container['meaning']
    indicators = parsed_eval_and_log_results_container['indicator'].split(';')

    # 解析测试类型和子类型
    test_type = "Cap Switch Turbo Charger"
    sub_type = "UNKNOWN"

    # 从测试项目中解析子类型
    if "First Vatt" in test_item:
        sub_type = "Initial Voltage Calibration"
    elif "Response Time" in test_item:
        sub_type = "Switch Response Time"
    elif "Voltage Stability" in test_item:
        sub_type = "Voltage Stability"
    elif "Current Impact" in test_item:
        sub_type = "Current Impact Suppression"
    elif "Temperature Control" in test_item:
        sub_type = "Temperature Control"
    # 新增ANT_CAP_SENSOR_ASM_相关解析
    elif "ANT_CAP_SENSOR_ASM_" in test_item:
        sub_type = "Antenna Capacitance Sensor Assembly"
    # 新增CAP_COMP_ASM_VALUE_XX相关解析（支持数字变化）
    elif re.search(r"CAP_COMP_ASM_VALUE_\d+", test_item):
        sub_type = "Capacitor Compensation Assembly Value"

    # 提取相关指标描述
    indicator_desc = ""
    for indicator in indicators:
        if sub_type in indicator or (sub_type == "Initial Voltage Calibration" and "初始电压校准" in indicator):
            indicator_desc = indicator.strip()
            break

    # 计算标准值范围和判断偏差（加粗突出显示）
    if low_limit is not None and up_limit is not None:
        standard_range = f"**{low_limit} - {up_limit}{unit}**"
        if test_data < low_limit:
            deviation = "**偏低**"
            deviation_en = "**lower than**"
        elif test_data > up_limit:
            deviation = "**偏高**"
            deviation_en = "**higher than**"
        else:
            deviation = "**正常**"
            deviation_en = "**within**"
    else:
        standard_range = "**未定义**"
        deviation = "**未知**"
        deviation_en = "**unknown**"

    # 格式化测试数据（加粗突出显示）
    formatted_test_data = f"**{test_data}{unit}**"

    # 生成Markdown格式内容
    if language == 'zh':
        # 主标题使用##级别
        main_title = "## 电容开关快充功能测试异常"

        # 测试详情部分
        details = f"""
### 测试详情
- 测试项: {meaning}
- 测试类型: {test_type}
- 子类型: {sub_type}
- 测试值: {formatted_test_data}
- 标准范围: {standard_range}
- 状态: {deviation}

### 指标说明
{indicator_desc if indicator_desc else '无详细指标说明'}
"""
    else:
        # 英文版本Markdown格式
        main_title = "## Cap Switch Turbo Charger Function Test Anomaly"

        details = f"""
### Test Details
- Test Item: {test_item}
- Test Type: {test_type}
- Sub-type: {sub_type}
- Test Value: {formatted_test_data}
- Standard Range: {standard_range}
- Status: {deviation_en}

### Indicator Description
{indicator_desc if indicator_desc else 'No detailed indicator description'}
"""

    # 选择问题生成器
    suggestion_generator_map = {
        "Initial Voltage Calibration": voltage_calibration_suggestion,
        "Switch Response Time": switch_response_time_suggestion,
        "Voltage Stability": voltage_stability_suggestion,
        "Current Impact Suppression": current_impact_suggestion,
        "Temperature Control": temperature_control_suggestion,
        "Antenna Capacitance Sensor Assembly": ant_cap_sensor_asm_suggestion,
        "Capacitor Compensation Assembly Value": cap_comp_asm_value_suggestion,  # 新增映射
        "UNKNOWN": default_cap_switch_suggestion
    }
    suggestion_generator = suggestion_generator_map.get(sub_type, default_cap_switch_suggestion)

    # 生成建议部分
    suggestions = suggestion_generator(
        sub_type=sub_type,
        language=language
    )

    # 组合所有部分为完整的Markdown内容
    markdown_content = f"{main_title}\n"
    markdown_content += f"{details}\n"
    markdown_content += "### 排查建议\n" if language == 'zh' else "### Troubleshooting Suggestions\n"
    markdown_content += suggestions

    return markdown_content


def voltage_calibration_suggestion(**kwargs):
    """初始电压校准问题的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查电压校准电路是否存在虚焊或接触不良
2. 重新执行电压校准程序，确保校准步骤完整
3. 验证校准参数是否正确应用到系统中
4. 检查校准参考电压源的稳定性
5. 对比同批次正常设备的校准数据，分析偏差原因"""
    else:
        return """1. Check if the voltage calibration circuit has cold solder joints or poor contact
2. Re-execute the voltage calibration procedure to ensure complete calibration steps
3. Verify that calibration parameters are correctly applied to the system
4. Check the stability of the calibration reference voltage source
5. Compare calibration data with normal devices of the same batch to analyze deviation causes"""


def switch_response_time_suggestion(**kwargs):
    """开关响应时间问题的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查开关驱动电路的元件参数是否符合设计规范
2. 优化控制信号的时序参数，减少延迟
3. 测试不同温度下的开关响应特性，确认温度影响
4. 检查电容老化状态对切换速度的影响
5. 验证驱动芯片输出能力是否满足要求"""
    else:
        return """1. Check if the component parameters of the switch drive circuit meet design specifications
2. Optimize the timing parameters of control signals to reduce delay
3. Test switch response characteristics at different temperatures to confirm temperature impact
4. Check the impact of capacitor aging on switching speed
5. Verify if the output capability of the driver chip meets requirements"""


def voltage_stability_suggestion(**kwargs):
    """电压稳定性问题的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查稳压电路中的电感、电容等元件是否损坏
2. 测试滤波电容的容值和ESR参数是否在正常范围
3. 分析负载变化规律，优化电源调整率
4. 检查PCB布局是否存在电源环路过大问题
5. 验证反馈控制环路的稳定性"""
    else:
        return """1. Check if inductors, capacitors and other components in the voltage regulator circuit are damaged
2. Test whether the capacitance and ESR parameters of filter capacitors are within normal range
3. Analyze load variation rules and optimize power supply regulation rate
4. Check if there is excessive power loop in PCB layout
5. Verify the stability of the feedback control loop"""


def current_impact_suggestion(**kwargs):
    """电流冲击问题的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查缓冲电路的设计参数是否合理
2. 优化开关的切换速度，减少di/dt变化率
3. 增加或调整限流保护电路的阈值设置
4. 测试不同负载条件下的冲击电流特性
5. 检查PCB布线是否能够承受峰值电流"""
    else:
        return """1. Check if the design parameters of the buffer circuit are reasonable
2. Optimize the switching speed to reduce di/dt change rate
3. Increase or adjust the threshold setting of current limiting protection circuit
4. Test inrush current characteristics under different load conditions
5. Check if PCB wiring can withstand peak current"""


def temperature_control_suggestion(**kwargs):
    """温度控制问题的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查散热片安装是否牢固，导热硅脂是否涂抹均匀
2. 校准温度传感器，确保测量准确性
3. 优化温控算法，避免温度波动过大
4. 检查散热风扇的工作状态和转速控制
5. 验证高温保护阈值设置是否合理"""
    else:
        return """1. Check if the heat sink is installed firmly and thermal grease is applied evenly
2. Calibrate the temperature sensor to ensure measurement accuracy
3. Optimize the temperature control algorithm to avoid excessive temperature fluctuations
4. Check the working status and speed control of the cooling fan
5. Verify if the high temperature protection threshold setting is reasonable"""


# 新增ANT_CAP_SENSOR_ASM_对应的建议生成函数
def ant_cap_sensor_asm_suggestion(**kwargs):
    """天线电容传感器组件问题建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查天线电容传感器的安装位置是否正确，是否有松动
2. 清洁传感器表面，确保无灰尘、油污等干扰物
3. 验证传感器与主板的连接排线是否完好
4. 检查传感器周围是否有金属物体干扰
5. 重新校准天线电容传感器的基准值
6. 测试环境温度是否在传感器正常工作范围内"""
    else:
        return """1. Check if the antenna capacitance sensor is installed correctly and not loose
2. Clean the sensor surface to ensure no dust, oil or other contaminants
3. Verify that the connecting cable between sensor and main board is in good condition
4. Check for metal objects that may interfere with the sensor
5. Recalibrate the reference value of the antenna capacitance sensor
6. Test if the ambient temperature is within the normal operating range of the sensor"""


# 新增CAP_COMP_ASM_VALUE_XX对应的建议生成函数
def cap_comp_asm_value_suggestion(**kwargs):
    """电容补偿组件值问题建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查电容补偿组件的安装是否到位，确认接触良好
2. 验证补偿电容的规格参数是否符合设计要求
3. 清洁组件连接触点，去除氧化层或污渍
4. 重新校准电容补偿值，确保在标准范围内
5. 检查周围环境温度和湿度是否影响电容性能
6. 替换同型号组件进行对比测试，确认是否为元件本身问题"""
    else:
        return """1. Check if the capacitor compensation component is properly installed and making good contact
2. Verify that the specifications of the compensation capacitor meet design requirements
3. Clean the component connection contacts to remove oxide layers or stains
4. Recalibrate the capacitance compensation value to ensure it is within the standard range
5. Check if ambient temperature and humidity affect capacitor performance
6. Replace with the same type of component for comparative testing to confirm if it is a component issue"""


def default_cap_switch_suggestion(**kwargs):
    """默认的电容开关问题建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return """1. 检查电容开关相关电路的连接是否正确
2. 验证所有元器件的规格是否符合设计要求
3. 重新进行完整的功能测试，记录异常现象
4. 检查控制软件版本是否为最新，必要时升级
5. 对比原理图，确认电路实现是否与设计一致"""
    else:
        return """1. Check if the connections of the capacitor switch related circuits are correct
2. Verify that all components meet the design specifications
3. Re-perform complete functional tests and record abnormal phenomena
4. Check if the control software version is up to date and upgrade if necessary
5. Compare with the schematic diagram to confirm whether the circuit implementation is consistent with the design"""


# BATTERY_LEVELS 分析与建议函数
def generate_issue_for_basic_band_BATTERY_LEVELS(language, parsed_eval_and_log_results_container):
    """
    从基础频段测试结果容器生成电池电量检测的问题描述和排查建议（Markdown格式）

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的Markdown格式问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    test_data = parsed_eval_and_log_results_container['test_data']
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    unit = parsed_eval_and_log_results_container['unit']
    meaning = parsed_eval_and_log_results_container['meaning']
    indicators = parsed_eval_and_log_results_container['indicator'].split(';')

    # 解析测试类型和子类型
    test_type = "Battery Levels Detection"
    sub_type = "UNKNOWN"

    # 从测试指标中解析子类型
    if any("电池充电水平状态获取准确性" in ind for ind in indicators):
        sub_type = "Charge Level Accuracy"
    elif any("Android系统电池电量获取可靠性" in ind for ind in indicators):
        sub_type = "Android Level Reliability"
    elif any("电池电量检测响应时间" in ind for ind in indicators):
        sub_type = "Detection Response Time"
    elif any("电池电量状态切换一致性" in ind for ind in indicators):
        sub_type = "State Switch Consistency"

    # 提取相关指标描述
    indicator_desc = ""
    for indicator in indicators:
        if (sub_type == "Charge Level Accuracy" and "电池充电水平状态获取准确性" in indicator) or \
                (sub_type == "Android Level Reliability" and "Android系统电池电量获取可靠性" in indicator) or \
                (sub_type == "Detection Response Time" and "电池电量检测响应时间" in indicator) or \
                (sub_type == "State Switch Consistency" and "电池电量状态切换一致性" in indicator):
            indicator_desc = indicator.strip()
            break

    # 计算标准值范围和判断偏差（适配P/F类型测试），加粗突出显示重要信息
    if unit == "P/F":
        standard_range = "**PASS**"
        if parsed_eval_and_log_results_container['state'] == 'FAILED':
            deviation = "**未通过**"
            deviation_en = "**failed**"
        else:
            deviation = "**通过**"
            deviation_en = "**passed**"
    elif low_limit is not None and up_limit is not None:
        standard_range = f"**{low_limit} - {up_limit}{unit}**"
        if test_data < low_limit:
            deviation = "**偏低**"
            deviation_en = "**lower than**"
        elif test_data > up_limit:
            deviation = "**偏高**"
            deviation_en = "**higher than**"
        else:
            deviation = "**正常**"
            deviation_en = "**within**"
    else:
        standard_range = "**未定义**"
        deviation = "**未知**"
        deviation_en = "**unknown**"

    # 格式化测试数据（加粗突出显示）
    formatted_test_data = f"**{test_data}{unit}**"

    # 根据语言选择描述文本
    if language == 'zh':
        test_item_desc = f"### {meaning}\n\n"
        deviation_text = deviation

        problem_desc_map = {
            "Charge Level Accuracy": "#### 电池充电水平状态获取准确性异常",
            "Android Level Reliability": "#### Android系统电池电量获取可靠性异常",
            "Detection Response Time": "#### 电池电量检测响应时间异常",
            "State Switch Consistency": "#### 电池电量状态切换一致性异常",
            "UNKNOWN": "#### 电池电量检测功能异常"
        }
    else:
        test_item_desc = f"### Battery levels test: {test_item}\n\n"
        deviation_text = deviation_en

        problem_desc_map = {
            "Charge Level Level Accuracy": "#### Battery Battery charge level status acquisition accuracy anomaly",
            "Android Level Reliability": "#### Android Android system battery level acquisition reliability anomaly",
            "Detection Response Time": "#### Battery level detection detection response time anomaly",
            "State Switch Consistency": "#### Battery level state switch consistency anomaly",
            "UNKNOWN": "#### Battery levels detection function anomaly"
        }
    # 选择问题生成器
    suggestion_generator_map = {
        "Charge Level Level Accuracy": battery_charge_level_accuracy_suggestion,
        "Android Level Reliability": android_battery_level_reliability_suggestion,
        "Detection Response Time": battery_level_response_time_suggestion,
        "State Switch Consistency": battery_level_switch_consistency_suggestion,
        "UNKNOWN": default_battery_levels_suggestion
    }
    suggestion_generator = suggestion_generator_map.get(sub_type, default_battery_levels_suggestion)

    # 生成结果
    return suggestion_generator(
        test_type=test_type,
        sub_type=sub_type,
        test_data=formatted_test_data,
        standard_range=standard_range,
        deviation=deviation_text,
        indicator_desc=indicator_desc,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc_map.get(sub_type, "####Battery Levels Test Anomaly"),
        language=language
    )


def battery_charge_level_accuracy_suggestion(**kwargs):
    """电池充电水平状态获取准确性异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 检测值: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查电池管理芯片(BMS)的电量计算算法\n" \
               f"> 2. 校准电池电量计，确保与实际电量一致\n" \
               f"> 3. 验证充电过程中电量百分比更新逻辑\n" \
               f"> 4. 检查是否存在系统资源占用过高导致的计算延迟"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test value: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check the battery management chip (BMS) charge calculation algorithm\n" \
               f"> 2. Calibrate the battery gauge to ensure consistency with actual capacity\n" \
               f"> 3. Verify charge percentage update logic during charging process\n" \
               f"> 4. Check for high system resource usage causing calculation delays"


def android_battery_level_reliability_suggestion(**kwargs):
    """Android系统电池电量获取可靠性异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 检测值: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查Android系统 BatteryManager 服务是否正常运行\n" \
               f"> 2. 验证电量广播(ACTION_BATTERY_CHANGED)接收机制\n" \
               f"> 3. 检查是否存在应用程序异常占用电量统计接口\n" \
               f"> 4. 测试不同系统版本下的电量获取稳定性\n" \
               f"> 5. 检查电池驱动与系统框架层的通信"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test value: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check if Android BatteryManager service is running properly\n" \
               f"> 2. Verify ACTION_BATTERY_CHANGED broadcast receiving mechanism\n" \
               f"> 3. Check for abnormal occupation of battery statistics interface by applications\n" \
               f"> 4. Test battery level acquisition stability across different system versions\n" \
               f"> 5. Inspect communication between battery driver and system framework"


def battery_level_response_time_suggestion(**kwargs):
    """电池电量检测响应时间异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 响应时间: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 优化电量检测接口的轮询频率和间隔设置\n" \
               f"> 2. 检查电池状态变化事件的触发机制\n" \
               f"> 3. 分析系统负载对电量检测响应速度的影响\n" \
               f"> 4. 验证低电量状态下的响应时间是否正常\n" \
               f"> 5. 检查硬件中断处理是否存在延迟"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Response time: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Optimize polling frequency and interval settings for battery detection interface\n" \
               f"> 2. Check trigger mechanism for battery state change events\n" \
               f"> 3. Analyze system load impact on battery detection response speed\n" \
               f"> 4. Verify response time under low battery conditions\n" \
               f"> 5. Check for delays in hardware interrupt processing"


def battery_level_switch_consistency_suggestion(**kwargs):
    """电池电量状态切换一致性异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 状态切换检测值: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查电量阈值设置是否合理（如低电量、满电阈值）\n" \
               f"> 2. 验证充电/放电状态切换时的电量计算逻辑\n" \
               f"> 3. 测试不同温度环境下的状态切换一致性\n" \
               f"> 4. 检查电池保护机制是否影响状态切换\n" \
               f"> 5. 验证系统休眠/唤醒时的电量状态同步机制"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- State switch test value: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check if battery level thresholds are set appropriately (low battery, full charge)\n" \
               f"> 2. Verify charge calculation logic during charge/discharge state switches\n" \
               f"> 3. Test state switch consistency across different temperature environments\n" \
               f"> 4. Check if battery protection mechanisms affect state switching\n" \
               f"> 5. Verify battery state synchronization during system sleep/wake"


def default_battery_levels_suggestion(**kwargs):
    """默认电池电量检测异常的建议生成（当子类型无法识别时使用）（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 检测值: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查电池硬件连接是否正常\n" \
               f"> 2. 验证电池管理系统(BMS)固件版本及兼容性\n" \
               f"> 3. 测试不同电池型号的兼容性\n" \
               f"> 4. 检查系统日志中与电池相关的错误信息\n" \
               f"> 5. 重启设备后重新进行电池检测"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test value: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check if battery hardware connections are normal\n" \
               f"> 2. Verify battery management system (BMS) firmware version and compatibility\n" \
               f"> 3. Test compatibility with different battery models\n" \
               f"> 4. Check system logs for battery-related error messages\n" \
               f"> 5. Reboot the device and perform battery detection again"


# 扬声器信息编程相关的 分析与建议函数
def generate_issue_for_basic_band_SPK_INFO_PROGAMMING(language, parsed_eval_and_log_results_container):
    """
    从基础频段基础频段测试结果容器生成扬声器信息编程功能的问题描述和排查建议（Markdown格式）

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的Markdown格式问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    test_data = parsed_eval_and_log_results_container['test_data']
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    unit = parsed_eval_and_log_results_container['unit']
    meaning = parsed_eval_and_log_results_container['meaning']
    indicators = parsed_eval_and_log_results_container['indicator'].split(';')

    # 解析测试类型和子类型
    test_type = "Speaker Information Programming"
    sub_type = "UNKNOWN"

    # 从测试指标中解析子类型
    if any("扬声器基本信息读取准确性" in ind for ind in indicators):
        sub_type = "Info Reading Accuracy"
    elif any("默认参数集编程完整性" in ind for ind in indicators):
        sub_type = "Default Parameter Programming"
    elif any("编程数据写入成功率" in ind for ind in indicators):
        sub_type = "Write Success Rate"
    elif any("编程后信息保存稳定性" in ind for ind in indicators):
        sub_type = "Info Saving Stability"
    elif any("编程编程接口通信可靠性" in ind for ind in indicators):
        sub_type = "Communication Reliability"

    # 提取相关指标描述
    indicator_desc = ""
    for indicator in indicators:
        if (sub_type == "Info Reading Accuracy" and "扬声器基本信息读取准确性" in indicator) or \
                (sub_type == "Default Parameter Programming" and "默认参数集编程完整性" in indicator) or \
                (sub_type == "Write Success Rate" and "编程编程数据写入成功率" in indicator) or \
                (sub_type == "Info Saving Stability" and "编程后信息保存稳定性" in indicator) or \
                (sub_type == "Communication Reliability" and "编程接口通信可靠性" in indicator):
            indicator_desc = indicator.strip()
            break

    # 计算标准值范围和判断偏差（适配P/F类型测试），加粗突出显示重要信息
    if unit == "P/F":
        standard_range = "**PASS**"
        if parsed_eval_and_log_results_container['state'] == 'FAILED':
            deviation = "**未通过**"
            deviation_en = "**failed**"
        else:
            deviation = "**通过**"
            deviation_en = "**passed**"
    elif low_limit is not None and up_limit is not None:
        standard_range = f"**{low_limit} - {up_limit}{unit}**"
        if test_data < low_limit:
            deviation = "**偏低**"
            deviation_en = "**lower than**"
        elif test_data > up_limit:
            deviation = "**偏高**"
            deviation_en = "**higher than**"
        else:
            deviation = "**正常**"
            deviation_en = "**within**"
    else:
        standard_range = "**未定义**"
        deviation = "**未知**"
        deviation_en = "**unknown**"

    # 格式化测试数据（加粗突出显示）
    formatted_test_data = f"**{test_data}{unit}**"

    # 根据语言选择描述文本
    if language == 'zh':
        test_item_desc = f"### {meaning}\n\n"
        deviation_text = deviation

        problem_desc_map = {
            "Info Reading Accuracy": "#### 扬声器基本信息读取准确性异常",
            "Default Parameter Programming": "#### 默认参数集编程完整性异常",
            "Write Success Rate": "#### 编程数据写入成功率异常",
            "Info Saving Stability": "#### 编程后信息保存稳定性异常",
            "Communication Reliability": "#### 编程接口通信可靠性异常",
            "UNKNOWN": "#### 扬声器信息编程功能异常"
        }
    else:
        test_item_desc = f"### Speaker info programming test: {test_item}\n\n"
        deviation_text = deviation_en

        problem_desc_map = {
            "Info Reading Accuracy": "#### Speaker basic information reading accuracy anomaly",
            "Default Parameter Programming": "#### Default parameter set programming integrity anomaly",
            "Write Success Rate": "#### Programming data write success rate anomaly",
            "Info Saving Stability": "#### Post-programming information storage stability anomaly",
            "Communication Reliability": "#### Programming interface communication reliability anomaly",
            "UNKNOWN": "#### Speaker information programming function anomaly"
        }

    # 选择问题生成器
    suggestion_generator_map = {
        "Info Reading Accuracy": spk_info_reading_suggestion,
        "Default Parameter Programming": spk_default_param_suggestion,
        "Write Success Rate": spk_write_success_suggestion,
        "Info Saving Stability": spk_saving_stability_suggestion,
        "Communication Reliability": spk_comm_reliability_suggestion,
        "UNKNOWN": default_spk_programming_suggestion
    }
    suggestion_generator = suggestion_generator_map.get(sub_type, default_spk_programming_suggestion)

    # 生成结果
    return suggestion_generator(
        test_type=test_type,
        sub_type=sub_type,
        test_data=formatted_test_data,
        standard_range=standard_range,
        deviation=deviation_text,
        indicator_desc=indicator_desc,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc_map.get(sub_type, "#### Speaker Programming Test Anomaly"),
        language=language
    )


def spk_info_reading_suggestion(**kwargs):
    """扬声器基本信息读取准确性异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标要求**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查扬声器通信协议是否匹配\n" \
               f"> 2. 验证制造商信息数据库完整性\n" \
               f"> 3. 测试读取命令格式是否正确\n" \
               f"> 4. 检查硬件接口连接稳定性"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator requirement**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check if speaker communication protocol matches\n" \
               f"> 2. Verify manufacturer info database integrity\n" \
               f"> 3. Test reading command format\n" \
               f"> 4. Inspect hardware interface stability"


def spk_default_param_suggestion(**kwargs):
    """默认参数集编程完整性异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标要求**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查默认参数集完整性\n" \
               f"> 2. 验证参数编程流程是否完整\n" \
               f"> 3. 测试参数校验机制\n" \
               f"> 4. 检查存储区域是否可正常访问"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator requirement**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check default parameter set integrity\n" \
               f"> 2. Verify parameter programming process completeness\n" \
               f"> 3. Test parameter verification mechanism\n" \
               f"> 4. Check storage area accessibility"


def spk_write_success_suggestion(**kwargs):
    """编程数据写入成功率异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标要求**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查写入命令响应机制\n" \
               f"> 2. 测试电源稳定性对写入的影响\n" \
               f"> 3. 验证写入重试机制\n" \
               f"> 4. 连续10次写入测试并分析失败模式"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator requirement**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check write command response mechanism\n" \
               f"> 2. Test power stability impact on writing\n" \
               f"> 3. Verify write retry mechanism\n" \
               f"> 4. Perform 10 consecutive write tests and analyze failure modes"


def spk_saving_stability_suggestion(**kwargs):
    """编程后信息保存稳定性异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标要求**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 测试断电保护机制\n" \
               f"> 2. 检查非易失性存储功能\n" \
               f"> 3. 验证重启后数据读取流程\n" \
               f"> 4. 多次断电重启测试并检查信息保存情况"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator requirement**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Test power-off protection mechanism\n" \
               f"> 2. Check non-volatile storage function\n" \
               f"> 3. Verify data reading process after restart\n" \
               f"> 4. Perform multiple power cycles and check information retention"


def spk_comm_reliability_suggestion(**kwargs):
    """编程接口通信可靠性异常的建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标要求**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查通信线路阻抗匹配\n" \
               f"> 2. 测试数据校验算法\n" \
               f"> 3. 验证超时重传机制\n" \
               f"> 4. 监控数据传输错误率并分析模式"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator requirement**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check communication line impedance matching\n" \
               f"> 2. Test data verification algorithm\n" \
               f"> 3. Verify timeout retransmission mechanism\n" \
               f"> 4. Monitor data transmission error rate and analyze patterns"


def default_spk_programming_suggestion(**kwargs):
    """默认的扬声器信息编程异常建议生成（Markdown格式）"""
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准范围: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标要求**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查扬声器信息编程整体流程\n" \
               f"> 2. 验证编程工具与设备兼容性\n" \
               f"> 3. 测试不同型号扬声器的适应性\n" \
               f"> 4. 检查系统日志中的错误记录"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard range: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator requirement**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting suggestions**:\n" \
               f"> 1. Check overall speaker info programming process\n" \
               f"> 2. Verify compatibility between programming tool and device\n" \
               f"> 3. Test adaptability with different speaker models\n" \
               f"> 4. Check error records in system logs"


# 磁力计信息编程相关的 分析与建议函数
def generate_issue_for_basic_band_ANDROID_MAGNETOMETER(language, parsed_eval_and_log_results_container):
    """
    从基础频段测试结果容器生成磁力计存在性检测的问题描述和排查建议（Markdown格式）

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的Markdown格式问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    test_data = parsed_eval_and_log_results_container['test_data']
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    unit = parsed_eval_and_log_results_container['unit']
    meaning = parsed_eval_and_log_results_container['meaning']
    indicators = parsed_eval_and_log_results_container['indicator'].split(';')

    # 解析测试类型和子类型
    test_type = "Magnetometer Presence Detection"
    sub_type = "UNKNOWN"

    # 从测试指标中解析子类型
    if any("磁力计硬件存在性检测准确性" in ind for ind in indicators):
        sub_type = "Hardware Presence Accuracy"
    elif any("磁力计驱动加载状态识别准确性" in ind for ind in indicators):
        sub_type = "Driver Status Recognition"
    elif any("磁力计使能/禁用状态切换响应时间" in ind for ind in indicators):
        sub_type = "Status Switch Response"
    elif any("磁力计状态持续监测稳定性" in ind for ind in indicators):
        sub_type = "Continuous Monitoring Stability"
    elif any("磁力计硬件ID识别准确性" in ind for ind in indicators):
        sub_type = "Hardware ID Recognition"

    # 提取相关指标描述
    indicator_desc = ""
    for indicator in indicators:
        if (sub_type == "Hardware Presence Accuracy" and "磁力计硬件存在性检测准确性" in indicator) or \
                (sub_type == "Driver Status Recognition" and "磁力计驱动加载状态识别准确性" in indicator) or \
                (sub_type == "Status Switch Response" and "磁力计使能/禁用状态切换响应时间" in indicator) or \
                (sub_type == "Continuous Monitoring Stability" and "磁力计状态持续监测稳定性" in indicator) or \
                (sub_type == "Hardware ID Recognition" and "磁力计硬件ID识别准确性" in indicator):
            indicator_desc = indicator.strip()
            break

    # 计算标准值范围和判断偏差（适配P/F类型测试），加粗突出显示重要信息
    if unit == "P/F":
        standard_range = "**PASS**"
        if parsed_eval_and_log_results_container['state'] == 'FAILED':
            deviation = "**未通过**"
            deviation_en = "**failed**"
        else:
            deviation = "**通过**"
            deviation_en = "**passed**"
    elif low_limit is not None and up_limit is not None:
        standard_range = f"**{low_limit} - {up_limit}{unit}**"
        if test_data < low_limit:
            deviation = "**偏低**"
            deviation_en = "**lower than**"
        elif test_data > up_limit:
            deviation = "**偏高**"
            deviation_en = "**higher than**"
        else:
            deviation = "**正常**"
            deviation_en = "**within**"
    else:
        standard_range = "**未定义**"
        deviation = "**未知**"
        deviation_en = "**unknown**"

    # 格式化测试数据（加粗突出显示）
    formatted_test_data = f"**{test_data}{unit}**"

    # 根据语言选择描述文本
    if language == 'zh':
        test_item_desc = f"### {meaning}\n\n"
        deviation_text = deviation

        problem_desc_map = {
            "Hardware Presence Accuracy": "#### 磁力计硬件存在性检测准确性异常",
            "Driver Status Recognition": "#### 磁力计驱动加载状态识别准确性异常",
            "Status Switch Response": "#### 磁力计状态切换响应时间异常",
            "Continuous Monitoring Stability": "#### 磁力计状态持续监测稳定性异常",
            "Hardware ID Recognition": "#### 磁力计硬件ID识别准确性异常",
            "UNKNOWN": "#### 磁力计存在性检测功能异常"
        }
    else:
        test_item_desc = f"### Magnetometer presence test: {test_item}\n\n"
        deviation_text = deviation_en

        problem_desc_map = {
            "Hardware Presence Accuracy": "#### Magnetometer hardware presence detection accuracy anomaly",
            "Driver Status Recognition": "#### Magnetometer driver status recognition accuracy anomaly",
            "Status Switch Response": "#### Magnetometer status switch response time anomaly",
            "Continuous Monitoring Stability": "#### Magnetometer continuous monitoring stability anomaly",
            "Hardware ID Recognition": "#### Magnetometer hardware ID recognition accuracy anomaly",
            "UNKNOWN": "#### Magnetometer presence detection function anomaly"
        }

    # 选择问题生成器
    suggestion_generator_map = {
        "Hardware Presence Accuracy": magnetometer_presence_accuracy_suggestion,
        "Driver Status Recognition": magnetometer_driver_status_suggestion,
        "Status Switch Response": magnetometer_status_switch_suggestion,
        "Continuous Monitoring Stability": magnetometer_monitoring_stability_suggestion,
        "Hardware ID Recognition": magnetometer_hardware_id_suggestion,
        "UNKNOWN": default_magnetometer_presence_suggestion
    }
    suggestion_generator = suggestion_generator_map.get(sub_type, default_magnetometer_presence_suggestion)

    # 生成结果
    return suggestion_generator(
        test_type=test_type,
        sub_type=sub_type,
        test_data=formatted_test_data,
        standard_range=standard_range,
        deviation=deviation_text,
        indicator_desc=indicator_desc,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc_map.get(sub_type, "#### Magnetometer Presence Test Anomaly"),
        language=language
    )


def magnetometer_presence_accuracy_suggestion(**kwargs):
    """
    磁力计硬件存在性检测准确性异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查磁力计硬件是否正确安装，连接器是否松动或氧化\n" \
               f"> 2. 验证设备固件是否识别到磁力计硬件（查看设备管理器或系统日志）\n" \
               f"> 3. 确认硬件型号与设备驱动的兼容性\n" \
               f"> 4. 尝试重启设备后重新检测\n" \
               f"> 5. 若问题持续，可能为硬件故障，建议更换磁力计模块"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if the magnetometer hardware is properly installed and connectors are not loose or oxidized\n" \
               f"> 2. Verify if device firmware recognizes the magnetometer (check device manager or system logs)\n" \
               f"> 3. Confirm compatibility between hardware model and device driver\n" \
               f"> 4. Try restarting the device and re-testing\n" \
               f"> 5. If problem persists, it may indicate hardware failure, recommend replacing the magnetometer module"


def magnetometer_driver_status_suggestion(**kwargs):
    """
    磁力计驱动加载状态识别准确性异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查磁力计驱动是否正确安装（设备管理器中查看是否有黄色感叹号）\n" \
               f"> 2. 确认驱动版本与设备固件版本兼容性\n" \
               f"> 3. 尝试卸载并重新安装最新版驱动\n" \
               f"> 4. 检查系统权限是否阻止驱动加载\n" \
               f"> 5. 验证驱动配置文件是否完整无损坏"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if magnetometer driver is properly installed (look for yellow exclamation mark in device manager)\n" \
               f"> 2. Confirm compatibility between driver version and device firmware version\n" \
               f"> 3. Try uninstalling and reinstalling the latest driver\n" \
               f"> 4. Check if system permissions are blocking driver loading\n" \
               f"> 5. Verify that driver configuration files are complete and not corrupted"


def magnetometer_status_switch_suggestion(**kwargs):
    """
    磁力计状态切换响应时间异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查磁力计使能/禁用控制接口是否正常工作\n" \
               f"> 2. 分析系统负载对响应时间的影响（高负载可能导致延迟）\n" \
               f"> 3. 验证驱动中状态切换的超时设置是否合理\n" \
               f"> 4. 检查磁力计硬件是否存在切换延迟过大的硬件问题\n" \
               f"> 5. 尝试更新固件至最新版本优化响应性能"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if magnetometer enable/disable control interface is working properly\n" \
               f"> 2. Analyze the impact of system load on response time (high load may cause delays)\n" \
               f"> 3. Verify that timeout settings for status switching in the driver are reasonable\n" \
               f"> 4. Check if magnetometer hardware has excessive switching delay issues\n" \
               f"> 5. Try updating firmware to the latest version to optimize response performance"


def magnetometer_monitoring_stability_suggestion(**kwargs):
    """
    磁力计状态持续监测稳定性异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查磁力计供电稳定性，是否存在电压波动\n" \
               f"> 2. 分析设备温度对磁力计稳定性的影响（过热可能导致漂移）\n" \
               f"> 3. 验证监测周期设置是否合理，过短可能导致资源耗尽\n" \
               f"> 4. 检查系统日志中是否有磁力计相关错误报告\n" \
               f"> 5. 尝试在不同环境条件下测试，排除外部干扰因素"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check magnetometer power supply stability for voltage fluctuations\n" \
               f"> 2. Analyze the impact of device temperature on magnetometer stability (overheating may cause drift)\n" \
               f"> 3. Verify that monitoring cycle settings are reasonable; too short may cause resource exhaustion\n" \
               f"> 4. Check system logs for magnetometer-related error reports\n" \
               f"> 5. Try testing under different environmental conditions to rule out external interference"


def magnetometer_hardware_id_suggestion(**kwargs):
    """
    磁力计硬件ID识别准确性异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查磁力计硬件ID是否与设备支持列表匹配\n" \
               f"> 2. 验证驱动是否正确识别硬件ID（查看驱动日志）\n" \
               f"> 3. 确认固件版本是否支持当前磁力计型号\n" \
               f"> 4. 尝试重新校准硬件ID识别机制\n" \
               f"> 5. 若为定制硬件，检查ID配置是否符合设备规范"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if magnetometer hardware ID matches the device support list\n" \
               f"> 2. Verify that the driver correctly identifies the hardware ID (check driver logs)\n" \
               f"> 3. Confirm that firmware version supports the current magnetometer model\n" \
               f"> 4. Try recalibrating the hardware ID recognition mechanism\n" \
               f"> 5. For custom hardware, check if ID configuration complies with device specifications"


def default_magnetometer_presence_suggestion(**kwargs):
    """
    磁力计存在性检测未知异常的默认排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 执行全面系统诊断，检查磁力计相关硬件和软件组件\n" \
               f"> 2. 确认测试环境符合设备规格要求\n" \
               f"> 3. 检查设备是否存在硬件冲突或资源争用\n" \
               f"> 4. 尝试恢复设备至出厂设置后重新测试\n" \
               f"> 5. 联系设备制造商获取技术支持，提供详细测试日志"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Perform a comprehensive system diagnosis to check magnetometer-related hardware and software components\n" \
               f"> 2. Confirm that the test environment meets device specification requirements\n" \
               f"> 3. Check for hardware conflicts or resource contention on the device\n" \
               f"> 4. Try restoring the device to factory settings and retesting\n" \
               f"> 5. Contact device manufacturer for technical support, providing detailed test logs"


# QC USIM Mechanical Switch Removed Detection  分析与建议函数
def generate_issue_for_basic_band_QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW(language,
                                                                        parsed_eval_and_log_results_container):
    """
    从基础频段测试结果容器生成USIM机械开关移除检测的问题描述和排查建议（Markdown格式）

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的Markdown格式问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    test_data = parsed_eval_and_log_results_container['test_data']
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    unit = parsed_eval_and_log_results_container['unit']
    meaning = parsed_eval_and_log_results_container['meaning']
    indicators = parsed_eval_and_log_results_container['indicator'].split(';')

    # 解析测试类型和子类型
    test_type = "QC USIM Mechanical Switch Removed Detection"
    sub_type = "UNKNOWN"

    # 从测试指标中解析子类型
    if any("USIM机械开关移除状态识别准确性" in ind for ind in indicators):
        sub_type = "Removal Status Recognition"
    elif any("USIM机械开关移除检测响应时间" in ind for ind in indicators):
        sub_type = "Detection Response Time"
    elif any("USIM机械开关状态切换可靠性" in ind for ind in indicators):
        sub_type = "State Switch Reliability"
    elif any("USIM机械开关移除检测稳定性" in ind for ind in indicators):
        sub_type = "Detection Stability"
    elif any("USIM机械开关硬件连接检测" in ind for ind in indicators):
        sub_type = "Hardware Connection Detection"

    # 提取相关指标描述
    indicator_desc = ""
    for indicator in indicators:
        if (sub_type == "Removal Status Recognition" and "USIM机械开关移除状态识别准确性" in indicator) or \
                (sub_type == "Detection Response Time" and "USIM机械开关移除检测响应时间" in indicator) or \
                (sub_type == "State Switch Reliability" and "USIM机械开关状态切换可靠性" in indicator) or \
                (sub_type == "Detection Stability" and "USIM机械开关移除检测稳定性" in indicator) or \
                (sub_type == "Hardware Connection Detection" and "USIM机械开关硬件连接检测" in indicator):
            indicator_desc = indicator.strip()
            break

    # 计算标准值范围和判断偏差（适配P/F类型测试），加粗突出显示重要信息
    if unit == "P/F":
        standard_range = "**PASS**"
        if parsed_eval_and_log_results_container['state'] == 'FAILED':
            deviation = "**未通过**"
            deviation_en = "**failed**"
        else:
            deviation = "**通过**"
            deviation_en = "**passed**"
    elif low_limit is not None and up_limit is not None:
        standard_range = f"**{low_limit} - {up_limit}{unit}**"
        if test_data < low_limit:
            deviation = "**偏低**"
            deviation_en = "**lower than**"
        elif test_data > up_limit:
            deviation = "**偏高**"
            deviation_en = "**higher than**"
        else:
            deviation = "**正常**"
            deviation_en = "**within**"
    else:
        standard_range = "**未定义**"
        deviation = "**未知**"
        deviation_en = "**unknown**"

    # 格式化测试数据（加粗突出显示）
    formatted_test_data = f"**{test_data}{unit}**"

    # 根据语言选择描述文本
    if language == 'zh':
        test_item_desc = f"### {meaning}\n\n"
        deviation_text = deviation

        problem_desc_map = {
            "Removal Status Recognition": "#### USIM机械开关移除状态识别准确性异常",
            "Detection Response Time": "#### USIM机械开关移除检测响应时间异常",
            "State Switch Reliability": "#### USIM机械开关状态切换可靠性异常",
            "Detection Stability": "#### USIM机械开关移除检测稳定性异常",
            "Hardware Connection Detection": "#### USIM机械开关硬件连接检测异常",
            "UNKNOWN": "#### USIM机械开关移除检测功能异常"
        }
    else:
        test_item_desc = f"### USIM mechanical switch test: {test_item}\n\n"
        deviation_text = deviation_en

        problem_desc_map = {
            "Removal Status Recognition": "#### USIM mechanical switch removal status recognition accuracy anomaly",
            "Detection Response Time": "#### USIM mechanical switch removal detection response time anomaly",
            "State Switch Reliability": "#### USIM mechanical switch state switch reliability anomaly",
            "Detection Stability": "#### USIM mechanical switch removal detection stability anomaly",
            "Hardware Connection Detection": "#### USIM mechanical switch hardware connection detection anomaly",
            "UNKNOWN": "#### USIM mechanical switch removal detection function anomaly"
        }

    # 选择问题生成器
    suggestion_generator_map = {
        "Removal Status Recognition": usim_switch_removal_status_suggestion,
        "Detection Response Time": usim_switch_response_time_suggestion,
        "State Switch Reliability": usim_switch_state_reliability_suggestion,
        "Detection Stability": usim_switch_detection_stability_suggestion,
        "Hardware Connection Detection": usim_switch_hardware_connection_suggestion,
        "UNKNOWN": default_usim_mechanical_switch_suggestion
    }
    suggestion_generator = suggestion_generator_map.get(sub_type, default_usim_mechanical_switch_suggestion)

    # 生成结果
    return suggestion_generator(
        test_type=test_type,
        sub_type=sub_type,
        test_data=formatted_test_data,
        standard_range=standard_range,
        deviation=deviation_text,
        indicator_desc=indicator_desc,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc_map.get(sub_type, "#### USIM Mechanical Switch Test Anomaly"),
        language=language
    )


def usim_switch_removal_status_suggestion(**kwargs):
    """
    USIM机械开关移除状态识别准确性异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查USIM卡插槽机械结构是否完好，有无异物堵塞\n" \
               f"> 2. 验证开关检测传感器灵敏度是否正常，必要时进行校准\n" \
               f"> 3. 清洁USIM卡触点和插槽，排除接触不良导致的识别错误\n" \
               f"> 4. 检查开关状态识别算法参数是否正确配置\n" \
               f"> 5. 测试不同厚度的USIM卡，确认兼容性范围"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if USIM card slot mechanical structure is intact and free of foreign objects\n" \
               f"> 2. Verify if switch detection sensor sensitivity is normal, calibrate if necessary\n" \
               f"> 3. Clean USIM card contacts and slot to eliminate recognition errors caused by poor contact\n" \
               f"> 4. Check if switch status recognition algorithm parameters are correctly configured\n" \
               f"> 5. Test USIM cards of different thicknesses to confirm compatibility range"


def usim_switch_response_time_suggestion(**kwargs):
    """
    USIM机械开关移除检测响应时间异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查开关信号传输线路是否存在延迟或干扰\n" \
               f"> 2. 优化开关状态检测采样频率，缩短响应间隔\n" \
               f"> 3. 检查系统处理线程优先级，确保开关检测任务优先执行\n" \
               f"> 4. 验证硬件中断响应机制是否正常工作\n" \
               f"> 5. 升级固件至最新版本，修复可能存在的响应延迟问题"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if there is delay or interference in switch signal transmission lines\n" \
               f"> 2. Optimize switch status detection sampling frequency to shorten response interval\n" \
               f"> 3. Check system processing thread priority to ensure switch detection tasks are executed first\n" \
               f"> 4. Verify if hardware interrupt response mechanism is working properly\n" \
               f"> 5. Upgrade firmware to the latest version to fix potential response delay issues"


def usim_switch_state_reliability_suggestion(**kwargs):
    """
    USIM机械开关状态切换可靠性异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查机械开关结构是否存在磨损或变形，影响切换可靠性\n" \
               f"> 2. 测试开关在不同温度环境下的切换性能，排除温度影响\n" \
               f"> 3. 增加状态切换确认机制，避免误判\n" \
               f"> 4. 调整开关触发阈值，提高抗干扰能力\n" \
               f"> 5. 进行多次切换耐久性测试，评估机械寿命是否达标"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if mechanical switch structure is worn or deformed, affecting switching reliability\n" \
               f"> 2. Test switch performance under different temperature environments to rule out temperature effects\n" \
               f"> 3. Add state switching confirmation mechanism to avoid misjudgment\n" \
               f"> 4. Adjust switch trigger threshold to improve anti-interference ability\n" \
               f"> 5. Conduct multiple switching durability tests to evaluate whether mechanical life meets standards"


def usim_switch_detection_stability_suggestion(**kwargs):
    """
    USIM机械开关移除检测稳定性异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查开关供电电压是否稳定，排除电源波动影响\n" \
               f"> 2. 加固开关连接线束，减少振动导致的接触不良\n" \
               f"> 3. 优化检测算法滤波参数，提高数据稳定性\n" \
               f"> 4. 增加冗余检测机制，避免单点故障导致的误报\n" \
               f"> 5. 在不同湿度环境下测试，验证环境适应性"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if switch supply voltage is stable to eliminate power fluctuation effects\n" \
               f"> 2. Reinforce switch connection harness to reduce poor contact caused by vibration\n" \
               f"> 3. Optimize detection algorithm filtering parameters to improve data stability\n" \
               f"> 4. Add redundant detection mechanism to avoid false alarms caused by single point failure\n" \
               f"> 5. Test under different humidity environments to verify environmental adaptability"


def usim_switch_hardware_connection_suggestion(**kwargs):
    """
    USIM机械开关硬件连接检测异常的排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 检查开关与主板的连接插件是否松动或氧化\n" \
               f"> 2. 用万用表测量开关引脚间电阻，确认导通性\n" \
               f"> 3. 检查PCB板上开关相关焊点是否存在虚焊或脱焊\n" \
               f"> 4. 替换连接线缆，排除线缆内部断线可能性\n" \
               f"> 5. 对比正常设备的连接阻抗值，确认是否在合理范围"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Check if the connection plug between switch and main board is loose or oxidized\n" \
               f"> 2. Measure the resistance between switch pins with a multimeter to confirm conductivity\n" \
               f"> 3. Check if there are cold solder joints or desoldering on switch related solder points on PCB\n" \
               f"> 4. Replace connecting cables to rule out the possibility of internal cable breakage\n" \
               f"> 5. Compare with the connection impedance value of normal equipment to confirm if it is within a reasonable range"


def default_usim_mechanical_switch_suggestion(**kwargs):
    """
    USIM机械开关未知异常的默认排查建议（Markdown格式）
    """
    if kwargs['language'] == 'zh':
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- 测试数据: {kwargs['test_data']}\n" \
               f"- 标准要求: {kwargs['standard_range']}\n" \
               f"- 状态: {kwargs['deviation']}\n\n" \
               f"**指标说明**: {kwargs['indicator_desc']}\n\n" \
               f"**排查建议**:\n" \
               f"> 1. 执行USIM机械开关全面功能测试，定位具体异常点\n" \
               f"> 2. 检查设备固件版本，确认是否为最新稳定版本\n" \
               f"> 3. 恢复设备出厂设置后重新测试，排除配置错误\n" \
               f"> 4. 对比正常设备的开关信号波形，分析差异点\n" \
               f"> 5. 联系硬件供应商获取技术支持，提供详细测试日志"
    else:
        return f"{kwargs['test_item_desc']}{kwargs['problem_desc']}\n\n" \
               f"- Test data: {kwargs['test_data']}\n" \
               f"- Standard requirement: {kwargs['standard_range']}\n" \
               f"- Status: {kwargs['deviation']}\n\n" \
               f"**Indicator Description**: {kwargs['indicator_desc']}\n\n" \
               f"**Troubleshooting Suggestions**:\n" \
               f"> 1. Perform a comprehensive functional test of USIM mechanical switch to locate specific abnormal points\n" \
               f"> 2. Check device firmware version to confirm if it is the latest stable version\n" \
               f"> 3. Restore device to factory settings and retest to rule out configuration errors\n" \
               f"> 4. Compare switch signal waveforms with normal equipment to analyze differences\n" \
               f"> 5. Contact hardware supplier for technical support and provide detailed test logs"


def generate_issue_for_basic_band_INCLINOMETER_MEASURE_A_and_G(language,
                                                               parsed_eval_and_log_results_container):
    """
    从基础频段测试结果容器生成倾角计A（加速度）和G（角加速度）测量的问题描述和排查建议（Markdown格式）

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的Markdown格式问题描述和排查建议
    """
    # 从容器中提取参数
    test_item = parsed_eval_and_log_results_container['test_item']
    test_data = parsed_eval_and_log_results_container['test_data']
    low_limit = parsed_eval_and_log_results_container['low_limit']
    up_limit = parsed_eval_and_log_results_container['up_limit']
    unit = parsed_eval_and_log_results_container['unit']
    meaning = parsed_eval_and_log_results_container['meaning']
    indicators = parsed_eval_and_log_results_container['indicator'].split(';')

    # 解析测试类型和子类型（适配倾角计A/G测量场景）
    test_type = "QC Inclinometer A&G (Acceleration & Gyro) Measurement"
    sub_type = "UNKNOWN"

    # 从测试指标中解析子类型（匹配倾角计核心测试维度）
    if any("加速度读数准确性" in ind for ind in indicators):
        sub_type = "Acceleration Reading Accuracy"
    elif any("角加速度读数稳定性" in ind for ind in indicators):
        sub_type = "Gyro Reading Stability"
    elif any("A&G数据响应时效性" in ind for ind in indicators):
        sub_type = "A&G Data Response Timeliness"
    elif any("倾角计环境适应性" in ind for ind in indicators):
        sub_type = "Inclinometer Environmental Adaptability"
    elif any("A&G数据同步一致性" in ind for ind in indicators):
        sub_type = "A&G Data Synchronization Consistency"

    # 提取相关指标描述（精准匹配当前子类型对应的指标）
    indicator_desc = ""
    for indicator in indicators:
        if (sub_type == "Acceleration Reading Accuracy" and "加速度读数准确性" in indicator) or \
                (sub_type == "Gyro Reading Stability" and "角加速度读数稳定性" in indicator) or \
                (sub_type == "A&G Data Response Timeliness" and "A&G数据响应时效性" in indicator) or \
                (sub_type == "Inclinometer Environmental Adaptability" and "倾角计环境适应性" in indicator) or \
                (sub_type == "A&G Data Synchronization Consistency" and "A&G数据同步一致性" in indicator):
            indicator_desc = indicator.strip()
            break

    # 计算标准值范围和判断偏差（复用原函数P/F/数值范围适配逻辑，确保兼容性）
    if unit == "P/F":
        standard_range = "**PASS**"
        if parsed_eval_and_log_results_container['state'] == 'FAILED':
            deviation = "**未通过**"
            deviation_en = "**failed**"
        else:
            deviation = "**通过**"
            deviation_en = "**passed**"
    elif low_limit is not None and up_limit is not None:
        standard_range = f"**{low_limit} - {up_limit}{unit}**"
        if test_data < low_limit:
            deviation = "**偏低**"
            deviation_en = "**lower than**"
        elif test_data > up_limit:
            deviation = "**偏高**"
            deviation_en = "**higher than**"
        else:
            deviation = "**正常**"
            deviation_en = "**within**"
    else:
        standard_range = "**未定义**"
        deviation = "**未知**"
        deviation_en = "**unknown**"

    # 格式化测试数据（加粗突出显示关键数据）
    formatted_test_data = f"**{test_data}{unit}**"

    # 根据语言选择描述文本（中英文场景精准适配）
    if language == 'zh':
        test_item_desc = f"### {meaning}\n\n"
        deviation_text = deviation

        problem_desc_map = {
            "Acceleration Reading Accuracy": "#### 倾角计加速度读数准确性异常",
            "Gyro Reading Stability": "#### 倾角计角加速度读数稳定性异常",
            "A&G Data Response Timeliness": "#### 倾角计A&G数据响应时效性异常",
            "Inclinometer Environmental Adaptability": "#### 倾角计环境适应性异常",
            "A&G Data Synchronization Consistency": "#### 倾角计A&G数据同步一致性异常",
            "UNKNOWN": "#### 倾角计A&G测量功能异常"
        }
    else:
        test_item_desc = f"### Inclinometer A&G measurement test: {test_item}\n\n"
        deviation_text = deviation_en

        problem_desc_map = {
            "Acceleration Reading Accuracy": "#### Inclinometer Acceleration Reading Accuracy Anomaly",
            "Gyro Reading Stability": "#### Inclinometer Gyro Reading Stability Anomaly",
            "A&G Data Response Timeliness": "#### Inclinometer A&G Data Response Timeliness Anomaly",
            "Inclinometer Environmental Adaptability": "#### Inclinometer Environmental Adaptability Anomaly",
            "A&G Data Synchronization Consistency": "#### Inclinometer A&G Data Synchronization Consistency Anomaly",
            "UNKNOWN": "#### Inclinometer A&G Measurement Function Anomaly"
        }

    # 选择问题生成器（绑定倾角计场景专属排查建议函数）
    suggestion_generator_map = {
        "Acceleration Reading Accuracy": inclinometer_acc_accuracy_suggestion,
        "Gyro Reading Stability": inclinometer_gyro_stability_suggestion,
        "A&G Data Response Timeliness": inclinometer_ag_response_suggestion,
        "Inclinometer Environmental Adaptability": inclinometer_env_adapt_suggestion,
        "A&G Data Synchronization Consistency": inclinometer_ag_sync_suggestion,
        "UNKNOWN": default_inclinometer_ag_suggestion
    }
    suggestion_generator = suggestion_generator_map.get(sub_type, default_inclinometer_ag_suggestion)

    # 生成结果（保持原函数返回结构，确保调用兼容性）
    return suggestion_generator(
        test_type=test_type,
        sub_type=sub_type,
        test_data=formatted_test_data,
        standard_range=standard_range,
        deviation=deviation_text,
        indicator_desc=indicator_desc,
        test_item_desc=test_item_desc,
        problem_desc=problem_desc_map.get(sub_type, "#### Inclinometer A&G Measurement Anomaly"),
        language=language
    )


def inclinometer_acc_accuracy_suggestion(test_type, sub_type, test_data, standard_range, deviation, indicator_desc, test_item_desc, problem_desc, language):
    """倾角计加速度读数准确性异常的排查建议"""
    if language == 'zh':
        return f"""
{test_item_desc}
{problem_desc}

### 一、测试结果详情
- 测试类型：{test_type}
- 异常子类型：{sub_type}
- 测试指标：{indicator_desc}
- 实际测试值：{test_data}
- 标准范围：{standard_range}
- 偏差状态：{deviation}

### 二、排查建议
1. **校准验证**：确认倾角计是否完成最新校准，建议使用标准加速度源重新执行X/Y/Z轴校准（参考设备手册第4.2节）
2. **硬件检查**：检查加速度传感器引脚连接是否松动，传感器表面是否存在物理损伤或污渍
3. **干扰排除**：确认测试环境无强电磁干扰（如远离大功率电机、射频设备），建议在电磁屏蔽环境复现测试
4. **数据对比**：对比同批次正常设备的加速度读数，判断是否为个体硬件差异或批次性问题
5. **固件更新**：确认设备固件为最新版本，旧版本可能存在加速度算法精度缺陷
"""
    else:
        return f"""
{test_item_desc}
{problem_desc}

### 1. Test Result Details
- Test Type: {test_type}
- Anomaly Subtype: {sub_type}
- Test Indicator: {indicator_desc}
- Actual Test Value: {test_data}
- Standard Range: {standard_range}
- Deviation Status: {deviation}

### 2. Troubleshooting Suggestions
1. **Calibration Verification**: Confirm if the inclinometer has completed the latest calibration. It is recommended to re-perform X/Y/Z axis calibration using a standard acceleration source (refer to Section 4.2 of the equipment manual)
2. **Hardware Check**: Inspect if the acceleration sensor pins are loose, and if there is physical damage or contamination on the sensor surface
3. **Interference Elimination**: Ensure there is no strong electromagnetic interference in the test environment (e.g., keep away from high-power motors, RF equipment). It is recommended to reproduce the test in an electromagnetic shielding environment
4. **Data Comparison**: Compare the acceleration readings with normal devices of the same batch to determine if it is an individual hardware difference or a batch issue
5. **Firmware Update**: Confirm the device firmware is the latest version. Older versions may have acceleration algorithm accuracy defects
"""


def inclinometer_gyro_stability_suggestion(test_type, sub_type, test_data, standard_range, deviation, indicator_desc, test_item_desc, problem_desc, language):
    """倾角计角加速度读数稳定性异常的排查建议"""
    if language == 'zh':
        return f"""
{test_item_desc}
{problem_desc}

### 一、测试结果详情
- 测试类型：{test_type}
- 异常子类型：{sub_type}
- 测试指标：{indicator_desc}
- 实际测试值：{test_data}
- 标准范围：{standard_range}
- 偏差状态：{deviation}

### 二、排查建议
1. **温度补偿**：检查角加速度传感器温度补偿功能是否启用，建议在恒温环境（25±2℃）重新测试
2. **电源稳定性**：测量传感器供电电压波动（要求≤±0.05V），排查电源模块是否存在纹波干扰
3. **机械固定**：确认倾角计安装是否牢固，避免因振动导致的读数漂移
4. **滤波参数**：检查角加速度数据滤波算法参数是否合理，必要时调整滤波窗口大小
5. **老化测试**：对设备进行48小时连续老化测试，观察稳定性是否随运行时间改善
"""
    else:
        return f"""
{test_item_desc}
{problem_desc}

### 1. Test Result Details
- Test Type: {test_type}
- Anomaly Subtype: {sub_type}
- Test Indicator: {indicator_desc}
- Actual Test Value: {test_data}
- Standard Range: {standard_range}
- Deviation Status: {deviation}

### 2. Troubleshooting Suggestions
1. **Temperature Compensation**: Check if the temperature compensation function of the gyro sensor is enabled. It is recommended to retest in a constant temperature environment (25±2℃)
2. **Power Stability**: Measure the power supply voltage fluctuation of the sensor (requirement ≤±0.05V) and check if the power module has ripple interference
3. **Mechanical Fixing**: Confirm the inclinometer is installed firmly to avoid reading drift caused by vibration
4. **Filter Parameters**: Check if the gyro data filtering algorithm parameters are reasonable, and adjust the filter window size if necessary
5. **Aging Test**: Perform a 48-hour continuous aging test on the device to observe if stability improves with operation time
"""


def inclinometer_ag_response_suggestion(test_type, sub_type, test_data, standard_range, deviation, indicator_desc, test_item_desc, problem_desc, language):
    """倾角计A&G数据响应时效性异常的排查建议"""
    if language == 'zh':
        return f"""
{test_item_desc}
{problem_desc}

### 一、测试结果详情
- 测试类型：{test_type}
- 异常子类型：{sub_type}
- 测试指标：{indicator_desc}
- 实际测试值：{test_data}
- 标准范围：{standard_range}
- 偏差状态：{deviation}

### 二、排查建议
1. **采样率检查**：确认A&G传感器采样率设置是否符合设计要求（建议≥100Hz）
2. **数据传输**：检查传感器与主控单元的通信速率（如I2C/SPI），排查传输延迟
3. **算法优化**：分析数据处理算法耗时，简化冗余计算步骤
4. **中断优先级**：调整传感器数据读取中断的优先级，避免被低优先级任务阻塞
5. **硬件性能**：确认主控芯片算力是否满足实时处理需求，必要时升级硬件规格
"""
    else:
        return f"""
{test_item_desc}
{problem_desc}

### 1. Test Result Details
- Test Type: {test_type}
- Anomaly Subtype: {sub_type}
- Test Indicator: {indicator_desc}
- Actual Test Value: {test_data}
- Standard Range: {standard_range}
- Deviation Status: {deviation}

### 2. Troubleshooting Suggestions
1. **Sampling Rate Check**: Confirm if the A&G sensor sampling rate setting meets the design requirements (recommended ≥100Hz)
2. **Data Transmission**: Check the communication rate between the sensor and the main control unit (e.g., I2C/SPI) and troubleshoot transmission delays
3. **Algorithm Optimization**: Analyze the time consumption of the data processing algorithm and simplify redundant calculation steps
4. **Interrupt Priority**: Adjust the priority of the sensor data reading interrupt to avoid blocking by low-priority tasks
5. **Hardware Performance**: Confirm if the main control chip computing power meets real-time processing requirements, and upgrade hardware specifications if necessary
"""


def inclinometer_env_adapt_suggestion(test_type, sub_type, test_data, standard_range, deviation, indicator_desc, test_item_desc, problem_desc, language):
    """倾角计环境适应性异常的排查建议"""
    if language == 'zh':
        return f"""
{test_item_desc}
{problem_desc}

### 一、测试结果详情
- 测试类型：{test_type}
- 异常子类型：{sub_type}
- 测试指标：{indicator_desc}
- 实际测试值：{test_data}
- 标准范围：{standard_range}
- 偏差状态：{deviation}

### 二、排查建议
1. **温湿度测试**：在设计温湿度范围（-40℃~85℃，10%~90%RH）内分段测试，定位异常区间
2. **振动冲击**：检查设备抗振动（10~500Hz）和冲击（1000G/0.5ms）性能是否达标
3. **电磁兼容**：执行EMC测试（如辐射骚扰、静电放电），确认无电磁干扰导致的读数异常
4. **防护等级**：检查设备外壳防护等级（建议IP65及以上），避免粉尘/液体侵入影响传感器
5. **环境补偿**：优化环境自适应算法，增加温湿度、振动等参数的实时补偿逻辑
"""
    else:
        return f"""
{test_item_desc}
{problem_desc}

### 1. Test Result Details
- Test Type: {test_type}
- Anomaly Subtype: {sub_type}
- Test Indicator: {indicator_desc}
- Actual Test Value: {test_data}
- Standard Range: {standard_range}
- Deviation Status: {deviation}

### 2. Troubleshooting Suggestions
1. **Temperature & Humidity Test**: Perform segmented tests within the design temperature and humidity range (-40℃~85℃, 10%~90%RH) to locate the abnormal range
2. **Vibration & Shock**: Check if the device's anti-vibration (10~500Hz) and anti-shock (1000G/0.5ms) performance meets the standards
3. **EMC Compliance**: Perform EMC tests (e.g., radiated emissions, electrostatic discharge) to confirm no reading anomalies caused by electromagnetic interference
4. **Protection Level**: Check the device enclosure protection level (IP65 and above is recommended) to prevent dust/liquid intrusion affecting the sensor
5. **Environmental Compensation**: Optimize the environment adaptive algorithm and add real-time compensation logic for temperature, humidity, vibration and other parameters
"""


def inclinometer_ag_sync_suggestion(test_type, sub_type, test_data, standard_range, deviation, indicator_desc, test_item_desc, problem_desc, language):
    """倾角计A&G数据同步一致性异常的排查建议"""
    if language == 'zh':
        return f"""
{test_item_desc}
{problem_desc}

### 一、测试结果详情
- 测试类型：{test_type}
- 异常子类型：{sub_type}
- 测试指标：{indicator_desc}
- 实际测试值：{test_data}
- 标准范围：{standard_range}
- 偏差状态：{deviation}

### 二、排查建议
1. **时间戳同步**：检查A&G传感器数据时间戳生成机制，确保使用统一时钟源
2. **传输延迟校准**：测量A&G数据传输路径延迟差异，添加延迟补偿参数
3. **数据对齐**：优化数据接收缓存机制，确保A&G数据帧按时间顺序对齐
4. **同步协议**：确认传感器是否支持硬件同步信号（如SYNC引脚），必要时启用该功能
5. **软件校准**：在数据处理层添加同步偏差校准算法，实时修正A&G数据时间差
"""
    else:
        return f"""
{test_item_desc}
{problem_desc}

### 1. Test Result Details
- Test Type: {test_type}
- Anomaly Subtype: {sub_type}
- Test Indicator: {indicator_desc}
- Actual Test Value: {test_data}
- Standard Range: {standard_range}
- Deviation Status: {deviation}

### 2. Troubleshooting Suggestions
1. **Timestamp Synchronization**: Check the A&G sensor data timestamp generation mechanism to ensure a unified clock source is used
2. **Transmission Delay Calibration**: Measure the delay difference of the A&G data transmission path and add delay compensation parameters
3. **Data Alignment**: Optimize the data reception buffer mechanism to ensure A&G data frames are aligned in time order
4. **Synchronization Protocol**: Confirm if the sensor supports hardware synchronization signals (e.g., SYNC pin) and enable this function if necessary
5. **Software Calibration**: Add a synchronization deviation calibration algorithm in the data processing layer to real-time correct the A&G data time difference
"""


def default_inclinometer_ag_suggestion(test_type, sub_type, test_data, standard_range, deviation, indicator_desc, test_item_desc, problem_desc, language):
    """倾角计A&G测量通用异常排查建议（默认）"""
    if language == 'zh':
        return f"""
{test_item_desc}
{problem_desc}

### 一、测试结果详情
- 测试类型：{test_type}
- 异常子类型：{sub_type}
- 测试指标：{indicator_desc if indicator_desc else '未明确'}
- 实际测试值：{test_data}
- 标准范围：{standard_range}
- 偏差状态：{deviation}

### 二、通用排查建议
1. **基础检查**：确认设备供电正常、接线无误，重启设备后重新测试
2. **测试环境**：确保测试环境符合设备手册要求（温度、湿度、电磁环境）
3. **固件版本**：升级设备固件至最新稳定版，排除已知软件缺陷
4. **硬件检测**：使用专用工具检测A&G传感器硬件状态，确认无故障
5. **数据验证**：对比多台同型号设备测试结果，判断是否为共性问题
6. **日志分析**：导出设备测试日志，分析异常发生时的系统状态和错误码
"""
    else:
        return f"""
{test_item_desc}
{problem_desc}

### 1. Test Result Details
- Test Type: {test_type}
- Anomaly Subtype: {sub_type}
- Test Indicator: {indicator_desc if indicator_desc else 'Not Specified'}
- Actual Test Value: {test_data}
- Standard Range: {standard_range}
- Deviation Status: {deviation}

### 2. General Troubleshooting Suggestions
1. **Basic Check**: Confirm the device power supply is normal, wiring is correct, and retest after restarting the device
2. **Test Environment**: Ensure the test environment meets the equipment manual requirements (temperature, humidity, electromagnetic environment)
3. **Firmware Version**: Upgrade the device firmware to the latest stable version to eliminate known software defects
4. **Hardware Detection**: Use professional tools to detect the hardware status of the A&G sensor and confirm no faults
5. **Data Verification**: Compare the test results of multiple devices of the same model to determine if it is a common issue
6. **Log Analysis**: Export the device test logs and analyze the system status and error codes when the anomaly occurs
"""


# def generate_issue_for_basic_band_ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS(language, parsed_eval_and_log_results_container):
#     """APK_GET_DATABASE_STATUS功能的异常分析与建议（Markdown格式）"""
#     # 初始化错误计数（针对单条结果判断是否为失败状态）
#     error_count = 1 if parsed_eval_and_log_results_container.get('state') == 'FAILED' else 0
#
#     # 提取失败的测试项详情
#     failed_test_item = parsed_eval_and_log_results_container.get('test_item', '未知测试项')
#     failed_indicators = parsed_eval_and_log_results_container.get('indicator', '无具体指标信息')
#
#     if language == 'zh':
#         return f"""### 数据库状态获取异常分析与建议
# > 检测到异常项数量：{error_count}
# > 失败测试项：{failed_test_item}
#
# #### 失败指标详情：
# {failed_indicators.replace(';', ';\n')}
#
# #### 建议解决方案：
# 1. **连接状态不一致**：检查数据库驱动版本兼容性，重新建立连接会话
# 2. **响应超时**：优化数据库查询语句，增加索引提升检索效率，扩大超时阈值配置
# 3. **权限错误**：验证当前用户角色权限集，补充数据库状态查看所需的最小权限
# 4. **版本协议不兼容**：更新APK内置的数据库通信协议库，增加协议自动协商机制
# 5. **高并发下准确性下降**：实施请求队列机制，增加结果缓存层，限制单位时间请求量
# 6. **日志记录不完整**：扩展异常日志字段，包含时间戳、请求参数和堆栈信息"""
#     else:
#         return f"""### Database Status Retrieval Exception Analysis and Suggestions
# > Detected number of abnormal items: {error_count}
# > Failed test item: {failed_test_item}
#
# #### Failed Indicator Details:
# {failed_indicators.replace(';', ';\n')}
#
# #### Recommended Solutions:
# 1. **Connection status inconsistency**: Check database driver version compatibility and re-establish connection sessions
# 2. **Response timeout**: Optimize database query statements, add indexes to improve retrieval efficiency, and expand timeout threshold configuration
# 3. **Permission errors**: Verify current user role permission sets and supplement minimum permissions required for database status viewing
# 4. **Version protocol incompatibility**: Update the database communication protocol library built into the APK and add protocol automatic negotiation mechanism
# 5. **Accuracy degradation under high concurrency**: Implement request queue mechanism, add result cache layer, and limit requests per unit time
# 6. **Incomplete log records**: Expand exception log fields to include timestamps, request parameters, and stack information"""
def generate_issue_for_basic_band_ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS(language, parsed_eval_and_log_results_container):
    """APK_GET_DATABASE_STATUS功能的异常分析与建议（Markdown格式）"""
    # 初始化错误计数（针对单条结果判断是否为失败状态）
    error_count = 1 if parsed_eval_and_log_results_container.get('state') == 'FAILED' else 0

    # 提取失败的测试项详情
    failed_test_item = parsed_eval_and_log_results_container.get('test_item', '未知测试项')
    failed_indicators = parsed_eval_and_log_results_container.get('indicator', '无具体指标信息')

    # 提前处理指标字符串（移到f-string外部，避免跨平台解析问题）
    # 1. 处理分号换行
    processed_indicators = failed_indicators.replace(';', ';\n')
    # 2. 移除可能存在的反斜杠（关键：避免f-string解析错误）
    processed_indicators = processed_indicators.replace('\\', '/')

    if language == 'zh':
        return f"""### 数据库状态获取异常分析与建议
> 检测到异常项数量：{error_count}
> 失败测试项：{failed_test_item}

#### 失败指标详情：
{processed_indicators}

#### 建议解决方案：
1. **连接状态不一致**：检查数据库驱动版本兼容性，重新建立连接会话
2. **响应超时**：优化数据库查询语句，增加索引提升检索效率，扩大超时阈值配置
3. **权限错误**：验证当前用户角色权限集，补充数据库状态查看所需的最小权限
4. **版本协议不兼容**：更新APK内置的数据库通信协议库，增加协议自动协商机制
5. **高并发下准确性下降**：实施请求队列机制，增加结果缓存层，限制单位时间请求量
6. **日志记录不完整**：扩展异常日志字段，包含时间戳、请求参数和堆栈信息"""
    else:
        return f"""### Database Status Retrieval Exception Analysis and Suggestions
> Detected number of abnormal items: {error_count}
> Failed test item: {failed_test_item}

#### Failed Indicator Details:
{processed_indicators}

#### Recommended Solutions:
1. **Connection status inconsistency**: Check database driver version compatibility and re-establish connection sessions
2. **Response timeout**: Optimize database query statements, add indexes to improve retrieval efficiency, and expand timeout threshold configuration
3. **Permission errors**: Verify current user role permission sets and supplement minimum permissions required for database status viewing
4. **Version protocol incompatibility**: Update the database communication protocol library built into the APK and add protocol automatic negotiation mechanism
5. **Accuracy degradation under high concurrency**: Implement request queue mechanism, add result cache layer, and limit requests per unit time
6. **Incomplete log records**: Expand exception log fields to include timestamps, request parameters, and stack information"""


# 通用的 分析与建议函数
def generate_issue_from_container(language,
                                  parsed_eval_and_log_results_container,
                                  platform='MTK',
                                  test_item_desc='',
                                  combined_regex=''):
    """
    从测试结果容器生成问题描述和排查建议

    参数:
        language: 语言选项，'zh'表示中文，'en'表示英文
        parsed_eval_and_log_results_container: 测试结果容器数据

    返回:
        格式化的问题描述和排查建议
    """

    result = None

    # TODO：这里添加异常分析与建议的函数
    if platform == 'MTK':
        result = generate_issue_from_container_for_mtk(language, parsed_eval_and_log_results_container)

    elif platform == 'Qualcomm':
        result = generate_issue_from_container_for_qc(language, parsed_eval_and_log_results_container)

    elif platform == 'Generic' and re.match(combined_regex, test_item_desc) and "CAP" in test_item_desc:
        # TODO：这里添加异常分析与建议的函数
        result = generate_issue_for_basic_band_CAP_SWITCH_TURBO_CHARGER(language, parsed_eval_and_log_results_container)

    elif platform == 'Generic' and re.match(combined_regex, test_item_desc) and ("SPK_INFO" in test_item_desc or "SPKINFO" in test_item_desc):
        result = generate_issue_for_basic_band_SPK_INFO_PROGAMMING(language, parsed_eval_and_log_results_container)

    elif platform == 'Generic' and re.match(combined_regex, test_item_desc) and re.search(r"_BATTERY_LEVEL(S)?", test_item_desc):
        result = generate_issue_for_basic_band_BATTERY_LEVELS(language, parsed_eval_and_log_results_container)

    elif platform == 'Generic' and re.match(combined_regex, test_item_desc) and "ANDROID_MAGNETOMETER" in test_item_desc:
        result = generate_issue_for_basic_band_ANDROID_MAGNETOMETER(language, parsed_eval_and_log_results_container)

    elif platform == 'Generic' and re.match(combined_regex, test_item_desc) and "QC_USIM" in test_item_desc:
        result = generate_issue_for_basic_band_QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW(language, parsed_eval_and_log_results_container)

    elif platform == 'Generic' and re.match(combined_regex, test_item_desc) and "INCLINOMETER_MEASURE" in test_item_desc:
        result = generate_issue_for_basic_band_INCLINOMETER_MEASURE_A_and_G(language, parsed_eval_and_log_results_container)

    elif platform == 'Generic' and re.match(combined_regex, test_item_desc) and "ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS" in test_item_desc:
        result = generate_issue_for_basic_band_ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS(language, parsed_eval_and_log_results_container)

    return result


def generate_issue_analysis_mtk_meta_trackid_from_md_nvram(
        test_type="MTK META TrackID",
        md_chip_model="请输入MD芯片型号(如: MT6765, MT6885等)",
        trackid_read_result="请输入TrackID读取结果(如: 空值, 错误码-1, 乱码等)",
        expected_result="请输入预期结果(如: 8位字符TrackID, 错误码0等)",
        problem_scenario="请输入问题场景(如: NVRAM损坏, META通信中断等)",
        test_item_desc="{{MTK_META_READ_TRACKID_FROM_MD_NVRAM测试项}}",
        problem_desc="{{TrackID读取异常问题描述}}",
        language='zh',
        meta_tool_version="请输入META工具版本(如: V5.1.2, V6.0.0等)"  # 新增：META工具版本参数
):
    """
    根据测试参数生成MTK META TrackID从MD NVRAM读取的问题描述和排查建议

    参数:
        test_type: 测试类型，默认"MTK META TrackID"
        md_chip_model: MD芯片型号 (如: MT6765, MT6885等)
        trackid_read_result: TrackID读取实际结果 (如: 空值, 错误码-1, 乱码等)
        expected_result: 预期结果 (如: 8位字符TrackID, 错误码0等)
        problem_scenario: 问题场景 (如: NVRAM损坏, META通信中断等)
        test_item_desc: 测试项描述，默认为"{{MTK_META_READ_TRACKID_FROM_MD_NVRAM测试项}}"
        problem_desc: 问题描述，默认为"{{TrackID读取异常问题描述}}"
        language: 语言选项，'zh'表示中文，'en'表示英文，默认为中文
        meta_tool_version: META工具版本 (如: V5.1.2, V6.0.0等)，新增参数

    返回:
        格式化的问题描述和排查建议
    """
    if language == 'zh':
        # 中文描述：聚焦TrackID读取核心问题，包含META工具、MD芯片、NVRAM专项排查
        issue_description = f"""
{test_item_desc}{problem_desc}简易排查方案
一、核心问题
{test_type}测试中，{md_chip_model}芯片在{problem_scenario}场景下，TrackID读取结果为「{trackid_read_result}」，
与预期结果「{expected_result}」不符，需快速排查META工具、通信链路及MD NVRAM硬件问题。
二、产线快速排查步骤
（一）META工具检查
版本匹配：确认当前使用的META工具版本为「{meta_tool_version}」，需与{md_chip_model}芯片适配（参考芯片手册推荐版本）；版本不匹配则升级/降级至适配版本。
连接状态：查看META工具「设备连接」界面，显示"Connected"视为正常；显示"Disconnected"则重新插拔USB数据线，重启工具重试。
日志查看：导出META工具错误日志（路径：ToolLog/MTK_META_Error.log），搜索"TrackID Read"关键词定位具体错误原因（如NVRAM访问权限不足）。
（二）通信链路检查
USB链路：更换无破损、接触良好的USB数据线；确认电脑USB端口为3.0及以上，避免供电不足导致通信中断。
MD芯片驱动：在设备管理器中检查「MTK Preloader USB VCOM」驱动是否正常（无黄色感叹号）；驱动异常则重新安装芯片配套驱动包。
META协议：重启被测设备进入META模式（按音量下键+开机键），确认设备在模式选择界面显示"Meta Mode"；未显示则检查设备硬件按键是否正常。
（三）MD NVRAM与硬件检查
NVRAM状态：使用MTK专用工具（如SP Flash Tool）读取NVRAM分区（路径：0x100000-0x200000），确认分区无损坏（无"Bad Block"标记）；分区损坏则重新烧录NVRAM镜像。
TrackID存储：在NVRAM分区中搜索"TrackID"字段，确认存在有效字符（非全0/乱码）；无有效数据则执行TrackID写入流程（需工厂授权）。
芯片接触：拆开设备工装，擦除md_chip_model芯片引脚氧化层（用酒精棉）；检查芯片焊接点有无虚焊，虚焊则重新补焊。
（四）复测与判定
软件复位：在META工具中执行「Device Reset」操作，复位后重新读取TrackID，观察结果是否恢复正常。
交叉验证：更换另一台适配{md_chip_model}的META设备，重复测试；若结果正常则判定原设备硬件故障，反之则为工具或协议问题。
故障判定：经上述排查后仍无法读取正常TrackID，且NVRAM分区正常，则判定为{md_chip_model}芯片故障，标记为待维修。
"""
    elif language == 'en':
        # 英文描述：对应中文逻辑，保持排查步骤一致性，适配英文场景
        issue_description = f"""
{test_item_desc}{problem_desc}Simple Troubleshooting Guide
I. Core Issue
During {test_type} testing, the {md_chip_model} chip shows TrackID read result as "{trackid_read_result}" under the "{problem_scenario}" scenario,
which does not match the expected result "{expected_result}". Quick troubleshooting of META tool, communication link, and MD NVRAM hardware issues is required.
II. Quick Troubleshooting Steps for Production Line
(1) META Tool Check
Version Compatibility: Confirm the current META tool version is "{meta_tool_version}", which must be compatible with {md_chip_model} chip (refer to chip manual for recommended version); Upgrade/downgrade to compatible version if mismatched.
Connection Status: Check the "Device Connection" interface in META tool, "Connected" is normal; If "Disconnected", re-plug USB data cable and restart the tool.
Log Inspection: Export META tool error log (path: ToolLog/MTK_META_Error.log), search for "TrackID Read" keyword to locate specific error causes (e.g., insufficient NVRAM access permission).
(2) Communication Link Check
USB Link: Replace USB data cable with no damage and good contact; Confirm computer USB port is 3.0 or above to avoid communication interruption due to insufficient power supply.
MD Chip Driver: Check if "MTK Preloader USB VCOM" driver is normal (no yellow exclamation mark) in Device Manager; Reinstall chip-specific driver package if driver is abnormal.
META Mode: Restart the device under test to enter META mode (press Volume Down + Power button), confirm the device shows "Meta Mode" on the mode selection interface; Check device hardware buttons if not displayed.
(3) MD NVRAM & Hardware Check
NVRAM Status: Use MTK dedicated tool (e.g., SP Flash Tool) to read NVRAM partition (path: 0x100000-0x200000), confirm no partition damage (no "Bad Block" mark); Re-flash NVRAM image if partition is damaged.
TrackID Storage: Search for "TrackID" field in NVRAM partition, confirm valid characters exist (not all 0/gibberish); Execute TrackID writing process (requires factory authorization) if no valid data.
Chip Contact: Disassemble device fixture, clean oxidation layer on {md_chip_model} chip pins (with alcohol wipe); Check for cold solder joints on chip welding points, re-solder if necessary.
(4) Retest & Determination
Software Reset: Execute "Device Reset" operation in META tool, re-read TrackID after reset and check if result returns to normal.
Cross Verification: Replace with another META-compatible device for {md_chip_model}, repeat test; If result is normal, determine original device hardware fault, otherwise tool or protocol issue.
Fault Determination: If normal TrackID still cannot be read after above troubleshooting and NVRAM partition is normal, determine {md_chip_model} chip fault and mark for repair.
"""
    else:
        # 默认返回中文，传递新增的META工具版本参数
        return generate_issue_analysis_mtk_meta_trackid_from_md_nvram(
            test_type=test_type,
            md_chip_model=md_chip_model,
            trackid_read_result=trackid_read_result,
            expected_result=expected_result,
            problem_scenario=problem_scenario,
            test_item_desc=test_item_desc,
            problem_desc=problem_desc,
            language='zh',
            meta_tool_version=meta_tool_version  # 补充传递META工具版本参数
        )

    return issue_description.strip()


# 示例使用
if __name__ == "__main__":
    # 测试结果容器数据
    parsed_eval_and_log_results_container = {
        'chart_content': '',
        'chart_name': '',
        'implied_problem_possibility': '',
        'indicator': '1. 2.4G频段C0通道的发射功率值; 2. LCH01模式下的功率稳定性; 3. 天线分集（ANT）配置下的功率一致性; 4. 连续波信号的功率谱密度合规性',
        'low_limit': 9.0,
        'meaning': '验证2.4G频段C0通道在LCH01模式下的天线CW发射功率（连续波模式）',
        'state': 'PASSED',
        'test_data': 14.28,
        'test_item': 'MTK_WLAN_2.4G_C0_TX_POWER_LCH01_ANT_CW',
        'title_name': 'test_result',
        'trend_analysis': '',
        'unit': 'dB',
        'up_limit': 21.0
    }

    # 生成中文问题与建议
    chinese_result = generate_issue_from_container('zh', parsed_eval_and_log_results_container)
    print("中文版本:")
    print(chinese_result)

    # 生成英文问题与建议
    english_result = generate_issue_from_container('en', parsed_eval_and_log_results_container)
    print("\n英文版本:")
    print(english_result)
