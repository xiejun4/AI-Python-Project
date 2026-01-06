import os
import re
import base64
import xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from string import Template
import json

from functions.CleanFilterDataEntity_L2AR import (
    MTKPatterns,
    TestTypes,
    QualcommPatterns,
    TestSites,
    Platforms,
    GenericPatterns, BasicBandPatterns)

from functions.JsonDataEntity_L2AR import (
    TestProjectResult,
    StatusIndicatorItem)


# 初始化 DataCleaner 类
class DataCleaningAndFiltering:
    class L2AR:
        class DataCleaner:
            """
            正则表达式的数据清洗与过滤
            1.提供2种类实例的初始化方式：
            1-1.带参数
            1-2.不带参数
            """

            def __init__(self, site=None, platform=None, test_type=None):
                if site is not None:
                    self.site = site
                if platform is not None:
                    self.platform = platform
                if test_type is not None:
                    self.test_type = test_type

            def get_patterns_v1(self, site=None, platform=None, test_type=None):
                """
                根据指定的测试站点、芯片平台和测试类型，获取对应的正则表达式列表。

                参数:
                site (str): 测试站点名称，例如 'L2AR'。
                platform (str): 芯片平台名称，例如 'MTK' 或 'Qualcomm'。
                test_type (str): 测试类型，'Comprehensive Test' 表示综测，'Calibration' 表示校准。

                返回:
                list: 匹配的正则表达式列表，如果未找到匹配项则返回空列表。
                """
                try:
                    mtk_pattern_dict = {
                        TestTypes.COMPREHENSIVE_TEST: MTKPatterns.COMPREHENSIVE_TEST,
                        TestTypes.CALIBRATION: MTKPatterns.CALIBRATION
                    }

                    qualcomm_pattern_dict = {
                        TestTypes.COMPREHENSIVE_TEST: QualcommPatterns.COMPREHENSIVE_TEST,
                        TestTypes.CALIBRATION: QualcommPatterns.CALIBRATION
                    }

                    all_patterns_dict = {
                        TestSites.L2AR: {
                            Platforms.MTK: mtk_pattern_dict,
                            Platforms.Qualcomm: qualcomm_pattern_dict
                        }
                    }

                    if (site is not None) and (platform is not None) and (test_type is not None):
                        result = all_patterns_dict.get(site, {}).get(platform, {}).get(test_type, [])
                    elif (self.site is not None) and (self.platform is not None) and (self.test_type is not None):
                        result = all_patterns_dict.get(self.site, {}).get(self.platform, {}).get(self.test_type, [])
                    else:
                        result = None
                    return result
                except Exception as e:
                    print(f"获取正则表达式时出现错误: {e}")
                    return []

            def get_patterns_v2(self, site=None, platform=None, test_type=None):
                """
                根据指定的测试站点、芯片平台和测试类型，获取对应的正则表达式列表。

                参数:
                site (str): 测试站点名称，例如 'L2AR'。
                platform (str): 芯片平台名称，例如 'MTK'、'Qualcomm' 或 'Generic'。
                test_type (str): 测试类型，如 'Comprehensive Test'、'Calibration'、'Speaker'、'Mic'、'Ear' 等。

                返回:
                list: 匹配的正则表达式列表，如果未找到匹配项则返回空列表。
                """

                def get_platform_dict(site_dict, platform_name):
                    """根据平台名称查找匹配的平台字典"""
                    for key in site_dict:
                        if isinstance(key, tuple) and key[0] == platform_name:
                            return site_dict[key]
                    return {}

                try:

                    mtk_pattern_dict = {
                        TestTypes.COMPREHENSIVE_TEST: MTKPatterns.COMPREHENSIVE_TEST,
                        TestTypes.CALIBRATION: MTKPatterns.CALIBRATION,
                    }

                    qualcomm_pattern_dict = {
                        TestTypes.COMPREHENSIVE_TEST: QualcommPatterns.COMPREHENSIVE_TEST,
                        TestTypes.CALIBRATION: QualcommPatterns.CALIBRATION,
                    }

                    generic_pattern_dict = {
                        TestTypes.SPEAKER: GenericPatterns.SPEAKER_TEST,
                        TestTypes.MIC: GenericPatterns.MIC_TEST,
                        TestTypes.EAR: GenericPatterns.EAR_TEST,
                    }

                    # TODO:在这里添加 L2AR基带的正则表达式表
                    #  key：基带测试项类型
                    #  value：基带测试项正则表达式表。
                    basic_band_dict = {
                        TestTypes.BASIC_BAND: BasicBandPatterns.L2AR_BASIC_BAND
                    }

                    all_patterns_dict = {
                        TestSites.L2AR: {
                            Platforms.MTK: mtk_pattern_dict,
                            Platforms.Qualcomm: qualcomm_pattern_dict,
                            Platforms.GENERIC: generic_pattern_dict,
                            # TODO:L2AR基带的正则表达式表添加到L2AR
                            Platforms.GENERIC_Basic_Band: basic_band_dict
                        }
                    }

                    # 优先使用传入的参数，如果没有则使用实例属性
                    if (site is not None) and (platform is not None) and (test_type is not None):
                        site_dict = all_patterns_dict.get(site, {})
                        platform_dict = get_platform_dict(site_dict, platform)
                        result = platform_dict.get(test_type, [])
                    elif (self.site is not None) and (self.platform is not None) and (self.test_type is not None):
                        site_dict = all_patterns_dict.get(self.site, {})
                        platform_dict = get_platform_dict(site_dict, self.platform)
                        result = platform_dict.get(self.test_type, [])
                    else:
                        result = []
                    return result
                except Exception as e:
                    print(f"获取正则表达式时出现错误: {e}")
                    return []

            def get_patterns_v3(self, site=None, platform=None, test_type=None):
                """
                根据指定的测试站点、芯片平台和测试类型，获取对应的正则表达式列表。

                参数:
                site (str): 测试站点名称，例如 'L2AR'。
                platform (str): 芯片平台名称，例如 'MTK'、'Qualcomm' 或 'Generic'。
                test_type (str): 测试类型，如 'Comprehensive Test'、'Calibration'、'Speaker'、'Mic'、'Ear' 等。

                返回:
                list: 匹配的正则表达式列表，如果未找到匹配项则返回空列表。
                """

                def get_platform_dict(site_dict, platform_name):
                    """根据平台名称查找匹配的平台字典"""
                    for key in site_dict:
                        if isinstance(key, (list, tuple)) and key[0] == platform_name:
                            return site_dict[key]
                    return {}

                try:
                    # 获取当前文件所在目录
                    current_dir = os.path.dirname(__file__)
                    # 向上一级找到项目根目录
                    project_root = os.path.dirname(current_dir)
                    # 拼接得到正确的JSON文件路径
                    json_path = os.path.join(project_root, "config", "clean_filter_data_entity.json")

                    # 读取JSON配置文件
                    with open(json_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)

                    # 从JSON中提取配置
                    patterns = config["Patterns"]
                    platforms = config["Platforms"]
                    test_types = config["TestTypes"]

                    # 构建平台对应的模式字典
                    mtk_pattern_dict = {
                        test_types["COMPREHENSIVE_TEST"]: patterns["MTKPatterns"]["COMPREHENSIVE_TEST"],
                        test_types["CALIBRATION"]: patterns["MTKPatterns"]["CALIBRATION"],
                    }

                    qualcomm_pattern_dict = {
                        test_types["COMPREHENSIVE_TEST"]: patterns["QualcommPatterns"]["COMPREHENSIVE_TEST"],
                        test_types["CALIBRATION"]: patterns["QualcommPatterns"]["CALIBRATION"],
                    }

                    generic_pattern_dict = {
                        test_types["SPEAKER"]: patterns["GenericPatterns"]["SPEAKER_TEST"],
                        test_types["MIC"]: patterns["GenericPatterns"]["MIC_TEST"],
                        test_types["EAR"]: patterns["GenericPatterns"]["EAR_TEST"],
                    }

                    basic_band_dict = {
                        test_types["BASIC_BAND"]: patterns["BasicBandPatterns"]["L2AR_BASIC_BAND"]
                    }

                    # 构建完整的模式映射
                    all_patterns_dict = {
                        config["TestSites"]["L2AR"]: {
                            platforms["MTK"]: mtk_pattern_dict,
                            platforms["Qualcomm"]: qualcomm_pattern_dict,
                            platforms["GENERIC"]: generic_pattern_dict,
                            platforms["GENERIC_Basic_Band"]: basic_band_dict
                        }
                    }

                    # 优先使用传入的参数，如果没有则使用实例属性
                    if (site is not None) and (platform is not None) and (test_type is not None):
                        site_dict = all_patterns_dict.get(site, {})
                        platform_dict = get_platform_dict(site_dict, platform)
                        result = platform_dict.get(test_type, [])
                    elif (self.site is not None) and (self.platform is not None) and (self.test_type is not None):
                        site_dict = all_patterns_dict.get(self.site, {})
                        platform_dict = get_platform_dict(site_dict, self.platform)
                        result = platform_dict.get(self.test_type, [])
                    else:
                        result = []
                    return result
                except FileNotFoundError:
                    print(f"错误：未找到配置文件 {json_path}")
                    return []
                except KeyError as e:
                    print(f"错误：配置文件中缺少必要的键 {e}")
                    return []
                except Exception as e:
                    print(f"获取正则表达式时出现错误: {e}")
                    return []

            def get_patterns(self, site=None, platform=None, test_type=None):
                """
                根据指定的测试站点、芯片平台和测试类型，获取对应的正则表达式列表。

                参数:
                site (str): 测试站点名称，例如 'L2AR'。
                platform (str): 芯片平台名称，例如 'MTK'、'Qualcomm' 或 'Generic'。
                test_type (str): 测试类型，如 'Comprehensive Test'、'Calibration'、'Speaker'、'Mic'、'Ear' 等。

                返回:
                list: 匹配的正则表达式列表，如果未找到匹配项则返回空列表。
                """

                def get_platform_dict(site_dict, platform_name):
                    """根据平台名称查找匹配的平台字典"""
                    # 遍历平台字典，比较平台名称（使用平台标识的第一个元素）
                    for platform_key, platform_value in site_dict.items():
                        if isinstance(platform_key, (list, tuple)) and platform_key[0] == platform_name:
                            return platform_value
                    return {}

                try:
                    # 获取当前文件所在目录
                    current_dir = os.path.dirname(__file__)
                    # 向上一级找到项目根目录
                    project_root = os.path.dirname(current_dir)
                    # 拼接得到正确的JSON文件路径
                    json_path = os.path.join(project_root, "config", "clean_filter_data_entity.json")

                    # 读取JSON配置文件
                    with open(json_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)

                    # 从JSON中提取配置
                    patterns = config["Patterns"]
                    platforms = config["Platforms"]
                    test_types = config["TestTypes"]

                    # 构建平台对应的模式字典
                    mtk_pattern_dict = {
                        test_types["COMPREHENSIVE_TEST"]: patterns["MTKPatterns"]["COMPREHENSIVE_TEST"],
                        test_types["CALIBRATION"]: patterns["MTKPatterns"]["CALIBRATION"],
                    }

                    qualcomm_pattern_dict = {
                        test_types["COMPREHENSIVE_TEST"]: patterns["QualcommPatterns"]["COMPREHENSIVE_TEST"],
                        test_types["CALIBRATION"]: patterns["QualcommPatterns"]["CALIBRATION"],
                    }

                    generic_pattern_dict = {
                        test_types["SPEAKER"]: patterns["GenericPatterns"]["SPEAKER_TEST"],
                        test_types["MIC"]: patterns["GenericPatterns"]["MIC_TEST"],
                        test_types["EAR"]: patterns["GenericPatterns"]["EAR_TEST"],
                    }

                    # TODO：这里添加基带的测试项类型
                    basic_band_dict = {
                        test_types["CAP_SWITCH_TURBO_CHARGER"]: patterns["BasicBandPatterns"]["CAP_SWITCH_TURBO_CHARGER"],
                        test_types["CAPSWTICH_TURBORCHARGE"]: patterns["BasicBandPatterns"]["CAPSWTICH_TURBORCHARGE"],
                        test_types["SPK_INFO_PROGAMMING"]: patterns["BasicBandPatterns"]["SPK_INFO_PROGAMMING"],
                        test_types["BATTERY_LEVELS"]: patterns["BasicBandPatterns"]["BATTERY_LEVELS"],
                        test_types["ANDROID_MAGNETOMETER"]: patterns["BasicBandPatterns"]["ANDROID_MAGNETOMETER"],
                        test_types["QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW"]: patterns["BasicBandPatterns"]["QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW"],
                        test_types["ANT_CAP_SENSOR_ASM_RESULT_SX9375_8CH_YWQ"]: patterns["BasicBandPatterns"]["ANT_CAP_SENSOR_ASM_RESULT_SX9375_8CH_YWQ"],
                        test_types["ONLINE_MODE"]: patterns["BasicBandPatterns"]["ONLINE_MODE"],
                        test_types["INCLINOMETER_MEASURE_A+G"]: patterns["BasicBandPatterns"]["INCLINOMETER_MEASURE_A+G"],
                        test_types["ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS"]: patterns["BasicBandPatterns"]["ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS"]
                    }

                    # 构建完整的模式映射 - 使用元组作为键（元组是可哈希的）
                    all_patterns_dict = {
                        config["TestSites"]["L2AR"]: {
                            tuple(platforms["MTK"]): mtk_pattern_dict,
                            tuple(platforms["Qualcomm"]): qualcomm_pattern_dict,
                            tuple(platforms["GENERIC"]): generic_pattern_dict,
                            tuple(platforms["GENERIC_Basic_Band"]): basic_band_dict
                        }
                    }

                    # 优先使用传入的参数，如果没有则使用实例属性
                    if (site is not None) and (platform is not None) and (test_type is not None):
                        site_dict = all_patterns_dict.get(site, {})
                        platform_dict = get_platform_dict(site_dict, platform)
                        result = platform_dict.get(test_type, [])
                    elif (self.site is not None) and (self.platform is not None) and (self.test_type is not None):
                        site_dict = all_patterns_dict.get(self.site, {})
                        platform_dict = get_platform_dict(site_dict, self.platform)
                        result = platform_dict.get(self.test_type, [])
                    else:
                        result = []
                    return result
                except FileNotFoundError:
                    print(f"错误：未找到配置文件 {json_path}")
                    return []
                except KeyError as e:
                    print(f"错误：配置文件中缺少必要的键 {e}")
                    return []
                except Exception as e:
                    print(f"获取正则表达式时出现错误: {e}")
                    return []

            def remove_timestamp2log_level(self, input_file, output_file):
                # 定义正则表达式：匹配并删除时间戳、日志级别、测试模块及后续时间戳
                # 模式说明：
                # ^ 从行首开始匹配
                # 第一部分：匹配时间戳1（如：2025-01-19 19:41:47,170）-> (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)
                # 第二部分：匹配日志级别（如：[] INFO ）-> \s+\[]\s+
                # 第三部分：匹配测试模块（如：TEST_APP_2010）-> \w+\s+
                # 第四部分：匹配后续时间戳（如：09:33:27.4305803），确保删除到第二个制表符后 -> (\d{2}:\d{2}:\d{2}.\d+)
                # 第五部分：匹配制表符，确保删除到具体内容前的最后一个制表符 -> \t
                pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+\[]\s+\w+\s+[^\t]+\t(\d{2}:\d{2}:\d{2}.\d+)\t'
                try:
                    # 使用utf-8编码并忽略解码错误
                    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f_in, \
                            open(output_file, 'w', encoding='utf-8') as f_out:
                        for line in f_in:
                            # 使用正则表达式删除匹配部分，保留剩余内容（从第三个制表符后开始保留）
                            processed_line = re.sub(pattern, '', line.strip())
                            if processed_line:  # 跳过空行
                                f_out.write(processed_line + '\n')
                    return True
                except FileNotFoundError:
                    print(f"error：文件未找到。请检查输入文件 '{input_file}' 是否存在。")
                except UnicodeDecodeError:
                    print(f"error：在读取文件 '{input_file}' 时出现编码问题。")
                    # 尝试使用其他编码
                    try:
                        with open(input_file, 'r', encoding='gb18030', errors='ignore') as f_in, \
                                open(output_file, 'w', encoding='utf-8') as f_out:
                            for line in f_in:
                                processed_line = re.sub(pattern, '', line.strip())
                                if processed_line:
                                    f_out.write(processed_line + '\n')
                        print("已成功使用gb18030编码处理文件。")
                        return True
                    except Exception as e:
                        print(f"无法使用其他编码处理文件：{e}")
                except Exception as e:
                    print(f"发生未知错误：{e}")
                return False

            def remove_timestamp2log_level_V1(self, input_file, output_file):
                # 定义正则表达式：匹配并删除时间戳、日志级别、测试模块及后续时间戳
                # 模式说明：
                # ^ 从行首开始匹配
                # 第一部分：匹配时间戳1（如：2025-01-19 19:41:47,170）-> (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)
                # 第二部分：匹配日志级别（如：[] INFO ）-> \s+\[]\s+
                # 第三部分：匹配测试模块（如：TEST_APP_2010）-> \w+\s+
                # 第四部分：匹配后续时间戳（如：09:33:27.4305803），确保删除到第二个制表符后 -> (\d{2}:\d{2}:\d{2}.\d+)
                # 第五部分：匹配制表符，确保删除到具体内容前的最后一个制表符 -> \t
                pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\s+\[]\s+\w+\s+[^\t]+\t(\d{2}:\d{2}:\d{2}.\d+)\t'
                try:
                    with open(input_file, 'r', encoding='gbk') as f_in, open(output_file, 'w', encoding='gbk') as f_out:
                        for line in f_in:
                            # 使用正则表达式删除匹配部分，保留剩余内容（从第三个制表符后开始保留）
                            processed_line = re.sub(pattern, '', line.strip())
                            if processed_line:  # 跳过空行
                                f_out.write(processed_line + '\n')
                    return True
                except FileNotFoundError:
                    print(f"error：文件未找到。请检查输入文件 '{input_file}' 是否存在。")
                except UnicodeDecodeError:
                    print(f"error：在读取文件 '{input_file}' 时出现编码问题，请检查文件编码是否为 'gbk'。")
                except Exception as e:
                    print(f"发生未知错误：{e}")
                return False

            def group_log_file_content(self, file_path, input_patterns):
                """
                此函数用于读取指定文件中的日志内容，
                使用预定义的正则表达式匹配符合条件的行，
                并将匹配到的行按照正则表达式和每行的键进行分组。

                参数:
                file_path (str): 要读取的日志文件的路径

                返回:
                dict: 分组后的字典，键为正则表达式，值为按键分组的行
                """
                # 尝试读取指定文件的内容，并按行分割成列表
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = file.read().splitlines()
                except FileNotFoundError:
                    # 若文件未找到，打印错误信息并返回 None
                    print(f"文件 {file_path} 未找到，请检查文件路径。")
                    return None

                # 定义一系列正则表达式，用于匹配文件中的特定行
                patterns = input_patterns

                # 用于存储每个正则表达式匹配到的行，键为正则表达式，值为匹配到的行列表
                matched_lines_dict = {}
                for pattern in patterns:
                    # 存储当前正则表达式匹配到的行
                    matched_lines = []
                    for line in data:
                        try:
                            # 检查当前行是否与正则表达式匹配
                            if re.match(pattern, line):
                                # 若匹配成功，将该行添加到匹配列表中
                                matched_lines.append(line)
                        except Exception as e:
                            # 若匹配过程中出现异常，打印异常信息
                            print(f"匹配模式 {pattern} 时出现异常: {e}")
                    # 将当前正则表达式及其匹配到的行列表存储到字典中
                    matched_lines_dict[pattern] = matched_lines

                # 用于存储最终分组后的结果，键为正则表达式，值为按键分组的行
                new_grouped_dict = {}
                try:
                    for pattern, lines in matched_lines_dict.items():
                        # 存储当前正则表达式匹配到的行按键分组的结果
                        pattern_grouped_dict = {}
                        for line in lines:
                            try:
                                # 按制表符分割当前行，最多分割一次
                                parts = line.split('\t', 1)
                                if len(parts) > 1:
                                    # 若分割后有两个部分，分别作为键和值
                                    key, value = parts
                                else:
                                    # 若分割后只有一个部分，将其作为键，值为空字符串
                                    key, value = parts[0], ''
                                if key not in pattern_grouped_dict:
                                    # 若键不在字典中，初始化一个空列表
                                    pattern_grouped_dict[key] = []
                                # 将值添加到对应键的列表中
                                pattern_grouped_dict[key].append(value)
                            except Exception as e:
                                # 若处理行时出现异常，打印异常信息
                                print(f"处理模式 {pattern} 下的行 {line} 时出现异常: {e}")
                        # 将当前正则表达式及其分组后的结果存储到最终字典中
                        new_grouped_dict[pattern] = pattern_grouped_dict
                except Exception as e:
                    # 若构建新分组字典时出现异常，打印异常信息并返回 None
                    print(f"构建新分组字典时出现异常: {e}")
                    return None

                # 返回正则表达式列表和最终分组后的字典
                return patterns, new_grouped_dict

            def extract_file_info(self, filter_results):
                """
                该函数用于从 filter_results 对象中提取第一个文件的相关信息。
                包括文件所在目录、文件名、文件扩展名以及不带扩展名的文件名。

                参数:
                filter_results (object): 包含 filtered_files 属性的对象，filtered_files 是一个文件路径列表。

                返回:
                tuple: 包含文件目录、文件名、文件扩展名和不带扩展名的文件名的元组。
                       如果过程中出现异常，则返回 None。
                """
                try:
                    # 尝试获取 filter_results 对象的 filtered_files 属性中的第一个文件路径
                    # 若 filtered_files 列表为空或者 filter_results 没有该属性，会触发异常
                    file_path = filter_results
                    # 获取文件所在的目录
                    file_dir = os.path.dirname(file_path)
                    # 获取完整的文件名
                    file_name = os.path.basename(file_path)
                    # 获取文件的扩展名
                    file_ext = os.path.splitext(file_name)[1]
                    # 获取不带扩展名的文件名
                    file_name_without_ext = os.path.splitext(file_name)[0]
                    return file_path, file_dir, file_name, file_ext, file_name_without_ext
                except AttributeError:
                    # 当 filter_results 对象没有 filtered_files 属性时触发此异常
                    print("错误: 传入的对象没有 'filtered_files' 属性。")
                except IndexError:
                    # 当 filtered_files 列表为空时触发此异常
                    print("错误: 'filtered_files' 列表为空。")
                except Exception as e:
                    # 捕获其他未知异常
                    print(f"发生未知错误: {e}")
                return None

            # TODO:在这里添加过滤测试项中需要分析的log函数
            def get_mtk_meta_trackid_read_from_md_nvram_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存tx_radiated_calibrate信息的容器
                    tx_radiated_calibrate = []

                    for data_item in target_data:
                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            exception_error_container,
                            tx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], ''

            def get_basic_band_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出包含指定关键词的日志数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 eval_and_log_results_container 和 exception_error_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 初始化结果容器，添加默认标识
                    eval_and_log_results_container = ["# EvalAndLogResults 数据"]
                    # 保存Exception error信息的容器
                    exception_error_container = ["# Exception error 数据"]

                    for data_item in target_data:
                        # 过滤包含"EvalAndLogResults"的日志
                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)

                        # 过滤包含"Exception error"的日志
                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                    # 打印过滤结果
                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    print("\n包含 'Exception error' 的数据:")
                    for item in exception_error_container:
                        print(item)

                    # 创建指定文件夹（保持与原函数一致的路径处理）
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                # 返回过滤后的结果容器
                return eval_and_log_results_container, exception_error_container, folder_path

            def parse_eval_and_log_results_for_basic_band(self, eval_and_log_results_container):
                """
                过滤出包含PASSED或* FAILED *的结果，并转换为字典

                参数:
                    eval_and_log_results_container (list): 包含EvalAndLogResults信息的列表

                返回:
                    dict: 处理后的结果字典，键为序号，值为对应的结果信息
                """
                # 存储过滤后的结果
                filtered_results = []

                # 过滤包含PASSED或* FAILED *的内容
                for item in eval_and_log_results_container:
                    # 跳过标题行
                    if item.startswith('#'):
                        continue

                    # 检查是否包含目标关键词
                    if "PASSED" in item or "* FAILED *" in item:
                        filtered_results.append(item)

                # 将列表转换为字典，键为序号（从1开始）
                result_dict = {
                    f"result_{i + 1}": item
                    for i, item in enumerate(filtered_results)
                }

                return result_dict

            def process_eval_and_log_results_for_basic_band2(self, eval_and_log_results_container):
                """
                过滤出包含PASSED或* FAILED *的结果，保留列表形式

                参数:
                    eval_and_log_results_container (list): 包含EvalAndLogResults信息的列表

                返回:
                    list: 过滤后的结果列表
                """
                # 存储过滤后的结果
                filtered_results = []

                # 过滤包含PASSED或* FAILED *的内容
                for item in eval_and_log_results_container:
                    # 跳过标题行
                    if item.startswith('#'):
                        continue

                    # 检查是否包含目标关键词
                    if "PASSED" in item or "* FAILED *" in item:
                        filtered_results.append(item)

                return filtered_results

            def get_wifi_tx_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """

                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存异常错误的容器
                    exception_error_container = []
                    for data_item in target_data:
                        if 'Measure Process	TX_POWER Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	TX_POWER measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            exception_error_container,
                            folder_path)
                else:
                    return [], [], [], [], ''

            def get_wifi_tx_cal_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存tx_radiated_calibrate信息的容器
                    tx_radiated_calibrate = []

                    for data_item in target_data:
                        if 'Measure Process	TX_POWER Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	TX_POWER measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "TX Radiated Calibrate" in data_item:
                            tx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            exception_error_container,
                            tx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], ''

            def get_wifi_rx_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []

                    for data_item in target_data:
                        if 'Measure Process	SIGNAL_LEVEL Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	SIGNAL_LEVEL measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            exception_error_container,
                            folder_path)
                else:
                    return [], [], [], [], ''

            def get_wifi_rx_cal_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存rx_radiated_calibrate信息的容器
                    rx_radiated_calibrate = []

                    for data_item in target_data:
                        if 'Measure Process	SIGNAL_LEVEL Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	SIGNAL_LEVEL measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "RX Radiated Calibrate" in data_item:
                            rx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            exception_error_container,
                            rx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], ''

            def get_gps_rx_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存tx_radiated_calibrate信息的容器
                    rx_radiated_calibrate = []

                    for data_item in target_data:
                        if 'Measure Process	SIGNAL_LEVEL Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	SIGNAL_LEVEL measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "RX Radiated Calibrate" in data_item:
                            rx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            exception_error_container,
                            rx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], ''

            def get_bluetooth_tx_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存tx_radiated_calibrate信息的容器
                    tx_radiated_calibrate = []

                    for data_item in target_data:
                        if 'Measure Process	TX_POWER Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	TX_POWER measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "TX Radiated Calibrate" in data_item:
                            tx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            exception_error_container,
                            tx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], ''

            def get_lte_tx_log_info_v1(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存route信息的容器
                    route_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存tx_radiated_calibrate信息的容器
                    tx_radiated_calibrate = []
                    for data_item in target_data:
                        if 'Measure Process	TX_POWER Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	TX_POWER measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if 'MTKtxRouteConfigFile' in data_item or 'Radiated TX	use route' in data_item:
                            route_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "TX Radiated Calibrate" in data_item:
                            tx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                        return (test_process_container,
                                eval_and_log_results_container,
                                satisifed_container,
                                route_container,
                                exception_error_container,
                                tx_radiated_calibrate,
                                folder_path)
                else:
                    return [], [], [], [], [], [], ''

            def get_lte_tx_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据，包含乱码处理

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含各类容器和文件夹路径的元组
                """

                # 辅助函数：检测字符串是否包含乱码
                def is_garbled(s):
                    try:
                        # 尝试UTF-8编码解码，检测不可正常解析的字符
                        s.encode('utf-8').decode('utf-8')
                        # 检查是否包含过多非打印字符（可能是乱码）
                        non_printable = sum(1 for c in s if not c.isprintable())
                        return non_printable / len(s) > 0.3 if s else False
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        return True

                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 初始化各类容器并添加默认标识
                    test_process_container = ["# test_process"]
                    eval_and_log_results_container = ["# test_result"]
                    satisifed_container = []
                    route_container = []
                    exception_error_container = []
                    tx_radiated_calibrate = []

                    for data_item in target_data:
                        # 处理乱码：如果检测到乱码则替换为默认值
                        if is_garbled(str(data_item)):
                            processed_item = "The content is garbled."
                        else:
                            processed_item = data_item

                        # 根据内容分类存储
                        if 'Measure Process	TX_POWER Reading' in processed_item or 'Final measurement' in processed_item:
                            test_process_container.append(processed_item)

                        if "EvalAndLogResults" in processed_item:
                            eval_and_log_results_container.append(processed_item)

                        if "Measure Process	TX_POWER measure process is complete because measurement criteria has been satisifed." in processed_item:
                            satisifed_container.append(processed_item)

                        if 'MTKtxRouteConfigFile' in processed_item or 'Radiated TX	use route' in processed_item:
                            route_container.append(processed_item)

                        if "Exception error" in processed_item:
                            exception_error_container.append(processed_item)

                        if "TX Radiated Calibrate" in processed_item:
                            tx_radiated_calibrate.append(processed_item)

                    # 打印处理后的结果
                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 创建文件夹（跨平台处理）
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'

                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 写入文件（跨平台路径处理）
                    if os.name == 'nt':
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:
                        output_file_path = f'{folder_path}/{key}.txt'

                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            route_container,
                            exception_error_container,
                            tx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], [], ''

            def get_lte_rx_log_info(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存route信息的容器
                    route_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存rx_radiated_calibrate信息的容器
                    rx_radiated_calibrate = []
                    for data_item in target_data:
                        if 'Measure Process	SIGNAL_LEVEL Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	SIGNAL_LEVEL measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if 'MTKrxRouteConfigFile' in data_item or 'Radiated RX	use route' in data_item:
                            route_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "RX Radiated Calibrate" in data_item:
                            rx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            route_container,
                            exception_error_container,
                            rx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], [], ''

            def get_ns_rx_log_info_for_mtk(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存route信息的容器
                    route_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存rx_radiated_calibrate信息的容器
                    rx_radiated_calibrate = []
                    for data_item in target_data:
                        if 'Measure Process	SIGNAL_LEVEL Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	SIGNAL_LEVEL measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if 'MTKrxRouteConfigFile' in data_item or 'Radiated RX	use route' in data_item:
                            route_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "RX Radiated Calibrate" in data_item:
                            rx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            route_container,
                            exception_error_container,
                            rx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], [], ''

            def get_ns_rx_log_info_for_qc(self, key, values, file_dir):
                """
                从分组后的数据中，过滤出测试过程数据和测试结果数据

                参数:
                key (dict): 组名
                values (list): 组内数据
                file_dir（str）：过滤文件目录

                返回:
                tuple: 包含 test_process_container、eval_and_log_results_container 和 satisifed_container 的元组
                """
                folder_path = ''
                output_file_path = ''

                if key:
                    target_data = values
                    # 添加默认值 "# test_process"
                    test_process_container = ["# test_process"]
                    # 添加默认值 "# test_result"
                    eval_and_log_results_container = ["# test_result"]
                    # 保存当前测试结果是否稳定的容器
                    satisifed_container = []
                    # 保存route信息的容器
                    route_container = []
                    # 保存Exception error信息的容器
                    exception_error_container = []
                    # 保存rx_radiated_calibrate信息的容器
                    rx_radiated_calibrate = []
                    for data_item in target_data:
                        if 'Measure Process	SIGNAL_LEVEL Reading' in data_item or 'Final measurement' in data_item:
                            test_process_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "EvalAndLogResults" in data_item:
                            eval_and_log_results_container.append(data_item)  # 保存包含 "EvalAndLogResults" 的数据项

                        if "Measure Process	SIGNAL_LEVEL measure process is complete because measurement criteria has been satisifed." in data_item:
                            satisifed_container.append(data_item)

                        if 'MTKrxRouteConfigFile' in data_item or 'Radiated RX	use route' in data_item:
                            route_container.append(data_item)  # 保存包含 "test_process 和 Final" 的数据项

                        if "Exception error" in data_item:
                            exception_error_container.append(data_item)

                        if "RX Radiated Calibrate" in data_item:
                            rx_radiated_calibrate.append(data_item)

                    print("\n包含 'Measure Process' 的数据:")
                    for item in test_process_container:
                        print(item)

                    print("\n包含 'EvalAndLogResults' 的数据:")
                    for item in eval_and_log_results_container:
                        print(item)

                    # 新增：创建指定文件夹
                    if os.name == 'nt':  # Windows系统
                        folder_path = f'{file_dir}\\{key}'
                    else:  # Linux/Unix系统
                        folder_path = f'{file_dir}/{key}'
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"文件夹 {folder_path} 创建成功。")
                    else:
                        print(f"文件夹 {folder_path} 已存在。")

                    # 4 - 1.将 test_process_container、eval_and_log_results_container 写入文件
                    # 添加操作系统检查
                    if os.name == 'nt':  # Windows系统
                        output_file_path = f'{folder_path}\\{key}.txt'
                    else:  # Linux/Unix系统
                        output_file_path = f'{folder_path}/{key}.txt'
                    with open(output_file_path, 'w', encoding='gbk', errors='replace') as output_file:
                        for item in test_process_container:
                            output_file.write(item + '\n')
                        for item in eval_and_log_results_container:
                            output_file.write(item + '\n')

                    return (test_process_container,
                            eval_and_log_results_container,
                            satisifed_container,
                            route_container,
                            exception_error_container,
                            rx_radiated_calibrate,
                            folder_path)
                else:
                    return [], [], [], [], [], [], ''

            def get_lte_route_info(self, route_container, target_str='MTK_MMRF_LTE_BC05_TX_20DB_V7_MCH20525'):
                result = {}
                # target_str = 'MTK_MMRF_LTE_BC05_TX_20DB_V7_MCH20525'
                for item in route_container:
                    if '=' in item:
                        key, value = item.split('=', 1)
                        key = key.replace(target_str, '').replace(' ', '').replace('\t', ' ').strip()
                        result[key] = value.strip()
                    elif ':' in item:
                        key, value = item.split(':', 1)
                        key = key.replace(target_str, '').replace(' ', '').replace('\t', ' ').strip()
                        result[key] = value.strip()
                return result

            def get_lte_rx_cal_exception_info(self, exception_error_container):
                if exception_error_container and len(exception_error_container) > 1:
                    try:
                        # 获取最后一个元素
                        last_element = exception_error_container[-1]
                        # 按 '\t' 分割元素内容
                        split_elements = last_element.split('\t')
                        # 去除空格
                        result = [element.strip() for element in split_elements]
                        if len(result) >= 2:
                            key = result[0]
                            value = result[1]
                            return True, {"Exception error": {key: value}}
                        else:
                            return False, {"Exception error": {}}
                    except IndexError:
                        return False, {"Exception error": {}}
                return False, {"Exception error": {}}

            def get_lte_rx_cal_exception_info2(self, lines):
                """
                 该函数用于将输入的字符串列表转换为特定格式的字典列表。
                 每行字符串代表一条错误信息，包含错误代码名称、错误代码、详细信息和建议。

                 参数:
                 lines (list): 包含错误信息的字符串列表

                 返回:
                 list: 包含转换后字典的列表，每个字典代表一条错误信息
                 """
                # 用于存储最终的字典列表，每个字典代表一条完整的错误信息
                result = []
                # 用于存储当前正在处理的错误信息的字典
                current_dict = {}
                # 用于存储当前错误信息的详细内容的字典
                details = {}
                # 标记是否处于处理详细信息部分的标志
                in_details = False
                # 用于临时存储详细信息部分的每一行内容
                details_lines = []
                # 用于临时存储清理后的异常信息的列表
                cleaned_lines = self.remove_lte_rx_cal_exception_error(lines)

                try:
                    # 遍历输入的每一行字符串
                    for line in cleaned_lines:
                        # 去除行首尾的空白字符
                        line = line.strip()
                        # 如果当前行以 "Error code name:" 开头，说明开始一个新的错误信息
                        if line.startswith("Error code name:"):
                            # 如果 current_dict 不为空，说明之前已经处理了一条完整的错误信息
                            if current_dict:
                                # 如果 details_lines 不为空，说明有详细信息内容
                                if details_lines:
                                    # 将详细信息的第一行内容作为 info 键的值
                                    details["info"] = details_lines[0]
                                    # 将详细信息的最后一行内容作为 Suggestion 键的值
                                    details["Suggestion"] = details_lines[-1]
                                    # 遍历详细信息的中间行，将包含 "=" 的行拆分为键值对添加到 details 字典
                                    for detail_line in details_lines[1:-1]:
                                        if "=" in detail_line:
                                            key, value = detail_line.split("=", 1)
                                            details[key.strip()] = value.strip()
                                    # 将处理好的详细信息字典添加到当前错误信息字典中
                                    current_dict["Details"] = details
                                # 将当前错误信息字典添加到结果列表中
                                result.append(current_dict)
                            # 重置 current_dict 为一个新的空字典，准备处理下一条错误信息
                            current_dict = {}
                            # 提取当前行中 "Error code name:" 后面的内容作为错误代码名称
                            current_dict["Error code name"] = line.split(": ")[1]
                            # 重置 details 字典为空
                            details = {}
                            # 重置 details_lines 列表为空
                            details_lines = []
                            # 标记当前不处于处理详细信息部分
                            in_details = False
                        # 如果当前行以 "Error code:" 开头
                        elif line.startswith("Error code:"):
                            # 提取当前行中 "Error code:" 后面的内容作为错误代码
                            current_dict["Error code"] = line.split(": ")[1]
                        # 如果当前行以 "Details:" 开头，说明开始处理详细信息部分
                        elif line.startswith("Details:"):
                            # 标记当前处于处理详细信息部分
                            in_details = True
                        # 如果当前处于处理详细信息部分且当前行不为空
                        elif in_details:
                            if line:
                                # 将当前行添加到 details_lines 列表中
                                details_lines.append(line)
                        # 如果当前行包含 "Calibration factors" 且不为空
                        elif line and "Calibration factors" in line:
                            # 将当前行作为建议信息添加到当前错误信息字典中
                            current_dict["Suggestion"] = line

                    # 处理最后一个 current_dict，避免最后一条错误信息未添加到结果列表
                    if current_dict:
                        if details_lines:
                            details["info"] = details_lines[0]
                            details["Suggestion"] = details_lines[-1]
                            for detail_line in details_lines[1:-1]:
                                if "=" in detail_line:
                                    key, value = detail_line.split("=", 1)
                                    details[key.strip()] = value.strip()
                            current_dict["Details"] = details
                        result.append(current_dict)

                    return result
                except IndexError:
                    print("错误：解析行时出现索引错误，请检查输入格式。")
                except ValueError:
                    print("错误：解析行时出现值错误，请检查输入格式。")
                except Exception as e:
                    print(f"未知错误: {e}")

            def remove_lte_rx_cal_exception_error(self, lines):
                """
                去掉每行字符串中的 'Exception error' 部分
                """
                return [line.replace("Exception error\t", "").replace("Exception error", "").strip() for line in lines]

            def parse_lte_rx_cal_exception_error_dict_to_string(self, exception_error_container_parse):
                if not exception_error_container_parse:
                    return ""
                last_dict = exception_error_container_parse[-1]
                result = []
                for key, value in last_dict.items():
                    result.append(f"{key};{value}")
                return '.'.join(result)

            def parse_test_result(self, test_result_container):
                """
                格式化测试结果数据

                参数:
                test_result_container (list): 测试结果容器

                返回:
                dict: 包含 parsed_test_result_container
                """

                # parsed_test_result_container_temp = {}
                parsed_test_result_container = {}
                # test_item = ""
                # low_limit = 0.0
                # up_limit = 0.0
                # test_data = 0.0
                # unit = ""
                # state = ""
                if len(test_result_container) > 1:  # 因为有默认值，所以判断长度大于1
                    first_item = test_result_container[1]  # 跳过默认值
                    print(f"\n【解析第一项】原始数据: {first_item}")

                    # 1. 按制表符切分数据
                    try:
                        fields = first_item.split('\t')
                        print(f"切分后字段数量: {len(fields)} 个")
                    except AttributeError:
                        print("错误: 第一项非字符串类型，无法切分")
                        return None

                    # 2. 验证字段数量是否足够（至少需要12个字段，索引0-11）
                    required_indices = {3, 4, 5, 6, 7, 10}  # 0-based索引
                    if len(fields) < max(required_indices) + 1:
                        print(f"警告: 字段数量不足（需要至少{max(required_indices) + 1}个，实际{len(fields)}个）")
                        missing = max(required_indices) + 1 - len(fields)
                        fields += ['N/A'] * missing  # 补全缺失字段

                    # 3. 提取目标字段（使用字典存储，键为"字段X"）
                    extracted = {
                        f"字段{idx + 1}": fields[idx].strip()  # 转换为1-based序号
                        for idx in required_indices
                    }

                    # 修改字段名
                    field_mapping = {
                        "字段4": "test_item",
                        "字段5": "low_limit",
                        "字段6": "up_limit",
                        "字段7": "test_data",
                        "字段8": "unit",
                        "字段11": "state"
                    }
                    new_extracted = {}
                    for key, value in extracted.items():
                        new_key = field_mapping.get(key, key)
                        new_extracted[new_key] = value
                    extracted = new_extracted

                    # 4. 格式化输出（带字段说明）
                    print("\n【提取结果】:")
                    for key, value in extracted.items():
                        print(f"{key}: {value if value else '[空值]'}")

                    # 5. 保存到新容器（示例：列表 of 字典）
                    parsed_test_result_container_temp = [extracted]
                    print(f"\n已保存到 parsed_container: {parsed_test_result_container_temp}")

                    # 提取 parsed_container 的数据
                    test_item = parsed_test_result_container_temp[0].get('test_item', "N/A")
                    low_limit = float(parsed_test_result_container_temp[0].get('low_limit', "N/A"))
                    up_limit = float(parsed_test_result_container_temp[0].get('up_limit', "N/A"))
                    test_data = float(parsed_test_result_container_temp[0].get('test_data', "N/A"))
                    unit = parsed_test_result_container_temp[0].get('unit', "N/A")

                    if 'FAILED' in parsed_test_result_container_temp[0].get('state', 'N/A'):
                        # 过滤 ' ' 和 '*'
                        parsed_test_result_container_temp[0]['state'] = (
                            parsed_test_result_container_temp[0]['state'].replace(' ', '').replace('*', ''))

                    state = parsed_test_result_container_temp[0].get('state', "N/A")
                    # "意义": "确保设备发射功率在合规范围内，避免干扰或信号弱。",
                    meaning = ''
                    # "指标": "发射端实际功率（dBm）",
                    indicator = ''
                    # "趋势分析": "值集中在中位区（稳定）",
                    trend_analysis = ''
                    # "隐含问题可能性": "低",
                    implied_problem_possibility = ''
                    # 图片名称
                    chart_name = ''
                    # 图片内容(base64)
                    chart_content = ''

                    parsed_test_result_container = {
                        'test_item': test_item,
                        'low_limit': low_limit,
                        'up_limit': up_limit,
                        'test_data': test_data,
                        'unit': unit,
                        'state': state,
                        'meaning': meaning,
                        'indicator': indicator,
                        'trend_analysis': trend_analysis,
                        'implied_problem_possibility': implied_problem_possibility,
                        'chart_name': chart_name,
                        'chart_content': chart_content
                    }

                else:
                    print("警告: eval_and_log_results_container 为空，无数据可解析")

                return parsed_test_result_container

            def parse_test_result_for_basic_band(self, test_result_dict):
                """
                解析基础频段的测试结果字典，提取关键信息并格式化

                参数:
                    test_result_dict (dict): 包含测试结果的字典，键为'result_1'等，值为测试结果字符串

                返回:
                    dict: 包含解析后的测试结果字典，键为原结果键名，值为包含详细信息的字典
                """
                parsed_test_result_container = {}  # 初始化字典用于存储结果

                # 遍历字典中的每个测试结果
                for result_key, result_value in test_result_dict.items():
                    # 按字符串按制表符切分
                    try:
                        fields = result_value.split('\t')
                        print(f"\n【解析{result_key}】原始数据: {result_value}")
                        print(f"切分后字段数量: {len(fields)} 个")
                    except AttributeError:
                        print(f"错误: {result_key}非字符串类型，无法切分")
                        continue

                    # 验证并补全必要字段（至少需要11个字段，索引0-10）
                    required_indices = {3, 4, 5, 6, 7, 10}  # 关键信息所在索引
                    if len(fields) < max(required_indices) + 1:
                        print(f"警告: 字段数量不足（需要至少{max(required_indices) + 1}个，实际{len(fields)}个）")
                        missing = max(required_indices) + 1 - len(fields)
                        fields += ['N/A'] * missing  # 补全缺失字段

                    # 提取关键字段并映射为有意义的名称
                    extracted = {
                        "test_item": fields[3].strip(),  # 测试项目名称
                        "low_limit": fields[4].strip(),  # 下限值
                        "up_limit": fields[5].strip(),  # 上限值
                        "test_data": fields[6].strip(),  # 测试数据
                        "unit": fields[7].strip(),  # 单位
                        "state": fields[10].strip()  # 测试状态（PASSED/FAILED）
                    }

                    # 格式化测试状态（去除*和空格）
                    if extracted["state"]:
                        extracted["state"] = extracted["state"].replace('*', '').replace(' ', '')

                    # 转换数值类型（异常处理）
                    try:
                        extracted["low_limit"] = float(extracted["low_limit"]) if extracted["low_limit"] else None
                        extracted["up_limit"] = float(extracted["up_limit"]) if extracted["up_limit"] else None
                        extracted["test_data"] = float(extracted["test_data"]) if extracted["test_data"] else None
                    except ValueError:
                        print(f"警告: {result_key}中数值转换失败，保留原始字符串")

                    # 添加额外分析字段
                    extracted.update({
                        "meaning": "",  # 可后续补充测试意义说明
                        "indicator": "",  # 可后续补充指标说明
                        "trend_analysis": "",  # 可后续补充趋势分析
                        "implied_problem_possibility": "",  # 可后续补充问题可能性
                        "chart_name": "",  # 可后续补充图表名称
                        "chart_content": ""  # 可后续补充图表内容
                    })

                    # 打印提取结果
                    print(f"【{result_key}提取结果】:")
                    for key, value in extracted.items():
                        print(f"{key}: {value if value is not None else '[空值]'}")

                    # 将提取的结果添加到字典，使用原键名作为键
                    parsed_test_result_container[result_key] = extracted

                return parsed_test_result_container

            def parse_test_process(self, test_process_container, parsed_eval_and_log_results_container, folder_path):
                parsed_test_process_container = {}  # 最终存储容器
                final_line_processed = False  # 标记最后一行是否处理

                # 跳过第一行的 "# test_process"
                lines = test_process_container[1:]
                if not lines:  # 空列表处理
                    print("警告：test_process_container 为空，无数据可解析")
                    return None

                final_line = lines[-1] if lines else ''  # 提取最后一行

                for idx, line in enumerate(lines):
                    if idx == len(lines) - 1 and line:  # 仅处理非空最后一行
                        # 先按": "分割，再处理value中的前缀
                        if ': ' in final_line:
                            key, raw_value = final_line.split(': ', 1)  # 仅分割第一个冒号
                            # 执行value替换（无论key是什么）
                            processed_value = raw_value.replace('Final measurement = ', '')
                            # 空值处理（替换后全为空的情况）
                            parsed_test_process_container[key.strip()] = processed_value.strip() or '-9999.99'
                        else:
                            # 无法分割时：key为整行，value使用默认值
                            parsed_test_process_container[final_line.strip()] = '-9999.99'
                        final_line_processed = True
                    else:
                        # 优先使用": "分割，回退制表符
                        if ': ' in line:
                            key, value = line.split(': ', 1)  # 只分割一次
                        else:
                            parts = line.split('\t', 1)  # 兼容原始制表符分隔
                            key = parts[0].strip()
                            value = parts[1].strip() if len(parts) > 1 else None
                        parsed_test_process_container[key] = value

                # 处理最后一行无Final前缀的情况（如果前面未处理）
                if not final_line_processed and lines:
                    parsed_test_process_container[lines[-1]] = None

                # 4-3-1.------------------- test_process_container的数据验证 -------------------
                print("\n结构化数据容器:")
                for k, v in parsed_test_process_container.items():
                    print(f"{k} → {v if v is not None else '[原始行]'}")

                # 4-4.将parsed_test_process_container和parsed_eval_and_log_results_container，先格式化，后写入文件。
                # 1. 在parsed_test_process_container的下标0处插入key="name"和value="test_process"
                new_dict = {"title_name": "test_process"}
                new_dict.update(parsed_test_process_container)
                parsed_test_process_container = new_dict

                # 2. 在parsed_eval_and_log_results_container的头部插入独立的name字段（保持原有数据完整性）
                if isinstance(parsed_eval_and_log_results_container, list):
                    if parsed_eval_and_log_results_container:
                        # 创建独立的头部标识（不影响原有元素）
                        header = {"title_name": "test_result"}
                        # 插入到列表头部（原数据后移）
                        parsed_eval_and_log_results_container.insert(0, header)
                    else:
                        # 空列表处理（保持代码健壮性）
                        parsed_eval_and_log_results_container = [{"title_name": "test_result"}]
                elif isinstance(parsed_eval_and_log_results_container, dict):
                    new_dict = {"title_name": "test_result"}
                    new_dict.update(parsed_eval_and_log_results_container)
                    parsed_eval_and_log_results_container = new_dict

                # 3. write them in file, they are parsed_test_process_container and parsed_eval_and_log_results_container.
                test_item = parsed_eval_and_log_results_container.get("test_item", "N/A") if isinstance(
                    parsed_eval_and_log_results_container, dict) else parsed_eval_and_log_results_container[0].get(
                    "test_item", "N/A")
                if os.name == 'nt':  # Windows OS
                    output_file_path_new = f'{folder_path}\\{test_item}_parsed_data.txt'
                else:  # Linux OS
                    output_file_path_new = f'{folder_path}/{test_item}_parsed_data.txt'

                try:
                    with open(output_file_path_new, 'w', encoding='gbk') as output_file_new:
                        for key, value in parsed_test_process_container.items():
                            output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                        if isinstance(parsed_eval_and_log_results_container, list):
                            for item in parsed_eval_and_log_results_container:
                                for key, value in item.items():
                                    output_file_new.write(f"{key}: {value}\n")
                        elif isinstance(parsed_eval_and_log_results_container, dict):
                            for key, value in parsed_eval_and_log_results_container.items():
                                output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                except Exception as e:
                    print(f"写入文件时出错: {e}")

                return parsed_test_process_container, parsed_eval_and_log_results_container

            def parse_judge_value_range(self, values, low_limit, up_limit, top_percentage_limit=0.5, language='zh'):
                """
                代码说明：
                judge_value_range 函数：
                首先，按照原逻辑对每个值进行判定，得到判定结果列表 results。
                接着，统计每种判定结果的数量，存储在 counts 字典中。
                然后，对 counts 字典按数量降序排序。
                若占比最高的判定结果占比超过 50%，则返回该判定结果；否则，返回所有非 “无效数据” 且数量大于 0 的判定结果，用逗号连接。
                主程序部分：调用 judge_value_range 函数得到数据方位并打印。
                """

                # 中英文对照字典
                translation_dict = {
                    "无效数据": "Invalid data",
                    "指标范围外偏下": "Below the lower limit",
                    "指标范围外偏上": "Above the upper limit",
                    "指标范围内偏下": "Lower within the limit",
                    "指标范围内偏上": "Upper within the limit",
                    "指标的中间": "In the middle of the limit",
                    "无有效数据": "No valid data"
                }

                results = []
                # for value_str in values:
                #     try:
                #         num_str = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', str(value_str))[0]
                #         value = float(num_str)
                #     except (IndexError, ValueError):
                #         results.append("无效数据")
                #         continue

                for value_str in values:
                    if isinstance(value_str, float):
                        value_str = str(value_str)
                    try:
                        num_str = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', value_str)[0]
                        value = float(num_str)
                    except (IndexError, ValueError):
                        results.append("无效数据")
                        continue

                    if value < low_limit:
                        results.append("指标范围外偏下")
                    elif value > up_limit:
                        results.append("指标范围外偏上")
                    else:
                        middle = (low_limit + up_limit) / 2
                        if value < middle:
                            results.append("指标范围内偏下")
                        elif value > middle:
                            results.append("指标范围内偏上")
                        else:
                            results.append("指标的中间")

                total_count = len(results)
                if total_count == 0:
                    result = "无有效数据"
                else:
                    counts = {
                        "指标范围外偏下": 0,
                        "指标范围外偏上": 0,
                        "指标范围内偏下": 0,
                        "指标范围内偏上": 0,
                        "指标的中间": 0,
                        "无效数据": 0
                    }
                    for result in results:
                        counts[result] += 1

                    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
                    top_result = sorted_counts[0]
                    top_percentage = top_result[1] / total_count

                    if top_percentage > top_percentage_limit:
                        result = top_result[0]
                    else:
                        significant_results = [res for res, count in sorted_counts if count > 0 and res != "无效数据"]
                        result = ", ".join(significant_results)

                if language == 'en':
                    if isinstance(result, str):
                        result = result.split(', ')
                        translated_result = [translation_dict.get(item, item) for item in result]
                        return ", ".join(translated_result)
                return result

            def parse_stability(self, satisifed_container, state='PASSED', language='zh'):
                """
                代码说明：
                check_stability 函数：
                该函数接收 satisifed_container 列表和 language 参数（默认值为 'zh' 表示中文）作为输入。
                遍历 satisifed_container 列表中的每个元素，使用 lower() 方法将元素转换为小写，然后检查是否包含 complete 或 satisifed。
                如果找到匹配项，则将状态设置为 "稳定" 并跳出循环；如果遍历完整个列表都没有找到匹配项，则将状态设置为 "不稳定"。
                根据 language 参数的值，若为 'en' 则使用 translation_dict 字典将状态描述转换为英文，否则直接返回中文描述。
                """

                # 中英文对照字典
                translation_dict = {
                    "无效数据": "Invalid data",
                    "指标范围外偏下": "Below the lower limit",
                    "指标范围外偏上": "Above the upper limit",
                    "指标范围内偏下": "Lower within the limit",
                    "指标范围内偏上": "Upper within the limit",
                    "指标的中间": "In the middle of the limit",
                    "无有效数据": "No valid data",
                    "稳定": "Stable",
                    "不稳定": "Unstable",
                    "低": "Low",
                    "高": "High"
                }
                for item in satisifed_container:
                    if 'complete' in item.lower() or 'satisifed' in item.lower():
                        status = "稳定"
                        break
                else:
                    status = "不稳定"

                level = "低" if state == 'PASSED' else "高"
                if language == 'en':
                    return [translation_dict.get(level, level), translation_dict.get(status, status)]
                return [level, status]

            def parse_wifi_tx_test_purpose2items_v1(self, param: str) -> dict:
                """
                解析MTK WLAN测试参数，生成中英文测试说明

                参数:
                    param: MTK WLAN测试参数（如：MTK_WLAN_2.4G_C0_TX_POWER_MCH07_ANT_CW）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 正则解析参数结构
                pattern = r"MTK_WLAN_(?P<band>\d+\.?\d*G)_C(?P<channel>\d+)_TX_POWER_(?P<mode>(H|M|L)CH\d+)_ANT_(?P<test_type>\w+)"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN参数格式: {param}")

                # 解析参数
                band = match.group('band')
                channel = match.group('channel')
                mode = match.group('mode')
                test_type = match.group('test_type')

                # 中英文对照字典
                desc = {
                    "test_purpose_zh": f"验证{band}频段C{channel}通道在{mode}模式下的天线{test_type}发射功率",
                    "test_items_zh": [
                        f"1. {band}频段C{channel}通道的发射功率值",
                        f"2. {mode}模式下的功率稳定性",
                        f"3. 天线分集（ANT）配置下的功率一致性"
                    ],
                    "test_purpose_en": f"Verify TX power of {band} band, channel {channel} under {mode} mode with ANT {test_type}",
                    "test_items_en": [
                        f"1. TX power value at {band} band, channel {channel}",
                        f"2. Power stability in {mode} mode",
                        f"3. Power consistency under antenna diversity (ANT) configuration"
                    ]
                }

                # 补充技术细节（基于MTK WLAN测试规范）
                if test_type == "CW":
                    desc["test_purpose_zh"] += "（连续波模式）"
                    desc["test_purpose_en"] += " (Continuous Wave mode)"
                    desc["test_items_zh"].append("4. 连续波信号的功率谱密度合规性")
                    desc["test_items_en"].append("4. Power spectral density compliance of CW signal")

                return desc

            def parse_wifi_tx_test_purpose2items(self, param: str) -> dict:
                """
                解析MTK WLAN测试参数，生成中英文测试说明

                参数:
                    param: MTK WLAN测试参数（如：MTK_WLAN_5G_C0_TX_POWER_MCH36_STATUS 或 MTK_WLAN_2.4G_C0_TX_POWER_MCH07_ANT_CW）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 正则解析参数结构（兼容两种格式：带ANT和不带ANT的情况）
                pattern = r"MTK_WLAN_(?P<band>\d+\.?\d*G)_C(?P<channel>\d+)_TX_POWER_(?P<mode>(H|M|L)CH\d+)_(?:ANT_)?(?P<test_type>\w+)"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN参数格式: {param}")

                # 解析参数
                band = match.group('band')
                channel = match.group('channel')
                mode = match.group('mode')
                test_type = match.group('test_type')
                has_ant = 'ANT_' in param.upper()  # 判断是否包含ANT配置

                # 中英文对照字典
                base_purpose_zh = f"验证{band}频段C{channel}通道在{mode}模式下的发射功率"
                base_purpose_en = f"Verify TX power of {band} band, channel {channel} under {mode} mode"

                # 根据是否有ANT配置补充说明
                if has_ant:
                    base_purpose_zh += "（天线配置）"
                    base_purpose_en += " (antenna configuration)"

                desc = {
                    "test_purpose_zh": base_purpose_zh,
                    "test_items_zh": [
                        f"1. {band}频段C{channel}通道在{mode}模式下的发射功率绝对值",
                        f"2. 不同温度环境下的功率稳定性（-40℃~85℃）",
                        f"3. 长时间工作（2小时）后的功率衰减量（≤1dB）"
                    ],
                    "test_purpose_en": base_purpose_en,
                    "test_items_en": [
                        f"1. Absolute TX power value of {band} band, channel {channel} under {mode} mode",
                        f"2. Power stability across temperature range (-40℃~85℃)",
                        f"3. Power attenuation after 2-hour operation (≤1dB)"
                    ]
                }

                # 根据测试类型补充技术细节
                if test_type == "CW":
                    desc["test_purpose_zh"] += "（连续波模式）"
                    desc["test_purpose_en"] += " (Continuous Wave mode)"
                    desc["test_items_zh"].extend([
                        "4. 连续波信号的功率谱密度（符合FCC/ETSI规范）",
                        "5. 载波频率误差（≤±20ppm）"
                    ])
                    desc["test_items_en"].extend([
                        "4. Power spectral density of CW signal (compliant with FCC/ETSI)",
                        "5. Carrier frequency error (≤±20ppm)"
                    ])
                elif test_type == "STATUS":
                    desc["test_purpose_zh"] += "（状态监测模式）"
                    desc["test_purpose_en"] += " (Status monitoring mode)"
                    desc["test_items_zh"].extend([
                        "4. 发射功率状态码正确性（0=正常，非0=异常）",
                        "5. 功率调节响应时间（≤10ms）",
                        "6. 多通道功率同步性（差值≤0.5dB）"
                    ])
                    desc["test_items_en"].extend([
                        "4. Correctness of TX power status code (0=normal, non-zero=abnormal)",
                        "5. Power adjustment response time (≤10ms)",
                        "6. Multi-channel power synchronization (difference ≤0.5dB)"
                    ])

                # 若有ANT配置，增加天线相关测试项
                if has_ant:
                    desc["test_items_zh"].insert(3, "4. 天线分集模式下的功率一致性（主副天线差值≤1dB）")
                    desc["test_items_en"].insert(3, "4. Power consistency in antenna diversity mode (difference ≤1dB)")

                return desc

            def parse_wifi_tx_test_purpose2items_for_qc(self, param: str) -> dict:
                """
                解析高通WLAN发射测试参数，生成中英文测试说明（修复5.0GHz模式字段匹配问题）

                参数:
                    param: 高通WLAN发射测试参数，支持两种格式：
                           - QC_WLAN_2.4GHz_11n_RADIATED_TX_C0_MCH_P2K_TRUE
                           - QC_WLAN_5.0GHz_80211ac_RADIATED_TX_C1_LCH36_P2K_FALSE
                           - QC_WLAN_5.0GHz_80211n_RADIATED_TX_C0_LCH_P2K_TRUE（新增支持）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 修复正则表达式，确保5.0GHz模式字段既支持带数字也支持不带数字的格式
                pattern = r'^(QC_WLAN_(?P<band1>2\.4GHZ)_(?P<standard1>\d+[a-zA-Z])_RADIATED_TX_C(?P<channel1>\d+)_(?P<mode1>(H|M|L)CH)_P2K_(?P<p2k_status1>TRUE|FALSE)|' \
                          r'QC_WLAN_(?P<band2>5\.0GHZ)_(?P<standard2>\d+[a-zA-Z])_RADIATED_TX_C(?P<channel2>\d+)_(?P<mode2>(H|M|L)CH\d*)_P2K_(?P<p2k_status2>TRUE|FALSE))$'

                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(
                        f"无效的高通WLAN TX参数格式: {param}，示例：\n"
                        f"1. QC_WLAN_2.4GHz_11n_RADIATED_TX_C0_MCH_P2K_TRUE\n"
                        f"2. QC_WLAN_5.0GHz_80211ac_RADIATED_TX_C1_LCH36_P2K_FALSE\n"
                        f"3. QC_WLAN_5.0GHz_80211n_RADIATED_TX_C0_LCH_P2K_TRUE"
                    )

                # 解析参数（区分2.4GHz和5.0GHz格式）
                if match.group('band1'):
                    # 2.4GHz参数解析（模式字段不带数字）
                    standard = match.group('standard1')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band1'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel1'),
                        "mode": match.group('mode1'),
                        "p2k_status": match.group('p2k_status1'),
                        "channel_type": "Main" if match.group('mode1').startswith('M') else "Low"
                    }
                else:
                    # 5.0GHz参数解析（模式字段支持带数字或不带数字）
                    standard = match.group('standard2')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band2'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel2'),
                        "mode": match.group('mode2'),
                        "p2k_status": match.group('p2k_status2'),
                        "channel_type": "Main" if match.group('mode2').startswith('M') else "Low"
                    }

                # 中英文测试说明
                desc = {
                    "test_purpose_zh": (f"验证高通{params['band']} {params['standard']}标准下，"
                                        f"辐射发射模式C{params['channel']}通道{params['channel_type']}信道（{params['mode']}）的"
                                        f"功率和调制特性（P2K模式{'开启' if params['p2k_status'] == 'TRUE' else '关闭'}）"),
                    "test_items_zh": [
                        f"1. {params['band']}频段C{params['channel']}通道的发射功率（目标范围：15-18dBm）",
                        f"2. {params['mode']}模式下的功率稳定性（100次测试波动≤0.5dB）",
                        f"3. {params['standard']}调制精度（EVM≤-25dB）",
                        f"4. 辐射方向图一致性（水平面360°测试偏差≤2dB）"
                    ],
                    "test_purpose_en": (
                        f"Verify power and modulation characteristics of Qualcomm {params['band']} {params['standard']} "
                        f"radiated TX mode at channel C{params['channel']}, {params['channel_type']} channel ({params['mode']}) "
                        f"(P2K mode {'enabled' if params['p2k_status'] == 'TRUE' else 'disabled'})"),
                    "test_items_en": [
                        f"1. TX power at {params['band']} band, channel C{params['channel']} (target range: 15-18dBm)",
                        f"2. Power stability in {params['mode']} mode (≤0.5dB variation over 100 tests)",
                        f"3. {params['standard']} modulation accuracy (EVM ≤ -25dB)",
                        f"4. Radiation pattern consistency (≤2dB deviation in 360° horizontal plane)"
                    ]
                }

                # 根据不同无线标准添加专属测试项
                if params['standard'] in ["802.11ac", "802.11ax"]:
                    desc["test_items_zh"].insert(4, f"4. {params['standard']} MU-MIMO功率控制精度（用户间偏差≤1dB）")
                    desc["test_items_en"].insert(4,
                                                 f"4. {params['standard']} MU-MIMO power control accuracy (≤1dB between users)")

                # P2K模式开启时增加专属测试项
                if params['p2k_status'] == 'TRUE':
                    desc["test_items_zh"].extend([
                        "5. P2K数据包功率控制响应时间（≤10µs）",
                        "6. 多用户MIMO场景下的功率分配准确性"
                    ])
                    desc["test_items_en"].extend([
                        "5. P2K packet power control response time (≤10µs)",
                        "6. Power allocation accuracy in multi-user MIMO scenarios"
                    ])

                # 5.0GHz频段专属测试项
                if params['band'] == '5.0GHz':
                    if params['standard'] in ["802.11ax", "802.11ac"]:
                        desc["test_items_zh"].append("7. 宽频带发射功率平坦度（80MHz带宽内偏差≤1dB）")
                        desc["test_items_en"].append(
                            "7. Wideband TX power flatness (≤1dB variation across 80MHz bandwidth)")
                    else:
                        desc["test_items_zh"].append("7. 动态频率选择（DFS）功能验证（雷达检测响应≤100ms）")
                        desc["test_items_en"].append(
                            "7. Dynamic Frequency Selection (DFS) verification (radar detection response ≤100ms)")

                # 2.4GHz频段专属测试项
                if params['band'] == '2.4GHz':
                    desc["test_items_zh"].append("7. 蓝牙共存干扰下的发射功率稳定性（偏差≤1dBm）")
                    desc["test_items_en"].append(
                        "7. TX power stability under Bluetooth coexistence (deviation ≤1dBm)")

                return desc

            def parse_basic_band_test_purpose2items_for_CAP_SWITCH_TURBO_CHARGER_v1(self, param: str) -> dict:
                """
                解析电容开关Turbo充电相关测试参数，生成中英文测试说明，使用两个正则表达式分别
                分别匹配匹配两种特定格式

                参数:
                    param: 电容开关Turbo充电测试参数，格式示例：
                           - Cap Switch Turbo Charger First Vatt
                           - Cap_Switch_Turbo_Cap_Switch_Chg_Curr_30W

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式1：匹配"Cap Switch Turbo Charger First Vatt"格式
                # 特征：包含FIRST VATT，无瓦数信息
                pattern1 = r'^CAP_SWITCH_TURBO_CHARGER_FIRST_VATT$'

                # 正则表达式2：匹配"Cap_Switch_Turbo_Cap_Switch_Chg_Curr_30W"格式
                # 特征：包含CHG_CURR，有瓦数信息
                pattern2 = r'^CAP_SWITCH_TURBO_CAP_SWITCH_CHG_CURR_(?P<wattage>\d+)W$'

                # 尝试匹配第一个模式
                match1 = re.match(pattern1, normalized_param)
                # 尝试匹配第二个模式
                match2 = re.match(pattern2, normalized_param)

                # 初始化参数字典
                params = {
                    "product": "未知产品",
                    "wattage": "默认",
                    "wattage_unit": ""
                }

                # 标记匹配的模式类型
                pattern_type = None

                if match1:
                    # 匹配第一个模式（电压测试相关）
                    pattern_type = 1
                    params["test_type"] = "voltage"  # 电压测试类型

                elif match2:
                    # 匹配第二个模式（电流测试相关，带瓦数）
                    pattern_type = 2
                    params["test_type"] = "current"  # 电流测试类型
                    params["wattage"] = match2.group('wattage')
                    params["wattage_unit"] = "W"

                else:
                    # 两个模式都不匹配时抛出错误
                    raise ValueError(
                        f"无效的电容开关Turbo充电参数格式: {param}，示例：\n"
                        f"1. Cap Switch Turbo Charger First Vatt\n"
                        f"2. Cap_Switch_Turbo_Cap_Switch_Chg_Curr_30W"
                    )

                # 中英文测试说明
                desc = {
                    "test_purpose_zh": (
                        f"验证{params['product']}的电容开关Turbo充电功能在{params['wattage']}{params['wattage_unit']}下的"
                        f"工作状态，确保充电过程中电容和开关协同工作正常"),
                    "test_items_zh": [
                        f"1. Turbo模式下电容开关的切换响应时间（目标≤50ms）",
                        f"2. 充电过程中电容电压稳定性（波动范围≤5%）",
                        f"3. 开关切换时的电流冲击抑制效果（峰值≤额定值1.2倍）",
                        f"4. 持续充电状态下的温度控制（≤45℃）"
                    ],
                    "test_purpose_en": (
                        f"Verify the operation status of capacitor switch Turbo charging function "
                        f"for {params['product']} under {params['wattage']}{params['wattage_unit']}, "
                        f"ensure proper coordination between capacitor and switch during charging"
                    ),
                    "test_items_en": [
                        f"1. Switching response time of capacitor switch in Turbo mode (target ≤50ms)",
                        f"2. Capacitor voltage stability during charging (fluctuation range ≤5%)",
                        f"3. Current surge suppression effect during switch transition (peak ≤1.2x rated value)",
                        f"4. Temperature control during continuous charging (≤45℃)"
                    ]
                }

                # 针对第一个模式（电压测试）添加专属测试项
                if pattern_type == 1:
                    desc["test_items_zh"].insert(1, "1.1 初始电压校准准确性（偏差≤2%）")
                    desc["test_items_en"].insert(1, "1.1 Initial voltage calibration accuracy (deviation ≤2%)")
                    desc["test_purpose_zh"] += "，重点验证电压特性"
                    desc["test_purpose_en"] += ", with focus on voltage characteristics"

                # 针对第二个模式（电流测试）添加专属测试项
                if pattern_type == 2:
                    desc["test_items_zh"].insert(2, "2.1 充电电流调节范围验证（符合设计规格）")
                    desc["test_items_en"].insert(2,
                                                 "2.1 Charging current adjustment range verification (meets design specs)")
                    desc["test_purpose_zh"] += "，重点验证电流特性"
                    desc["test_purpose_en"] += ", with focus on current characteristics"

                    # 根据瓦数添加功率相关测试项
                    wattage = int(params['wattage'])
                    if wattage >= 60:
                        desc["test_items_zh"].extend([
                            f"5. {wattage}{params['wattage_unit']}高功率模式下的散热系统有效性",
                            f"6. 长时间高功率充电对电容寿命的影响评估"
                        ])
                        desc["test_items_en"].extend([
                            f"5. Effectiveness of heat dissipation system under {wattage}{params['wattage_unit']} high-power mode",
                            f"6. Impact assessment of long-term high-power charging on capacitor life"
                        ])
                    elif wattage < 30:
                        desc["test_items_zh"].extend([
                            f"5. 低功率模式下的能量转换效率（目标≥90%）",
                            f"6. 待机状态下的电容漏电电流检测（≤10μA）"
                        ])
                        desc["test_items_en"].extend([
                            f"5. Energy conversion efficiency in low-power mode (target ≥90%)",
                            f"6. Capacitor leakage current detection in standby state (≤10μA)"
                        ])

                return desc

            def parse_basic_band_test_purpose2items_for_CAP_SWITCH_TURBO_CHARGER(self, param: str) -> dict:
                """
                解析电容开关Turbo充电相关测试参数，生成中英文测试说明，使用三个正则表达式分别
                匹配三种特定格式

                参数:
                    param: 电容开关Turbo充电测试参数，格式示例：
                           - Cap Switch Turbo Charger First Vatt
                           - Cap_Switch_Turbo_Cap_Switch_Chg_Curr_30W
                           - Cap Switch Turbo Charger Test Overall Status

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式1：匹配"Cap Switch Turbo Charger First Vatt"格式
                # 特征：包含FIRST VATT，无瓦数信息
                pattern1 = r'^CAP_SWITCH_TURBO_CHARGER_FIRST_VATT$'

                # 正则表达式2：匹配"Cap_Switch_Turbo_Cap_Switch_Chg_Curr_30W"格式
                # 特征：包含CHG_CURR，有瓦数信息
                pattern2 = r'^CAP_SWITCH_TURBO_CAP_SWITCH_CHG_CURR_(?P<wattage>\d+)W$'

                # 正则表达式3：匹配"Cap Switch Turbo Charger Test Overall Status"格式
                # 特征：包含TEST OVERALL STATUS，整体状态测试
                pattern3 = r'^CAP_SWITCH_TURBO_CHARGER_TEST_OVERALL_STATUS$'

                # 尝试匹配各个模式
                match1 = re.match(pattern1, normalized_param)
                match2 = re.match(pattern2, normalized_param)
                match3 = re.match(pattern3, normalized_param)

                # 初始化参数字典
                params = {
                    "product": "未知产品",
                    "wattage": "默认",
                    "wattage_unit": ""
                }

                # 标记匹配的模式类型
                pattern_type = None

                if match1:
                    # 匹配第一个模式（电压测试相关）
                    pattern_type = 1
                    params["test_type"] = "voltage"  # 电压测试类型

                elif match2:
                    # 匹配第二个模式（电流测试相关，带瓦数）
                    pattern_type = 2
                    params["test_type"] = "current"  # 电流测试类型
                    params["wattage"] = match2.group('wattage')
                    params["wattage_unit"] = "W"

                elif match3:
                    # 匹配第三个模式（整体状态测试）
                    pattern_type = 3
                    params["test_type"] = "overall_status"  # 整体状态测试类型

                else:
                    # 所有模式都不匹配时抛出错误
                    raise ValueError(
                        f"无效的电容开关Turbo充电参数格式: {param}，示例：\n"
                        f"1. Cap Switch Turbo Charger First Vatt\n"
                        f"2. Cap_Switch_Turbo_Cap_Switch_Chg_Curr_30W\n"
                        f"3. Cap Switch Turbo Charger Test Overall Status"
                    )

                # 中英文测试说明
                desc = {
                    "test_purpose_zh": (
                        f"验证{params['product']}的电容开关Turbo充电功能在{params['wattage']}{params['wattage_unit']}下的"
                        f"工作状态，确保充电过程中电容和开关协同工作正常"),
                    "test_items_zh": [
                        f"1. Turbo模式下电容开关的切换响应时间（目标≤50ms）",
                        f"2. 充电过程中电容电压稳定性（波动范围≤5%）",
                        f"3. 开关切换时的电流冲击抑制效果（峰值≤额定值1.2倍）",
                        f"4. 持续充电状态下的温度控制（≤45℃）"
                    ],
                    "test_purpose_en": (
                        f"Verify the operation status of capacitor switch Turbo charging function "
                        f"for {params['product']} under {params['wattage']}{params['wattage_unit']}, "
                        f"ensure proper coordination between capacitor and switch during charging"
                    ),
                    "test_items_en": [
                        f"1. Switching response time of capacitor switch in Turbo mode (target ≤50ms)",
                        f"2. Capacitor voltage stability during charging (fluctuation range ≤5%)",
                        f"3. Current surge suppression effect during switch transition (peak ≤1.2x rated value)",
                        f"4. Temperature control during continuous charging (≤45℃)"
                    ]
                }

                # 针对第一个模式（电压测试）添加专属测试项
                if pattern_type == 1:
                    desc["test_items_zh"].insert(1, "1.1 初始电压校准准确性（偏差≤2%）")
                    desc["test_items_en"].insert(1, "1.1 Initial voltage calibration accuracy (deviation ≤2%)")
                    desc["test_purpose_zh"] += "，重点验证电压特性"
                    desc["test_purpose_en"] += ", with focus on voltage characteristics"

                # 针对第二个模式（电流测试）添加专属测试项
                if pattern_type == 2:
                    desc["test_items_zh"].insert(2, "2.1 充电电流调节范围验证（符合设计规格）")
                    desc["test_items_en"].insert(2,
                                                 "2.1 Charging current adjustment range verification (meets design specs)")
                    desc["test_purpose_zh"] += "，重点验证电流特性"
                    desc["test_purpose_en"] += ", with focus on current characteristics"

                    # 根据瓦数添加功率相关测试项
                    wattage = int(params['wattage'])
                    if wattage >= 60:
                        desc["test_items_zh"].extend([
                            f"5. {wattage}{params['wattage_unit']}高功率模式下的散热系统有效性",
                            f"6. 长时间高功率充电对电容寿命的影响评估"
                        ])
                        desc["test_items_en"].extend([
                            f"5. Effectiveness of heat dissipation system under {wattage}{params['wattage_unit']} high-power mode",
                            f"6. Impact assessment of long-term high-power charging on capacitor life"
                        ])
                    elif wattage < 30:
                        desc["test_items_zh"].extend([
                            f"5. 低功率模式下的能量转换效率（目标≥90%）",
                            f"6. 待机状态下的电容漏电电流检测（≤10μA）"
                        ])
                        desc["test_items_en"].extend([
                            f"5. Energy conversion efficiency in low-power mode (target ≥90%)",
                            f"6. Capacitor leakage current detection in standby state (≤10μA)"
                        ])

                # 针对第三个模式（整体状态测试）添加专属测试项
                if pattern_type == 3:
                    desc["test_items_zh"].extend([
                        f"5. 全功率范围内的模式切换可靠性（1000次循环测试）",
                        f"6. 异常条件下的保护机制有效性（过压、过流、过温）",
                        f"7. 长期使用后的性能衰减评估（等效1000次充电循环）",
                        f"8. 与不同充电器型号的兼容性验证"
                    ])
                    desc["test_items_en"].extend([
                        f"5. Mode switching reliability across full power range (1000 cycle test)",
                        f"6. Effectiveness of protection mechanisms under abnormal conditions (overvoltage, overcurrent, overtemperature)",
                        f"7. Performance degradation assessment after long-term use (equivalent to 1000 charge cycles)",
                        f"8. Compatibility verification with different charger models"
                    ])
                    desc["test_purpose_zh"] = (
                        f"全面验证{params['product']}的电容开关Turbo充电功能的整体工作状态，"
                        f"确保在各种条件下的稳定性和可靠性"
                    )
                    desc["test_purpose_en"] = (
                        f"Comprehensively verify the overall operating status of the capacitor switch Turbo charging function "
                        f"for {params['product']}, ensuring stability and reliability under various conditions"
                    )

                return desc

            def parse_basic_band_test_purpose2items_for_SPK_INFO_PROGAMMING_v1(self, param: str) -> dict:
                """
                解析扬声器信息编程相关测试参数，生成中英文测试说明，使用正则表达式匹配基础格式

                参数:
                    param: 扬声器信息编程测试参数，格式需以SPK_INFO_PROGAMMING开头，示例：
                           - SPK_INFO_PROGAMMING_BASIC
                           - SPK_INFO_PROGAMMING_TYPE_INTERNAL
                           - SPK_INFO_PROGAMMING_POWER_2W

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式：仅匹配以SPK_INFO_PROGAMMING开头的格式
                pattern = r'^SPK_INFO_PROGAMMING'

                # 尝试匹配模式
                match = re.match(pattern, normalized_param)

                # 初始化参数字典
                params = {
                    "product": "未知产品",
                    "speaker_type": "通用",
                    "power": "标准",
                    "power_unit": ""
                }

                if match:
                    # 提取参数中的类型信息（如果存在）
                    if '_TYPE_' in normalized_param:
                        type_part = normalized_param.split('_TYPE_')[-1]
                        params["speaker_type"] = type_part.lower()
                        params["programming_type"] = "type_specific"
                    # 提取参数中的功率信息（如果存在）
                    elif '_POWER_' in normalized_param:
                        power_part = normalized_param.split('_POWER_')[-1]
                        # 提取数字部分
                        power_match = re.search(r'(\d+)', power_part)
                        if power_match:
                            params["power"] = power_match.group(1)
                            params["power_unit"] = "W"
                        params["programming_type"] = "power_specific"
                    # 基础模式
                    else:
                        params["programming_type"] = "basic"

                else:
                    # 模式不匹配时抛出错误
                    raise ValueError(
                        f"无效的扬声器信息编程参数格式: {param}，参数必须以SPK_INFO_PROGAMMING开头，示例：\n"
                        f"1. SPK_INFO_PROGAMMING_BASIC\n"
                        f"2. SPK_INFO_PROGAMMING_TYPE_INTERNAL\n"
                        f"3. SPK_INFO_PROGAMMING_POWER_2W"
                    )

                # 中英文测试说明
                desc = {
                    "test_purpose_zh": (
                        f"验证{params['product']}的扬声器信息编程功能在{params['speaker_type']}类型、"
                        f"{params['power']}{params['power_unit']}功率下的工作状态，确保编程信息准确无误"
                    ),
                    "test_items_zh": [
                        f"1. 扬声器基本信息读取准确性（制造商、型号、规格）",
                        f"2. 编程数据写入成功率验证（连续10次写入无失败）",
                        f"3. 编程后信息保存稳定性（断电重启后验证）",
                        f"4. 编程接口通信可靠性（无数据传输错误）"
                    ],
                    "test_purpose_en": (
                        f"Verify the operation status of speaker information programming function "
                        f"for {params['product']} with {params['speaker_type']} type and "
                        f"{params['power']}{params['power_unit']} power, ensure programming information is accurate"
                    ),
                    "test_items_en": [
                        f"1. Accuracy of speaker basic information reading (manufacturer, model, specifications)",
                        f"2. Verification of programming data writing success rate (10 consecutive writes without failure)",
                        f"3. Stability of information保存 after programming (verify after power cycle)",
                        f"4. Reliability of programming interface communication (no data transmission errors)"
                    ]
                }

                # 针对基础模式添加专属测试项
                if params["programming_type"] == "basic":
                    desc["test_items_zh"].insert(1, "1.1 默认参数集编程完整性验证")
                    desc["test_items_en"].insert(1, "1.1 Verification of default parameter set programming integrity")
                    desc["test_purpose_zh"] += "，重点验证基础功能完整性"
                    desc["test_purpose_en"] += ", with focus on basic function integrity"

                # 针对特定类型模式添加专属测试项
                if params["programming_type"] == "type_specific":
                    desc["test_items_zh"].insert(2, f"2.1 {params['speaker_type']}类型扬声器专属参数编程验证")
                    desc["test_items_en"].insert(2,
                                                 f"2.1 {params['speaker_type']} type specific parameter programming verification")
                    desc["test_purpose_zh"] += "，重点验证类型适配性"
                    desc["test_purpose_en"] += ", with focus on type compatibility"

                # 针对特定功率模式添加专属测试项
                if params["programming_type"] == "power_specific":
                    desc["test_items_zh"].insert(2, f"2.1 {params['power']}{params['power_unit']}功率参数精准度验证")
                    desc["test_items_en"].insert(2,
                                                 f"2.1 {params['power']}{params['power_unit']} power parameter accuracy verification")
                    desc["test_purpose_zh"] += "，重点验证功率匹配性"
                    desc["test_purpose_en"] += ", with focus on power matching"

                    # 根据功率添加相关测试项
                    try:
                        power = int(params['power'])
                        if power >= 5:
                            desc["test_items_zh"].extend([
                                f"5. 高功率扬声器保护参数编程验证",
                                f"6. 散热控制相关参数配置准确性"
                            ])
                            desc["test_items_en"].extend([
                                f"5. Programming verification of high-power speaker protection parameters",
                                f"6. Accuracy of thermal control related parameter configuration"
                            ])
                        elif power < 1:
                            desc["test_items_zh"].extend([
                                f"5. 微型扬声器灵敏度参数校准",
                                f"6. 低功耗模式下的参数优化验证"
                            ])
                            desc["test_items_en"].extend([
                                f"5. Sensitivity parameter calibration for micro speakers",
                                f"6. Parameter optimization verification in low-power mode"
                            ])
                    except (ValueError, TypeError):
                        # 功率参数无法转换为数字时不添加额外测试项
                        pass

                return desc

            def parse_basic_band_test_purpose2items_for_SPK_INFO_PROGAMMING(self, param: str) -> dict:
                """
                解析扬声器信息编程或关键部件匹配规格相关测试参数，生成中英文测试说明

                参数:
                    param: 测试参数，格式需以SPK_INFO_PROGAMMING或KEY_PART_MATCH_SPEC开头，示例：
                           - SPK_INFO_PROGAMMING_BASIC
                           - SPK_INFO_PROGAMMING_TYPE_INTERNAL
                           - KEY_PART_MATCH_SPEC_BASIC
                           - KEY_PART_MATCH_SPEC_SPEC_HIGH

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式：匹配两种前缀格式
                pattern = r'^(SPK_INFO_PROGAMMING|KEY_PART_MATCH_SPEC)'
                match = re.match(pattern, normalized_param)

                if not match:
                    # 模式不匹配时抛出错误，更新示例说明
                    raise ValueError(
                        f"无效的参数格式: {param}，参数必须以SPK_INFO_PROGAMMING或KEY_PART_MATCH_SPEC开头，示例：\n"
                        f"1. SPK_INFO_PROGAMMING_BASIC\n"
                        f"2. SPK_INFO_PROGAMMING_TYPE_INTERNAL\n"
                        f"3. KEY_PART_MATCH_SPEC_BASIC\n"
                        f"4. KEY_PART_MATCH_SPEC_SPEC_HIGH"
                    )

                # 初始化参数字典，新增参数类型标识
                params = {
                    "product": "未知产品",
                    "param_type": match.group(1),  # 记录参数前缀类型
                    "subtype": "通用",
                    "spec_value": "标准",
                    "spec_unit": ""
                }

                # 解析SPK_INFO_PROGAMMING前缀的参数
                if params["param_type"] == "SPK_INFO_PROGAMMING":
                    if '_TYPE_' in normalized_param:
                        params["subtype"] = normalized_param.split('_TYPE_')[-1].lower()
                        params["detail_type"] = "type_specific"
                    elif '_POWER_' in normalized_param:
                        power_part = normalized_param.split('_POWER_')[-1]
                        power_match = re.search(r'(\d+)', power_part)
                        if power_match:
                            params["spec_value"] = power_match.group(1)
                            params["spec_unit"] = "W"
                        params["detail_type"] = "power_specific"
                    else:
                        params["detail_type"] = "basic"

                # 解析KEY_PART_MATCH_SPEC前缀的参数
                else:  # KEY_PART_MATCH_SPEC
                    if '_TYPE_' in normalized_param:
                        params["subtype"] = normalized_param.split('_TYPE_')[-1].lower()
                        params["detail_type"] = "type_specific"
                    elif '_SPEC_' in normalized_param:
                        spec_part = normalized_param.split('_SPEC_')[-1]
                        # 尝试提取数值规格（如HIGH/LOW/500等）
                        spec_match = re.search(r'(\d+|HIGH|LOW|STANDARD)', spec_part, re.IGNORECASE)
                        if spec_match:
                            params["spec_value"] = spec_match.group(1).lower()
                            params["spec_unit"] = "标准单位" if spec_match.group(1).isdigit() else ""
                        params["detail_type"] = "spec_specific"
                    else:
                        params["detail_type"] = "basic"

                # 初始化中英文测试说明（根据参数类型区分基础描述）
                if params["param_type"] == "SPK_INFO_PROGAMMING":
                    base_desc_zh = (f"验证{params['product']}的扬声器信息编程功能在{params['subtype']}类型、"
                                    f"{params['spec_value']}{params['spec_unit']}规格下的工作状态")
                    base_desc_en = (f"Verify the speaker information programming function of {params['product']} "
                                    f"under {params['subtype']} type and {params['spec_value']}{params['spec_unit']} specification")
                    base_items_zh = [
                        "1. 扬声器基本信息读取准确性（制造商、型号、规格）",
                        "2. 编程数据写入成功率验证（连续10次写入无失败）",
                        "3. 编程后信息保存稳定性（断电重启后验证）",
                        "4. 编程接口通信可靠性（无数据传输错误）"
                    ]
                    base_items_en = [
                        "1. Accuracy of speaker basic information reading (manufacturer, model, specifications)",
                        "2. Verification of programming data writing success rate (10 consecutive writes without failure)",
                        "3. Stability of information after programming (verify after power cycle)",
                        "4. Reliability of programming interface communication (no data transmission errors)"
                    ]

                else:  # KEY_PART_MATCH_SPEC
                    base_desc_zh = (f"验证{params['product']}的关键部件匹配规格功能在{params['subtype']}类型、"
                                    f"{params['spec_value']}{params['spec_unit']}规格下的匹配准确性")
                    base_desc_en = (f"Verify the key part matching specification function of {params['product']} "
                                    f"under {params['subtype']} type and {params['spec_value']}{params['spec_unit']} specification")
                    base_items_zh = [
                        "1. 关键部件型号匹配准确性（与设计规格比对）",
                        "2. 部件参数一致性验证（连续5次检测无偏差）",
                        "3. 匹配结果存储可靠性（系统重启后验证）",
                        "4. 部件识别接口通信稳定性（无识别超时）"
                    ]
                    base_items_en = [
                        "1. Accuracy of key part model matching (compared with design specifications)",
                        "2. Verification of component parameter consistency (5 consecutive detections without deviation)",
                        "3. Reliability of matching result storage (verify after system restart)",
                        "4. Stability of component recognition interface communication (no recognition timeout)"
                    ]

                # 组装最终描述
                desc = {
                    "test_purpose_zh": f"{base_desc_zh}，确保相关信息准确无误",
                    "test_items_zh": base_items_zh.copy(),
                    "test_purpose_en": f"{base_desc_en}, ensure relevant information is accurate",
                    "test_items_en": base_items_en.copy()
                }

                # 针对基础模式添加专属测试项
                if params["detail_type"] == "basic":
                    if params["param_type"] == "SPK_INFO_PROGAMMING":
                        desc["test_items_zh"].insert(1, "1.1 默认参数集编程完整性验证")
                        desc["test_items_en"].insert(1,
                                                     "1.1 Verification of default parameter set programming integrity")
                        desc["test_purpose_zh"] += "，重点验证基础功能完整性"
                        desc["test_purpose_en"] += ", with focus on basic function integrity"
                    else:
                        desc["test_items_zh"].insert(1, "1.1 基础规格匹配库完整性验证")
                        desc["test_items_en"].insert(1,
                                                     "1.1 Verification of basic specification matching library integrity")
                        desc["test_purpose_zh"] += "，重点验证基础匹配逻辑正确性"
                        desc["test_purpose_en"] += ", with focus on basic matching logic correctness"

                # 针对类型特定模式添加专属测试项
                if params["detail_type"] == "type_specific":
                    desc["test_items_zh"].insert(2, f"2.1 {params['subtype']}类型专属参数验证")
                    desc["test_items_en"].insert(2, f"2.1 {params['subtype']} type specific parameter verification")
                    desc["test_purpose_zh"] += "，重点验证类型适配性"
                    desc["test_purpose_en"] += ", with focus on type compatibility"

                # 针对SPK_INFO_PROGAMMING的功率特定模式
                if params["param_type"] == "SPK_INFO_PROGAMMING" and params["detail_type"] == "power_specific":
                    desc["test_items_zh"].insert(2,
                                                 f"2.1 {params['spec_value']}{params['spec_unit']}功率参数精准度验证")
                    desc["test_items_en"].insert(2,
                                                 f"2.1 {params['spec_value']}{params['spec_unit']} power parameter accuracy verification")
                    desc["test_purpose_zh"] += "，重点验证功率匹配性"
                    desc["test_purpose_en"] += ", with focus on power matching"

                    # 根据功率值添加额外测试项
                    try:
                        power = int(params['spec_value'])
                        if power >= 5:
                            desc["test_items_zh"].extend([
                                "5. 高功率扬声器保护参数编程验证",
                                "6. 散热控制相关参数配置准确性"
                            ])
                            desc["test_items_en"].extend([
                                "5. Programming verification of high-power speaker protection parameters",
                                "6. Accuracy of thermal control related parameter configuration"
                            ])
                        elif power < 1:
                            desc["test_items_zh"].extend([
                                "5. 微型扬声器灵敏度参数校准",
                                "6. 低功耗模式下的参数优化验证"
                            ])
                            desc["test_items_en"].extend([
                                "5. Sensitivity parameter calibration for micro speakers",
                                "6. Parameter optimization verification in low-power mode"
                            ])
                    except (ValueError, TypeError):
                        pass

                # 针对KEY_PART_MATCH_SPEC的规格特定模式
                if params["param_type"] == "KEY_PART_MATCH_SPEC" and params["detail_type"] == "spec_specific":
                    desc["test_items_zh"].insert(2, f"2.1 {params['spec_value']}{params['spec_unit']}规格匹配精度验证")
                    desc["test_items_en"].insert(2,
                                                 f"2.1 {params['spec_value']}{params['spec_unit']} specification matching accuracy verification")
                    desc["test_purpose_zh"] += "，重点验证规格一致性"
                    desc["test_purpose_en"] += ", with focus on specification consistency"

                    # 根据规格值添加额外测试项
                    spec_val = params['spec_value']
                    if spec_val == "high":
                        desc["test_items_zh"].extend([
                            "5. 高精度部件容差范围验证",
                            "6. 高规格模式下性能衰减测试"
                        ])
                        desc["test_items_en"].extend([
                            "5. Verification of high-precision component tolerance range",
                            "6. Performance degradation test under high specification mode"
                        ])
                    elif spec_val == "low":
                        desc["test_items_zh"].extend([
                            "5. 基础规格兼容性验证",
                            "6. 低规格模式下稳定性测试"
                        ])
                        desc["test_items_en"].extend([
                            "5. Verification of basic specification compatibility",
                            "6. Stability test under low specification mode"
                        ])

                return desc

            def parse_basic_band_test_purpose2items_for_ANDROID_GET_BATTERY_LEVEL(self, param: str) -> dict:
                """
                解析Android设备电池电量获取相关测试参数，生成中英文测试说明

                参数:
                    param: 测试参数，格式需以ANDROID_GET_BATTERY_LEVEL开头

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式：仅匹配以ANDROID_GET_BATTERY_LEVEL开头的格式
                pattern = r'^ANDROID_GET_BATTERY_LEVEL'
                match = re.match(pattern, normalized_param)

                if not match:
                    # 模式不匹配时抛出错误
                    raise ValueError(
                        f"无效的参数格式: {param}，参数必须以ANDROID_GET_BATTERY_LEVEL开头"
                    )

                # 初始化参数字典（仅保留基础参数）
                params = {
                    "device": "未知Android设备",
                    "detail_type": "basic"  # 仅保留基础模式
                }

                # 初始化中英文测试说明（基于基础模式）
                base_desc_zh = (f"验证{params['device']}的电池电量获取基础功能的工作状态")
                base_desc_en = (f"Verify the basic battery level retrieval function of {params['device']}")

                base_items_zh = [
                    "1. 电池电量百分比读取准确性（与实际电量对比）",
                    "2. 电量数据获取响应时间验证（单次获取耗时≤100ms）",
                    "3. 连续获取稳定性测试（连续100次无数据丢失）",
                    "4. 系统API调用成功率验证（无调用失败）"
                ]
                base_items_en = [
                    "1. Accuracy of battery level percentage reading (compared with actual level)",
                    "2. Verification of data retrieval response time (single retrieval time ≤ 100ms)",
                    "3. Stability test for continuous retrieval (100 consecutive times without data loss)",
                    "4. Verification of system API call success rate (no call failures)"
                ]

                # 组装最终描述
                desc = {
                    "test_purpose_zh": f"{base_desc_zh}，确保电量信息准确可靠",
                    "test_items_zh": base_items_zh.copy(),
                    "test_purpose_en": f"{base_desc_en}, ensure battery level information is accurate and reliable",
                    "test_items_en": base_items_en.copy()
                }

                # 基础模式专属测试项
                desc["test_items_zh"].insert(1, "1.1 基础电量状态（满电/低电）识别准确性")
                desc["test_items_en"].insert(1, "1.1 Accuracy of basic battery status (full/low) recognition")
                desc["test_purpose_zh"] += "，重点验证基础功能可用性"
                desc["test_purpose_en"] += ", with focus on basic function availability"

                return desc

            def parse_basic_band_test_purpose2items_for_BATTERY_CHARGE_LEVEL(self, param: str) -> dict:
                """
                解析电池充电电量相关测试参数，生成中英文测试说明

                参数:
                    param: 测试参数，格式需以BATTERY_CHARGE_LEVEL开头

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式：仅匹配以BATTERY_CHARGE_LEVEL开头的格式
                pattern = r'^BATTERY_CHARGE_LEVEL'
                match = re.match(pattern, normalized_param)

                if not match:
                    # 模式不匹配时抛出错误
                    raise ValueError(
                        f"无效的参数格式: {param}，参数必须以BATTERY_CHARGE_LEVEL开头"
                    )

                # 初始化参数字典（仅保留基础参数）
                params = {
                    "device": "未知设备",
                    "detail_type": "basic"  # 仅保留基础模式
                }

                # 初始化中英文测试说明（基于基础模式）
                base_desc_zh = (f"验证{params['device']}的电池充电电量监测基础功能的工作状态")
                base_desc_en = (f"Verify the basic battery charge level monitoring function of {params['device']}")

                base_items_zh = [
                    "1. 充电电量百分比读取准确性（与实际充电量对比）",
                    "2. 充电电量数据获取响应时间验证（单次获取耗时≤100ms）",
                    "3. 充电过程中连续监测稳定性测试（全程无数据丢失）",
                    "4. 充电状态下API调用成功率验证（无调用失败）"
                ]
                base_items_en = [
                    "1. Accuracy of charge level percentage reading (compared with actual charge amount)",
                    "2. Verification of charge level data retrieval response time (single retrieval time ≤ 100ms)",
                    "3. Stability test for continuous monitoring during charging (no data loss throughout the process)",
                    "4. Verification of API call success rate in charging state (no call failures)"
                ]

                # 组装最终描述
                desc = {
                    "test_purpose_zh": f"{base_desc_zh}，确保充电电量信息准确可靠",
                    "test_items_zh": base_items_zh.copy(),
                    "test_purpose_en": f"{base_desc_en}, ensure charge level information is accurate and reliable",
                    "test_items_en": base_items_en.copy()
                }

                # 基础模式专属测试项
                desc["test_items_zh"].insert(1, "1.1 充电状态（快充/慢充/涓流充）识别准确性")
                desc["test_items_en"].insert(1, "1.1 Accuracy of charging state (fast/slow/trickle charge) recognition")
                desc["test_purpose_zh"] += "，重点验证充电状态下的基础功能可用性"
                desc["test_purpose_en"] += ", with focus on basic function availability in charging state"

                return desc

            def parse_basic_band_test_purpose2items_for_BATTERY_LEVELS(self, param: str) -> dict:
                """
                解析电池电量相关测试参数（包括Android设备电量获取、电池充电电量和充电状态），生成中英文测试说明

                参数:
                    param: 测试参数，格式需以ANDROID_GET_BATTERY_LEVEL、BATTERY_CHARGE_LEVEL或GET_BATTERY_CHARGE_LEVEL_STATUS开头

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式：匹配三种参数前缀格式
                pattern = r'^(ANDROID_GET_BATTERY_LEVEL|BATTERY_CHARGE_LEVEL|GET_BATTERY_CHARGE_LEVEL_STATUS)'
                match = re.match(pattern, normalized_param)

                if not match:
                    # 模式不匹配时抛出错误
                    raise ValueError(
                        f"无效的参数格式: {param}，参数必须以以下之一开头：\n"
                        f"ANDROID_GET_BATTERY_LEVEL、BATTERY_CHARGE_LEVEL、GET_BATTERY_CHARGE_LEVEL_STATUS"
                    )

                # 获取匹配的参数类型
                param_type = match.group(1)

                # 初始化参数字典
                params = {
                    "device": "未知Android设备" if param_type == "ANDROID_GET_BATTERY_LEVEL" else "未知设备",
                    "detail_type": "basic"  # 仅保留基础模式
                }

                # 根据参数类型初始化不同的测试说明
                if param_type == "ANDROID_GET_BATTERY_LEVEL":
                    # Android设备电量获取相关测试说明
                    base_desc_zh = (f"验证{params['device']}的电池电量获取基础功能的工作状态")
                    base_desc_en = (f"Verify the basic battery level retrieval function of {params['device']}")

                    base_items_zh = [
                        "1. 电池电量百分比读取准确性（与实际电量对比）",
                        "2. 电量数据获取响应时间验证（单次获取耗时≤100ms）",
                        "3. 连续获取稳定性测试（连续100次无数据丢失）",
                        "4. 系统API调用成功率验证（无调用失败）"
                    ]
                    base_items_en = [
                        "1. Accuracy of battery level percentage reading (compared with actual level)",
                        "2. Verification of data retrieval response time (single retrieval time ≤ 100ms)",
                        "3. Stability test for continuous retrieval (100 consecutive times without data loss)",
                        "4. Verification of system API call success rate (no call failures)"
                    ]

                    # 基础模式专属测试项
                    specific_item_zh = "1.1 基础电量状态（满电/低电）识别准确性"
                    specific_item_en = "1.1 Accuracy of basic battery status (full/low) recognition"
                    purpose_suffix_zh = "，重点验证基础功能可用性"
                    purpose_suffix_en = ", with focus on basic function availability"

                elif param_type == "BATTERY_CHARGE_LEVEL":
                    # 电池充电电量相关测试说明
                    base_desc_zh = (f"验证{params['device']}的电池充电电量监测基础功能的工作状态")
                    base_desc_en = (f"Verify the basic battery charge level monitoring function of {params['device']}")

                    base_items_zh = [
                        "1. 充电电量百分比读取准确性（与实际充电量对比）",
                        "2. 充电电量数据获取响应时间验证（单次获取耗时≤100ms）",
                        "3. 充电过程中连续监测稳定性测试（全程无数据丢失）",
                        "4. 充电状态下API调用成功率验证（无调用失败）"
                    ]
                    base_items_en = [
                        "1. Accuracy of charge level percentage reading (compared with actual charge amount)",
                        "2. Verification of charge level data retrieval response time (single retrieval time ≤ 100ms)",
                        "3. Stability test for continuous monitoring during charging (no data loss throughout the process)",
                        "4. Verification of API call success rate in charging state (no call failures)"
                    ]

                    # 基础模式专属测试项
                    specific_item_zh = "1.1 充电状态（快充/慢充/涓流充）识别准确性"
                    specific_item_en = "1.1 Accuracy of charging state (fast/slow/trickle charge) recognition"
                    purpose_suffix_zh = "，重点验证充电状态下的基础功能可用性"
                    purpose_suffix_en = ", with focus on basic function availability in charging state"

                else:  # GET_BATTERY_CHARGE_LEVEL_STATUS
                    # 电池充电状态相关测试说明
                    base_desc_zh = (f"验证{params['device']}的电池充电状态识别与上报基础功能的工作状态")
                    base_desc_en = (
                        f"Verify the basic function of battery charge status recognition and reporting for {params['device']}")

                    base_items_zh = [
                        "1. 充电状态（充电中/未充电）识别准确性",
                        "2. 充电类型（有线/无线）识别准确性",
                        "3. 充电状态切换响应时间验证（状态变化后≤200ms识别）",
                        "4. 充电状态持续监测稳定性（连续30分钟无错误上报）"
                    ]
                    base_items_en = [
                        "1. Accuracy of charging status (charging/not charging) recognition",
                        "2. Accuracy of charging type (wired/wireless) recognition",
                        "3. Verification of charging status switch response time (≤200ms after status change)",
                        "4. Stability of continuous charging status monitoring (no false reports for 30 consecutive minutes)"
                    ]

                    # 基础模式专属测试项
                    specific_item_zh = "1.1 充电阶段（预充/快充/满充）识别准确性"
                    specific_item_en = "1.1 Accuracy of charging phase (pre-charge/fast-charge/full-charge) recognition"
                    purpose_suffix_zh = "，重点验证状态识别的准确性和及时性"
                    purpose_suffix_en = ", with focus on accuracy and timeliness of status recognition"

                # 组装最终描述
                desc = {
                    "test_purpose_zh": f"{base_desc_zh}，确保电量信息准确可靠{purpose_suffix_zh}",
                    "test_items_zh": base_items_zh.copy(),
                    "test_purpose_en": f"{base_desc_en}, ensure battery level information is accurate and reliable{purpose_suffix_en}",
                    "test_items_en": base_items_en.copy()
                }

                # 添加基础模式专属测试项
                desc["test_items_zh"].insert(1, specific_item_zh)
                desc["test_items_en"].insert(1, specific_item_en)

                return desc

            def parse_basic_band_test_purpose2items_for_ANDROID_MAGNETOMETER(self, param: str, pattern: str) -> dict:
                """
                解析磁力计相关测试参数（包括Android设备磁力计数据获取、磁力计存在性检测等），生成中英文测试说明

                参数:
                    param: 测试参数，格式需以ANDROID_MAGNETOMETER、MAGNETOMETER_PRESENSE_APK_STATUS、
                           MAGNETOMETER_X_AXIS_ABSOLUTE_MAG_FIELD_APK或MAGNETOMETER_Y_AXIS_ABSOLUTE_MAG_FIELD_APK开头
                    pattern: 匹配模式，需包含一个捕获组，例如:
                             r'^(ANDROID_MAGNETOMETER|MAGNETOMETER_PRESENSE_APK_STATUS|MAGNETOMETER_X_AXIS_ABSOLUTE_MAG_FIELD_APK|MAGNETOMETER_Y_AXIS_ABSOLUTE_MAG_FIELD_APK)'

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式：匹配三种参数前缀格式（使用捕获组统一获取匹配的前缀）
                # 修复点：将所有可选前缀放在一个捕获组中，确保group(1)能获取到匹配的参数类型
                match = re.match(pattern, normalized_param)

                if not match:
                    # 模式不匹配时抛出错误，更新提示信息包含新的前缀
                    raise ValueError(
                        f"无效的参数格式: {param}，参数必须以以下之一开头：\n"
                        f"ANDROID_MAGNETOMETER、"
                        f"MAGNETOMETER_PRESENSE_APK_STATUS、"
                        f"MAGNETOMETER_X_AXIS_ABSOLUTE_MAG_FIELD_APK、"
                        f"MAGNETOMETER_Y_AXIS_ABSOLUTE_MAG_FIELD_APK、"
                        f"MAGNETOMETER_Z_AXIS_ABSOLUTE_MAG_FIELD_APK"
                    )

                # 修复捕获组问题：先检查是否有分组，再获取参数类型
                if match.groups():  # 确保存在捕获组
                    param_type = match.group(1)
                else:
                    # 如果没有捕获组，直接使用完整匹配结果
                    param_type = match.group(0)

                # 初始化参数字典
                params = {
                    "device": "未知Android设备",
                    "detail_type": "basic"
                }

                # 根据参数类型处理（保持原有逻辑）
                if param_type == "ANDROID_MAGNETOMETER":
                    base_desc_zh = f"验证{params['device']}的磁力计数据获取基础功能的工作状态"
                    base_desc_en = f"Verify the basic magnetometer data retrieval function of {params['device']}"
                    base_items_zh = [
                        "1. 磁力计三轴数据（X/Y/Z）读取准确性（与标准磁场对比）",
                        "2. 磁力计数据获取响应时间验证（单次获取耗时≤100ms）",
                        "3. 连续数据采集稳定性测试（连续100次无数据丢失）",
                        "4. 磁力计系统API调用成功率验证（无调用失败）"
                    ]
                    base_items_en = [
                        "1. Accuracy of magnetometer 3-axis data (X/Y/Z) reading (compared with standard magnetic field)",
                        "2. Verification of data retrieval response time (single retrieval time ≤ 100ms)",
                        "3. Stability test for continuous data collection (100 consecutive times without data loss)",
                        "4. Verification of magnetometer system API call success rate (no call failures)"
                    ]

                    # 基础模式专属测试项
                    specific_item_zh = "1.1 磁力计数据单位转换准确性（微特斯拉）"
                    specific_item_en = "1.1 Accuracy of magnetometer data unit conversion (microtesla)"
                    purpose_suffix_zh = "，重点验证基础数据采集功能可用性"
                    purpose_suffix_en = ", with focus on basic data collection function availability"

                elif param_type == "MAGNETOMETER_PRESENSE_APK_STATUS":
                    base_desc_zh = f"验证{params['device']}的磁力计硬件存在性及驱动状态识别基础功能"
                    base_desc_en = f"Verify the basic function of magnetometer hardware presence and driver status recognition for {params['device']}"
                    base_items_zh = [
                        "1. 磁力计硬件存在性检测准确性",
                        "2. 磁力计驱动加载状态识别准确性",
                        "3. 磁力计使能/禁用状态切换响应时间验证（状态变化后≤200ms识别）",
                        "4. 磁力计状态持续监测稳定性（连续30分钟无错误上报）"
                    ]
                    base_items_en = [
                        "1. Accuracy of magnetometer hardware presence detection",
                        "2. Accuracy of magnetometer driver loading status recognition",
                        "3. Verification of magnetometer enable/disable status switch response time (≤200ms after status change)",
                        "4. Stability of continuous magnetometer status monitoring (no false reports for 30 consecutive minutes)"
                    ]

                    # 基础模式专属测试项
                    specific_item_zh = "1.1 磁力计硬件ID识别准确性"
                    specific_item_en = "1.1 Accuracy of magnetometer hardware ID recognition"
                    purpose_suffix_zh = "，重点验证硬件存在性识别的准确性"
                    purpose_suffix_en = ", with focus on accuracy of hardware presence recognition"

                elif param_type == "MAGNETOMETER_X_AXIS_ABSOLUTE_MAG_FIELD_APK":
                    base_desc_zh = f"验证{params['device']}的磁力计X轴绝对磁场强度检测基础功能"
                    base_desc_en = f"Verify the basic function of magnetometer X-axis absolute magnetic field strength detection for {params['device']}"
                    base_items_zh = [
                        "1. X轴绝对磁场强度测量准确性（与标准磁场源对比）",
                        "2. X轴磁场强度零漂测试（常温下≤5微特斯拉/小时）",
                        "3. X轴磁场数据温度稳定性（-10℃~60℃范围内误差≤3%）",
                        "4. 长期测量重复性验证（连续24小时测试偏差≤2%）"
                    ]
                    base_items_en = [
                        "1. Accuracy of X-axis absolute magnetic field strength measurement (compared with standard magnetic field source)",
                        "2. X-axis magnetic field zero drift test (≤5μT/h at room temperature)",
                        "3. X-axis magnetic field data temperature stability (error ≤3% within -10℃~60℃)",
                        "4. Long-term measurement repeatability verification (continuous 24-hour test deviation ≤2%)"
                    ]

                    # 新增类型专属测试项
                    specific_item_zh = "1.1 X轴磁场强度校准后误差验证（≤1微特斯拉）"
                    specific_item_en = "1.1 X-axis magnetic field strength error verification after calibration (≤1μT)"
                    purpose_suffix_zh = "，重点验证X轴绝对磁场测量精度"
                    purpose_suffix_en = ", with focus on X-axis absolute magnetic field measurement accuracy"

                elif param_type == "MAGNETOMETER_Y_AXIS_ABSOLUTE_MAG_FIELD_APK":
                    base_desc_zh = f"验证{params['device']}的磁力计Y轴绝对磁场强度检测基础功能"
                    base_desc_en = f"Verify the basic function of magnetometer Y-axis absolute magnetic field strength detection for {params['device']}"
                    base_items_zh = [
                        "1. Y轴绝对磁场强度测量准确性（与标准磁场源对比）",
                        "2. Y轴磁场强度零漂测试（常温下≤5微特斯拉/小时）",
                        "3. Y轴磁场数据温度稳定性（-10℃~60℃范围内误差≤3%）",
                        "4. 长期测量重复性验证（连续24小时测试偏差≤2%）"
                    ]
                    base_items_en = [
                        "1. Accuracy of Y-axis absolute magnetic field strength measurement (compared with standard magnetic field source)",
                        "2. Y-axis magnetic field zero drift test (≤5μT/h at room temperature)",
                        "3. Y-axis magnetic field data temperature stability (error ≤3% within -10℃~60℃)",
                        "4. Long-term measurement repeatability verification (continuous 24-hour test deviation ≤2%)"
                    ]
                    specific_item_zh = "1.1 Y轴磁场强度校准后误差验证（≤1微特斯拉）"
                    specific_item_en = "1.1 Y-axis magnetic field strength error verification after calibration (≤1μT)"
                    purpose_suffix_zh = "，重点验证Y轴绝对磁场测量精度"
                    purpose_suffix_en = ", with focus on Y-axis absolute magnetic field measurement accuracy"

                elif param_type == "MAGNETOMETER_Z_AXIS_ABSOLUTE_MAG_FIELD_APK":
                    base_desc_zh = f"验证{params['device']}的磁力计Z轴绝对磁场强度检测基础功能"
                    base_desc_en = f"Verify the basic function of magnetometer Z-axis absolute magnetic field strength detection for {params['device']}"
                    base_items_zh = [
                        "1. Z轴绝对磁场强度测量准确性（与标准磁场源对比）",
                        "2. Z轴磁场强度零漂测试（常温下≤5微特斯拉/小时）",
                        "3. Z轴磁场数据温度稳定性（-10℃~60℃范围内误差≤3%）",
                        "4. 长期测量重复性验证（连续24小时测试偏差≤2%）"
                    ]
                    base_items_en = [
                        "1. Accuracy of Z-axis absolute magnetic field strength measurement (compared with standard magnetic field source)",
                        "2. Z-axis magnetic field zero drift test (≤5μT/h at room temperature)",
                        "3. Z-axis magnetic field data temperature stability (error ≤3% within -10℃~60℃)",
                        "4. Long-term measurement repeatability verification (continuous 24-hour test deviation ≤2%)"
                    ]
                    specific_item_zh = "1.1 Z轴磁场强度校准后误差验证（≤1微特斯拉）"
                    specific_item_en = "1.1 Z-axis magnetic field strength error verification after calibration (≤1μT)"
                    purpose_suffix_zh = "，重点验证Z轴绝对磁场测量精度"
                    purpose_suffix_en = ", with focus on Z-axis absolute magnetic field measurement accuracy"

                else:
                    raise ValueError(f"不支持的参数类型: {param_type}")

                # 组装最终描述
                desc = {
                    "test_purpose_zh": f"{base_desc_zh}，确保磁力计信息准确可靠{purpose_suffix_zh}",
                    "test_items_zh": base_items_zh.copy(),
                    "test_purpose_en": f"{base_desc_en}, ensure magnetometer information is accurate and reliable{purpose_suffix_en}",
                    "test_items_en": base_items_en.copy()
                }

                # 添加基础模式专属测试项
                desc["test_items_zh"].insert(1, specific_item_zh)
                desc["test_items_en"].insert(1, specific_item_en)

                return desc

            def parse_basic_band_test_purpose2items_for_QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW(self, param: str) -> dict:
                """
                解析USIM机械开关移除检测相关测试参数，生成中英文测试说明

                参数:
                    param: 测试参数，格式需以QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW或MECH_SWITCH_STATE_SIM_REMOVED开头

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 标准化参数：转为大写并将空格替换为下划线，统一格式处理
                normalized_param = param.upper().replace(' ', '_')

                # 正则表达式：匹配两种参数前缀格式
                pattern = r'^(QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW_[0-9A-Z]{2}_[0-9A-Z]{4}|MECH_SWITCH_STATE_SIM_REMOVED)'
                match = re.match(pattern, normalized_param)

                if not match:
                    # 模式不匹配时抛出错误
                    raise ValueError(
                        f"无效的参数格式: {param}，参数必须符合以下格式之一：\n"
                        f"QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW_[0-9A-Z]{2}_[0-9A-Z]{4}、MECH_SWITCH_STATE_SIM_REMOVED"
                    )

                # 获取匹配的参数类型
                param_type = match.group(1)

                # 初始化参数字典，QC明确为高通设备
                params = {
                    "device": "高通设备",  # 将"未知设备"更新为"高通设备"，因为QC代表高通
                    "detail_type": "basic"  # 仅保留基础模式
                }

                # 根据参数类型初始化不同的测试说明
                if param_type.startswith("QC_USIM_MECHANICAL_SWITCH_REMOVED_RAW"):
                    # USIM机械开关移除原始数据检测相关测试说明
                    base_desc_zh = (f"验证{params['device']}的USIM机械开关移除原始数据检测基础功能的工作状态")
                    base_desc_en = (
                        f"Verify the basic function of USIM mechanical switch removal raw data detection for {params['device']}")

                    base_items_zh = [
                        "1. 开关移除状态原始数据读取准确性（与实际状态对比）",
                        "2. 原始数据获取响应时间验证（单次获取耗时≤100ms）",
                        "3. 连续数据采集稳定性测试（连续100次无数据丢失）",
                        "4. 原始数据传输完整性验证（无传输错误）"
                    ]
                    base_items_en = [
                        "1. Accuracy of switch removal status raw data reading (compared with actual status)",
                        "2. Verification of raw data retrieval response time (single retrieval time ≤ 100ms)",
                        "3. Stability test for continuous data collection (100 consecutive times without data loss)",
                        "4. Verification of raw data transmission integrity (no transmission errors)"
                    ]

                    # 基础模式专属测试项
                    specific_item_zh = "1.1 原始数据噪声水平检测（噪声值≤5mV）"
                    specific_item_en = "1.1 Raw data noise level detection (noise value ≤ 5mV)"
                    purpose_suffix_zh = "，重点验证原始数据采集的准确性和稳定性"
                    purpose_suffix_en = ", with focus on accuracy and stability of raw data collection"

                else:  # MECH_SWITCH_STATE_SIM_REMOVED
                    # USIM机械开关状态检测相关测试说明
                    base_desc_zh = (f"验证{params['device']}的USIM机械开关状态识别与上报基础功能")
                    base_desc_en = (
                        f"Verify the basic function of USIM mechanical switch state recognition and reporting for {params['device']}")

                    base_items_zh = [
                        "1. 开关状态（插入/移除）识别准确性",
                        "2. 状态变化识别响应时间验证（状态变化后≤200ms识别）",
                        "3. 开关状态连续监测稳定性（连续30分钟无错误上报）",
                        "4. 状态识别算法容错能力测试（抗电磁干扰能力）"
                    ]
                    base_items_en = [
                        "1. Accuracy of switch state (inserted/removed) recognition",
                        "2. Verification of state change recognition response time (≤200ms after state change)",
                        "3. Stability of continuous switch state monitoring (no false reports for 30 consecutive minutes)",
                        "4. Fault tolerance test of state recognition algorithm (anti-electromagnetic interference capability)"
                    ]

                    # 基础模式专属测试项
                    specific_item_zh = "1.1 边缘状态识别准确性（半插入状态识别）"
                    specific_item_en = "1.1 Accuracy of edge state recognition (half-inserted state recognition)"
                    purpose_suffix_zh = "，重点验证状态识别的准确性和及时性"
                    purpose_suffix_en = ", with focus on accuracy and timeliness of state recognition"

                # 组装最终描述
                desc = {
                    "test_purpose_zh": f"{base_desc_zh}，确保开关状态信息准确可靠{purpose_suffix_zh}",
                    "test_items_zh": base_items_zh.copy(),
                    "test_purpose_en": f"{base_desc_en}, ensure switch state information is accurate and reliable{purpose_suffix_en}",
                    "test_items_en": base_items_en.copy()
                }

                # 添加基础模式专属测试项
                desc["test_items_zh"].insert(1, specific_item_zh)
                desc["test_items_en"].insert(1, specific_item_en)

                return desc

            def parse_wifi_rx_test_description(self, param: str) -> dict:
                """
                解析MTK WLAN接收测试参数（仅支持RX场景），生成中英文测试说明

                参数:
                    param: MTK WLAN接收测试参数（如：MTK_WLAN2.4G_RX_C0_HQA_RSSI_MCH7）
                           标准格式：MTK_WLAN[2.4G/5G]_RX_C[0-14]_[HQA/LQA/BEAM]_RSSI_MCH[1-16]

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # ✅ 仅匹配RX场景的正则（移除TX选项）
                pattern = r"MTK_WLAN(?P<band>\d+\.?\d*G)_?RX_(?P<channel>C\d+)_(?P<test_mode>HQA|LQA|BEAM)_RSSI_(?P<mode>MCH\d+)"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN接收参数: {param}，标准格式示例：MTK_WLAN2.4G_RX_C1_HQA_RSSI_MCH7")

                # 解析参数（固定为接收场景）
                params = {
                    "band": match.group('band'),
                    "channel": match.group('channel')[1:],  # C0 → 0
                    "test_mode": {  # 仅保留RX相关模式
                        "HQA": "高量子聚合帧（HT/VHT/MU-MIMO）",
                        "LQA": "低量子单帧（legacy 802.11n）",
                        "BEAM": "波束赋形接收"
                    }[match.group('test_mode')],
                    "mode": match.group('mode')  # MCH1-MCH16（MTK私有测试模式）
                }

                # 根据param是否包含'HQA'设置test_mode_item
                test_mode_item = ''
                if 'HQA' in param.upper():
                    test_mode_item = 'HQA'
                elif 'LQA' in param.upper():
                    test_mode_item = 'LQA'
                elif 'BEAM' in param.upper():
                    test_mode_item = 'BEAM'

                # 测试目的（固定为接收场景）
                purpose_zh = f"验证{params['band']}频段接收链路在{params['test_mode'][test_mode_item]}模式下的C{params['channel']}信道RSSI测量准确性"
                purpose_en = f"Validate RSSI measurement accuracy of {params['band']} receive link on channel {params['channel']} in {params['test_mode'][test_mode_item]} mode"

                # 测试项（深度优化RX场景）
                test_items_zh = [
                    f"1. {params['band']}频段C{params['channel']}信道RSSI绝对值误差（±1dBm，MTK标准：±0.8dBm）",
                    f"2. {params['test_mode'][test_mode_item]}模式下RSSI稳定性（连续100帧波动≤0.5dBm，产线标准）",
                    f"3. 不同MCS等级（0-11）RSSI线性度（R²≥0.995）",
                    f"4. 天线分集RSSI一致性（主副天线差值≤1dBm，MIMO必备）",
                    f"5. 聚合帧长度影响（A-MPDU 11454字节 vs 1024字节，RSSI偏差≤0.8dBm）",
                    f"6. 干扰抗噪能力（AWGN SNR=10dB时，RSSI误差≤1.5dBm，3GPP标准）"
                ]
                test_items_en = [
                    f"1. RSSI absolute error at {params['band']} Ch{params['channel']} (±1dBm, MTK spec: ±0.8dBm)",
                    f"2. RSSI stability in {params['test_mode'][test_mode_item]} (≤0.5dBm fluctuation over 100 frames, production spec)",
                    f"3. RSSI linearity across MCS 0-11 (R²≥0.995)",
                    f"4. Antenna diversity consistency (≤1dBm difference, MIMO requirement)",
                    f"5. A-MPDU length impact (11454B vs 1024B, ≤0.8dBm deviation)",
                    f"6. AWGN immunity (SNR=10dB, error≤1.5dBm, 3GPP compliant)"
                ]

                return {
                    "test_purpose_zh": f"{purpose_zh}（{params['test_mode']}帧结构）",
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": f"{purpose_en} ({params['test_mode']} frame structure)",
                    "test_items_en": test_items_en,
                    "param_spec": params  # 调试用参数详情
                }

            def parse_wifi_rx_test_description2(self, param: str) -> dict:
                """
                解析MTK WLAN接收测试参数（仅支持RX场景），生成中英文测试说明

                参数:
                    param: MTK WLAN接收测试参数（如：MTK_WLAN_2.4G_C0_CH07_RSSI_ANT_CW）
                           标准格式：MTK_WLAN_[2.4G/5G]_C[0-14]_CH[1-16]_RSSI_ANT_CW

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # 匹配新格式的正则
                pattern = r"MTK_WLAN_(?P<band>\d+\.?\d*G)_C(?P<channel>\d+)_(H|M|L)CH(?P<ch_num>\d+)_RSSI_ANT_CW"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN接收参数: {param}，标准格式示例：MTK_WLAN_2.4G_C0_CH07_RSSI_ANT_CW")

                # 解析参数（固定为接收场景）
                params = {
                    "band": match.group('band'),
                    "channel": match.group('channel'),
                    "ch_num": match.group('ch_num')
                }

                # 测试目的（固定为接收场景）
                purpose_zh = f"验证{params['band']}频段接收链路在C{params['channel']}信道，CH{params['ch_num']}下的RSSI测量准确性"
                purpose_en = f"Validate RSSI measurement accuracy of {params['band']} receive link on channel C{params['channel']}, CH{params['ch_num']}"

                # 测试项（深度优化RX场景）
                test_items_zh = [
                    f"1. {params['band']}频段C{params['channel']}信道，CH{params['ch_num']}下RSSI绝对值误差（±1dBm，MTK标准：±0.8dBm）",
                    f"2. RSSI稳定性（连续100帧波动≤0.5dBm，产线标准）",
                    f"3. 不同MCS等级（0-11）RSSI线性度（R²≥0.995）",
                    f"4. 天线分集RSSI一致性（主副天线差值≤1dBm，MIMO必备）",
                    f"5. 聚合帧长度影响（A-MPDU 11454字节 vs 1024字节，RSSI偏差≤0.8dBm）",
                    f"6. 干扰抗噪能力（AWGN SNR=10dB时，RSSI误差≤1.5dBm，3GPP标准）"
                ]
                test_items_en = [
                    f"1. RSSI absolute error at {params['band']} C{params['channel']}, CH{params['ch_num']} (±1dBm, MTK spec: ±0.8dBm)",
                    f"2. RSSI stability (≤0.5dBm fluctuation over 100 frames, production spec)",
                    f"3. RSSI linearity across MCS 0-11 (R²≥0.995)",
                    f"4. Antenna diversity consistency (≤1dBm difference, MIMO requirement)",
                    f"5. A-MPDU length impact (11454B vs 1024B, ≤0.8dBm deviation)",
                    f"6. AWGN immunity (SNR=10dB, error≤1.5dBm, 3GPP compliant)"
                ]

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "param_spec": params  # 调试用参数详情
                }

            def parse_wifi_rx_test_description3(self, param: str) -> dict:
                """
                解析MTK WLAN接收测试参数（仅支持RX场景），生成中英文测试说明

                参数:
                    param: MTK WLAN接收测试参数（如：MTK_WLAN_2.4G_C0_CH07_RSSI_ANT_CW）
                           标准格式：MTK_WLAN_[2.4G/5.0G]_C[0-14]_CH[1-16]_RSSI_ANT_CW

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # 匹配新格式的正则
                pattern = r"MTK_WLAN_(?P<band>\d+\.?\d*G)_C(?P<channel>\d+)_CH(?P<ch_num>\d+)_RSSI_ANT"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN接收参数: {param}，标准格式示例：MTK_WLAN_2.4G_C0_CH07_RSSI_ANT")

                # 解析参数（固定为接收场景）
                params = {
                    "band": match.group('band'),
                    "channel": match.group('channel'),
                    "ch_num": match.group('ch_num')
                }

                # 测试目的（固定为接收场景）
                purpose_zh = f"验证{params['band']}频段接收链路在C{params['channel']}信道，CH{params['ch_num']}下的RSSI测量准确性"
                purpose_en = f"Validate RSSI measurement accuracy of {params['band']} receive link on channel C{params['channel']}, CH{params['ch_num']}"

                # 测试项（深度优化RX场景）
                test_items_zh = [
                    f"1. {params['band']}频段C{params['channel']}信道，CH{params['ch_num']}下RSSI绝对值误差（±1dBm，MTK标准：±0.8dBm）",
                    f"2. RSSI稳定性（连续100帧波动≤0.5dBm，产线标准）",
                    f"3. 不同MCS等级（0-11）RSSI线性度（R²≥0.995）",
                    f"4. 天线分集RSSI一致性（主副天线差值≤1dBm，MIMO必备）",
                    f"5. 聚合帧长度影响（A-MPDU 11454字节 vs 1024字节，RSSI偏差≤0.8dBm）",
                    f"6. 干扰抗噪能力（AWGN SNR=10dB时，RSSI误差≤1.5dBm，3GPP标准）"
                ]
                test_items_en = [
                    f"1. RSSI absolute error at {params['band']} C{params['channel']}, CH{params['ch_num']} (±1dBm, MTK spec: ±0.8dBm)",
                    f"2. RSSI stability (≤0.5dBm fluctuation over 100 frames, production spec)",
                    f"3. RSSI linearity across MCS 0-11 (R²≥0.995)",
                    f"4. Antenna diversity consistency (≤1dBm difference, MIMO requirement)",
                    f"5. A-MPDU length impact (11454B vs 1024B, ≤0.8dBm deviation)",
                    f"6. AWGN immunity (SNR=10dB, error≤1.5dBm, 3GPP compliant)"
                ]

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "param_spec": params  # 调试用参数详情
                }

            def parse_wifi_rx_test_description4(self, param: str) -> dict:
                """
                解析MTK WLAN接收测试参数（仅支持特定RX场景），生成中英文测试说明

                参数:
                    param: MTK WLAN接收测试参数（如：MTK_WLAN2.4G_RX_V2_RSSI_CH07_X）
                           标准格式：MTK_WLAN[2.4G/5.0G]_RX_V[版本号]_RSSI_CH[信道号]_X

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # 匹配目标格式的正则表达式
                pattern = r"MTK_WLAN(?P<band>\d+\.\d+G)_RX_V(?P<version>\d+)_RSSI_CH(?P<channel>\d+)_X"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN接收参数: {param}，标准格式示例：MTK_WLAN2.4G_RX_V2_RSSI_CH07_X")

                # 解析参数（固定为接收场景）
                params = {
                    "band": match.group('band'),
                    "version": match.group('version'),
                    "channel": match.group('channel')
                }

                # 测试目的（基于版本和信道的接收场景）
                purpose_zh = f"验证{params['band']}频段V{params['version']}版本接收链路在CH{params['channel']}信道下的RSSI测量性能"
                purpose_en = f"Validate RSSI measurement performance of {params['band']} receive link (V{params['version']}) on channel CH{params['channel']}"

                # 测试项（针对该版本的RX场景优化）
                test_items_zh = [
                    f"1. {params['band']}频段V{params['version']}版本CH{params['channel']}信道RSSI绝对值误差（±1dBm）",
                    f"2. 温度稳定性（-40℃~85℃范围内，RSSI漂移≤2dBm）",
                    f"3. 长期稳定性（连续24小时测试，误差≤1.2dBm）",
                    f"4. 不同带宽模式（20/40/80MHz）下RSSI一致性（差值≤1dBm）",
                    f"5. 接收灵敏度与RSSI相关性（R²≥0.99）",
                    f"6. 多用户场景下RSSI测量准确性（MU-MIMO 4用户配置）"
                ]
                test_items_en = [
                    f"1. RSSI absolute error at {params['band']} V{params['version']} CH{params['channel']} (±1dBm)",
                    f"2. Temperature stability (-40℃~85℃, RSSI drift ≤2dBm)",
                    f"3. Long-term stability (24h continuous test, error ≤1.2dBm)",
                    f"4. RSSI consistency across bandwidth modes (20/40/80MHz, difference ≤1dBm)",
                    f"5. Correlation between receive sensitivity and RSSI (R²≥0.99)",
                    f"6. RSSI measurement accuracy in multi-user scenario (MU-MIMO 4 users)"
                ]

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "param_spec": params  # 调试用参数详情
                }

            def parse_wifi_rx_test_description5(self, param: str) -> dict:
                """
                解析MTK WLAN接收测试参数（支持基础RX场景），生成中英文测试说明

                参数:
                    param: MTK WLAN接收测试参数（如：MTK_WLAN_2.4G_CH06_RSSI）
                           标准格式：MTK_WLAN_[2.4G/5.0G]_CH[信道号]_RSSI

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # 匹配目标格式的正则表达式
                pattern = r"MTK_WLAN_(?P<band>\d+\.\d+G)_CH(?P<channel>\d+)_RSSI"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN接收参数: {param}，标准格式示例：MTK_WLAN_2.4G_CH06_RSSI")

                # 解析参数（固定为接收场景）
                params = {
                    "band": match.group('band'),
                    "channel": match.group('channel')
                }

                # 测试目的（基础RX场景）
                purpose_zh = f"验证{params['band']}频段接收链路在CH{params['channel']}信道下的RSSI基础测量性能"
                purpose_en = f"Validate basic RSSI measurement performance of {params['band']} receive link on channel CH{params['channel']}"

                # 测试项（基础RX场景核心指标）
                test_items_zh = [
                    f"1. {params['band']}频段CH{params['channel']}信道RSSI基础测量误差（±2dBm）",
                    f"2. 标准信号强度下的RSSI重复性（连续10次测量偏差≤1dBm）",
                    f"3. 宽功率范围（-90dBm至-30dBm）的RSSI线性响应（R²≥0.99）",
                    f"4. 信道中心与边缘频率点的RSSI一致性（差值≤1.5dBm）",
                    f"5. 常温环境下（25℃）的RSSI稳定性（1小时波动≤0.8dBm）",
                    f"6. 标准带宽（20MHz）下的RSSI测量精度（符合MTK基础规范）"
                ]
                test_items_en = [
                    f"1. Basic RSSI measurement error at {params['band']} CH{params['channel']} (±2dBm)",
                    f"2. RSSI repeatability under standard signal strength (≤1dBm deviation over 10 measurements)",
                    f"3. RSSI linear response across wide power range (-90dBm to -30dBm, R²≥0.99)",
                    f"4. RSSI consistency between channel center and edge (difference ≤1.5dBm)",
                    f"5. RSSI stability at room temperature (25℃, ≤0.8dBm fluctuation in 1 hour)",
                    f"6. RSSI measurement accuracy at standard bandwidth (20MHz, compliant with MTK basic specifications)"
                ]

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "param_spec": params  # 调试用参数详情
                }

            def parse_wifi_rx_test_description3_for_qc_v1(self, param: str) -> dict:
                """
                解析高通WLAN接收测试参数（支持多种RX场景及校准场景），生成中英文测试说明

                参数:
                    param: 高通WLAN接收测试参数（如：QC_WLAN_2.4GHZ_11n_RADIATED_RX_C0_MCH_EQ 或 QC_WLAN_5.0GHz_80211a_RADIATED_RX_C0_LCH_-60）
                           支持多种标准格式，包括带数字字母混合标识的EQ和校准功率模式

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # 修复正则表达式：1. 修正重复分组名问题 2. 确保匹配80211a等标准格式
                pattern = r"^(QC_WLAN_(?P<band1>2\.4GHZ|5\.0GHZ)_(?P<standard1>\d+[a-zA-Z])_RADIATED_RX_C(?P<channel1>\d+)_(?P<mode1>(H|M|L)CH(\d*?))_(?P<rssi>-?\d+)|" \
                          r"QC_WLAN_(?P<band2>2\.4GHZ|5\.0GHZ)_(?P<standard2>\d+[a-zA-Z])_RAD_RX_C(?P<channel2>\d+)_CAL_(?P<mode2>(H|M|L)CH)_ANT_CW|" \
                          r"QC_WLAN_(?P<band3>2\.4GHZ|5\.0GHZ)_(?P<standard3>\d+[a-zA-Z])_RADIATED_RX_C(?P<channel3>\d+)_(?P<mode3>(H|M|L)CH)_EQ|" \
                          r"QC_WLAN_(?P<band4>2\.4GHZ|5\.0GHZ)_(?P<standard4>\d+[a-zA-Z])_RAD_RX_C(?P<channel4>\d+)_CAL_POWER_(?P<mode4>(H|M|L)CH))$"
                match = re.match(pattern, param.upper())  # 使用upper()确保匹配时不区分大小写

                if not match:
                    raise ValueError(
                        f"无效的高通WLAN接收参数: {param}，标准格式示例：\n"
                        f"1. QC_WLAN_5.0GHZ_80211a_RADIATED_RX_C1_LCH36_-60\n"
                        f"2. QC_WLAN_5.0GHZ_80211a_RAD_RX_C0_CAL_LCH_ANT_CW\n"
                        f"3. QC_WLAN_2.4GHZ_11n_RADIATED_RX_C0_MCH_EQ\n"
                        f"4. QC_WLAN_2.4GHZ_11ac_RAD_RX_C1_CAL_POWER_LCH"
                    )

                # 解析参数（区分不同场景类型）
                scenario_type = None
                params = {}

                # 检查匹配的是哪种模式
                if match.group('band1'):
                    # 普通RX场景（修复标准解析逻辑）
                    scenario_type = "regular_rx"
                    is_calibration = False
                    standard = match.group('standard1')
                    # 统一标准解析逻辑，支持80211a/n/ac等格式
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band1'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel1'),
                        "mode": match.group('mode1'),
                        "rssi": f"{match.group('rssi')}dBm",
                        "scenario": "常规接收",
                        "channel_type": "主信道" if match.group('mode1').startswith('M') else "低信道",
                        "freq_info": "2401-2483.5MHz (ISM频段)" if match.group(
                            'band1') == '2.4GHZ' else "5150-5825MHz (UNII频段)"
                    }
                elif match.group('band2'):
                    # 校准场景（天线连续波）
                    scenario_type = "calibration_ant_cw"
                    is_calibration = True
                    standard = match.group('standard2')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band2'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel2'),
                        "mode": match.group('mode2'),
                        "scenario": "天线校准",
                        "channel_type": "主信道" if match.group('mode2').startswith('M') else "低信道",
                        "freq_info": "2401-2483.5MHz (ISM频段)" if match.group(
                            'band2') == '2.4GHZ' else "5150-5825MHz (UNII频段)"
                    }
                elif match.group('band3'):
                    # EQ模式场景
                    scenario_type = "eq_mode"
                    is_calibration = False
                    standard = match.group('standard3')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band3'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel3'),
                        "mode": match.group('mode3'),
                        "scenario": "均衡模式接收",
                        "channel_type": "主信道" if match.group('mode3').startswith('M') else "低信道",
                        "freq_info": "2401-2483.5MHz (ISM频段)"
                    }
                elif match.group('band4'):
                    # 校准功率场景
                    scenario_type = "calibration_power"
                    is_calibration = True
                    standard = match.group('standard4')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band4'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel4'),
                        "mode": match.group('mode4'),
                        "scenario": "功率校准",
                        "channel_type": "主信道" if match.group('mode4').startswith('M') else "低信道",
                        "freq_info": "2401-2483.5MHz (ISM频段)"
                    }

                # 测试目的（根据不同场景类型）
                if scenario_type == "regular_rx":
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收模式C{params['channel']}通道{params['channel_type']}（{params['mode']}）的"
                                  f"接收信号强度（RSSI）测量准确性，测试信号强度为{params['rssi']}")
                    purpose_en = (
                        f"Validate RSSI measurement accuracy of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX mode at channel C{params['channel']}, {params['channel_type']} ({params['mode']}) "
                        f"with test signal strength {params['rssi']}")
                elif scenario_type == "calibration_ant_cw":
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收校准模式C{params['channel']}通道{params['channel_type']}（{params['mode']}）的"
                                  f"天线连续波（CW）接收一致性")
                    purpose_en = (
                        f"Validate antenna CW reception consistency of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX calibration mode at channel C{params['channel']}, {params['channel_type']} ({params['mode']})")
                elif scenario_type == "eq_mode":
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收均衡模式（EQ）C{params['channel']}通道{params['channel_type']}（{params['mode']}）的"
                                  f"信号均衡与接收性能")
                    purpose_en = (
                        f"Validate signal equalization and reception performance of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX EQ mode at channel C{params['channel']}, {params['channel_type']} ({params['mode']})")
                else:  # calibration_power
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收功率校准模式C{params['channel']}通道{params['channel_type']}（{params['mode']}）的"
                                  f"功率测量准确性与校准效果")
                    purpose_en = (
                        f"Validate power measurement accuracy and calibration effect of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX power calibration mode at channel C{params['channel']}, {params['channel_type']} ({params['mode']})")

                # 基础测试项（通用部分）
                test_items_zh = [
                    f"1. {params['band']}频段C{params['channel']}通道的接收链路增益一致性（±0.5dB，高通校准标准）",
                    f"2. {params['mode']}模式下的天线端口隔离度（≥25dB，MIMO配置）",
                    f"3. 接收频率偏移（≤±20ppm，802.11标准）",
                    f"4. 本振泄漏抑制（≥40dBc，高通射频规范）"
                ]
                test_items_en = [
                    f"1. RX chain gain consistency at {params['band']} channel C{params['channel']} (±0.5dB, Qualcomm cal spec)",
                    f"2. Antenna port isolation in {params['mode']} mode (≥25dB, MIMO config)",
                    f"3. RX frequency offset (≤±20ppm, 802.11 standard)",
                    f"4. LO leakage suppression (≥40dBc, Qualcomm RF spec)"
                ]

                # 场景专属测试项
                if scenario_type == "regular_rx":
                    test_items_zh.extend([
                        f"5. 信号强度{params['rssi']}下的接收灵敏度（PER≤10%@MCS0）",
                        f"6. {params['mode']}模式下的RSSI稳定性（连续500帧波动≤0.3dBm）",
                        f"7. 不同调制方式的RSSI一致性（差值≤0.5dBm）"
                    ])
                    test_items_en.extend([
                        f"5. RX sensitivity at {params['rssi']} (PER≤10%@MCS0)",
                        f"6. RSSI stability in {params['mode']} mode (≤0.3dBm fluctuation over 500 frames)",
                        f"7. RSSI consistency across modulations (≤0.5dBm difference)"
                    ])
                elif scenario_type == "calibration_ant_cw":
                    test_items_zh.extend([
                        f"5. 连续波（CW）信号接收灵敏度（≤-100dBm@BER=1e-6）",
                        f"6. 多天线校准一致性（各通道增益差值≤0.3dB）",
                        f"7. 温度漂移补偿效果（-40~85℃范围内偏差≤1dB）"
                    ])
                    test_items_en.extend([
                        f"5. CW signal reception sensitivity (≤-100dBm@BER=1e-6)",
                        f"6. Multi-antenna calibration consistency (gain difference ≤0.3dB across channels)",
                        f"7. Temperature drift compensation (-40~85℃, deviation ≤1dB)"
                    ])
                elif scenario_type == "eq_mode":
                    test_items_zh.extend([
                        f"5. 均衡器（EQ）频率响应平坦度（±0.5dB，20MHz带宽内）",
                        f"6. 不同信号强度下的EQ自适应响应时间（≤100µs）",
                        f"7. 多径环境下的EQ校正效果（EVM改善≥6dB）",
                        f"8. 邻近信道干扰抑制（≥30dB，±20MHz偏移）"
                    ])
                    test_items_en.extend([
                        f"5. Equalizer (EQ) frequency response flatness (±0.5dB across 20MHz bandwidth)",
                        f"6. EQ adaptive response time under varying signal strength (≤100µs)",
                        f"7. EQ correction effectiveness in multipath environment (EVM improvement ≥6dB)",
                        f"8. Adjacent channel interference rejection (≥30dB at ±20MHz offset)"
                    ])
                else:  # calibration_power
                    test_items_zh.extend([
                        f"5. 功率校准精度（目标值±0.2dBm，全温度范围内）",
                        f"6. 功率检测线性度（R²≥0.999，-80~-20dBm范围）",
                        f"7. 校准后功率稳定性（24小时漂移≤0.3dBm）",
                        f"8. 不同信道间的功率一致性（差值≤0.5dBm）"
                    ])
                    test_items_en.extend([
                        f"5. Power calibration accuracy (target ±0.2dBm across full temperature range)",
                        f"6. Power detection linearity (R²≥0.999, -80~-20dBm range)",
                        f"7. Post-calibration power stability (≤0.3dBm drift over 24 hours)",
                        f"8. Power consistency across channels (≤0.5dBm difference)"
                    ])

                # 频段专属测试项
                if params['band'] == '5.0GHZ' and scenario_type in ["regular_rx", "calibration_ant_cw"]:
                    test_items_zh.append(f"8. 动态频率选择（DFS）功能验证（校准模式下雷达信号检测率100%）"
                                         if is_calibration else
                                         f"8. 动态频率选择（DFS）响应时间（≤100ms）")
                    test_items_en.append(
                        f"8. Dynamic Frequency Selection (DFS) verification (100% radar detection in calibration)"
                        if is_calibration else
                        f"8. Dynamic Frequency Selection (DFS) response time (≤100ms)")

                if params['band'] == '2.4GHZ':
                    # 2.4GHz频段专属测试项，根据场景调整
                    if scenario_type in ["regular_rx", "calibration_ant_cw"]:
                        test_items_zh.append(f"8. 蓝牙共存校准（BT信号存在时增益补偿误差≤0.5dB）"
                                             if is_calibration else
                                             f"8. 蓝牙共存干扰下的RSSI稳定性（偏差≤1dBm）")
                        test_items_en.append(
                            f"8. Bluetooth coexistence calibration (gain compensation error ≤0.5dB with BT signal)"
                            if is_calibration else
                            f"8. RSSI stability under Bluetooth coexistence (≤1dBm deviation)")
                    elif scenario_type == "eq_mode":
                        test_items_zh.append(f"9. 2.4GHZ ISM频段多系统共存下的EQ适应性（Wi-Fi/BT/ZigBee环境）")
                        test_items_en.append(
                            f"9. EQ adaptability in 2.4GHZ ISM band multi-system coexistence (Wi-Fi/BT/ZigBee)")
                    else:  # calibration_power
                        test_items_zh.append(f"9. 功率校准对蓝牙共存的影响（BT吞吐量损失≤5%）")
                        test_items_en.append(
                            f"9. Impact of power calibration on Bluetooth coexistence (BT throughput loss ≤5%)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "param_spec": params,  # 调试用参数详情
                    "is_calibration": is_calibration,  # 标识是否为校准场景
                    "scenario_type": scenario_type  # 场景类型细分
                }


            def parse_wifi_rx_test_description3_for_qc(self, param: str) -> dict:
                """
                解析高通WLAN接收测试参数（支持多种RX场景及校准场景），生成中英文测试说明

                参数:
                    param: 高通WLAN接收测试参数（如：QC_WLAN_2.4GHZ_11n_RADIATED_RX_C0_MCH_EQ 或 QC_WLAN_5.0GHz_80211a_RADIATED_RX_C0_LCH_-60）
                           支持多种标准格式，包括带数字字母混合标识的EQ和校准功率模式

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # 修复正则表达式：1. 修正重复分组名问题 2. 确保匹配80211a等标准格式
                pattern = r"^(QC_WLAN_(?P<band1>2\.4GHZ|5\.0GHZ)_(?P<standard1>\d+[a-zA-Z])_RADIATED_RX_C(?P<channel1>\d+)_(?P<mode1>(H|M|L)CH(\d*?))_(?P<rssi>-?\d+)|" \
                          r"QC_WLAN_(?P<band2>2\.4GHZ|5\.0GHZ)_(?P<standard2>\d+[a-zA-Z])_RAD_RX_C(?P<channel2>\d+)_CAL_(?P<mode2>(H|M|L)CH)_ANT_CW|" \
                          r"QC_WLAN_(?P<band3>2\.4GHZ|5\.0GHZ)_(?P<standard3>\d+[a-zA-Z])_RADIATED_RX_C(?P<channel3>\d+)_(?P<mode3>(H|M|L)CH)_EQ|" \
                          r"QC_WLAN_(?P<band4>2\.4GHZ|5\.0GHZ)_(?P<standard4>\d+[a-zA-Z])_RAD_RX_C(?P<channel4>\d+)_CAL_POWER_(?P<mode4>(H|M|L)CH))$"
                match = re.match(pattern, param.upper())  # 使用upper()确保匹配时不区分大小写

                if not match:
                    raise ValueError(
                        f"无效的高通WLAN接收参数: {param}，标准格式示例：\n"
                        f"1. QC_WLAN_5.0GHZ_80211a_RADIATED_RX_C1_LCH36_-60\n"
                        f"2. QC_WLAN_5.0GHZ_80211a_RAD_RX_C0_CAL_LCH_ANT_CW\n"
                        f"3. QC_WLAN_2.4GHZ_11n_RADIATED_RX_C0_MCH_EQ\n"
                        f"4. QC_WLAN_2.4GHZ_11ac_RAD_RX_C1_CAL_POWER_LCH"
                    )

                # 解析参数（区分不同场景类型）
                scenario_type = None
                params = {}

                # 检查匹配的是哪种模式
                if match.group('band1'):
                    # 普通RX场景（修复标准解析逻辑）
                    scenario_type = "regular_rx"
                    is_calibration = False
                    standard = match.group('standard1')
                    # 统一标准解析逻辑，支持80211a/n/ac等格式
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band1'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel1'),
                        "mode": match.group('mode1'),
                        "rssi": f"{match.group('rssi')}dBm",
                        # 新增：中英文场景描述
                        "scenario_zh": "常规接收",
                        "scenario_en": "Regular Reception",
                        # 新增：中英文信道类型描述
                        "channel_type_zh": "主信道" if match.group('mode1').startswith('M') else "低信道",
                        "channel_type_en": "Main Channel" if match.group('mode1').startswith('M') else "Low Channel",
                        # 新增：中英文频段信息描述
                        "freq_info_zh": "2401-2483.5MHz (ISM频段)" if match.group('band1') == '2.4GHZ' else "5150-5825MHz (UNII频段)",
                        "freq_info_en": "2401-2483.5MHz (ISM Band)" if match.group('band1') == '2.4GHZ' else "5150-5825MHz (UNII Band)"
                    }
                elif match.group('band2'):
                    # 校准场景（天线连续波）
                    scenario_type = "calibration_ant_cw"
                    is_calibration = True
                    standard = match.group('standard2')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band2'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel2'),
                        "mode": match.group('mode2'),
                        # 新增：中英文场景描述
                        "scenario_zh": "天线校准",
                        "scenario_en": "Antenna Calibration",
                        # 新增：中英文信道类型描述
                        "channel_type_zh": "主信道" if match.group('mode2').startswith('M') else "低信道",
                        "channel_type_en": "Main Channel" if match.group('mode2').startswith('M') else "Low Channel",
                        # 新增：中英文频段信息描述
                        "freq_info_zh": "2401-2483.5MHz (ISM频段)" if match.group('band2') == '2.4GHZ' else "5150-5825MHz (UNII频段)",
                        "freq_info_en": "2401-2483.5MHz (ISM Band)" if match.group('band2') == '2.4GHZ' else "5150-5825MHz (UNII Band)"
                    }
                elif match.group('band3'):
                    # EQ模式场景
                    scenario_type = "eq_mode"
                    is_calibration = False
                    standard = match.group('standard3')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band3'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel3'),
                        "mode": match.group('mode3'),
                        # 新增：中英文场景描述
                        "scenario_zh": "均衡模式接收",
                        "scenario_en": "Equalization Mode Reception",
                        # 新增：中英文信道类型描述
                        "channel_type_zh": "主信道" if match.group('mode3').startswith('M') else "低信道",
                        "channel_type_en": "Main Channel" if match.group('mode3').startswith('M') else "Low Channel",
                        # 新增：中英文频段信息描述
                        "freq_info_zh": "2401-2483.5MHz (ISM频段)" if match.group('band3') == '2.4GHZ' else "5150-5825MHz (UNII频段)",
                        "freq_info_en": "2401-2483.5MHz (ISM Band)" if match.group('band3') == '2.4GHZ' else "5150-5825MHz (UNII Band)"
                    }
                elif match.group('band4'):
                    # 校准功率场景
                    scenario_type = "calibration_power"
                    is_calibration = True
                    standard = match.group('standard4')
                    formatted_standard = f"802.11{standard[3:].lower()}" if standard.startswith('80211') else \
                        f"802.11{standard[2:].lower()}" if standard.startswith('11') else standard

                    params = {
                        "band": match.group('band4'),
                        "standard": formatted_standard,
                        "original_standard": standard,
                        "channel": match.group('channel4'),
                        "mode": match.group('mode4'),
                        # 新增：中英文场景描述
                        "scenario_zh": "功率校准",
                        "scenario_en": "Power Calibration",
                        # 新增：中英文信道类型描述
                        "channel_type_zh": "主信道" if match.group('mode4').startswith('M') else "低信道",
                        "channel_type_en": "Main Channel" if match.group('mode4').startswith('M') else "Low Channel",
                        # 新增：中英文频段信息描述
                        "freq_info_zh": "2401-2483.5MHz (ISM频段)" if match.group('band4') == '2.4GHZ' else "5150-5825MHz (UNII频段)",
                        "freq_info_en": "2401-2483.5MHz (ISM Band)" if match.group('band4') == '2.4GHZ' else "5150-5825MHz (UNII Band)"
                    }

                # 测试目的（根据不同场景类型，同步使用params的中英文字段）
                if scenario_type == "regular_rx":
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收模式C{params['channel']}通道{params['channel_type_zh']}（{params['mode']}）的"
                                  f"接收信号强度（RSSI）测量准确性，测试信号强度为{params['rssi']}")
                    purpose_en = (
                        f"Validate RSSI measurement accuracy of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX mode at channel C{params['channel']}, {params['channel_type_en']} ({params['mode']}) "
                        f"with test signal strength {params['rssi']}")
                elif scenario_type == "calibration_ant_cw":
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收校准模式C{params['channel']}通道{params['channel_type_zh']}（{params['mode']}）的"
                                  f"天线连续波（CW）接收一致性")
                    purpose_en = (
                        f"Validate antenna CW reception consistency of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX calibration mode at channel C{params['channel']}, {params['channel_type_en']} ({params['mode']})")
                elif scenario_type == "eq_mode":
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收均衡模式（EQ）C{params['channel']}通道{params['channel_type_zh']}（{params['mode']}）的"
                                  f"信号均衡与接收性能")
                    purpose_en = (
                        f"Validate signal equalization and reception performance of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX EQ mode at channel C{params['channel']}, {params['channel_type_en']} ({params['mode']})")
                else:  # calibration_power
                    purpose_zh = (f"验证高通{params['band']} {params['standard']}标准下，"
                                  f"辐射接收功率校准模式C{params['channel']}通道{params['channel_type_zh']}（{params['mode']}）的"
                                  f"功率测量准确性与校准效果")
                    purpose_en = (
                        f"Validate power measurement accuracy and calibration effect of Qualcomm {params['band']} {params['standard']} "
                        f"radiated RX power calibration mode at channel C{params['channel']}, {params['channel_type_en']} ({params['mode']})")

                # 基础测试项（通用部分，同步使用params的中英文字段）
                test_items_zh = [
                    f"1. {params['band']}频段C{params['channel']}通道的接收链路增益一致性（±0.5dB，高通校准标准）",
                    f"2. {params['mode']}模式下的天线端口隔离度（≥25dB，MIMO配置）",
                    f"3. 接收频率偏移（≤±20ppm，802.11标准）",
                    f"4. 本振泄漏抑制（≥40dBc，高通射频规范）"
                ]
                test_items_en = [
                    f"1. RX chain gain consistency at {params['band']} channel C{params['channel']} (±0.5dB, Qualcomm cal spec)",
                    f"2. Antenna port isolation in {params['mode']} mode (≥25dB, MIMO config)",
                    f"3. RX frequency offset (≤±20ppm, 802.11 standard)",
                    f"4. LO leakage suppression (≥40dBc, Qualcomm RF spec)"
                ]

                # 场景专属测试项（同步使用params的中英文字段）
                if scenario_type == "regular_rx":
                    test_items_zh.extend([
                        f"5. 信号强度{params['rssi']}下的接收灵敏度（PER≤10%@MCS0）",
                        f"6. {params['mode']}模式下的RSSI稳定性（连续500帧波动≤0.3dBm）",
                        f"7. 不同调制方式的RSSI一致性（差值≤0.5dBm）"
                    ])
                    test_items_en.extend([
                        f"5. RX sensitivity at {params['rssi']} (PER≤10%@MCS0)",
                        f"6. RSSI stability in {params['mode']} mode (≤0.3dBm fluctuation over 500 frames)",
                        f"7. RSSI consistency across modulations (≤0.5dBm difference)"
                    ])
                elif scenario_type == "calibration_ant_cw":
                    test_items_zh.extend([
                        f"5. 连续波（CW）信号接收灵敏度（≤-100dBm@BER=1e-6）",
                        f"6. 多天线校准一致性（各通道增益差值≤0.3dB）",
                        f"7. 温度漂移补偿效果（-40~85℃范围内偏差≤1dB）"
                    ])
                    test_items_en.extend([
                        f"5. CW signal reception sensitivity (≤-100dBm@BER=1e-6)",
                        f"6. Multi-antenna calibration consistency (gain difference ≤0.3dB across channels)",
                        f"7. Temperature drift compensation (-40~85℃, deviation ≤1dB)"
                    ])
                elif scenario_type == "eq_mode":
                    test_items_zh.extend([
                        f"5. 均衡器（EQ）频率响应平坦度（±0.5dB，20MHz带宽内）",
                        f"6. 不同信号强度下的EQ自适应响应时间（≤100µs）",
                        f"7. 多径环境下的EQ校正效果（EVM改善≥6dB）",
                        f"8. 邻近信道干扰抑制（≥30dB，±20MHz偏移）"
                    ])
                    test_items_en.extend([
                        f"5. Equalizer (EQ) frequency response flatness (±0.5dB across 20MHz bandwidth)",
                        f"6. EQ adaptive response time under varying signal strength (≤100µs)",
                        f"7. EQ correction effectiveness in multipath environment (EVM improvement ≥6dB)",
                        f"8. Adjacent channel interference rejection (≥30dB at ±20MHz offset)"
                    ])
                else:  # calibration_power
                    test_items_zh.extend([
                        f"5. 功率校准精度（目标值±0.2dBm，全温度范围内）",
                        f"6. 功率检测线性度（R²≥0.999，-80~-20dBm范围）",
                        f"7. 校准后功率稳定性（24小时漂移≤0.3dBm）",
                        f"8. 不同信道间的功率一致性（差值≤0.5dBm）"
                    ])
                    test_items_en.extend([
                        f"5. Power calibration accuracy (target ±0.2dBm across full temperature range)",
                        f"6. Power detection linearity (R²≥0.999, -80~-20dBm range)",
                        f"7. Post-calibration power stability (≤0.3dBm drift over 24 hours)",
                        f"8. Power consistency across channels (≤0.5dBm difference)"
                    ])

                # 频段专属测试项（同步使用params的中英文字段）
                if params['band'] == '5.0GHZ' and scenario_type in ["regular_rx", "calibration_ant_cw"]:
                    test_items_zh.append(f"8. 动态频率选择（DFS）功能验证（校准模式下雷达信号检测率100%）"
                                         if is_calibration else
                                         f"8. 动态频率选择（DFS）响应时间（≤100ms）")
                    test_items_en.append(
                        f"8. Dynamic Frequency Selection (DFS) verification (100% radar detection in calibration)"
                        if is_calibration else
                        f"8. Dynamic Frequency Selection (DFS) response time (≤100ms)")

                if params['band'] == '2.4GHZ':
                    # 2.4GHz频段专属测试项，根据场景调整
                    if scenario_type in ["regular_rx", "calibration_ant_cw"]:
                        test_items_zh.append(f"8. 蓝牙共存校准（BT信号存在时增益补偿误差≤0.5dB）"
                                             if is_calibration else
                                             f"8. 蓝牙共存干扰下的RSSI稳定性（偏差≤1dBm）")
                        test_items_en.append(
                            f"8. Bluetooth coexistence calibration (gain compensation error ≤0.5dB with BT signal)"
                            if is_calibration else
                            f"8. RSSI stability under Bluetooth coexistence (≤1dBm deviation)")
                    elif scenario_type == "eq_mode":
                        test_items_zh.append(f"9. {params['freq_info_zh']}多系统共存下的EQ适应性（Wi-Fi/BT/ZigBee环境）")
                        test_items_en.append(
                            f"9. EQ adaptability in {params['freq_info_en']} multi-system coexistence (Wi-Fi/BT/ZigBee)")
                    else:  # calibration_power
                        test_items_zh.append(f"9. 功率校准对蓝牙共存的影响（BT吞吐量损失≤5%）")
                        test_items_en.append(
                            f"9. Impact of power calibration on Bluetooth coexistence (BT throughput loss ≤5%)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "param_spec": params,  # 调试用参数详情（含中英文字段）
                    "is_calibration": is_calibration,  # 标识是否为校准场景
                    "scenario_type": scenario_type  # 场景类型细分
                }


            def parse_wifi_rx_test_description_select(self, param: str) -> dict:
                """
                根据输入的param选择合适的解析函数

                参数:
                    param: MTK WLAN接收测试参数

                返回:
                    dict: 包含中英文测试目的、测试项及技术细节的结构化说明
                """
                # 适配的字符串： MTK_WLAN_X.XG_CX_(H|M|L)CHXX_RSSI_ANT_CW
                if re.match(r"MTK_WLAN_\d+\.\d+G_C\d+_(H|M|L)CH\d+_RSSI_ANT_CW", param.upper()):
                    return self.parse_wifi_rx_test_description2(param)

                # 适配的字符串： MTK_WLAN_X.XG_CX_[HQA|LQA|BEAM]_RSSI_(H|M|L)CHXX
                elif re.match(r"MTK_WLAN\d+\.\d+G_RX_C\d+_[HQA|LQA|BEAM]_RSSI_(H|M|L)CH\d+", param.upper()):
                    return self.parse_wifi_rx_test_description(param)

                # 适配的字符串： MTK_WLAN_X.XG_CX_(H|M|L)CHXX_RSSI_ANT_CW
                elif re.match(r"MTK_WLAN_(?P<band>\d+\.?\d*G)_C(?P<channel>\d+)_CH(?P<ch_num>\d+)_RSSI_ANT", param.upper()):
                    return self.parse_wifi_rx_test_description3(param)

                # 适配的字符串：MTK_WLAN2.4G_RX_V2_RSSI_CH07_X
                elif re.match(r"MTK_WLAN(?P<band>\d+\.\d+G)_RX_V(?P<version>\d+)_RSSI_CH(?P<channel>\d+)_X", param.upper()):
                    return self.parse_wifi_rx_test_description4(param)

                # 适配的字符串：MTK_WLAN_2.4G_CH06_RSSI
                elif re.match(r"MTK_WLAN_(?P<band>\d+\.\d+G)_CH(?P<channel>\d+)_RSSI", param.upper()):
                    return self.parse_wifi_rx_test_description5(param)

                else:
                    raise ValueError(f"无效的MTK WLAN接收参数: {param}，请提供符合格式的参数")

            def parse_gps_rx_test_description2(self, param: str) -> dict:
                # """
                # 解析MTK GPS接收测试参数（仅RX场景），生成双语技术说明
                #
                # 参数:
                #     param: MTK GPS接收参数（如：MTK_GPS_RX_V3_L1_-100DB）
                #            标准格式：MTK_GPS_RX_V[1-4]_(L1|L2|L5)_(?P<rssi>-?\d+)DB
                #            注：L1=1575.42MHz（C/A码），L2=1227.60MHz（P码），L5=1176.45MHz（新信号）
                #
                # 返回:
                #     dict: 含测试目的、测试项（带MTK标准值）的双语说明
                # """
                # GPS RX专属正则（强化版本和频段解析）
                pattern = r"MTK_GPS_RX_V(?P<version>\d+)_(?P<band>L1|L2|L5)_(?P<rssi>-?\d+)DB"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效GPS接收参数: {param}，示例：MTK_GPS_RX_V3_L1_-100DB")

                # 解析参数（基于MTK GPS接收机规范）
                params = {
                    "version": int(match.group('version')),  # 接收机版本（V3+支持RTK）
                    "band": {
                        "L1": {
                            "zh": "1575.42MHz (C/A码, 民用)",
                            "en": "1575.42MHz (C/A code, civilian use)"
                        },
                        "L2": {
                            "zh": "1227.60MHz (P码, 军用/高精度)",
                            "en": "1227.60MHz (P code, military/high precision)"
                        },
                        "L5": {
                            "zh": "1176.45MHz (新信号, 抗干扰)",
                            "en": "1176.45MHz (New signal, anti-interference)"
                        }
                    }[match.group('band')],
                    "rssi": f"{match.group('rssi')}dBm",  # 接收信号强度
                    "carrier": {  # 频段对应载波
                        "L1": 1575.42,
                        "L2": 1227.60,
                        "L5": 1176.45
                    }[match.group('band')]
                }

                # 根据param是否包含'L1'设置 band_item
                band_item_zh = params['band']['zh']
                band_item_en = params['band']['en']

                # 根据param是否包含'L1'设置 carrier_item
                carrier_item = params['carrier']

                # 测试目的生成（弱信号场景）
                purpose_zh = f"验证MTK GPS V{params['version']}接收机在{band_item_zh}频段，{params['rssi']}弱信号下的捕获与跟踪性能"
                purpose_en = f"Validate acquisition/tracking performance of MTK GPS V{params['version']} at {params['rssi']} in {band_item_en} band"

                # 测试项（含MTK产线标准）
                test_items_zh = [
                    f"1. 信号强度误差（MTK内控±0.5dBm，行业±1dBm）",
                    f"2. 首次定位时间（TTFF）≤30秒（{params['rssi']}，热启动）",
                    f"3. 多径环境下的C/N0（载噪比）≥30dBHz（L1标准）",
                    f"4. AGC（自动增益控制）响应时间≤50ms（信号突变时）",
                    f"5. 连续10分钟跟踪丢星次数≤2次（MTK良率标准）",
                    f"6. 邻频干扰（±4MHz）下的定位精度≤10米（2DRMS）"
                ]
                test_items_en = [
                    f"1. RSSI error (MTK ±0.5dBm, industry ±1dBm)",
                    f"2. TTFF ≤30s at {params['rssi']} (warm start)",
                    f"3. C/N0 ≥30dBHz in multipath (L1 spec)",
                    f"4. AGC response time ≤50ms (signal transition)",
                    f"5. Satellite loss ≤2 times/10min (MTK yield criteria)",
                    f"6. Position error ≤10m (2DRMS) with ±4MHz interference"
                ]

                # V3+版本专属增强（RTK支持）
                if params['version'] >= 3:
                    test_items_zh.append(f"7. RTK浮点解收敛时间≤120秒（{params['rssi']}，L1+L5双频）")
                    test_items_en.append(f"7. RTK float solution time ≤120s (L1+L5 dual-band at {params['rssi']})")

                # 频段专属测试项
                if 'L1' in param.upper():
                    test_items_zh.append(f"8. C/A码相关峰噪比（CNR）≥15dB（MTK基带算法标准）")
                    test_items_en.append(f"8. C/A code CNR ≥15dB (MTK baseband algorithm spec)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "mtk_spec": {
                        "sensitivity": "-160dBm (L1, 热噪声极限)",
                        "frequency": f"{carrier_item}MHz",
                        "version_note": "V3+支持北斗/Galileo多系统联合定位"
                    }
                }

            def parse_gps_rx_test_description2_for_qc(self, param: str) -> dict:
                """
                解析高通GPS接收测试参数（仅RX场景），生成双语技术说明

                参数:
                    param: 高通GPS接收参数（如：QC_GPS_RAD_CARRIER_TO_NOISE_GEN8_L3_EQ）
                           标准格式：QC_GPS_RAD_CARRIER_TO_NOISE_GEN\d+_(WR|L\d+_EQ)
                           注：L1=1575.42MHz，L2=1227.60MHz，L3=1381.05MHz，L5=1176.45MHz

                返回:
                    dict: 含测试目的、测试项（带高通标准值）的双语说明
                """
                # 高通GPS RX专属正则（强化版本和频段解析）
                pattern = r"^QC_GPS_RAD_CARRIER_TO_NOISE_GEN(?P<gen>\d+)_(?P<mode>WR|L(?P<band>\d+)_EQ)$"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效高通GPS接收参数: {param}，示例：QC_GPS_RAD_CARRIER_TO_NOISE_GEN8_L3_EQ")

                # 解析参数（基于高通GPS接收机规范）
                gen = int(match.group('gen'))
                mode = match.group('mode')
                band = match.group('band') if match.group('band') else None

                # 频段信息映射表
                band_info = {
                    "1": {
                        "frequency": 1575.42,
                        "zh": "1575.42MHz (L1频段, C/A码)",
                        "en": "1575.42MHz (L1 band, C/A code)"
                    },
                    "2": {
                        "frequency": 1227.60,
                        "zh": "1227.60MHz (L2频段, P码)",
                        "en": "1227.60MHz (L2 band, P code)"
                    },
                    "3": {
                        "frequency": 1381.05,
                        "zh": "1381.05MHz (L3频段, 核探测)",
                        "en": "1381.05MHz (L3 band, nuclear detection)"
                    },
                    "5": {
                        "frequency": 1176.45,
                        "zh": "1176.45MHz (L5频段, 安全服务)",
                        "en": "1176.45MHz (L5 band, safety-of-life service)"
                    }
                }

                # 模式信息
                mode_info = {
                    "WR": {
                        "zh": "宽频接收模式",
                        "en": "Wideband reception mode"
                    },
                    "EQ": {
                        "zh": "均衡滤波模式",
                        "en": "Equalized filtering mode"
                    }
                }

                # 构建参数字典
                params = {
                    "gen": gen,  # 芯片代次（GEN8及以上支持双频）
                    "mode": mode,
                    "mode_desc": mode_info["EQ"] if "EQ" in mode else mode_info["WR"],
                    "band": band_info[band] if band else None,
                    "frequency": band_info[band]["frequency"] if (band and band in band_info) else "Multiple"
                }

                # 测试目的生成
                if band:
                    purpose_zh = (f"验证高通第{params['gen']}代GPS接收机在{params['band']['zh']}，"
                                  f"{params['mode_desc']['zh']}下的载噪比特性")
                    purpose_en = (
                        f"Verify carrier-to-noise characteristics of Qualcomm GEN{params['gen']} GPS receiver "
                        f"in {params['band']['en']} with {params['mode_desc']['en']}")
                else:
                    purpose_zh = (f"验证高通第{params['gen']}代GPS接收机在{params['mode_desc']['zh']}下的"
                                  f"多频段载噪比综合特性")
                    purpose_en = (f"Verify multi-band carrier-to-noise characteristics of Qualcomm GEN{params['gen']} "
                                  f"GPS receiver with {params['mode_desc']['en']}")

                # 测试项（含高通产线标准）
                test_items_zh = [
                    f"1. 载噪比（C/N0）测量精度（高通内控±1dBHz，行业±2dBHz）",
                    f"2. 信号捕获灵敏度（≤-158dBm@C/N0=25dBHz，冷启动）",
                    f"3. 载噪比动态范围（20-55dBHz，无饱和失真）",
                    f"4. {params['mode_desc']['zh']}下的抗窄带干扰能力（≥30dB抑制比）",
                    f"5. 连续跟踪稳定性（1小时C/N0波动≤2dBHz）"
                ]
                test_items_en = [
                    f"1. C/N0 measurement accuracy (Qualcomm ±1dBHz, industry ±2dBHz)",
                    f"2. Signal acquisition sensitivity (≤-158dBm@C/N0=25dBHz, cold start)",
                    f"3. C/N0 dynamic range (20-55dBHz, no saturation)",
                    f"4. Narrowband interference rejection in {params['mode_desc']['en']} (≥30dB)",
                    f"5. Continuous tracking stability (≤2dBHz variation over 1 hour)"
                ]

                # GEN8+版本专属增强（双频支持）
                if params['gen'] >= 8:
                    test_items_zh.append(f"6. 双频融合C/N0计算精度（L1+L5联合解算误差≤0.5dBHz）")
                    test_items_en.append(f"6. Dual-band fused C/N0 accuracy (L1+L5 combined error ≤0.5dBHz)")

                # 均衡模式专属测试项
                if "EQ" in params['mode']:
                    test_items_zh.append(f"7. 多径抑制比（≥15dB，城区环境模拟）")
                    test_items_en.append(f"7. Multipath rejection ratio (≥15dB, urban simulation)")

                # 宽频模式专属测试项
                if params['mode'] == "WR":
                    test_items_zh.append(f"7. 频段间干扰隔离度（≥40dB，多系统共存场景）")
                    test_items_en.append(f"7. Inter-band interference isolation (≥40dB, multi-system coexistence)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "qc_spec": {
                        "sensitivity": "-163dBm (追踪灵敏度, L1频段)",
                        "frequency": f"{params['frequency']}MHz",
                        "gen_note": "GEN8及以上支持GPS/GLONASS/北斗多星座联合定位"
                    }
                }

            def parse_bluetooth_tx_test_description(self, param: str) -> dict:
                # """
                # 解析MTK蓝牙发射测试参数（仅TX场景），生成双语技术说明
                #
                # 参数:
                #     param: MTK蓝牙发射参数（如：MTK_BLUETOOTH_TX_POWER_V2_CH39）
                #            标准格式：MTK_BLUETOOTH_TX_POWER_V[1-3]_(CH\d{1,2})
                #            注：CH0-39（0-36数据信道，37-39广播信道，CH39=2480MHz）
                #
                # 返回:
                #     dict: 含测试目的、测试项（带蓝牙5.3标准）的双语说明
                # """
                # 蓝牙TX专属正则（强化版本和信道解析）
                pattern = r"MTK_BLUETOOTH_TX_POWER_V(?P<version>\d+)_CH(?P<channel>\d{1,2})"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效蓝牙发射参数: {param}，示例：MTK_BLUETOOTH_TX_POWER_V2_CH39")

                # 解析参数（基于蓝牙5.3发射规范）
                params = {
                    "version": int(match.group('version')),  # 版本（V2支持LE编码S8）
                    "channel": int(match.group('channel')),
                    "frequency": 2402 + int(match.group('channel')) * 2,  # 蓝牙信道频率计算
                    "channel_type": "Broadcast" if 37 <= int(match.group('channel')) <= 39 else "Data"
                }

                # 测试目的生成（区分版本和信道类型）
                purpose_zh = f"验证MTK蓝牙V{params['version']}发射机在{params['channel_type']}信道（CH{params['channel']}，{params['frequency']}MHz）的功率准确性与调制质量"
                purpose_en = f"Validate TX power accuracy & modulation quality of MTK Bluetooth V{params['version']} on {params['channel_type']} channel (CH{params['channel']}, {params['frequency']}MHz)"

                # 测试项（含蓝牙5.3和MTK内控标准）
                test_items_zh = [
                    f"1. 发射功率误差（MTK内控±0.5dBm，蓝牙标准±2dBm）",
                    f"2. {params['channel_type']}信道功率一致性（连续100帧波动≤0.3dBm）",
                    f"3. GFSK调制频偏（160±40kHz，蓝牙5.3合规）",
                    f"4. 邻道泄漏功率比（ACLR）≥30dB（数据信道）/≥20dB（广播信道）",
                    f"5. 带内杂散辐射≤-20dBm（2.4GHz ISM频段）"
                ]
                test_items_en = [
                    f"1. TX power error (MTK ±0.5dBm, BT5.3 ±2dBm)",
                    f"2. {params['channel_type']} channel power consistency (≤0.3dBm over 100 frames)",
                    f"3. GFSK frequency deviation 160±40kHz (BT5.3 compliance)",
                    f"4. ACLR ≥30dB (data)/≥20dB (advertising) channels",
                    f"5. In-band spurious ≤-20dBm (2.4GHz ISM band)"
                ]

                # V2+版本专属增强（LE编码S8）
                if params['version'] >= 2:
                    test_items_zh.append(f"6. LE编码S8（2Mbps）功率保持（与S1编码差值≤1dBm）")
                    test_items_en.append(f"6. LE编码S8 (2Mbps) power consistency (≤1dBm vs S1)")

                # 广播信道专属测试项（CH37-39）
                if 37 <= params['channel'] <= 39:
                    test_items_zh.append(f"7. 广播帧功率稳定性（间隔100ms，波动≤0.5dBm）")
                    test_items_en.append(f"7. Advertising frame power stability (≤0.5dBm over 100ms intervals)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "mtk_spec": {
                        "power_range": "0-10dBm (Class 2)",
                        "frequency": f"{params['frequency']}MHz",
                        "version_note": "V2支持LE 2Mbps编码，V3支持LE 5Mbps"
                    }
                }

            def parse_bluetooth_tx_test_description_for_qc(self, param: str) -> dict:
                # """
                # 解析高通蓝牙发射测试参数（仅TX场景），生成双语技术说明
                #
                # 参数:
                #     param: 高通蓝牙发射参数（如：QC_BT_RAD_MEAS_CW_POW_MCH39_PRO）
                #            标准格式：QC_BT_RAD_MEAS_CW_POW_(H|M|L)CH\d+_PRO
                #            注：CH0-39（0-36数据信道，37-39广播信道，CH39=2480MHz）
                #
                # 返回:
                #     dict: 含测试目的、测试项（带蓝牙5.3标准）的双语说明
                # """
                # 高通蓝牙TX专属正则（强化模式和信道解析）
                pattern = r"^QC_BT_RAD_MEAS_CW_POW_(?P<mode>M|L)CH(?P<channel>\d+)_PRO$"
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效高通蓝牙发射参数: {param}，示例：QC_BT_RAD_MEAS_CW_POW_MCH39_PRO")

                # 解析参数（基于蓝牙5.3发射规范）
                channel = int(match.group('channel'))
                params = {
                    "mode": match.group('mode'),  # M模式或L模式
                    "channel": channel,
                    "frequency": 2402 + channel * 2,  # 蓝牙信道频率计算
                    "channel_type": "Broadcast" if 37 <= channel <= 39 else "Data"
                }

                # 测试目的生成（区分模式和信道类型）
                purpose_zh = f"验证高通蓝牙在{params['mode']}模式下{params['channel_type']}信道（CH{params['channel']}，{params['frequency']}MHz）的连续波发射功率特性"
                purpose_en = f"Validate continuous wave transmission power characteristics of Qualcomm Bluetooth in {params['mode']} mode on {params['channel_type']} channel (CH{params['channel']}, {params['frequency']}MHz)"

                # 测试项（含蓝牙5.3和高通内控标准）
                test_items_zh = [
                    f"1. 发射功率误差（高通内控±0.3dBm，蓝牙标准±2dBm）",
                    f"2. 功率平坦度（全信道范围内波动≤1.0dB）",
                    f"3. 连续波频谱模板（符合FCC 15.247规范）",
                    f"4. 杂散辐射（带外≤-41dBm/MHz，1GHz以下≤-36dBm）",
                    f"5. {params['mode']}模式功率切换响应时间（≤10µs）"
                ]
                test_items_en = [
                    f"1. TX power error (Qualcomm ±0.3dBm, BT5.3 ±2dBm)",
                    f"2. Power flatness (≤1.0dB variation across all channels)",
                    f"3. CW spectrum mask (compliant with FCC 15.247)",
                    f"4. Spurious emissions (≤-41dBm/MHz out-of-band, ≤-36dBm below 1GHz)",
                    f"5. {params['mode']} mode power switching response time (≤10µs)"
                ]

                # 模式专属测试项
                if params['mode'] == 'M':
                    test_items_zh.append(f"6. M模式最大功率输出（≥10dBm，Class 1设备标准）")
                    test_items_en.append(f"6. M mode maximum power output (≥10dBm, Class 1 device standard)")
                else:  # L模式
                    test_items_zh.append(f"6. L模式低功耗优化（≤0.5dBm，延长电池寿命）")
                    test_items_en.append(f"6. L mode low power optimization (≤0.5dBm, extended battery life)")

                # 广播信道专属测试项（CH37-39）
                if 37 <= params['channel'] <= 39:
                    test_items_zh.append(f"7. 广播信道功率稳定性（1小时监测波动≤0.2dBm）")
                    test_items_en.append(f"7. Broadcast channel power stability (≤0.2dBm over 1 hour monitoring)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "qc_spec": {
                        "power_range": "M模式: 8-12dBm, L模式: -20-0dBm",
                        "frequency": f"{params['frequency']}MHz",
                        "mode_note": "M模式适用于远距离传输，L模式适用于低功耗场景"
                    }
                }

            def parse_lte_tx_test_description(self, param: str) -> dict:
                # """
                # 解析MTK LTE/NR发射测试参数（BC42专属），生成双语技术说明
                #
                # 参数:
                #     param: MTK LTE发射参数（如：MTK_MMRF_LTE_BC42_TX_20DB_V7_MCH42590）
                #            标准格式：MTK_MMRF_LTE_BC(?P<band>\d+)_TX_(?P<power>\d+)DB_V(?P<version>\d+)_MCH(?P<freq>\d+\.?\d*)
                #            注：BC42=3500-3600MHz（n42，5G NR扩展频段）
                #
                # 返回:
                #     dict: 含测试目的、测试项（带3GPP/MTK双标准）的双语说明
                # """
                # LTE/NR TX专属正则（强化BC42解析）
                # pattern = r"MTK_MMRF_LTE_BC(?P<band>\d+)_TX_(?P<power>\d+)DB_V(?P<version>\d+)_MCH(?P<freq>\d+\.?\d*)"
                pattern = re.compile(
                    r"MTK_MMRF_LTE_BC(?P<band>\d+)_TX_(?P<power>\d+)DB_V(?P<version>\d+)_MCH(?P<freq>\d+\.?\d*)"
                    r"(?:_ANT_CW)?"  # 可选的_ANT_CW后缀，非捕获组不新增分组
                )
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效参数: {param}，示例：MTK_MMRF_LTE_BC42_TX_20DB_V7_MCH42590")

                # 解析参数（基于3GPP TS 36.101）
                params = {
                    "band": "n42 (3500-3600MHz)",  # 固定BC42对应n42
                    "power": f"{match.group('power')}dBm",
                    "version": int(match.group('version')),  # V7支持CA载波聚合
                    "center_freq": float(match.group('freq')),  # 中心频率（MHz）
                    # 将match.group('freq')转换为浮点数后进行计算
                    "channel": (float(match.group('freq')) - 3500) * 2  # n42信道号计算 3500MHz=0，步进0.5M
                }

                # 测试目的生成（n42频段专属）
                purpose_zh = f"验证MTK LTE V{params['version']}发射机在n42频段（{params['center_freq']}MHz），{params['power']}发射功率下的调制精度与频谱合规性"
                purpose_en = f"Validate modulation accuracy & spectrum compliance of MTK LTE V{params['version']} at {params['power']} on n42 ({params['center_freq']}MHz)"

                # 测试项（3GPP R17 + MTK内控）
                test_items_zh = [
                    f"1. 发射功率误差（MTK: ±0.8dBm，3GPP: ±2dBm）",
                    f"2. 256QAM调制EVM≤-25dB（n42 100MHz带宽）",
                    f"3. 邻道泄漏比（ACLR）≥45dB（相邻5MHz信道）",
                    f"4. 带内波动（OBW）≤0.5dB（100MHz载波）",
                    f"5. 功率控制步长≤1dB（MCS 0-28）",
                    f"6. 多天线发射一致性（主副天线差≤1dB，MIMO必备）"
                ]
                test_items_en = [
                    f"1. TX power error (MTK ±0.8dBm, 3GPP ±2dBm)",
                    f"2. 256QAM EVM ≤-25dB (100MHz n42)",
                    f"3. ACLR ≥45dB (5MHz adjacent channel)",
                    f"4. OBW ≤0.5dB (100MHz carrier)",
                    f"5. Power control step ≤1dB (MCS 0-28)",
                    f"6. Antenna TX consistency ≤1dB (MIMO requirement)"
                ]

                # V7版本专属增强（CA载波聚合）
                if params['version'] >= 7:
                    test_items_zh.append(f"7. 载波聚合（CA）功率平衡（主辅载波差≤1.5dB）")
                    test_items_en.append(f"7. CA power balance ≤1.5dB (primary-secondary carrier)")

                # n42频段专属测试项
                if 3500 <= params['center_freq'] <= 3600:
                    test_items_zh.append(f"8. 动态TDD切换时间≤50μs（n42时分双工特性）")
                    test_items_en.append(f"8. Dynamic TDD switch time ≤50μs (n42 TDD feature)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "mtk_spec": {
                        "band_info": "n42 (3500-3600MHz, 100MHz BW, TDD)",
                        "center_freq": f"{params['center_freq']}MHz",
                        "version_cap": "V7+支持3CC CA（3载波聚合）"
                    }
                }

            def parse_lte_tx_test_description_for_qc(self, param: str) -> dict:
                """
                解析高通LTE发射测试参数，生成双语技术说明

                参数:
                    param: 高通LTE发射参数（如：QC_LTE_BC13_QRRFR_TX_POWER_MCH_4500_V3）
                           标准格式：QC_LTE_BC(?P<band>\d+)_QRRFR_TX_POWER_(?P<mode>(H|M|L)CH)_(?P<freq>\d+)_V(?P<version>\d+)

                返回:
                    dict: 含测试目的、测试项（带3GPP/高通双标准）的双语说明
                """
                # 高通LTE TX专属正则表达式
                pattern = r'^QC_LTE_BC(?P<band>\d+)_QRRFR_TX_POWER_(?P<mode>(H|M|L)CH)_(?P<freq>\d+)_V(?P<version>\d+)$'
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(
                        f"无效的高通LTE发射参数: {param}，标准格式示例：\n"
                        f"QC_LTE_BC13_QRRFR_TX_POWER_MCH_4500_V3\n"
                        f"QC_LTE_BC20_QRRFR_TX_POWER_LCH_3500_V5"
                    )

                # 解析参数（基于3GPP TS 36.101和高通规范）
                band = match.group('band')
                # 映射BC频段到具体频率范围（示例数据，实际需根据高通规范调整）
                band_info_map = {
                    '1': '2100MHz (FDD)',
                    '3': '1800MHz (FDD)',
                    '7': '2600MHz (FDD)',
                    '13': '700MHz (FDD)',
                    '20': '800MHz (FDD)',
                    '42': '3500MHz (TDD)'
                }
                band_info = band_info_map.get(band, f"BC{band} (Unknown band)")

                params = {
                    "band": f"BC{band} ({band_info})",
                    "mode": match.group('mode'),
                    "mode_desc": "main channel" if match.group('mode') == 'MCH' else "secondary channel",
                    "center_freq": f"{match.group('freq')}MHz",
                    "version": int(match.group('version')),
                    "channel_type": "main channel" if match.group('mode').startswith('M') else "secondary channel"
                }

                # 测试目的生成
                purpose_zh = (f"验证高通LTE发射机在{params['band']}频段（中心频率{params['center_freq']}），"
                              f"{params['mode_desc']}模式下的发射功率特性（V{params['version']}版本规范）")
                purpose_en = (
                    f"Validate transmit power characteristics of Qualcomm LTE transmitter in {params['band']} "
                    f"band (center freq {params['center_freq']}), {params['mode']} mode (V{params['version']} spec)")

                # 测试项（3GPP + 高通内控标准）
                test_items_zh = [
                    f"1. 发射功率误差（高通: ±0.5dBm，3GPP: ±1dBm）",
                    f"2. 功率控制动态范围（-40~24dBm，步进1dB）",
                    f"3. 邻道泄漏比（ACLR）≥45dBc（1.4MHz带宽）",
                    f"4. 杂散辐射（≤-36dBm/100kHz，1GHz以下频段）",
                    f"5. {params['mode']}模式下功率切换时间≤10μs"
                ]
                test_items_en = [
                    f"1. TX power error (Qualcomm: ±0.5dBm, 3GPP: ±1dBm)",
                    f"2. Power control dynamic range (-40~24dBm, 1dB step)",
                    f"3. Adjacent Channel Leakage Ratio (ACLR) ≥45dBc (1.4MHz BW)",
                    f"4. Spurious emissions (≤-36dBm/100kHz, below 1GHz)",
                    f"5. Power switching time in {params['mode']} mode ≤10μs"
                ]

                # 高版本专属测试项（V5及以上支持载波聚合）
                if params['version'] >= 5:
                    test_items_zh.extend([
                        f"6. 载波聚合（CA）功率平衡（主辅载波差≤0.8dB）",
                        f"7. 跨频段CA切换时间≤20μs"
                    ])
                    test_items_en.extend([
                        f"6. Carrier Aggregation (CA) power balance (≤0.8dB between carriers)",
                        f"7. Cross-band CA switching time ≤20μs"
                    ])

                # TDD频段专属测试项（如BC42）
                if band == '42':
                    test_items_zh.append(f"8. TDD时隙功率比精度（±0.3dB，DL:UL=3:1配置）")
                    test_items_en.append(f"8. TDD slot power ratio accuracy (±0.3dB, DL:UL=3:1 config)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "qc_spec": {
                        "band_details": params['band'],
                        "version_features": f"V{params['version']}支持{'CA' if params['version'] >= 5 else '基础'}功能",
                        "freq_range": f"{int(match.group('freq')) - 10}~{int(match.group('freq')) + 10}MHz"
                    }
                }

            def parse_lte_rx_test_description(self, param: str) -> dict:
                # """
                # 解析MTK LTE/NR接收测试参数（BC42专属），生成双语技术说明
                #
                # 参数:
                #     param: MTK LTE接收参数（如：MTK_MMRF_LTE_BC42_RX_C0_RSSI_V9_MCH42590_EP）
                #            标准格式：MTK_MMRF_LTE_BC42_RX_(C\d+)_RSSI_V(?P<version>\d+)_MCH(?P<freq>\d+\.?\d*)_EP
                #            注：C0-C3为n42频点，EP=误包率测试（Enhanced Packet）
                #
                # 返回:
                #     dict: 含测试目的、测试项（带3GPP/MTK双标准）的双语说明
                # """
                # BC42 RX专属正则（强化RSSI和EP解析）
                # 定义匹配模式：包含两种格式（带EP/ROW后缀和不带后缀）
                # 统一添加命名分组，便于提取band、channel_id等参数
                pattern = re.compile(
                    r"MTK_MMRF_LTE_BC(?P<band>\d+)_RX_(?P<channel_id>C\d+)_RSSI_V(?P<version>\d+)_MCH(?P<freq>\d+\.?\d*)"
                    r"(?:_(?P<region>EP|ROW))?"  # 可选的EP/ROW后缀，非捕获组不影响整体匹配
                )
                # 转换为大写以忽略大小写差异
                match = pattern.match(param.upper())
                # pattern = r"MTK_MMRF_LTE_BC(?P<band>\d+)_RX_(C\d+)_RSSI_V(?P<version>\d+)_MCH(?P<freq>\d+\.?\d*)_(EP|ROW)"
                # match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效参数: {param}，示例：MTK_MMRF_LTE_BC42_RX_C0_RSSI_V9_MCH3550_(EP|ROW)")

                # 解析参数（基于3GPP TS 36.101接收标准）
                params = {
                    "band": "n42 (3500-3600MHz)",
                    "freq_point": match.group(2),  # C0-C3频点（对应中心频率偏移）
                    "version": int(match.group('version')),  # V9支持4x4 MIMO
                    "center_freq": float(match.group('freq')),
                    "mimo": f"{int(match.group('version')) // 2}x{int(match.group('version')) // 2}"  # V9=4x4 MIMO
                }

                # 假设RSSI为一个固定值，这里可以根据实际情况修改
                rssi = -105
                params["rssi"] = f"{rssi}dBm"

                # 频率合法性校验（n42实际范围3500-3600MHz）
                if not (3500 <= params['center_freq'] <= 3600):
                    params["freq_warning"] = f"⚠️ 中心频率{params['center_freq']}MHz超出n42范围（3500-3600MHz）"

                # 测试目的生成（RX弱信号场景）
                purpose_zh = f"验证MTK LTE V{params['version']}接收机在n42频段（{params['center_freq']}MHz，{params['freq_point']}频点），{params['rssi']}弱信号下的解调能力与误包率"
                purpose_en = f"Validate demodulation capability & PER of MTK LTE V{params['version']} at {params['rssi']} on n42 ({params['center_freq']}MHz, {params['freq_point']})"

                # 测试项（3GPP R17 + MTK接收增强）
                test_items_zh = [
                    f"1. RSSI测量误差（MTK: ±0.5dBm，3GPP: ±2dBm）",
                    f"2. 256QAM解调EVM≤-22dB（{params['rssi']}，4x4 MIMO）",
                    f"3. 误包率（PER）≤10%（1000帧，MCS28）",
                    f"4. 邻道选择性（ACS）≥33dB（5MHz间隔，-52dBm干扰）",
                    f"5. 多径衰落（EPA5Hz）下的BLER≤5%",
                    f"6. 同频干扰（+6dB SINR）解调成功率≥95%"
                ]
                test_items_en = [
                    f"1. RSSI measurement error (MTK ±0.5dBm, 3GPP ±2dBm)",
                    f"2. 256QAM EVM ≤-22dB at {params['rssi']} (4x4 MIMO)",
                    f"3. Packet Error Rate (PER) ≤10% (1000 packets, MCS28)",
                    f"4. Adjacent Channel Selectivity (ACS) ≥33dB (5MHz offset, -52dBm interference)",
                    f"5. BLER ≤5% under multipath fading (EPA5Hz)",
                    f"6. Co-channel interference (+6dB SINR) success rate ≥95%"
                ]

                # V9版本专属增强（4x4 MIMO）
                if params['version'] >= 9:
                    test_items_zh.append(f"7. 4x4 MIMO层间不平衡度≤3dB（MTK天线校准标准）")
                    test_items_en.append(f"7. 4x4 MIMO layer imbalance ≤3dB (MTK antenna calibration spec)")

                # 弱信号专属测试项（RSSI≤-100dBm）
                if int(params['rssi'].replace('dBm', '')) <= -100:
                    test_items_zh.append(f"8. 连续10分钟丢包次数≤5次（{params['rssi']}，热噪声极限-110dBm）")
                    test_items_en.append(f"8. Packet loss ≤5 times/10min at {params['rssi']} (thermal noise -110dBm)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "mtk_spec": {
                        "band_info": "n42 (3500-3600MHz, 100MHz BW, TDD)",
                        "rssi": params['rssi'],
                        "mimo_cap": f"{params['mimo']} MIMO",
                        "warning": params.get("freq_warning", "")
                    }
                }

            def parse_ns_rx_test_description_for_mtk(self, param: str) -> dict:
                # """
                # 解析MTK NR5G接收测试参数（NS77专属），生成双语技术说明
                #
                # 参数:
                #     param: MTK NR5G接收参数（如：MTK_MMRF_NR5G_NS77_RX_C0_V9_RSSI_MCH650000）
                #            标准格式：MTK_MMRF_NR5G_NS\d+_RX_(C\d+)_V(?P<version>\d+)_RSSI_MCH(?P<freq>\d+\.?\d*)
                #            注：NS77对应n77频段(3300-4200MHz)，支持FR1中频段
                #
                # 返回:
                #     dict: 含测试目的、测试项（带3GPP/MTK双标准）的双语说明
                # """
                # NR5G NS77专属正则（适配NR5G频段和结构）
                pattern = re.compile(
                    r"MTK_MMRF_NR(?P<generation>\d+)G_NS(?P<band>\d+)_RX_(?P<channel_id>C\d+)_V(?P<version>\d+)_RSSI_MCH(?P<freq>\d+\.?\d*)"
                    r"(?:_(?P<antenna>ANT_CW))?"  # 可选的天线校准后缀
                )

                # 转换为大写以忽略大小写差异
                match = pattern.match(param.upper())

                if not match:
                    raise ValueError(f"无效参数: {param}，示例：MTK_MMRF_NR5G_NS77_RX_C0_V9_RSSI_MCH3600")

                # 提取原始频率字符串
                freq_str = match.group('freq')
                # 优化频率转换逻辑：根据NR5G频段特性，MCH后数字通常为kHz单位
                # 转换为MHz（除以1000）
                center_freq = float(freq_str) / 1000

                # 解析参数（基于3GPP TS 38.101 NR接收标准）
                params = {
                    "generation": match.group('generation'),  # 5G/6G标识
                    "band": f"n{match.group('band')} (3300-4200MHz, FR1)",  # n77频段信息
                    "freq_point": match.group('channel_id'),  # C0-Cx频点
                    "version": int(match.group('version')),
                    "center_freq": center_freq,  # 已转换为MHz
                    "antenna_type": "校准天线" if match.group('antenna') else "常规天线",
                    "mimo": f"{int(match.group('version'))}T{int(match.group('version'))}R"  # V9对应9T9R
                }

                # 计算实际RSSI（NR5G弱信号阈值通常比LTE更低）
                rssi = -110  # NR5G典型弱信号场景
                params["rssi"] = f"{rssi}dBm"

                # 频率合法性校验（n77实际范围3300-4200MHz）
                if not (3300 <= params['center_freq'] <= 4200):
                    params["freq_warning"] = f"⚠️ 中心频率{params['center_freq']}MHz超出n77范围（3300-4200MHz）"

                # 测试目的生成（NR5G新空口特性）
                purpose_zh = f"验证MTK NR{params['generation']}G V{params['version']}接收机在{params['band']}（{params['center_freq']}MHz，{params['freq_point']}频点），{params['rssi']}弱信号下的波束赋形与解调性能"
                purpose_en = f"Validate beamforming & demodulation performance of MTK NR{params['generation']}G V{params['version']} at {params['rssi']} on {params['band']} ({params['center_freq']}MHz, {params['freq_point']})"

                # 测试项（3GPP R17 NR标准 + MTK增强特性）
                test_items_zh = [
                    f"1. RSSI测量误差（MTK: ±0.3dBm，3GPP: ±1.5dBm）",
                    f"2. 256QAM解调EVM≤-24dB（{params['rssi']}，{params['mimo']} MIMO）",
                    f"3. 误块率（BLER）≤8%（1000帧，MCS32）",
                    f"4. 邻道抑制比（ACLR）≥45dB（10MHz间隔，-48dBm干扰）",
                    f"5. 多普勒频偏（300km/h）下解调成功率≥90%",
                    f"6. 波束赋形增益≥12dB（水平±60°，垂直±30°扫描）"
                ]
                test_items_en = [
                    f"1. RSSI measurement error (MTK ±0.3dBm, 3GPP ±1.5dBm)",
                    f"2. 256QAM EVM ≤-24dB at {params['rssi']} ({params['mimo']} MIMO)",
                    f"3. Block Error Rate (BLER) ≤8% (1000 frames, MCS32)",
                    f"4. Adjacent Channel Leakage Ratio ≥45dB (10MHz offset, -48dBm interference)",
                    f"5. Demodulation success rate ≥90% with Doppler shift (300km/h)",
                    f"6. Beamforming gain ≥12dB (azimuth ±60°, elevation ±30°)"
                ]

                # V9版本专属增强（Massive MIMO特性）
                if params['version'] >= 9:
                    test_items_zh.append(f"7. 9层空间复用信道估计误差≤2°（NR MIMO增强）")
                    test_items_en.append(f"7. 9-layer spatial multiplexing channel estimation error ≤2° (NR MIMO enhancement)")

                # 弱信号专属测试项（RSSI≤-105dBm）
                if int(params['rssi'].replace('dBm', '')) <= -105:
                    test_items_zh.append(f"8. 连续30分钟无线链路失败(RLF)次数=0（{params['rssi']}，3GPP RRC连接标准）")
                    test_items_en.append(f"8. Radio Link Failure (RLF) = 0 in 30min at {params['rssi']} (3GPP RRC standard)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "mtk_spec": {
                        "band_info": f"n{match.group('band')} (3300-4200MHz, 200MHz BW, TDD)",
                        "rssi": params['rssi'],
                        "mimo_cap": f"{params['mimo']} Massive MIMO",
                        "antenna": params['antenna_type'],
                        "warning": params.get("freq_warning", "")
                    }
                }

            def parse_lte_rx_test_description_for_qc(self, param: str) -> dict:
                """
                解析高通LTE接收测试参数，生成双语技术说明

                参数:
                    param: 高通LTE接收参数（如：QC_LTE_BC13_QRRFR_ACTION_V3_RX_C0_MCH_4500）
                           标准格式：QC_LTE_BC(?P<band>\d+)_QRRFR_ACTION_V(?P<version>\d+)_RX_C(?P<channel>\d+)_(?P<mode>(H|M|L)CH)_(?P<freq>\d+)

                返回:
                    dict: 含测试目的、测试项（带3GPP/高通双标准）的双语说明
                """
                # 高通LTE RX专属正则表达式
                pattern = r'^QC_LTE_BC(?P<band>\d+)_QRRFR_ACTION_V(?P<version>\d+)_RX_C(?P<channel>\d+)_(?P<mode>(H|M|L)CH)_(?P<freq>\d+)$'
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(
                        f"无效的高通LTE接收参数: {param}，标准格式示例：\n"
                        f"QC_LTE_BC13_QRRFR_ACTION_V3_RX_C0_MCH_4500\n"
                        f"QC_LTE_BC42_QRRFR_ACTION_V7_RX_C2_LCH_3550"
                    )

                # 解析参数（基于3GPP TS 36.101和高通接收规范）
                band = match.group('band')
                # 映射BC频段到具体频率范围
                band_info_map = {
                    '1': '2100MHz (FDD)',
                    '3': '1800MHz (FDD)',
                    '7': '2600MHz (FDD)',
                    '13': '700MHz (FDD)',
                    '20': '800MHz (FDD)',
                    '42': '3500MHz (TDD)'
                }
                band_info = band_info_map.get(band, f"BC{band} (Unknown band)")

                # 计算RSSI值（示例逻辑，可根据实际规范调整）
                rssi_base = -100
                rssi_offset = int(match.group('channel')) * 5
                rssi = rssi_base + rssi_offset

                params = {
                    "band": f"BC{band} ({band_info})",
                    "version": int(match.group('version')),
                    "channel": f"C{match.group('channel')}",
                    "mode": match.group('mode'),
                    "mode_desc": "主信道" if match.group('mode') == 'MCH' else "辅信道",
                    "center_freq": f"{match.group('freq')}MHz",
                    "rssi": f"{rssi}dBm"
                }

                # 频率合法性校验
                freq = int(match.group('freq'))
                freq_range = {
                    '1': (1920, 1980),
                    '3': (1805, 1880),
                    '7': (2620, 2690),
                    '13': (777, 787),
                    '20': (791, 821),
                    '42': (3400, 3600)
                }.get(band, (0, float('inf')))

                if not (freq_range[0] <= freq <= freq_range[1]):
                    params[
                        "freq_warning"] = f"⚠️ 中心频率{freq}MHz超出{params['band']}范围（{freq_range[0]}-{freq_range[1]}MHz）"

                # 测试目的生成
                purpose_zh = (
                    f"验证高通LTE V{params['version']}接收机在{params['band']}频段（{params['center_freq']}，{params['channel']}），"
                    f"{params['mode_desc']}模式下{params['rssi']}信号的接收性能与解调能力")
                purpose_en = (
                    f"Validate reception performance and demodulation capability of Qualcomm LTE V{params['version']} receiver "
                    f"at {params['rssi']} in {params['band']} ({params['center_freq']}, {params['channel']}), {params['mode']} mode")

                # 测试项（3GPP + 高通接收标准）
                test_items_zh = [
                    f"1. RSSI测量精度（高通: ±0.3dBm，3GPP: ±1dBm）",
                    f"3. 误包率（PER）≤0.1%（10000帧，MCS15）",
                    f"4. 邻道选择性（ACS）≥40dB（1.4MHz带宽，-40dBm干扰）",
                    f"5. 阻塞特性（带外-40dBm信号下灵敏度损失≤3dB）",
                    f"6. 多径衰落（ETU300）环境下BLER≤10%"
                ]
                test_items_en = [
                    f"1. RSSI measurement accuracy (Qualcomm: ±0.3dBm, 3GPP: ±1dBm)",
                    f"3. Packet Error Rate (PER) ≤0.1% (10000 packets, MCS15)",
                    f"4. Adjacent Channel Selectivity (ACS) ≥40dB (1.4MHz BW, -40dBm interference)",
                    f"5. Blocking performance (sensitivity loss ≤3dB with out-of-band -40dBm signal)",
                    f"6. BLER ≤10% under multipath fading (ETU300) environment"
                ]

                # 高版本专属测试项（V5及以上支持高阶MIMO）
                if params['version'] >= 5:
                    test_items_zh.extend([
                        f"7. {params['mimo']} MIMO层间一致性（幅度差≤2dB，相位差≤5°）",
                        f"8. 接收分集增益≥3dB（对比单天线配置）"
                    ])
                    test_items_en.extend([
                        f"7. {params['mimo']} MIMO inter-layer consistency (amplitude ≤2dB, phase ≤5°)",
                        f"8. Receive diversity gain ≥3dB (compared to single antenna)"
                    ])

                # TDD频段专属测试项（如BC42）
                if band == '42':
                    test_items_zh.append(f"9. TDD时隙同步精度（±3μs，UL/DL切换点）")
                    test_items_en.append(f"9. TDD slot synchronization accuracy (±3μs, UL/DL switch point)")

                # 弱信号场景专属测试项（RSSI≤-100dBm）
                if int(params['rssi'].replace('dBm', '')) <= -100:
                    test_items_zh.append(f"10. 低信噪比（SNR=5dB）下解调成功率≥99%")
                    test_items_en.append(f"10. Demodulation success rate ≥99% at low SNR (5dB)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "qc_spec": {
                        "band_details": params['band'],
                        "rssi_level": params['rssi'],
                        "version_features": f"V{params['version']}支持{'高阶MIMO' if params['version'] >= 5 else '基础'}接收功能",
                        "warning": params.get("freq_warning", "")
                    }
                }

            def parse_ns_rx_test_description_for_qc(self, param: str) -> dict:
                """
                解析高通NS（New Radio）接收测试参数，生成双语技术说明

                参数:
                    param: 高通NS接收参数（如：QC_NS_N78_RX_RSSI_C1_MCH_636667_ANT_CW）
                                   QC_NS_N78_QRRFR_ACTION_V2_RX_C0_MCH_636667
                           标准格式：QC_NS_N(?P<band>\d+)_(QRRFR_ACTION_V(?P<version>\d+)_)?RX_(RSSI_)?C(?P<channel>\d+)_(?P<mode>(H|M|L)CH)_(?P<freq>\d+)(_ANT_(?P<antenna>\w+))?

                返回:
                    dict: 含测试目的、测试项（带3GPP/高通双标准）的双语说明
                """
                # 高通NS RX专属正则表达式，支持两种格式
                pattern = r'^QC_NS_N(?P<band>\d+)_(QRRFR_ACTION_V(?P<version>\d+)_)?RX_(RSSI_)?C(?P<channel>\d+)_(?P<mode>(H|M|L)CH)_(?P<freq>\d+)(_ANT_(?P<antenna>\w+))?$'
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(
                        f"无效的高通NS接收参数: {param}，标准格式示例：\n"
                        f"QC_NS_N78_RX_RSSI_C1_MCH_636667_ANT_CW\n"
                        f"QC_NS_N78_QRRFR_ACTION_V2_RX_C0_MCH_636667"
                    )

                # 解析参数（基于3GPP TS 38.101和高通接收规范）
                band = match.group('band')
                # 映射N频段到具体频率范围（5G NR频段）
                band_info_map = {
                    '1': '2100MHz (FDD)',
                    '2': '1900MHz (FDD)',
                    '3': '1800MHz (FDD)',
                    '7': '2600MHz (FDD)',
                    '28': '700MHz (FDD)',
                    '38': '2600MHz (TDD)',
                    '41': '2500-2690MHz (TDD)',
                    '77': '3300-4200MHz (TDD)',
                    '78': '3300-3800MHz (TDD)',
                    '79': '4400-5000MHz (TDD)'
                }
                band_info = band_info_map.get(band, f"N{band} (Unknown band)")

                # 处理版本信息，默认为1如果未指定
                version = int(match.group('version')) if match.group('version') else 1

                # 处理天线信息
                antenna = match.group('antenna') if match.group('antenna') else "default configuration"
                antenna_desc = "Continuous wave antenna testing" if antenna == "CW" else antenna

                # 计算RSSI值（优化C0信道的计算逻辑）
                channel = int(match.group('channel'))
                if channel == 0:
                    rssi = -110  # C0信道使用基准值
                else:
                    rssi_base = -110
                    rssi_offset = channel * 4
                    rssi = rssi_base + rssi_offset

                # 先确定调制方式，再添加到params字典
                modulation = "256QAM" if version >= 2 else "64QAM"

                params = {
                    "band": f"N{band} ({band_info})",
                    "version": version,
                    "channel": f"C{match.group('channel')}",
                    "mode": match.group('mode'),
                    "mode_desc": "主信道" if match.group('mode') == 'MCH' else "辅信道",
                    "center_freq": f"{match.group('freq')}MHz",
                    "rssi": f"{rssi}dBm",
                    "antenna": antenna,
                    "antenna_desc": antenna_desc,
                    "mimo": "4x4" if version >= 3 else "2x2",  # V3及以上支持4x4 MIMO
                    "modulation": modulation  # 现在在这里添加modulation键
                }

                # 频率合法性校验（针对N78频段优化）
                freq = int(match.group('freq'))
                freq_range = {
                    '1': (1920, 1980),
                    '2': (1850, 1910),
                    '3': (1710, 1785),
                    '7': (2500, 2570),
                    '28': (703, 748),
                    '38': (2570, 2620),
                    '41': (2496, 2690),
                    '77': (3300, 4200),
                    '78': (3300, 3800),  # N78频段范围
                    '79': (4400, 5000)
                }.get(band, (0, float('inf')))

                if not (freq_range[0] <= freq <= freq_range[1]):
                    params[
                        "freq_warning"] = f"⚠️ 中心频率{freq}MHz超出{params['band']}范围（{freq_range[0]}-{freq_range[1]}MHz）"

                # 测试目的生成（明确包含V2版本信息）
                purpose_zh = (
                    f"验证高通NS V{params['version']}接收机在{params['band']}频段（{params['center_freq']}，{params['channel']}），"
                    f"{params['mode_desc']}模式下{params['rssi']}信号的接收性能与解调能力，天线配置：{params['antenna_desc']}")
                purpose_en = (
                    f"Validate reception performance and demodulation capability of Qualcomm NS V{params['version']} receiver "
                    f"at {params['rssi']} in {params['band']} ({params['center_freq']}, {params['channel']}), {params['mode']} mode, "
                    f"Antenna config: {params['antenna_desc']}")

                # 测试项（3GPP + 高通接收标准，针对V2版本优化）
                test_items_zh = [
                    f"1. RSRP测量精度（高通: ±0.5dB，3GPP: ±1dB）",
                    f"2. RSRQ测量精度（高通: ±1dB，3GPP: ±2dB）",
                    f"3. 误块率（BLER）≤0.01%（100000帧，调制方式{params['modulation']}）",
                    f"4. 邻道抑制比（ACLR）≥45dB（30kHz子载波间隔）",
                    f"5. 带外阻塞（-40dBm干扰下灵敏度损失≤2dB）",
                    f"6. 多普勒频偏（300km/h）环境下性能衰减≤3dB"
                ]
                test_items_en = [
                    f"1. RSRP measurement accuracy (Qualcomm: ±0.5dB, 3GPP: ±1dB)",
                    f"2. RSRQ measurement accuracy (Qualcomm: ±1dB, 3GPP: ±2dB)",
                    f"3. Block Error Rate (BLER) ≤0.01% (100000 blocks, modulation {params['modulation']})",
                    f"4. Adjacent Channel Leakage Ratio (ACLR) ≥45dB (30kHz subcarrier spacing)",
                    f"5. Out-of-band blocking (sensitivity loss ≤2dB with -40dBm interference)",
                    f"6. Performance degradation ≤3dB under Doppler shift (300km/h) environment"
                ]

                # 高版本专属测试项（V3及以上支持更高级功能）
                if params['version'] >= 3:
                    test_items_zh.extend([
                        f"7. {params['mimo']} MIMO空间复用效率≥95%（TM9模式）",
                        f"8. 毫米波波束赋形增益≥15dBi（EIRP测量）",
                        f"9. 双连接（EN-DC）状态下切换时延≤50ms"
                    ])
                    test_items_en.extend([
                        f"7. {params['mimo']} MIMO spatial multiplexing efficiency ≥95% (TM9 mode)",
                        f"8. Millimeter wave beamforming gain ≥15dBi (EIRP measurement)",
                        f"9. Handover delay ≤50ms in EN-DC state"
                    ])

                # 毫米波频段专属测试项
                if band in ['257', '258', '260', '261']:
                    test_items_zh.append(f"10. 雨衰补偿能力（10mm/h降雨率下性能损失≤2dB）")
                    test_items_en.append(
                        f"10. Rain fade compensation capability (performance loss ≤2dB at 10mm/h rainfall rate)")

                # 弱信号场景专属测试项（针对C0信道的-110dBm优化）
                if int(params['rssi'].replace('dBm', '')) <= -105:
                    test_items_zh.append(f"11. 低信噪比（SNR=3dB）下解调成功率≥98%")
                    test_items_en.append(f"11. Demodulation success rate ≥98% at low SNR (3dB)")

                return {
                    "test_purpose_zh": purpose_zh,
                    "test_items_zh": test_items_zh,
                    "test_purpose_en": purpose_en,
                    "test_items_en": test_items_en,
                    "qc_spec": {
                        "band_details": params['band'],
                        "rssi_level": params['rssi'],
                        "version_features": f"V{params['version']}支持{params['mimo']} MIMO和{params['modulation']}调制",
                        "antenna_config": params['antenna_desc'],
                        "warning": params.get("freq_warning", "")
                    }
                }

            def parse_MTK_META_TRACKID_READ_FROM_MD_NVRAM_test_description(self,
                                                                           param: str) -> dict:
                """
                解析MTK META TRACKID从MD NVRAM读取的测试参数（仅支持MTK_META_TRACKID_READ_FROM_MD_NVRAM），生成中英文测试说明

                参数:
                    param: MTK META TRACKID测试参数（固定为：MTK_META_TRACKID_READ_FROM_MD_NVRAM）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 正则匹配：仅验证固定参数MTK_META_TRACKID_READ_FROM_MD_NVRAM
                pattern = r"^MTK_META_TRACKID_READ_FROM_MD_NVRAM$"
                match = re.fullmatch(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK META TRACKID参数格式: {param}，"
                                     "当前函数仅支持唯一合法参数：MTK_META_TRACKID_READ_FROM_MD_NVRAM")

                # 针对固定参数生成专属测试说明（聚焦TrackID类数据通用读取功能验证）
                desc = {
                    "test_purpose_zh": "验证MTK META模式下，从MD NVRAM（调制解调器内存）读取TrackID类核心数据（SN/IMEI/MEID）的基础功能有效性与稳定性（默认V1协议版本）",
                    "test_items_zh": [
                        "1. META指令与MD NVRAM的基础通信链路建立与连通性验证",
                        "2. TrackID类数据（SN/IMEI/MEID）通用读取接口的可用性与响应速度测试",
                        "3. V1版本协议下META与MD NVRAM交互的连续性与容错性验证",
                        "4. 读取结果的格式合规性校验（符合TrackID类数据通用编码标准）",
                        "5. 多轮次连续读取的结果一致性与数据完整性验证"
                    ],
                    "test_purpose_en": "Verify the basic functional validity and stability of reading core TrackID data (SN/IMEI/MEID) from MD NVRAM (Modem NVRAM) in MTK META mode (default V1 protocol version)",
                    "test_items_en": [
                        "1. Verification of basic communication link establishment and connectivity between META commands and MD NVRAM",
                        "2. Availability and response speed test of general reading interface for TrackID data (SN/IMEI/MEID)",
                        "3. Continuity and fault tolerance verification of interaction between META and MD NVRAM under V1 protocol version",
                        "4. Format compliance check of read results (meets general encoding standards for TrackID data)",
                        "5. Consistency and data integrity verification of results from multiple consecutive reading rounds"
                    ]
                }

                return desc

            def chart_generate_and_save2_v1(self,
                                            parsed_eval_and_log_results_container,
                                            parsed_test_process_container,
                                            folder_path,
                                            test_index=1,
                                            show_image=True):  # 新增参数控制是否显示图片
                """
                根据解析后的评估和日志结果容器、解析后的测试过程容器生成图表，并将图表保存为图片文件和 Base64 编码文件。

                参数:
                parsed_eval_and_log_results_container (dict): 解析后的评估和日志结果容器，包含测试数据、状态、测试项、上下限等信息。
                parsed_test_process_container (dict): 解析后的测试过程容器，包含测试过程中的各种数据。
                folder_path (str): 图表和 Base64 编码文件保存的文件夹路径。
                test_index (int, 可选): 测试索引，用于生成图表的名称，默认为 1。
                show_image (bool, 可选): 是否显示生成的图片，默认为 True。

                返回:
                dict: 包含图表名称和 Base64 编码文件路径的字典。如果没有有效数值数据可绘制图表，返回空字典。
                """

                result = {}
                unit = parsed_eval_and_log_results_container['unit']
                test_data = float(parsed_eval_and_log_results_container['test_data'])
                state = parsed_eval_and_log_results_container['state']
                test_item = parsed_eval_and_log_results_container['test_item']
                low_limit = float(parsed_eval_and_log_results_container['low_limit'])
                up_limit = float(parsed_eval_and_log_results_container['up_limit'])
                new_parsed_test_process_container = {k.replace('\t', ' '): v for k, v in
                                                     parsed_test_process_container.items()}

                if new_parsed_test_process_container:
                    valid_data = []
                    for k, v in new_parsed_test_process_container.items():
                        try:
                            # 直接尝试将值转换为浮点数
                            value = float(v)
                            valid_data.append((k, value))
                        except (ValueError, TypeError):
                            print(f"跳过无效值: {k} → {v}")

                    if not valid_data:
                        print("警告：无有效数值数据可绘制图表")
                        return {}  # 修改为返回空字典，与函数文档一致

                    if valid_data:
                        # 添加测试项，测试值
                        keys = [k for k, _ in valid_data]
                        values = [v for _, v in valid_data]

                        plt.figure(figsize=(10, 6))
                        plt.plot(keys, values, marker='o', label='Test Data', linewidth=2)
                        plt.axhline(y=low_limit, color='#dc2626', linestyle='--',
                                    linewidth=2.5, label=f'Low Limit: {low_limit:.1f}{unit}')
                        plt.axhline(y=up_limit, color='#dc2626', linestyle='--',
                                    linewidth=2.5, label=f'Up Limit: {up_limit:.1f}{unit}')

                        # 添加 avg_value
                        values = [v for _, v in valid_data]
                        avg_value = sum(values) / len(values)
                        if avg_value is not None:
                            plt.axhline(y=avg_value, color='#2563eb', linestyle='-.',
                                        linewidth=2, label=f'Avg Value: {avg_value:.1f}{unit}')

                        plt.text(0.05, 0.9, f'State:{state}', transform=plt.gca().transAxes, color='green', ha='left',
                                 va='top')
                        plt.xlabel('Keys')
                        plt.ylabel('Values')
                        plt.title(f'{test_item}_Chart{test_index}')
                        plt.xticks(rotation=90)
                        plt.legend()
                        plt.tight_layout()

                        if os.name == 'nt':  # Windows系统
                            image_path = f'{folder_path}\\{test_item}.png'
                        else:  # Linux/Unix系统
                            image_path = f'{folder_path}/{test_item}.png'
                        plt.savefig(image_path)
                        print(f"图片：{image_path}保存成功。")

                        # 根据参数决定是否显示图片
                        if show_image:
                            plt.show()
                            print("调试：这里为了能看一下生成的图片。")

                        plt.close()

                        if os.name == 'nt':  # Windows系统
                            base64_file_path = f'{folder_path}\\{test_item}_base64.txt'
                        else:  # Linux/Unix系统
                            base64_file_path = f'{folder_path}/{test_item}_base64.txt'
                        with open(image_path, 'rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                        with open(base64_file_path, 'w') as base64_file:
                            base64_file.write(encoded_string.decode('gbk'))
                        print(f"文件：{base64_file_path}写入成功。")

                        result = {"chart_name": f'{test_item}_Chart{test_index}',
                                  "chart_content": base64_file_path}
                else:
                    print("警告：数据容器为空，无法生成图表")

                return result

            def chart_generate_and_save2_v1(self,
                                         parsed_eval_and_log_results_container,
                                         parsed_test_process_container,
                                         folder_path,
                                         test_index=1,
                                         show_image=True):  # 新增参数控制是否显示图片
                """
                根据解析后的评估和日志结果容器、解析后的测试过程容器生成图表，并将图表保存为图片文件和 Base64 编码文件。

                参数:
                parsed_eval_and_log_results_container (dict): 解析后的评估和日志结果容器，包含测试数据、状态、测试项、上下限等信息。
                parsed_test_process_container (dict): 解析后的测试过程容器，包含测试过程中的各种数据。
                folder_path (str): 图表和 Base64 编码文件保存的文件夹路径。
                test_index (int, 可选): 测试索引，用于生成图表的名称，默认为 1。
                show_image (bool, 可选): 是否显示生成的图片，默认为 True。

                返回:
                dict: 包含图表名称和 Base64 编码文件路径的字典。如果没有有效数值数据可绘制图表，返回空字典。
                """

                result = {}
                unit = parsed_eval_and_log_results_container['unit']
                test_data = float(parsed_eval_and_log_results_container['test_data'])
                state = parsed_eval_and_log_results_container['state']
                test_item = parsed_eval_and_log_results_container['test_item']
                low_limit = float(parsed_eval_and_log_results_container['low_limit'])
                up_limit = float(parsed_eval_and_log_results_container['up_limit'])
                new_parsed_test_process_container = {k.replace('\t', ' '): v for k, v in
                                                     parsed_test_process_container.items()}

                if new_parsed_test_process_container:
                    valid_data = []
                    for k, v in new_parsed_test_process_container.items():
                        try:
                            # 直接尝试将值转换为浮点数
                            value = float(v)
                            valid_data.append((k, value))
                        except (ValueError, TypeError):
                            print(f"跳过无效值: {k} → {v}")

                    if not valid_data:
                        print("警告：无有效数值数据可绘制图表")
                        return {}  # 修改为返回空字典，与函数文档一致

                    if valid_data:
                        # 添加测试项，测试值
                        keys = [k for k, _ in valid_data]
                        values = [v for _, v in valid_data]

                        plt.figure(figsize=(10, 6))

                        # 根据状态确定测试数据的颜色（正常为绿色，异常为红色）
                        line_color = 'green' if state == 'PASSED' else 'red'
                        plt.plot(keys, values, marker='o', label='Test Data',
                                 linewidth=2, color=line_color)

                        # 将上下限改为黑色
                        plt.axhline(y=low_limit, color='black', linestyle='--',
                                    linewidth=2.5, label=f'Low Limit: {low_limit:.1f}{unit}')
                        plt.axhline(y=up_limit, color='black', linestyle='--',
                                    linewidth=2.5, label=f'Up Limit: {up_limit:.1f}{unit}')

                        # # 添加 avg_value
                        # values = [v for _, v in valid_data]
                        # avg_value = sum(values) / len(values)
                        # if avg_value is not None:
                        #     plt.axhline(y=avg_value, color='#2563eb', linestyle='-.',
                        #                 linewidth=2, label=f'Avg Value: {avg_value:.1f}{unit}')

                        # 根据状态设置文本颜色
                        text_color = 'green' if state == 'PASSED' else 'red'
                        plt.text(0.05, 0.9, f'State:{state}', transform=plt.gca().transAxes,
                                 color=text_color, ha='left', va='top')

                        plt.xlabel('Keys')
                        plt.ylabel('Values')
                        plt.title(f'{test_item}_Chart{test_index}')
                        plt.xticks(rotation=90)
                        plt.legend()
                        plt.tight_layout()

                        if os.name == 'nt':  # Windows系统
                            image_path = f'{folder_path}\\{test_item}.png'
                        else:  # Linux/Unix系统
                            image_path = f'{folder_path}/{test_item}.png'
                        plt.savefig(image_path)
                        print(f"图片：{image_path}保存成功。")

                        # 根据参数决定是否显示图片
                        if show_image:
                            plt.show()
                            print("调试：这里为了能看一下生成的图片。")

                        plt.close()

                        if os.name == 'nt':  # Windows系统
                            base64_file_path = f'{folder_path}\\{test_item}_base64.txt'
                        else:  # Linux/Unix系统
                            base64_file_path = f'{folder_path}/{test_item}_base64.txt'
                        with open(image_path, 'rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                        with open(base64_file_path, 'w') as base64_file:
                            base64_file.write(encoded_string.decode('gbk'))
                        print(f"文件：{base64_file_path}写入成功。")

                        result = {"chart_name": f'{test_item}_Chart{test_index}',
                                  "chart_content": base64_file_path}
                else:
                    print("警告：数据容器为空，无法生成图表")

                return result


            def chart_generate_and_save2_v2(self,
                                         parsed_eval_and_log_results_container,
                                         parsed_test_process_container,
                                         folder_path,
                                         test_index=1,
                                         show_image=True):  # 新增参数控制是否显示图片
                """
                根据解析后的评估和日志结果容器、解析后的测试过程容器生成图表，并将图表保存为图片文件和 Base64 编码文件。

                参数:
                parsed_eval_and_log_results_container (dict): 解析后的评估和日志结果容器，包含测试数据、状态、测试项、上下限等信息。
                parsed_test_process_container (dict): 解析后的测试过程容器，包含测试过程中的各种数据。
                folder_path (str): 图表和 Base64 编码文件保存的文件夹路径。
                test_index (int, 可选): 测试索引，用于生成图表的名称，默认为 1。
                show_image (bool, 可选): 是否显示生成的图片，默认为 True。

                返回:
                dict: 包含图表名称和 Base64 编码文件路径的字典。如果没有有效数值数据可绘制图表，返回空字典。
                """

                result = {}
                unit = parsed_eval_and_log_results_container['unit']
                test_data = float(parsed_eval_and_log_results_container['test_data'])
                state = parsed_eval_and_log_results_container['state']
                test_item = parsed_eval_and_log_results_container['test_item']
                low_limit = float(parsed_eval_and_log_results_container['low_limit'])
                up_limit = float(parsed_eval_and_log_results_container['up_limit'])
                new_parsed_test_process_container = {k.replace('\t', ' '): v for k, v in
                                                     parsed_test_process_container.items()}

                if new_parsed_test_process_container:
                    valid_data = []
                    for k, v in new_parsed_test_process_container.items():
                        try:
                            # 直接尝试将值转换为浮点数
                            value = float(v)
                            valid_data.append((k, value))
                        except (ValueError, TypeError):
                            print(f"跳过无效值: {k} → {v}")

                    if not valid_data:
                        print("警告：无有效数值数据可绘制图表")
                        return {}  # 修改为返回空字典，与函数文档一致

                    # 如果数据个数超过20个，排序后提取最差的10个数据
                    # 假设"最差"指的是数值最大的数据，若为数值最小则将reverse=False
                    if len(valid_data) > 20:
                        print(f"数据个数超过20个({len(valid_data)}个)，将提取最差的10个数据进行绘图")
                        # 按数值排序，取最大的10个（最差的10个）
                        valid_data.sort(key=lambda x: x[1], reverse=True)
                        valid_data = valid_data[:10]

                    # 提取处理后的数据
                    keys = [k for k, _ in valid_data]
                    values = [v for _, v in valid_data]

                    plt.figure(figsize=(10, 6))

                    # 根据状态确定测试数据的颜色（正常为绿色，异常为红色）
                    line_color = 'green' if state == 'PASSED' else 'red'
                    plt.plot(keys, values, marker='o', label='Test Data',
                             linewidth=2, color=line_color)

                    # 将上下限改为黑色
                    plt.axhline(y=low_limit, color='black', linestyle='--',
                                linewidth=2.5, label=f'Low Limit: {low_limit:.1f}{unit}')
                    plt.axhline(y=up_limit, color='black', linestyle='--',
                                linewidth=2.5, label=f'Up Limit: {up_limit:.1f}{unit}')

                    # 根据状态设置文本颜色
                    text_color = 'green' if state == 'PASSED' else 'red'
                    plt.text(0.05, 0.9, f'State:{state}', transform=plt.gca().transAxes,
                             color=text_color, ha='left', va='top')

                    plt.xlabel('Keys')
                    plt.ylabel('Values')
                    plt.title(f'{test_item}_Chart{test_index}')
                    plt.xticks(rotation=90)
                    plt.legend()
                    plt.tight_layout()

                    if os.name == 'nt':  # Windows系统
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:  # Linux/Unix系统
                        image_path = f'{folder_path}/{test_item}.png'
                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    # 根据参数决定是否显示图片
                    if show_image:
                        plt.show()
                        print("调试：这里为了能看一下生成的图片。")

                    plt.close()

                    if os.name == 'nt':  # Windows系统
                        base64_file_path = f'{folder_path}\\{test_item}_base64.txt'
                    else:  # Linux/Unix系统
                        base64_file_path = f'{folder_path}/{test_item}_base64.txt'
                    with open(image_path, 'rb') as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    with open(base64_file_path, 'w') as base64_file:
                        base64_file.write(encoded_string.decode('gbk'))
                    print(f"文件：{base64_file_path}写入成功。")

                    result = {"chart_name": f'{test_item}_Chart{test_index}',
                              "chart_content": base64_file_path}
                else:
                    print("警告：数据容器为空，无法生成图表")

                return result


            def chart_generate_and_save2(self,
                                         parsed_eval_and_log_results_container,
                                         parsed_test_process_container,
                                         folder_path,
                                         test_index=1,
                                         show_image=True):  # 新增参数控制是否显示图片
                """
                根据解析后的评估和日志结果容器、解析后的测试过程容器生成图表，并将图表保存为图片文件和 Base64 编码文件。

                参数:
                parsed_eval_and_log_results_container (dict): 解析后的评估和日志结果容器，包含测试数据、状态、测试项、上下限等信息。
                parsed_test_process_container (dict): 解析后的测试过程容器，包含测试过程中的各种数据。
                folder_path (str): 图表和 Base64 编码文件保存的文件夹路径。
                test_index (int, 可选): 测试索引，用于生成图表的名称，默认为 1。
                show_image (bool, 可选): 是否显示生成的图片，默认为 True。

                返回:
                dict: 包含图表名称和 Base64 编码文件路径的字典。如果没有有效数值数据可绘制图表，返回空字典。
                """

                result = {}
                unit = parsed_eval_and_log_results_container['unit']
                test_data = float(parsed_eval_and_log_results_container['test_data'])
                state = parsed_eval_and_log_results_container['state']
                test_item = parsed_eval_and_log_results_container['test_item']
                low_limit = float(parsed_eval_and_log_results_container['low_limit'])
                up_limit = float(parsed_eval_and_log_results_container['up_limit'])
                new_parsed_test_process_container = {k.replace('\t', ' '): v for k, v in
                                                     parsed_test_process_container.items()}

                if new_parsed_test_process_container:
                    valid_data = []
                    for k, v in new_parsed_test_process_container.items():
                        try:
                            # 直接尝试将值转换为浮点数
                            value = float(v)
                            valid_data.append((k, value))
                        except (ValueError, TypeError):
                            print(f"跳过无效值: {k} → {v}")

                    if not valid_data:
                        print("警告：无有效数值数据可绘制图表")
                        return {}  # 修改为返回空字典，与函数文档一致

                    # 如果数据个数超过20个，排序后提取最差的10个数据
                    # 假设"最差"指的是数值最大的数据，若为数值最小则将reverse=False
                    if len(valid_data) > 20:
                        print(f"数据个数超过20个({len(valid_data)}个)，将提取最差的10个数据进行绘图")
                        # 按数值排序，取最大的10个（最差的10个）
                        valid_data.sort(key=lambda x: x[1], reverse=True)
                        valid_data = valid_data[:10]

                    # 提取处理后的数据
                    keys = [k for k, _ in valid_data]
                    values = [v for _, v in valid_data]

                    plt.figure(figsize=(10, 6))

                    # 为每个数据点单独判断合格性并设置颜色
                    for i, (key, value) in enumerate(valid_data):
                        # 判断数据是否在合格范围内
                        if low_limit <= value <= up_limit:
                            point_color = 'blue'  # 合格数据点
                        else:
                            point_color = 'red'  # 不合格数据点

                        # 绘制单个数据点
                        plt.scatter(key, value, color=point_color, s=100, zorder=3)

                        # 如果不是第一个点，绘制与前一个点的连接线
                        if i > 0:
                            prev_key, prev_value = valid_data[i - 1]
                            plt.plot([prev_key, key], [prev_value, value], color='gray', linestyle='-', linewidth=1, zorder=2)

                    # 绘制上下限参考线
                    plt.axhline(y=low_limit, color='black', linestyle='--',
                                linewidth=2.5, label=f'Low Limit: {low_limit:.1f}{unit}')
                    plt.axhline(y=up_limit, color='black', linestyle='--',
                                linewidth=2.5, label=f'Up Limit: {up_limit:.1f}{unit}')

                    # 根据状态设置文本颜色
                    text_color = 'green' if state == 'PASSED' else 'red'
                    plt.text(0.05, 0.9, f'State:{state}', transform=plt.gca().transAxes,
                             color=text_color, ha='left', va='top')

                    plt.xlabel('Keys')
                    plt.ylabel('Values')
                    plt.title(f'{test_item}_Chart{test_index}')
                    plt.xticks(rotation=90)
                    # 添加颜色图例
                    plt.scatter([], [], color='blue', label='pass data', s=100)
                    plt.scatter([], [], color='red', label='failed data', s=100)
                    plt.legend()
                    plt.tight_layout()

                    if os.name == 'nt':  # Windows系统
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:  # Linux/Unix系统
                        image_path = f'{folder_path}/{test_item}.png'
                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    # 根据参数决定是否显示图片
                    if show_image:
                        plt.show()
                        print("调试：这里为了能看一下生成的图片。")

                    plt.close()

                    if os.name == 'nt':  # Windows系统
                        base64_file_path = f'{folder_path}\\{test_item}_base64.txt'
                    else:  # Linux/Unix系统
                        base64_file_path = f'{folder_path}/{test_item}_base64.txt'
                    with open(image_path, 'rb') as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    with open(base64_file_path, 'w') as base64_file:
                        base64_file.write(encoded_string.decode('gbk'))
                    print(f"文件：{base64_file_path}写入成功。")

                    result = {"chart_name": f'{test_item}_Chart{test_index}',
                              "chart_content": base64_file_path}
                else:
                    print("警告：数据容器为空，无法生成图表")

                return result

            def chart_generate_generate_and_save_for_mtk_common(self,
                                                                test_result_dict,
                                                                folder_path,
                                                                test_index=1,
                                                                show_image=False):
                """
                根据MTK解析后的test_result字典生成测试图表，并保存为图片文件和Base64编码文件
                适配结构：test_result_dict = {'test_result': {'name':..., 'data':..., 'unit':..., 'state':..., 'lowlimit':..., 'uplimit':...,...}}

                参数:
                    test_result_dict (dict): MTK解析后的测试结果字典，外层含'test_result'键，内层含测试项名、数据、上下限、状态等
                    folder_path (str): 图表和Base64文件保存的文件夹路径（需提前创建，否则会报错）
                    test_index (int, 可选): 测试索引，用于图表名称区分，默认为1
                    show_image (bool, 可选): 是否显示生成的图片，默认为False（产线场景默认不显示）

                返回:
                    dict: 包含图表名称(chart_name)和Base64文件路径(chart_content)的字典；无有效数据时返回空字典
                """
                result = {}
                # 步骤1：提取test_result内层核心数据（处理键不存在的异常）
                try:
                    # 从外层字典获取内层test_result数据
                    inner_test_result = test_result_dict.get('test_result', {})
                    # 提取关键字段（测试项名、数据、单位、状态、上下限）
                    test_item = inner_test_result.get('test_item', f'MTK_Test_{test_index}')  # 测试项名（默认兜底）
                    data_str = inner_test_result.get('test_data', '')  # 原始数据（可能为字符串格式）
                    unit = inner_test_result.get('unit', '')  # 单位（如P/F、dBm等）
                    state = inner_test_result.get('state', 'UNKNOWN').upper()  # 状态（统一转为大写，如PASSED/FAILED）
                    low_limit_str = inner_test_result.get('low_limit', '0')  # 下限
                    up_limit_str = inner_test_result.get('up_limit', '0')  # 上限

                    # 步骤2：数据格式转换（字符串转浮点数，确保可绘图）
                    # 处理data：支持单个数据或逗号分隔的多数据（如"-1"或"2,3,4"）
                    data_list = []
                    if data_str:
                        # 按逗号分割多数据，过滤空字符串
                        raw_data = [d.strip() for d in data_str.split(',') if d.strip()]
                        for d in raw_data:
                            try:
                                data_list.append(float(d))
                            except (ValueError, TypeError):
                                print(f"跳过无效测试数据: {d}（非数值格式）")

                    # 处理上下限（确保为浮点数）
                    low_limit = float(low_limit_str) if low_limit_str.replace('.', '').isdigit() else 0.0
                    up_limit = float(up_limit_str) if up_limit_str.replace('.', '').isdigit() else 0.0

                    # 步骤3：验证有效数据（无有效测试数据则返回空字典）
                    if not data_list:
                        print(f"警告：测试项[{test_item}]无有效数值数据（原始数据：{data_str}），无法生成图表")
                        return result

                    # 步骤4：构造绘图数据（生成x轴标签，对应数据索引）
                    # x轴为数据点序号（如1,2,3...），y轴为测试数据
                    x_labels = [f'Data_{i + 1}' for i in range(len(data_list))]
                    y_values = data_list

                    # 步骤5：创建图表（参考chart_generate_and_save2的样式）
                    plt.figure(figsize=(10, 6))  # 固定图表尺寸

                    # 绘制测试数据折线（根据状态设置颜色：PASSED绿色，其他红色）
                    line_color = 'green' if state == 'PASSED' else 'red'
                    plt.plot(x_labels, y_values, marker='o', label='Test Data', linewidth=2, color=line_color)

                    # 绘制上下限虚线（统一黑色，加粗）
                    plt.axhline(y=low_limit, color='black', linestyle='--', linewidth=2.5,
                                label=f'Low Limit: {low_limit:.1f}{unit}' if unit else f'Low Limit: {low_limit:.1f}')
                    plt.axhline(y=up_limit, color='black', linestyle='--', linewidth=2.5,
                                label=f'Up Limit: {up_limit:.1f}{unit}' if unit else f'Up Limit: {up_limit:.1f}')

                    # 添加状态文本（位置：左上角，颜色与折线一致）
                    text_color = 'green' if state == 'PASSED' else 'red'
                    plt.text(0.05, 0.9, f'Test State: {state}', transform=plt.gca().transAxes,
                             color=text_color, ha='left', va='top', fontsize=10, weight='bold')

                    # 设置图表标签与标题
                    plt.xlabel('Test Data Point', fontsize=10)
                    plt.ylabel(f'Value ({unit})' if unit else 'Value', fontsize=10)
                    plt.title(f'{test_item}_Chart_{test_index}', fontsize=12, weight='bold')
                    plt.xticks(rotation=45)  # x轴标签旋转45度，避免重叠
                    plt.legend(loc='upper right', fontsize=9)
                    plt.tight_layout()  # 自动调整布局，防止标签截断

                    # 步骤6：创建保存路径（处理Windows/Linux路径分隔符）
                    # 确保文件夹存在（不存在则创建）
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        print(f"提示：自动创建文件夹 {folder_path}")

                    # 生成图片路径和Base64文件路径
                    if os.name == 'nt':  # Windows系统（路径分隔符\）
                        image_path = f'{folder_path}\\{test_item}_Chart{test_index}.png'
                        base64_file_path = f'{folder_path}\\{test_item}_Chart{test_index}_base64.txt'
                    else:  # Linux/Unix系统（路径分隔符/）
                        image_path = f'{folder_path}/{test_item}_Chart{test_index}.png'
                        base64_file_path = f'{folder_path}/{test_item}_Chart{test_index}_base64.txt'

                    # 步骤7：保存图表图片
                    plt.savefig(image_path, dpi=100, bbox_inches='tight')  # dpi=100确保清晰度，bbox_inches避免标签截断
                    print(f"成功保存图表图片：{image_path}")

                    # 步骤8：根据参数决定是否显示图片
                    if show_image:
                        plt.show()
                        print("提示：已显示图表（仅调试场景启用）")
                    plt.close()  # 关闭图表，释放内存

                    # 步骤9：生成Base64编码文件
                    with open(image_path, 'rb') as image_file:
                        encoded_bytes = base64.b64encode(image_file.read())  # 读取图片并编码为Base64
                    with open(base64_file_path, 'w', encoding='utf-8') as base64_file:
                        base64_file.write(encoded_bytes.decode('utf-8'))  # 写入Base64文本文件
                    print(f"成功保存Base64文件：{base64_file_path}")

                    # 步骤10：构造返回结果（与chart_generate_and_save2返回格式一致）
                    result = {
                        "chart_name": f'{test_item}_Chart_{test_index}',
                        "chart_content": base64_file_path
                    }

                except Exception as e:
                    # 捕获所有异常，避免程序崩溃，返回空字典
                    print(f"生成MTK图表时发生错误：{str(e)}（测试索引：{test_index}，文件夹路径：{folder_path}）")
                    result = {}

                return result

            def chart_generate_and_save3_v1(self,
                                            parsed_eval_and_log_results_container,
                                            parsed_test_process_container,
                                            route_container_parse,
                                            folder_path,
                                            test_index=1,
                                            show_image=True):
                result = {}
                unit = parsed_eval_and_log_results_container['unit']
                test_data = float(parsed_eval_and_log_results_container['test_data'])
                state = parsed_eval_and_log_results_container['state']
                test_item = parsed_eval_and_log_results_container['test_item']
                low_limit = float(parsed_eval_and_log_results_container['low_limit'])
                up_limit = float(parsed_eval_and_log_results_container['up_limit'])
                new_parsed_test_process_container = {k.replace('\t', ' '): v for k, v in parsed_test_process_container.items()}

                if new_parsed_test_process_container:
                    valid_data = []
                    for k, v in new_parsed_test_process_container.items():
                        try:
                            # 直接尝试将值转换为浮点数
                            value = float(v)
                            valid_data.append((k, value))
                        except (ValueError, TypeError):
                            print(f"跳过无效值: {k} → {v}")

                    if not valid_data:
                        print("警告：无有效数值数据可绘制图表")
                        return

                    if valid_data:

                        # 循环筛选波动较大的数据，直到数据项数量在10-30之间
                        valid_data = self.filter_data_by_deviation(valid_data, test_index)
                        # while len(valid_data) > 30:
                        #     # 计算每个数据点的偏差
                        #     deviated_data = calculate_deviation(valid_data)
                        #     # 按偏差降序排序
                        #     sorted_data = sorted(deviated_data, key=lambda x: x[2], reverse=True)
                        #     # 保留波动最大的前30%数据，但至少保留10个
                        #     retain_count = max(10, int(len(sorted_data) * 0.3))
                        #     # 提取筛选后的数据
                        #     valid_data = [(k, v) for k, v, _ in sorted_data[:retain_count]]
                        #
                        #     # 如果筛选后的数据仍然超过30个，继续下一轮筛选
                        #     if len(valid_data) > 30:
                        #         print(f"第{test_index}次筛选后数据点数量: {len(valid_data)}，继续筛选...")
                        #     else:
                        #         print(f"第{test_index}次筛选后数据点数量: {len(valid_data)}，符合要求")
                        #
                        # if len(valid_data) < 10:
                        #     print(f"警告：筛选后有效数据点数量过少 ({len(valid_data)})，可能影响图表质量")

                        # 添加测试数据，测试项
                        keys = [k for k, _ in valid_data]
                        values = [v for _, v in valid_data]

                        plt.figure(figsize=(10, 6))
                        plt.plot(keys, values, marker='o', label='Test Data', linewidth=2)
                        plt.axhline(y=low_limit, color='#dc2626', linestyle='--',
                                    linewidth=2.5, label=f'Low Limit: {low_limit:.1f}{unit}')
                        plt.axhline(y=up_limit, color='#dc2626', linestyle='--',
                                    linewidth=2.5, label=f'Up Limit: {up_limit:.1f}{unit}')

                        # 添加 avg_value
                        values = [v for _, v in valid_data]
                        avg_value = sum(values) / len(values)
                        if avg_value is not None:
                            plt.axhline(y=avg_value, color='#2563eb', linestyle='-.',
                                        linewidth=2, label=f'Avg Value: {avg_value:.1f}{unit}')

                        # 添加 state,route_container_parse 中的数据
                        route_text = "\n".join([f"{k}: {v}" for k, v in route_container_parse.items()])
                        plt.text(0.05, 0.9, f'State:{state}\n{route_text}', transform=plt.gca().transAxes, color='green', ha='left',
                                 va='top')

                        plt.xlabel('Keys')
                        plt.ylabel('Values')
                        plt.title(f'{test_item}_Chart{test_index}')
                        plt.xticks(rotation=90)
                        plt.legend()
                        plt.tight_layout()

                        if os.name == 'nt':  # Windows系统
                            image_path = f'{folder_path}\\{test_item}.png'
                        else:  # Linux/Unix系统
                            image_path = f'{folder_path}/{test_item}.png'
                        plt.savefig(image_path)
                        print(f"图片：{image_path}保存成功。")

                        # 根据参数决定是否显示图片
                        if show_image:
                            plt.show()
                            print("调试：这里为了能看一下生成的图片。")
                        # 关闭绘图工具，不显示图片
                        plt.close()

                        if os.name == 'nt':  # Windows系统
                            base64_file_path = f'{folder_path}\\{test_item}_base64.txt'
                        else:  # Linux/Unix系统
                            base64_file_path = f'{folder_path}/{test_item}_base64.txt'
                        with open(image_path, 'rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                        with open(base64_file_path, 'w') as base64_file:
                            base64_file.write(encoded_string.decode('gbk'))
                        print(f"文件：{base64_file_path}写入成功。")

                        result = {"chart_name": f'{test_item}_Chart{test_index}',
                                  "chart_content": base64_file_path}
                else:
                    print("警告：数据容器为空，无法生成图表")

                return result

            def chart_generate_and_save3_v2(self,
                                            parsed_eval_and_log_results_container,
                                            parsed_test_process_container,
                                            route_container_parse,
                                            folder_path,
                                            test_index=1,
                                            show_image=True):
                result = {}
                unit = parsed_eval_and_log_results_container['unit']
                test_data = float(parsed_eval_and_log_results_container['test_data'])
                state = parsed_eval_and_log_results_container['state']
                test_item = parsed_eval_and_log_results_container['test_item']
                low_limit = float(parsed_eval_and_log_results_container['low_limit'])
                up_limit = float(parsed_eval_and_log_results_container['up_limit'])
                new_parsed_test_process_container = {k.replace('\t', ' '): v for k, v in
                                                     parsed_test_process_container.items()}

                if new_parsed_test_process_container:
                    valid_data = []
                    for k, v in new_parsed_test_process_container.items():
                        try:
                            # 直接尝试将值转换为浮点数
                            value = float(v)
                            valid_data.append((k, value))
                        except (ValueError, TypeError):
                            print(f"跳过无效值: {k} → {v}")

                    if not valid_data:
                        print("警告：无有效数值数据可绘制图表")
                        return

                    if valid_data:

                        # 循环筛选波动较大的数据，直到数据项数量在10-30之间
                        valid_data = self.filter_data_by_deviation(valid_data, test_index)

                        # 添加测试数据，测试项
                        keys = [k for k, _ in valid_data]
                        values = [v for _, v in valid_data]

                        plt.figure(figsize=(10, 6))

                        # 根据状态确定测试数据的颜色（正常为绿色，异常为红色）
                        line_color = 'green' if state == '正常' else 'red'
                        plt.plot(keys, values, marker='o', label='Test Data', linewidth=2, color=line_color)

                        # 将上下限改为黑色
                        plt.axhline(y=low_limit, color='black', linestyle='--',
                                    linewidth=2.5, label=f'Low Limit: {low_limit:.1f}{unit}')
                        plt.axhline(y=up_limit, color='black', linestyle='--',
                                    linewidth=2.5, label=f'Up Limit: {up_limit:.1f}{unit}')

                        # 添加 avg_value
                        values = [v for _, v in valid_data]
                        avg_value = sum(values) / len(values)
                        if avg_value is not None:
                            plt.axhline(y=avg_value, color='#2563eb', linestyle='-.',
                                        linewidth=2, label=f'Avg Value: {avg_value:.1f}{unit}')

                        # 添加 state,route_container_parse 中的数据，根据状态设置文本颜色
                        text_color = 'green' if state == '正常' else 'red'
                        route_text = "\n".join([f"{k}: {v}" for k, v in route_container_parse.items()])
                        plt.text(0.05, 0.9, f'State:{state}\n{route_text}', transform=plt.gca().transAxes,
                                 color=text_color, ha='left', va='top')

                        plt.xlabel('Keys')
                        plt.ylabel('Values')
                        plt.title(f'{test_item}_Chart{test_index}')
                        plt.xticks(rotation=90)
                        plt.legend()
                        plt.tight_layout()

                        if os.name == 'nt':  # Windows系统
                            image_path = f'{folder_path}\\{test_item}.png'
                        else:  # Linux/Unix系统
                            image_path = f'{folder_path}/{test_item}.png'
                        plt.savefig(image_path)
                        print(f"图片：{image_path}保存成功。")

                        # 根据参数决定是否显示图片
                        if show_image:
                            plt.show()
                            print("调试：这里为了能看一下生成的图片。")
                        # 关闭绘图工具，不显示图片
                        plt.close()

                        if os.name == 'nt':  # Windows系统
                            base64_file_path = f'{folder_path}\\{test_item}_base64.txt'
                        else:  # Linux/Unix系统
                            base64_file_path = f'{folder_path}/{test_item}_base64.txt'
                        with open(image_path, 'rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                        with open(base64_file_path, 'w') as base64_file:
                            base64_file.write(encoded_string.decode('gbk'))
                        print(f"文件：{base64_file_path}写入成功。")

                        result = {"chart_name": f'{test_item}_Chart{test_index}',
                                  "chart_content": base64_file_path}
                else:
                    print("警告：数据容器为空，无法生成图表")

                return result

            def chart_generate_and_save3(self,
                                         parsed_eval_and_log_results_container,
                                         parsed_test_process_container,
                                         route_container_parse,
                                         folder_path,
                                         test_index=1,
                                         show_image=True):
                result = {}
                unit = parsed_eval_and_log_results_container['unit']
                test_data = float(parsed_eval_and_log_results_container['test_data'])
                # 显式获取状态并去除可能的空白字符，确保判断准确性
                state = parsed_eval_and_log_results_container.get('state', '').strip()
                test_item = parsed_eval_and_log_results_container['test_item']
                low_limit = float(parsed_eval_and_log_results_container['low_limit'])
                up_limit = float(parsed_eval_and_log_results_container['up_limit'])
                new_parsed_test_process_container = {k.replace('\t', ' '): v for k, v in
                                                     parsed_test_process_container.items()}

                # 调试：打印状态值，确认实际状态
                print(f"调试：当前测试项[{test_item}]的状态为: '{state}'")

                if new_parsed_test_process_container:
                    valid_data = []
                    for k, v in new_parsed_test_process_container.items():
                        try:
                            value = float(v)
                            valid_data.append((k, value))
                        except (ValueError, TypeError):
                            print(f"跳过无效值: {k} → {v}")

                    if not valid_data:
                        print("警告：无有效数值数据可绘制图表")
                        return

                    if valid_data:
                        valid_data = self.filter_data_by_deviation(valid_data, test_index)
                        keys = [k for k, _ in valid_data]
                        values = [v for _, v in valid_data]

                        plt.figure(figsize=(10, 6))

                        # 精确判断状态，确保合格项显示绿色
                        # 考虑可能的状态值变体（如"合格"也视为正常）
                        # is_normal = state in ['PASSED', 'FAILED']
                        line_color = 'green' if state == 'PASSED' else 'red'
                        plt.plot(keys, values, marker='o', label='Test Data', linewidth=2, color=line_color)

                        # 上下限保持黑色
                        plt.axhline(y=low_limit, color='black', linestyle='--',
                                    linewidth=2.5, label=f'Low Limit: {low_limit:.1f}{unit}')
                        plt.axhline(y=up_limit, color='black', linestyle='--',
                                    linewidth=2.5, label=f'Up Limit: {up_limit:.1f}{unit}')

                        # # 添加平均值线
                        # avg_value = sum(values) / len(values) if values else None
                        # if avg_value is not None:
                        #     plt.axhline(y=avg_value, color='#2563eb', linestyle='-.',
                        #                 linewidth=2, label=f'Avg Value: {avg_value:.1f}{unit}')

                        # 状态文本颜色与线条颜色保持一致
                        text_color = 'green' if state == 'PASSED' else 'red'
                        route_text = "\n".join([f"{k}: {v}" for k, v in route_container_parse.items()])
                        plt.text(0.05, 0.9, f'State:{state}\n{route_text}', transform=plt.gca().transAxes,
                                 color=text_color, ha='left', va='top')

                        plt.xlabel('Keys')
                        plt.ylabel('Values')
                        plt.title(f'{test_item}_Chart{test_index}')
                        plt.xticks(rotation=90)
                        plt.legend()
                        plt.tight_layout()

                        # 路径处理
                        if os.name == 'nt':
                            image_path = f'{folder_path}\\{test_item}.png'
                            base64_file_path = f'{folder_path}\\{test_item}_base64.txt'
                        else:
                            image_path = f'{folder_path}/{test_item}.png'
                            base64_file_path = f'{folder_path}/{test_item}_base64.txt'

                        # 保存图片
                        plt.savefig(image_path)
                        print(f"图片：{image_path}保存成功。")

                        if show_image:
                            plt.show()
                            print("调试：显示生成的图片。")
                        plt.close()

                        # 生成base64文件
                        with open(image_path, 'rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                        with open(base64_file_path, 'w') as base64_file:
                            base64_file.write(encoded_string.decode('gbk'))
                        print(f"文件：{base64_file_path}写入成功。")

                        result = {"chart_name": f'{test_item}_Chart{test_index}',
                                  "chart_content": base64_file_path}
                else:
                    print("警告：数据容器为空，无法生成图表")

                return result

            def chart_generate_and_save3_for_basic_band(self,
                                                        parsed_eval_and_log_results_container,
                                                        folder_path,
                                                        show_image=True):
                try:
                    # 创建图表
                    plt.figure(figsize=(12, 8))

                    # 用于存储所有测试项名称，以便设置x轴
                    test_items = []
                    test_results = []
                    colors = []
                    labels = []

                    # 遍历容器中的每个测试结果，收集数据
                    for result_key, result_data in parsed_eval_and_log_results_container.items():
                        # 提取当前测试结果的基本信息
                        unit = result_data['unit']
                        test_data = float(result_data['test_data'])
                        state = result_data.get('state', '').strip()
                        test_item = result_data['test_item']

                        # 存储数据用于绘图
                        test_items.append(f"{test_item}\n({result_key})")  # 合并测试项和结果键
                        test_results.append(test_data)

                        # 根据状态确定颜色
                        is_passed = state == 'PASSED'
                        colors.append('green' if is_passed else 'red')

                        # 保存标签信息
                        labels.append(f"{test_item} ({result_key}): {test_data:.1f}{unit} - {state}")

                    # 绘制所有测试数据点
                    plt.scatter(test_items, test_results, color=colors, s=150, zorder=3)

                    # 为每个测试项绘制上下限参考线
                    for i, (result_key, result_data) in enumerate(parsed_eval_and_log_results_container.items()):
                        unit = result_data['unit']
                        low_limit = float(result_data['low_limit'])
                        up_limit = float(result_data['up_limit'])

                        # 绘制垂直线表示该测试项的位置
                        plt.axvline(x=i, color='gray', linestyle=':', alpha=0.5)

                        # 绘制上下限横线，范围限定在当前测试项位置
                        plt.hlines(y=low_limit, xmin=i - 0.3, xmax=i + 0.3, color='black', linestyle='-',
                                   linewidth=1.5,
                                   label=f'Low Limit ({result_key}): {low_limit:.1f}{unit}' if i == 0 else "")
                        plt.hlines(y=up_limit, xmin=i - 0.3, xmax=i + 0.3, color='black', linestyle='-',
                                   linewidth=1.5,
                                   label=f'Up Limit ({result_key}): {up_limit:.1f}{unit}' if i == 0 else "")

                    # 添加图例说明状态颜色
                    plt.scatter([], [], color='green', s=100, label='PASSED')
                    plt.scatter([], [], color='red', s=100, label='FAILED')

                    # 设置图表属性
                    plt.xlabel('Test Items')
                    first_unit = next(iter(parsed_eval_and_log_results_container.values()))['unit']
                    plt.ylabel(f'Value ({first_unit})')
                    plt.title('All Test Results Comparison')
                    plt.xticks(rotation=45, ha='right')
                    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # 图例放在图表右侧
                    plt.grid(True, linestyle=':', alpha=0.7, axis='y')
                    plt.tight_layout()

                    # 处理文件路径
                    if os.name == 'nt':
                        image_path = f'{folder_path}\\all_test_results.png'
                        base64_file_path = f'{folder_path}\\all_test_results_base64.txt'
                    else:
                        image_path = f'{folder_path}/all_test_results.png'
                        base64_file_path = f'{folder_path}/all_test_results_base64.txt'

                    # 保存图片
                    plt.savefig(image_path, bbox_inches='tight')  # 确保图例完整保存
                    print(f"图片：{image_path}保存成功。")

                    # 显示图片（如果需要）
                    if show_image:
                        plt.show()
                    plt.close()

                    # 生成base64编码文件
                    with open(image_path, 'rb') as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    with open(base64_file_path, 'w') as base64_file:
                        base64_file.write(encoded_string.decode('gbk'))
                    print(f"文件：{base64_file_path}写入成功。")

                    # 存储结果的图表信息
                    result = {
                        "chart_name": "All_Test_Results_Comparison",
                        "chart_content": base64_file_path
                    }

                    return result

                except Exception as e:
                    print(f"处理测试结果时出错: {str(e)}")
                    return None

            def filter_data_by_deviation(self, valid_data, test_index=1, min_count=10, max_count=30,
                                         retain_ratio=0.3):
                """
                根据数据点的波动程度筛选数据，确保数据点数量在指定范围内。

                参数:
                valid_data (list): 包含(key, value)元组的有效数据列表
                test_index (int): 测试索引，用于日志输出
                min_count (int): 最小保留数据点数量
                max_count (int): 最大保留数据点数量
                retain_ratio (float): 每次筛选保留的比例(0.0-1.0)

                返回:
                list: 筛选后的有效数据列表
                """

                # 计算偏差
                def calculate_deviation(data_list):
                    """计算每个数据点与平均值的绝对偏差"""
                    if not data_list:
                        return []
                    values = [v for _, v in data_list]
                    avg = sum(values) / len(values)
                    return [(k, v, abs(v - avg)) for k, v in data_list]

                # 复制数据避免修改原始列表
                filtered_data = valid_data.copy()

                # 循环筛选波动较大的数据，直到数据项数量在min_count-max_count之间
                iteration = 0
                while len(filtered_data) > max_count:
                    iteration += 1
                    # 计算每个数据点的偏差
                    deviated_data = calculate_deviation(filtered_data)
                    # 按偏差降序排序
                    sorted_data = sorted(deviated_data, key=lambda x: x[2], reverse=True)
                    # 保留波动最大的数据，但至少保留min_count个
                    retain_count = max(min_count, int(len(sorted_data) * retain_ratio))
                    # 提取筛选后的数据
                    filtered_data = [(k, v) for k, v, _ in sorted_data[:retain_count]]

                    # 输出筛选过程信息
                    if len(filtered_data) > max_count:
                        print(
                            f"第{test_index}次筛选(迭代{iteration})后数据点数量: {len(filtered_data)}，继续筛选...")
                    else:
                        print(
                            f"第{test_index}次筛选(迭代{iteration})后数据点数量: {len(filtered_data)}，符合要求")

                if len(filtered_data) < min_count:
                    print(f"警告：筛选后有效数据点数量过少 ({len(filtered_data)})，可能影响图表质量")

                return filtered_data

            def chart_get_base64_read_file(self, file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    file_name = os.path.basename(file_path)
                    return file_name, content
                except FileNotFoundError:
                    print(f"错误：文件 {file_path} 未找到。")
                    return None, None
                except Exception as e:
                    print(f"错误：发生了未知错误 {e}。")
                    return None, None

            def chart_get_base64_read_image(self, image_path):
                try:
                    with open(image_path, 'rb', encoding='utf-8') as image_file:
                        base64_string = base64.b64encode(image_file.read())
                    print(f"文件：{image_path} 转换base64成功。")
                    return image_path, base64_string
                except FileNotFoundError:
                    print(f"错误：文件 {image_path} 未找到。")
                    return None
                except Exception as e:
                    print(f"错误：发生了未知错误 {e}。")
                    return None

            def parse_test_result_cal(self,
                                      test_result_container,
                                      key_name):

                parsed_eval_and_log_results_cal_container = {}
                start_parsing = False
                keys = ['PREV_CAL', 'NEW_CAL', key_name, 'STATUS']
                index = 0

                for line in test_result_container:
                    if line.strip() == '# test_result':
                        start_parsing = True
                        continue

                    if start_parsing:
                        # 检查 line 是否包含 keys 中的任何一个元素
                        if not any(key in line for key in keys):
                            continue
                        if index < len(keys):
                            # 如果索引超出 keys 范围，跳过当前行
                            if index >= len(keys):
                                continue
                            parts = line.strip().split('\t')
                            sub_dict = {
                                'test_item': parts[3],
                                'low_limit': parts[4],
                                'up_limit': parts[5],
                                'test_data': parts[6],
                                'unit': parts[7],
                                'state': parts[10]
                            }
                            parsed_eval_and_log_results_cal_container[keys[index]] = sub_dict
                            index += 1
                            # 检查 sub_dict 中的 'test_item' 是否包含 keys 中的某一个元素
                            for key in keys:
                                if key in sub_dict['test_item']:
                                    parsed_eval_and_log_results_cal_container[key] = sub_dict
                                    index += 1
                                    break

                # 将 key_name 的 unit 数值赋给 PREV_CAL 和 NEW_CAL
                if key_name in parsed_eval_and_log_results_cal_container:
                    key_name_unit = parsed_eval_and_log_results_cal_container[key_name]['unit']
                    if 'PREV_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['PREV_CAL']['unit'] = key_name_unit
                    if 'NEW_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['NEW_CAL']['unit'] = key_name_unit

                    # 提取 parsed_container 的数据
                    test_item = parsed_eval_and_log_results_cal_container[key_name].get('test_item', "N/A")
                    low_limit = float(parsed_eval_and_log_results_cal_container[key_name].get('low_limit', "N/A"))
                    up_limit = float(parsed_eval_and_log_results_cal_container[key_name].get('up_limit', "N/A"))
                    test_data = float(parsed_eval_and_log_results_cal_container[key_name].get('test_data', "N/A"))
                    unit = parsed_eval_and_log_results_cal_container[key_name].get('unit', "N/A")

                    if 'FAILED' in parsed_eval_and_log_results_cal_container[key_name].get('state', 'N/A'):
                        # 过滤 ' ' 和 '*'
                        parsed_eval_and_log_results_cal_container[key_name]['state'] = (
                            parsed_eval_and_log_results_cal_container[key_name]['state'].replace(' ', '').replace('*',
                                                                                                                  ''))

                    state = parsed_eval_and_log_results_cal_container[key_name].get('state', "N/A")
                    # "意义": "确保设备发射功率在合规范围内，避免干扰或信号弱。",
                    meaning = ''
                    # "指标": "发射端实际功率（dBm）",
                    indicator = ''
                    # "趋势分析": "值集中在中位区（稳定）",
                    trend_analysis = ''
                    # "隐含问题可能性": "低",
                    implied_problem_possibility = ''
                    # 图片名称
                    chart_name = ''
                    # 图片内容(base64)
                    chart_content = ''

                    parsed_eval_and_log_results_cal_container_key_name = {
                        'test_item': test_item,
                        'low_limit': low_limit,
                        'up_limit': up_limit,
                        'test_data': test_data,
                        'unit': unit,
                        'state': state,
                        'meaning': meaning,
                        'indicator': indicator,
                        'trend_analysis': trend_analysis,
                        'implied_problem_possibility': implied_problem_possibility,
                        'chart_name': chart_name,
                        'chart_content': chart_content
                    }

                parsed_eval_and_log_results_cal_container[key_name] = parsed_eval_and_log_results_cal_container_key_name
                return parsed_eval_and_log_results_cal_container

            def parse_test_result_for_mtk_common(self, input_list):
                """
                 从指定列表中提取内容，生成多层级字典
                 核心逻辑：
                 1. 解析核心字段生成基础字典（name、uplimit等）
                 2. 提取Details字段并将其作为键值对直接并入基础字典
                 3. 新增6个固定字段（meaning、indicator等）到核心字典
                 4. 最终外层基础字典作为外层字典的唯一值，形成统一嵌套结构

                 参数:
                     input_list (list): 待提取内容的列表，需符合特定格式

                 返回:
                     dict: 外层为单key字典，内层为包含原有字段+新增字段的统一字典
                 """
                result_dict = {}
                # 初始化核心字典（存储所有字段：核心索引字段 + Details + 新增6个字段）
                core_dict = {}

                # 步骤1：解析核心索引字段，存入核心字典
                if len(input_list) >= 2:
                    # 处理外层key（后续用于外层字典）
                    raw_outer_key = input_list[0]
                    filtered_outer_key = raw_outer_key.replace(" ", "").replace("#", "")

                    # 处理核心字段值：过滤前缀→分割→按索引提取
                    raw_core_value = input_list[1]
                    filtered_core_value = raw_core_value.replace("EvalAndLogResults\t", "", 1)
                    value_parts = filtered_core_value.split("\t")

                    # 按索引映射核心字段（防索引越界）
                    index_field_map = {
                        2: "test_item",
                        3: "up_limit",
                        4: "low_limit",
                        5: "test_data",
                        6: "unit",
                        9: "state"
                    }
                    for idx, field_name in index_field_map.items():
                        if idx < len(value_parts):
                            field_val = value_parts[idx]
                            # state字段特殊处理：过滤*并清理空格
                            if field_name == "state":
                                field_val = field_val.replace("*", "").strip()
                            core_dict[field_name] = field_val

                # 步骤2：提取Details字段，并入核心字典
                for i in range(len(input_list)):
                    if "Details:" in input_list[i]:
                        # 处理Details的key：过滤前缀和冒号
                        raw_detail_key = input_list[i]
                        filtered_detail_key = raw_detail_key.replace("EvalAndLogResults\t", "", 1).replace(":", "")
                        # 处理Details的value：过滤前缀
                        if i + 1 < len(input_list):
                            raw_detail_val = input_list[i + 1]
                            filtered_detail_val = raw_detail_val.replace("EvalAndLogResults\t", "", 1)
                            # 关键步骤：将Details键值对直接入核心字典
                            core_dict[filtered_detail_key] = filtered_detail_val
                        break  # 假设列表中仅存在一个Details字段

                # 步骤3：新增6个固定字段到核心字典（初始值设为None，可根据实际需求调整默认值）
                new_fields = {
                    "meaning": None,  # 含义字段（可后续根据业务逻辑赋值）
                    "indicator": None,  # 指标字段（可后续根据业务逻辑赋值）
                    "trend_analysis": None,  # 趋势分析字段（可后续根据业务逻辑赋值）
                    "stability": None,  # 稳定分析字段（可后续根据业务逻辑赋值）
                    "implied_problem_possibility": None,  # 隐含问题可能性字段（可后续根据业务逻辑赋值）
                    "chart_name": None,  # 图表名称字段（可后续根据业务逻辑赋值）
                    "chart_content": None  # 图表内容字段（可后续根据业务逻辑赋值）
                }
                # 将新增字段合并到核心字典（若字段名冲突，以新增字段的None值覆盖，可根据需求调整优先级）
                core_dict.update(new_fields)

                # 步骤4：构建最终结构（外层字典包裹合并后的核心字典）
                if core_dict:  # 仅当核心字典非空时构建结果
                    raw_outer_key = input_list[0] if len(input_list) > 0 else "default_key"
                    filtered_outer_key = raw_outer_key.replace(" ", "").replace("#", "")
                    result_dict[filtered_outer_key] = core_dict

                return result_dict

            def parse_test_result_lte_rx_error_cal(self,
                                                   test_result_container,
                                                   key_name):

                parsed_eval_and_log_results_cal_container = {}
                start_parsing = False
                keys = ['PREV_CAL', 'NEW_CAL', key_name]
                index = 0

                for line in test_result_container:
                    if line.strip() == '# test_result':
                        start_parsing = True
                        continue

                    if start_parsing:
                        # 检查 line 是否包含 keys 中的任何一个元素
                        if not any(key in line for key in keys):
                            continue

                        # 如果索引超出 keys 范围，跳过当前行
                        if index >= len(keys):
                            continue

                        parts = line.strip().split('\t')
                        sub_dict = {
                            'test_item': parts[3],
                            'low_limit': parts[4],
                            'up_limit': parts[5],
                            'test_data': parts[6],
                            'unit': parts[7],
                            'state': parts[10]
                        }
                        # 检查 sub_dict 中的 'test_item' 是否包含 keys 中的某一个元素
                        for key in keys:
                            if key in sub_dict['test_item']:
                                parsed_eval_and_log_results_cal_container[key] = sub_dict
                                index += 1
                                break

                # # 仅处理包含 keys 中元素的记录
                # new_parsed_container = {}
                # for key in keys:
                #     if key in parsed_eval_and_log_results_cal_container:
                #         new_parsed_container[key] = parsed_eval_and_log_results_cal_container[key]
                #
                # parsed_eval_and_log_results_cal_container = new_parsed_container

                # 将 key_name 的 unit 数值赋给 PREV_CAL 和 NEW_CAL
                if key_name in parsed_eval_and_log_results_cal_container:
                    key_name_unit = parsed_eval_and_log_results_cal_container[key_name]['unit']
                    if 'PREV_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['PREV_CAL']['unit'] = key_name_unit
                    if 'NEW_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['NEW_CAL']['unit'] = key_name_unit

                    # 提取 parsed_container 的数据
                    test_item = parsed_eval_and_log_results_cal_container[key_name].get('test_item', "N/A")
                    low_limit = float(parsed_eval_and_log_results_cal_container[key_name].get('low_limit', "N/A"))
                    up_limit = float(parsed_eval_and_log_results_cal_container[key_name].get('up_limit', "N/A"))
                    test_data = float(parsed_eval_and_log_results_cal_container[key_name].get('test_data', "N/A"))
                    unit = parsed_eval_and_log_results_cal_container[key_name].get('unit', "N/A")

                    if 'FAILED' in parsed_eval_and_log_results_cal_container[key_name].get('state', 'N/A'):
                        # 过滤 ' ' 和 '*'
                        parsed_eval_and_log_results_cal_container[key_name]['state'] = (
                            parsed_eval_and_log_results_cal_container[key_name]['state'].replace(' ', '').replace('*',
                                                                                                                  ''))

                    state = parsed_eval_and_log_results_cal_container[key_name].get('state', "N/A")
                    # "意义": "确保设备发射功率在合规范围内，避免干扰或信号弱。",
                    meaning = ''
                    # "指标": "发射端实际功率（dBm）",
                    indicator = ''
                    # "趋势分析": "值集中在中位区（稳定）",
                    trend_analysis = ''
                    # "隐含问题可能性": "低",
                    implied_problem_possibility = ''
                    # 图片名称
                    chart_name = ''
                    # 图片内容(base64)
                    chart_content = ''

                    parsed_eval_and_log_results_cal_container_key_name = {
                        'test_item': test_item,
                        'low_limit': low_limit,
                        'up_limit': up_limit,
                        'test_data': test_data,
                        'unit': unit,
                        'state': state,
                        'meaning': meaning,
                        'indicator': indicator,
                        'trend_analysis': trend_analysis,
                        'implied_problem_possibility': implied_problem_possibility,
                        'chart_name': chart_name,
                        'chart_content': chart_content
                    }

                parsed_eval_and_log_results_cal_container[key_name] = parsed_eval_and_log_results_cal_container_key_name
                return parsed_eval_and_log_results_cal_container

            def parse_test_result_lte_rx_error_cal2(self,
                                                    parse_test_result_lte_rx_error_cal):

                parsed_eval_and_log_results_cal_container = {}
                keys = ['PREV_CAL']
                sub_dict = {}
                last_failed_test_item = None  # 追踪上一个FAILED测试项的键

                for index, line in enumerate(parse_test_result_lte_rx_error_cal):
                    # 处理包含FAILED的行
                    if '* FAILED *' in line:
                        parts = line.strip().split('\t')
                        # 确保有足够的字段
                        if len(parts) >= 11:
                            test_item = parts[3]
                            sub_dict[test_item] = {
                                'test_item': test_item,
                                'low_limit': parts[4],
                                'up_limit': parts[5],
                                'test_data': parts[6],  # 初始值，可能会被Details内容覆盖
                                'unit': parts[7],
                                'state': parts[10].replace(' ', '').replace('*', ''),
                            }
                            last_failed_test_item = test_item  # 记录当前FAILED测试项

                    # 处理包含Details的行的下一行
                    elif 'Details:' in line and index + 1 < len(parse_test_result_lte_rx_error_cal):
                        details_line = parse_test_result_lte_rx_error_cal[index + 1]
                        # 提取Details内容（从第1个制表符后开始，跳过EvalAndLogResults）
                        details_parts = details_line.strip().split('\t', 1)
                        if len(details_parts) >= 2:
                            details_content = details_parts[1]  # 获取第1个制表符后的所有内容
                            # 去掉#之后的内容
                            if '#' in details_content:
                                details_content = details_content.split('#', 1)[0].strip()
                            # 如果有上一个FAILED测试项，则更新其test_data
                            if last_failed_test_item and last_failed_test_item in sub_dict:
                                sub_dict[last_failed_test_item]['test_data'] = details_content

                    # 将sub_dict赋值给容器变量
                parsed_eval_and_log_results_cal_container = sub_dict

                # 将sub_dict转换为指定格式的容器
                if parsed_eval_and_log_results_cal_container:
                    # 处理所有测试项
                    for key in list(parsed_eval_and_log_results_cal_container.keys()):
                        test_item_data = parsed_eval_and_log_results_cal_container[key]

                        state = test_item_data.get('state', "N/A")
                        # "意义": "确保设备发射功率在合规范围内，避免干扰或信号弱。",
                        meaning = ''
                        # "指标": "发射端实际功率（dBm）",
                        indicator = ''
                        # "趋势分析": "值集中在中位区（稳定）",
                        trend_analysis = ''
                        # "隐含问题可能性": "低",
                        implied_problem_possibility = ''
                        # 图片名称
                        chart_name = ''
                        # 图片内容(base64)
                        chart_content = ''

                        parsed_eval_and_log_results_cal_container[key] = {
                            'test_item': test_item_data['test_item'],
                            'low_limit': float(test_item_data['low_limit']),
                            'up_limit': float(test_item_data['up_limit']),
                            'test_data': test_item_data['test_data'],
                            'unit': test_item_data['unit'],
                            'state': state,
                            'meaning': meaning,
                            'indicator': indicator,
                            'trend_analysis': trend_analysis,
                            'implied_problem_possibility': implied_problem_possibility,
                            'chart_name': chart_name,
                            'chart_content': chart_content
                        }

                return parsed_eval_and_log_results_cal_container  # 返回更新后的容器

            def parse_test_result_tx_cal(self,
                                         test_result_container):
                parsed_eval_and_log_results_cal_container = {}
                start_parsing = False
                keys = ['PREV_CAL', 'NEW_CAL', 'TX_POWER', 'STATUS']
                index = 0

                for line in test_result_container:
                    if line.strip() == '# test_result':
                        start_parsing = True
                        continue
                    if start_parsing:
                        if index < len(keys):
                            parts = line.strip().split('\t')
                            sub_dict = {
                                'test_item': parts[3],
                                'low_limit': parts[4],
                                'up_limit': parts[5],
                                'test_data': parts[6],
                                'unit': parts[7],
                                'state': parts[10]
                            }
                            parsed_eval_and_log_results_cal_container[keys[index]] = sub_dict
                            index += 1

                # 将 TX_POWER 的 unit 数值赋给 PREV_CAL 和 NEW_CAL
                if 'TX_POWER' in parsed_eval_and_log_results_cal_container:
                    tx_power_unit = parsed_eval_and_log_results_cal_container['TX_POWER']['unit']
                    if 'PREV_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['PREV_CAL']['unit'] = tx_power_unit
                    if 'NEW_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['NEW_CAL']['unit'] = tx_power_unit

                    # 提取 parsed_container 的数据
                    test_item = parsed_eval_and_log_results_cal_container['TX_POWER'].get('test_item', "N/A")
                    low_limit = float(parsed_eval_and_log_results_cal_container['TX_POWER'].get('low_limit', "N/A"))
                    up_limit = float(parsed_eval_and_log_results_cal_container['TX_POWER'].get('up_limit', "N/A"))
                    test_data = float(parsed_eval_and_log_results_cal_container['TX_POWER'].get('test_data', "N/A"))
                    unit = parsed_eval_and_log_results_cal_container['TX_POWER'].get('unit', "N/A")

                    if 'FAILED' in parsed_eval_and_log_results_cal_container['TX_POWER'].get('state', 'N/A'):
                        # 过滤 ' ' 和 '*'
                        parsed_eval_and_log_results_cal_container['TX_POWER']['state'] = (
                            parsed_eval_and_log_results_cal_container['TX_POWER']['state'].replace(' ', '').replace('*', ''))

                    state = parsed_eval_and_log_results_cal_container['TX_POWER'].get('state', "N/A")
                    # "意义": "确保设备发射功率在合规范围内，避免干扰或信号弱。",
                    meaning = ''
                    # "指标": "发射端实际功率（dBm）",
                    indicator = ''
                    # "趋势分析": "值集中在中位区（稳定）",
                    trend_analysis = ''
                    # "隐含问题可能性": "低",
                    implied_problem_possibility = ''
                    # 图片名称
                    chart_name = ''
                    # 图片内容(base64)
                    chart_content = ''

                    parsed_eval_and_log_results_cal_container_tx_power = {
                        'test_item': test_item,
                        'low_limit': low_limit,
                        'up_limit': up_limit,
                        'test_data': test_data,
                        'unit': unit,
                        'state': state,
                        'meaning': meaning,
                        'indicator': indicator,
                        'trend_analysis': trend_analysis,
                        'implied_problem_possibility': implied_problem_possibility,
                        'chart_name': chart_name,
                        'chart_content': chart_content
                    }

                parsed_eval_and_log_results_cal_container['TX_POWER'] = parsed_eval_and_log_results_cal_container_tx_power
                return parsed_eval_and_log_results_cal_container

            def parse_test_result_rx_cal(self,
                                         test_result_container):
                parsed_eval_and_log_results_cal_container = {}
                start_parsing = False
                keys = ['PREV_CAL', 'NEW_CAL', 'RSSI_ANT', 'STATUS']
                index = 0

                for line in test_result_container:
                    if line.strip() == '# test_result':
                        start_parsing = True
                        continue
                    if start_parsing:
                        if index < len(keys):
                            parts = line.strip().split('\t')
                            sub_dict = {
                                'test_item': parts[3],
                                'low_limit': parts[4],
                                'up_limit': parts[5],
                                'test_data': parts[6],
                                'unit': parts[7],
                                'state': parts[10]
                            }
                            parsed_eval_and_log_results_cal_container[keys[index]] = sub_dict
                            index += 1

                # 将 TX_POWER 的 unit 数值赋给 PREV_CAL 和 NEW_CAL
                if 'RSSI_ANT' in parsed_eval_and_log_results_cal_container:
                    tx_power_unit = parsed_eval_and_log_results_cal_container['RSSI_ANT']['unit']
                    if 'PREV_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['PREV_CAL']['unit'] = tx_power_unit
                    if 'NEW_CAL' in parsed_eval_and_log_results_cal_container:
                        parsed_eval_and_log_results_cal_container['NEW_CAL']['unit'] = tx_power_unit

                    # 提取 parsed_container 的数据
                    test_item = parsed_eval_and_log_results_cal_container['RSSI_ANT'].get('test_item', "N/A")
                    low_limit = float(parsed_eval_and_log_results_cal_container['RSSI_ANT'].get('low_limit', "N/A"))
                    up_limit = float(parsed_eval_and_log_results_cal_container['RSSI_ANT'].get('up_limit', "N/A"))
                    test_data = float(parsed_eval_and_log_results_cal_container['RSSI_ANT'].get('test_data', "N/A"))
                    unit = parsed_eval_and_log_results_cal_container['RSSI_ANT'].get('unit', "N/A")

                    if 'FAILED' in parsed_eval_and_log_results_cal_container['RSSI_ANT'].get('state', 'N/A'):
                        # 过滤 ' ' 和 '*'
                        parsed_eval_and_log_results_cal_container['RSSI_ANT']['state'] = (
                            parsed_eval_and_log_results_cal_container['RSSI_ANT']['state'].replace(' ', '').replace('*', ''))

                    state = parsed_eval_and_log_results_cal_container['RSSI_ANT'].get('state', "N/A")
                    # "意义": "确保设备发射功率在合规范围内，避免干扰或信号弱。",
                    meaning = ''
                    # "指标": "发射端实际功率（dBm）",
                    indicator = ''
                    # "趋势分析": "值集中在中位区（稳定）",
                    trend_analysis = ''
                    # "隐含问题可能性": "低",
                    implied_problem_possibility = ''
                    # 图片名称
                    chart_name = ''
                    # 图片内容(base64)
                    chart_content = ''

                    parsed_eval_and_log_results_cal_container_rx_power = {
                        'test_item': test_item,
                        'low_limit': low_limit,
                        'up_limit': up_limit,
                        'test_data': test_data,
                        'unit': unit,
                        'state': state,
                        'meaning': meaning,
                        'indicator': indicator,
                        'trend_analysis': trend_analysis,
                        'implied_problem_possibility': implied_problem_possibility,
                        'chart_name': chart_name,
                        'chart_content': chart_content
                    }

                parsed_eval_and_log_results_cal_container['RSSI_ANT'] = parsed_eval_and_log_results_cal_container_rx_power
                return parsed_eval_and_log_results_cal_container

            def parse_test_process_cal(self,
                                       test_process_container,
                                       parsed_eval_and_log_results_container,
                                       folder_path,
                                       key_name):
                parsed_test_process_container = {}
                current_round = 0
                current_data = {}
                try:
                    # 跳过第一行
                    for line in test_process_container[1:]:
                        if ':' in line:
                            try:
                                key_part, value_part = line.split(':', 1)
                                key_part = key_part.strip()
                                value_part = value_part.strip()
                                if 'Final measurement =' in value_part:
                                    try:
                                        current_round += 1
                                        final_measurement = float(value_part.split('=')[1].strip())
                                        current_data['Final measurement'] = final_measurement
                                        parsed_test_process_container[current_round] = current_data
                                        current_data = {}
                                    except ValueError:
                                        print(f"Error converting final measurement in line: {line}")
                                else:
                                    try:
                                        current_data[key_part] = float(value_part)
                                    except ValueError:
                                        print(f"Error converting value in line: {line}")
                            except ValueError:
                                print(f"Error splitting line: {line}")
                except IndexError:
                    print("The data list is too short to skip the first line.")

                # 4-3-1.------------------- test_process_container的数据验证 -------------------
                print("\n结构化数据容器:")
                for k, v in parsed_test_process_container.items():
                    print(f"{k} → {v if v is not None else '[原始行]'}")

                # 4-4.将parsed_test_process_container和parsed_eval_and_log_results_container，先格式化，后写入文件。
                # 1. 在parsed_test_process_container的下标0处插入key="name"和value="test_process"
                new_dict = {"title_name": "test_process"}
                new_dict.update(parsed_test_process_container)
                parsed_test_process_container = new_dict

                # 2. 在parsed_eval_and_log_results_container的头部插入独立的name字段（保持原有数据完整性）
                if isinstance(parsed_eval_and_log_results_container, list):
                    if parsed_eval_and_log_results_container:
                        # 创建独立的头部标识（不影响原有元素）
                        header = {"title_name": "test_result"}
                        # 插入到列表头部（原数据后移）
                        parsed_eval_and_log_results_container.insert(0, header)
                    else:
                        # 空列表处理（保持代码健壮性）
                        parsed_eval_and_log_results_container = [{"title_name": "test_result"}]
                elif isinstance(parsed_eval_and_log_results_container, dict):
                    new_dict = {"title_name": "test_result"}
                    new_dict.update(parsed_eval_and_log_results_container)
                    parsed_eval_and_log_results_container = new_dict
                    output_file_path_new = ''
                    if (isinstance(parsed_eval_and_log_results_container, dict)
                            and key_name in parsed_eval_and_log_results_container
                            and 'test_item' in parsed_eval_and_log_results_container[key_name]):
                        test_item = parsed_eval_and_log_results_container[key_name]['test_item']

                        if os.name == 'nt':  # windows OS
                            output_file_path_new = f'{folder_path}\\{test_item}_parsed_data.txt'
                        else:  # Linux OS
                            output_file_path_new = f'{folder_path}/{test_item}_parsed_data.txt'
                        print(output_file_path_new)
                    else:
                        print("字典结构不符合要求，无法生成文件路径。")

                # 3. 将parsed_test_process_container和parsed_eval_and_log_results_container写入文件
                try:
                    with open(output_file_path_new, 'w', encoding='gbk') as output_file_new:
                        for key, value in parsed_test_process_container.items():
                            output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                        if isinstance(parsed_eval_and_log_results_container, list):
                            for item in parsed_eval_and_log_results_container:
                                for key, value in item.items():
                                    output_file_new.write(f"{key}: {value}\n")
                        elif isinstance(parsed_eval_and_log_results_container, dict):
                            for key, value in parsed_eval_and_log_results_container.items():
                                output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                except Exception as e:
                    print(f"写入文件时出错: {e}")

                return parsed_test_process_container, parsed_eval_and_log_results_container

            def parse_test_process_tx_cal(self,
                                          test_process_container,
                                          parsed_eval_and_log_results_container,
                                          folder_path):
                parsed_test_process_container = {}
                current_round = 0
                current_data = {}
                try:
                    # 跳过第一行
                    for line in test_process_container[1:]:
                        if ':' in line:
                            try:
                                key_part, value_part = line.split(':', 1)
                                key_part = key_part.strip()
                                value_part = value_part.strip()
                                if 'Final measurement =' in value_part:
                                    try:
                                        current_round += 1
                                        final_measurement = float(value_part.split('=')[1].strip())
                                        current_data['Final measurement'] = final_measurement
                                        parsed_test_process_container[current_round] = current_data
                                        current_data = {}
                                    except ValueError:
                                        print(f"Error converting final measurement in line: {line}")
                                else:
                                    try:
                                        current_data[key_part] = float(value_part)
                                    except ValueError:
                                        print(f"Error converting value in line: {line}")
                            except ValueError:
                                print(f"Error splitting line: {line}")
                except IndexError:
                    print("The data list is too short to skip the first line.")

                # 4-3-1.------------------- test_process_container的数据验证 -------------------
                print("\n结构化数据容器:")
                for k, v in parsed_test_process_container.items():
                    print(f"{k} → {v if v is not None else '[原始行]'}")

                # 4-4.将parsed_test_process_container和parsed_eval_and_log_results_container，先格式化，后写入文件。
                # 1. 在parsed_test_process_container的下标0处插入key="name"和value="test_process"
                new_dict = {"title_name": "test_process"}
                new_dict.update(parsed_test_process_container)
                parsed_test_process_container = new_dict

                # 2. 在parsed_eval_and_log_results_container的头部插入独立的name字段（保持原有数据完整性）
                if isinstance(parsed_eval_and_log_results_container, list):
                    if parsed_eval_and_log_results_container:
                        # 创建独立的头部标识（不影响原有元素）
                        header = {"title_name": "test_result"}
                        # 插入到列表头部（原数据后移）
                        parsed_eval_and_log_results_container.insert(0, header)
                    else:
                        # 空列表处理（保持代码健壮性）
                        parsed_eval_and_log_results_container = [{"title_name": "test_result"}]
                elif isinstance(parsed_eval_and_log_results_container, dict):
                    new_dict = {"title_name": "test_result"}
                    new_dict.update(parsed_eval_and_log_results_container)
                    parsed_eval_and_log_results_container = new_dict
                    output_file_path_new = ''
                    if (isinstance(parsed_eval_and_log_results_container, dict)
                            and 'TX_POWER' in parsed_eval_and_log_results_container
                            and 'test_item' in parsed_eval_and_log_results_container['TX_POWER']):
                        test_item = parsed_eval_and_log_results_container['TX_POWER']['test_item']
                        output_file_path_new = f'{folder_path}\\{test_item}_parsed_data.txt'
                        print(output_file_path_new)
                    else:
                        print("字典结构不符合要求，无法生成文件路径。")

                # 3. 将parsed_test_process_container和parsed_eval_and_log_results_container写入文件
                try:
                    with open(output_file_path_new, 'w', encoding='gbk') as output_file_new:
                        for key, value in parsed_test_process_container.items():
                            output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                        if isinstance(parsed_eval_and_log_results_container, list):
                            for item in parsed_eval_and_log_results_container:
                                for key, value in item.items():
                                    output_file_new.write(f"{key}: {value}\n")
                        elif isinstance(parsed_eval_and_log_results_container, dict):
                            for key, value in parsed_eval_and_log_results_container.items():
                                output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                except Exception as e:
                    print(f"写入文件时出错: {e}")

                return parsed_test_process_container, parsed_eval_and_log_results_container

            def parse_test_process_rx_cal(self,
                                          test_process_container,
                                          parsed_eval_and_log_results_container,
                                          folder_path):
                parsed_test_process_container = {}
                current_round = 0
                current_data = {}
                try:
                    # 跳过第一行
                    for line in test_process_container[1:]:
                        if ':' in line:
                            try:
                                key_part, value_part = line.split(':', 1)
                                key_part = key_part.strip()
                                value_part = value_part.strip()
                                if 'Final measurement =' in value_part:
                                    try:
                                        current_round += 1
                                        final_measurement = float(value_part.split('=')[1].strip())
                                        current_data['Final measurement'] = final_measurement
                                        parsed_test_process_container[current_round] = current_data
                                        current_data = {}
                                    except ValueError:
                                        print(f"Error converting final measurement in line: {line}")
                                else:
                                    try:
                                        current_data[key_part] = float(value_part)
                                    except ValueError:
                                        print(f"Error converting value in line: {line}")
                            except ValueError:
                                print(f"Error splitting line: {line}")
                except IndexError:
                    print("The data list is too short to skip the first line.")

                # 4-3-1.------------------- test_process_container的数据验证 -------------------
                print("\n结构化数据容器:")
                for k, v in parsed_test_process_container.items():
                    print(f"{k} → {v if v is not None else '[原始行]'}")

                # 4-4.将parsed_test_process_container和parsed_eval_and_log_results_container，先格式化，后写入文件。
                # 1. 在parsed_test_process_container的下标0处插入key="name"和value="test_process"
                new_dict = {"title_name": "test_process"}
                new_dict.update(parsed_test_process_container)
                parsed_test_process_container = new_dict

                # 2. 在parsed_eval_and_log_results_container的头部插入独立的name字段（保持原有数据完整性）
                if isinstance(parsed_eval_and_log_results_container, list):
                    if parsed_eval_and_log_results_container:
                        # 创建独立的头部标识（不影响原有元素）
                        header = {"title_name": "test_result"}
                        # 插入到列表头部（原数据后移）
                        parsed_eval_and_log_results_container.insert(0, header)
                    else:
                        # 空列表处理（保持代码健壮性）
                        parsed_eval_and_log_results_container = [{"title_name": "test_result"}]
                elif isinstance(parsed_eval_and_log_results_container, dict):
                    new_dict = {"title_name": "test_result"}
                    new_dict.update(parsed_eval_and_log_results_container)
                    parsed_eval_and_log_results_container = new_dict
                    output_file_path_new = ''
                    if (isinstance(parsed_eval_and_log_results_container, dict)
                            and 'RSSI_ANT' in parsed_eval_and_log_results_container
                            and 'test_item' in parsed_eval_and_log_results_container['RSSI_ANT']):
                        test_item = parsed_eval_and_log_results_container['RSSI_ANT']['test_item']
                        output_file_path_new = f'{folder_path}\\{test_item}_parsed_data.txt'
                        print(output_file_path_new)
                    else:
                        print("字典结构不符合要求，无法生成文件路径。")

                # 3. 将parsed_test_process_container和parsed_eval_and_log_results_container写入文件
                try:
                    with open(output_file_path_new, 'w', encoding='gbk') as output_file_new:
                        for key, value in parsed_test_process_container.items():
                            output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                        if isinstance(parsed_eval_and_log_results_container, list):
                            for item in parsed_eval_and_log_results_container:
                                for key, value in item.items():
                                    output_file_new.write(f"{key}: {value}\n")
                        elif isinstance(parsed_eval_and_log_results_container, dict):
                            for key, value in parsed_eval_and_log_results_container.items():
                                output_file_new.write(f"{key}: {value}\n")
                        output_file_new.write("\n")
                except Exception as e:
                    print(f"写入文件时出错: {e}")

                return parsed_test_process_container, parsed_eval_and_log_results_container

            def convert_dict_to_list(self,
                                     parsed_test_process_cal_container):
                temp_values = []
                for key, value in parsed_test_process_cal_container.items():
                    if str(key).isdigit():
                        temp_values.append(value)
                values = list(temp_values)

                # 将所有字典中的值组成一个新的列表
                lst_values = []
                for sub_dict in values:
                    lst_values.extend(sub_dict.values())
                return lst_values

            def convert_dict_to_list_for_mtk_common(self,
                                                    parsed_test_process_cal_container):
                """
                从输入的result_dict中提取test_result下的data字段内容，转换为列表并返回

                参数:
                    result_dict (dict): 输入字典，需包含"test_result"键，且其对应值中包含"data"键

                返回:
                    list: 若成功提取data，返回转换后的列表；若提取失败（如键不存在、data为空），返回空列表
                """
                # 初始化返回的空列表
                data_list = []

                # 1. 检查外层字典是否包含"test_result"键
                if "test_result" in parsed_test_process_cal_container:
                    test_result_dict = parsed_test_process_cal_container["test_result"]
                    # 2. 检查test_result字典是否包含"data"键
                    if "data" in test_result_dict:
                        data_value = test_result_dict["data"]
                        # 3. 确保data值不为空，再转换为列表（支持字符串直接转列表，或已为列表的情况）
                        if data_value is not None and str(data_value).strip() != "":
                            # 若data是字符串（如"-1"或"1,2,3"），按常见分隔符分割；若已是列表则直接使用
                            if isinstance(data_value, str):
                                # 支持逗号、制表符、空格等常见分隔符，可根据实际数据格式调整
                                separators = [",", "\t", " "]
                                for sep in separators:
                                    if sep in data_value:
                                        data_list = [item.strip() for item in data_value.split(sep) if item.strip()]
                                        break
                                else:
                                    # 若没有找到分隔符，将单个数据作为列表唯一元素
                                    data_list = [data_value.strip()]
                            elif isinstance(data_value, list):
                                # 若data已是列表，直接返回（过滤空元素）
                                data_list = [item.strip() for item in data_value if str(item).strip()]

                return data_list

            def parse_judge_value_range3(self,
                                         values,
                                         low_limit,
                                         up_limit,
                                         top_percentage_limit=0.5,
                                         language='zh'):
                """
                代码说明：
                judge_value_range 函数：
                首先，按照原逻辑对每个值进行判定，得到判定结果列表 results。
                接着，统计每种判定结果的数量，存储在 counts 字典中。
                然后，对 counts 字典按数量降序排序。
                若占比最高的判定结果占比超过 50%，则返回该判定结果；否则，返回所有非 “无效数据” 且数量大于 0 的判定结果，用逗号连接。
                主程序部分：调用 judge_value_range 函数得到数据方位并打印。
                """

                # 中英文对照字典
                translation_dict = {
                    "无效数据": "Invalid data",
                    "指标范围外偏下": "Below the lower limit",
                    "指标范围外偏上": "Above the upper limit",
                    "指标范围内偏下": "Lower within the limit",
                    "指标范围内偏上": "Upper within the limit",
                    "指标的中间": "In the middle of the limit",
                    "无有效数据": "No valid data"
                }

                results = []
                # for value_str in values:
                #     try:
                #         num_str = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', str(value_str))[0]
                #         value = float(num_str)
                #     except (IndexError, ValueError):
                #         results.append("无效数据")
                #         continue

                for value_str in values:
                    if isinstance(value_str, float):
                        value_str = str(value_str)
                    try:
                        num_str = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', value_str)[0]
                        value = float(num_str)
                    except (IndexError, ValueError):
                        results.append("无效数据")
                        continue

                    if value < low_limit:
                        results.append("指标范围外偏下")
                    elif value > up_limit:
                        results.append("指标范围外偏上")
                    else:
                        middle = (low_limit + up_limit) / 2
                        if value < middle:
                            results.append("指标范围内偏下")
                        elif value > middle:
                            results.append("指标范围内偏上")
                        else:
                            results.append("指标的中间")

                total_count = len(results)
                if total_count == 0:
                    result = "无有效数据"
                else:
                    counts = {
                        "指标范围外偏下": 0,
                        "指标范围外偏上": 0,
                        "指标范围内偏下": 0,
                        "指标范围内偏上": 0,
                        "指标的中间": 0,
                        "无效数据": 0
                    }
                    for result in results:
                        counts[result] += 1

                    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
                    top_result = sorted_counts[0]
                    top_percentage = top_result[1] / total_count

                    if top_percentage > top_percentage_limit:
                        result = top_result[0]
                    else:
                        significant_results = [res for res, count in sorted_counts if count > 0 and res != "无效数据"]
                        result = ", ".join(significant_results)

                if language == 'en':
                    if isinstance(result, str):
                        result = result.split(', ')
                        translated_result = [translation_dict.get(item, item) for item in result]
                        return ", ".join(translated_result)
                return result

            def parse_wifi_tx_test_purpose2items_cal(self,
                                                     param: str) -> dict:
                """
                解析MTK WLAN测试参数，生成中英文测试说明

                参数:
                    param: MTK WLAN测试参数（如：MTK_WLAN_2.4G_C0_TX_POWER_MCH07_ANT_CW 或 MTK_WLAN2.4G_TX_C0_HQA_15DB_MCH7_CAL）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 正则解析参数结构，支持新格式
                pattern = r"MTK_WLAN(?:_)?(?P<band1>\d+\.?\d*G)_TX_C(?P<channel1>\d+)_(?P<quality1>HQ[A-Z]?)_(?P<attenuation1>\d+DB)_(?P<mode1>(H|M|L)CH\d+)_CAL|" \
                          r"MTK_WLAN_(?P<band2>\d+\.?\d*G)_C(?P<channel2>\d+)_(?P<test_type>TX_POWER|RX_SENSITIVITY)_(?P<mode2>(H|M|L)CH\d+)_ANT_(?P<cal_type>\w+)|" \
                          r"MTK_WLAN(?P<band3>\d+\.?\d*G)_TX_(?P<quality3>HQ[A-Z]?)_C(?P<antenna3>\d+)_(?P<attenuation3>\d+DB)_CH(?P<channel3>\d+)_CAL"

                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN参数格式: {param}")

                # 解析第一种新格式参数
                if match.group('band1'):
                    band = match.group('band1')
                    channel = match.group('channel1')
                    quality = match.group('quality1')
                    attenuation = match.group('attenuation1')
                    mode = match.group('mode1')

                    desc = {
                        "test_purpose_zh": f"验证{band}频段C{channel}通道在{quality}质量、{attenuation}衰减和{mode}模式下的发射校准",
                        "test_items_zh": [
                            f"1. {band}频段C{channel}通道的发射性能指标",
                            f"2. {quality}质量下的信号稳定性",
                            f"3. {attenuation}衰减时的信号强度",
                            f"4. {mode}模式下的校准准确性"
                        ],
                        "test_purpose_en": f"Verify the transmission calibration of {band} band, channel {channel} under {quality} quality, {attenuation} attenuation and {mode} mode",
                        "test_items_en": [
                            f"1. Transmission performance indicators at {band} band, channel {channel}",
                            f"2. Signal stability under {quality} quality",
                            f"3. Signal strength at {attenuation} attenuation",
                            f"4. Calibration accuracy in {mode} mode"
                        ]
                    }
                # 解析旧格式参数
                elif match.group('band2'):
                    band = match.group('band2')
                    channel = match.group('channel2')
                    test_type = match.group('test_type')
                    mode = match.group('mode2')
                    cal_type = match.group('cal_type')

                    if test_type == "TX_POWER":
                        test_type_zh = "发射功率"
                        test_type_en = "Transmit power"
                    else:
                        test_type_zh = "接收灵敏度"
                        test_type_en = "Receive sensitivity"

                    desc = {
                        "test_purpose_zh": f"验证{band}频段C{channel}通道在{mode}模式下的天线{cal_type}{test_type_zh}",
                        "test_items_zh": [
                            f"1. {band}频段C{channel}通道的{test_type_zh}值",
                            f"2. {mode}模式下的{test_type_zh}稳定性",
                            f"3. 天线分集（ANT）配置下的{test_type_zh}一致性"
                        ],
                        "test_purpose_en": f"Verify {test_type_en} of {band} band, channel {channel} under {mode} mode with ANT {cal_type}",
                        "test_items_en": [
                            f"1. {test_type_en} value at {band} band, channel {channel}",
                            f"2. {test_type_en} stability in {mode} mode",
                            f"3. {test_type_en} consistency under antenna diversity (ANT) configuration"
                        ]
                    }

                    if cal_type == "CW":
                        desc["test_purpose_zh"] += "（连续波模式）"
                        desc["test_purpose_en"] += " (Continuous Wave mode)"
                        desc["test_items_zh"].append(f"4. 连续波信号的{test_type_zh}谱密度合规性")
                        desc["test_items_en"].append(f"4. {test_type_en} spectral density compliance of CW signal")
                # 解析第二种新格式参数
                else:
                    band = match.group('band3')
                    antenna = match.group('antenna3')
                    quality = match.group('quality3')
                    attenuation = match.group('attenuation3')
                    channel = match.group('channel3')

                    desc = {
                        "test_purpose_zh": f"验证{band}频段天线C{antenna}、通道CH{channel}在{quality}质量、{attenuation}衰减下的发射校准",
                        "test_items_zh": [
                            f"1. {band}频段天线C{antenna}、通道CH{channel}的发射性能指标",
                            f"2. {quality}质量下的信号稳定性",
                            f"3. {attenuation}衰减时的信号强度",
                            f"4. 发射校准的准确性"
                        ],
                        "test_purpose_en": f"Verify the transmission calibration of {band} band, antenna C{antenna}, channel CH{channel} under {quality} quality and {attenuation} attenuation",
                        "test_items_en": [
                            f"1. Transmission performance indicators at {band} band, antenna C{antenna}, channel CH{channel}",
                            f"2. Signal stability under {quality} quality",
                            f"3. Signal strength at {attenuation} attenuation",
                            f"4. Calibration accuracy of transmission"
                        ]
                    }

                return desc

            def parse_mtk_meta_trackid_from_md_nvram(self, param: str) -> dict:
                """
                解析基础版MTK_META_READ_TRACKID_FROM_MD_NVRAM参数，仅返回指定中英文测试目的与测试项
                仅支持标准参数：MTK_META_READ_TRACKID_FROM_MD_NVRAM

                参数:
                    param: MTK TrackID读取参数（仅支持：MTK_META_READ_TRACKID_FROM_MD_NVRAM）

                返回:
                    dict: 包含test_purpose_zh、test_items_zh、test_purpose_en、test_items_en的结构化说明
                """
                # 正则严格匹配标准参数，不支持任何后缀或变体
                pattern = r"^MTK_META_READ_TRACKID_FROM_MD_NVRAM$"
                match = re.fullmatch(pattern, param.upper())

                if not match:
                    raise ValueError(
                        f"无效的MTK META TrackID参数格式: {param}，仅支持标准参数：MTK_META_READ_TRACKID_FROM_MD_NVRAM"
                    )

                # 仅构建目标字段的返回字典，聚焦测试目的与测试项
                desc = {
                    "test_purpose_zh": "MTK META模式下从MD NVRAM存储器读取TrackID的功能验证，确保设备身份标识读取准确性与硬件匹配性",
                    "test_items_zh": [
                        "1. META工具与MD芯片的通信链路完整性校验，确认可正常访问NVRAM分区",
                        "2. 读取TrackID的格式合规性检查（字符长度、编码规则符合MTK硬件规范）",
                        "3. NVRAM读取TrackID与扫描枪获取的物理TrackID一致性比对",
                        "4. 异常场景（NVRAM损坏、通信中断）下的错误码返回准确性验证",
                        "5. 不同MD芯片型号（MT67xx/MT68xx系列）的功能兼容性测试"
                    ],
                    "test_purpose_en": "Function verification of TrackID reading from MD NVRAM storage in MTK META mode, ensuring accuracy of device identity reading and hardware compatibility",
                    "test_items_en": [
                        "1. Integrity check of communication link between META tool and MD chip, confirming normal access to NVRAM partition",
                        "2. Format compliance check of read TrackID (character length and encoding rules meet MTK hardware specifications)",
                        "3. Consistency comparison between TrackID read from NVRAM and physical TrackID obtained by scanner",
                        "4. Accuracy verification of error code return under abnormal scenarios (NVRAM damage, communication interruption)",
                        "5. Function compatibility test across different MD chip models (MT67xx/MT68xx series)"
                    ]
                }

                return desc

            def parse_wifi_rx_test_purpose2items_cal(self,
                                                     param: str) -> dict:
                """
                解析MTK WLAN测试参数，生成中英文测试说明

                参数:
                    param: MTK WLAN测试参数（如：MTK_WLAN_2.4G_C0_CH07_RSSI_ANT_CW）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 正则解析参数结构
                pattern = (
                    r"MTK_WLAN_(?P<band1>\d+\.?\d*G)_C(?P<ant1>\d+)_CH(?P<channel1>\d+)_(?P<test_type1>RSSI|RX_SENSITIVITY)_ANT_(?P<cal_type1>\w+)"
                    r"|MTK_WLAN(?P<band2>\d+\.?\d*G)_RX_C(?P<ant2>\d+)_HQA_(?P<test_type2>RSSI)_MCH(?P<channel2>\d+)_(?P<cal_type2>\w+)"
                    r"|MTK_WLAN(?P<band3>\d+\.?\d*G)_RX_C(?P<ant3>\d+)_HQA_CH(?P<channel3>\d+)_(?P<cal_type3>\w+)"
                )
                match = re.match(pattern, param.upper())

                if not match:
                    raise ValueError(f"无效的MTK WLAN参数格式: {param}")

                # 判断是哪个模式匹配成功
                if match.group('band1'):
                    band = match.group('band1')
                    ant = match.group('ant1')
                    channel = match.group('channel1')
                    test_type = match.group('test_type1')
                    cal_type = match.group('cal_type1')
                elif match.group('band2'):
                    band = match.group('band2')
                    ant = match.group('ant2')
                    channel = match.group('channel2')
                    test_type = match.group('test_type2')
                    cal_type = match.group('cal_type2')
                else:
                    band = match.group('band3')
                    ant = match.group('ant3')
                    channel = match.group('channel3')
                    cal_type = match.group('cal_type3')
                    # 假设在这种格式下，测试类型总是 RSSI
                    test_type = "RSSI"

                if test_type == "RSSI":
                    test_type_zh = "接收信号强度指示"
                    test_type_en = "Received Signal Strength Indication"
                elif test_type == "RX_SENSITIVITY":
                    test_type_zh = "接收灵敏度"
                    test_type_en = "Receive sensitivity"

                desc = {
                    "test_purpose_zh": f"验证{band}频段C{ant}天线CH{channel}通道的{cal_type}{test_type_zh}",
                    "test_items_zh": [
                        f"1. {band}频段C{ant}天线CH{channel}通道的{test_type_zh}值",
                        f"2. {test_type_zh}稳定性",
                        f"3. 天线分集（ANT）配置下的{test_type_zh}一致性"
                    ],
                    "test_purpose_en": f"Verify {test_type_en} of {band} band, antenna C{ant}, channel CH{channel} with ANT {cal_type}",
                    "test_items_en": [
                        f"1. {test_type_en} value at {band} band, antenna C{ant}, channel CH{channel}",
                        f"2. {test_type_en} stability",
                        f"3. {test_type_en} consistency under antenna diversity (ANT) configuration"
                    ]
                }

                if cal_type == "CW":
                    desc["test_purpose_zh"] += "（连续波模式）"
                    desc["test_purpose_en"] += " (Continuous Wave mode)"
                    desc["test_items_zh"].append(f"4. 连续波信号的{test_type_zh}谱密度合规性")
                    desc["test_items_en"].append(f"4. {test_type_en} spectral density compliance of CW signal")

                return desc

            def parse_merge_and_modify_dicts_cal2(self,
                                                  parsed_test_process_cal_container: object,
                                                  key_name: str) -> object:
                """
                该函数用于合并并修改 parsed_test_process_cal_container 字典中的子字典。
                它会对特定的键进行重命名和序号更新操作，最终返回一个更新后的合并字典。
                针对校准内容，一般要进行多个轮次的，所以将校准项目名称更改为：校准项目名称_轮次_序号。

                参数:
                parsed_test_process_cal_container (dict): 一个包含多个子字典的字典，函数将处理除第一个子字典之外的其他子字典。

                返回:
                dict or None: 如果处理过程中没有发生异常，返回一个更新后的合并字典；
                              如果发生异常，返回 None，并打印相应的错误信息。
                """
                try:
                    # 初始化一个空字典，用于存储合并和修改后的结果
                    merged_dict = {}
                    # 获取除第一个字典表外的其他字典表
                    dict_list = list(parsed_test_process_cal_container.values())[1:]

                    round_num = 1
                    item_num = 1
                    for sub_dict in dict_list:
                        for key, value in sub_dict.items():
                            if key == 'Final measurement':
                                # 遇到 Final measurement 表示当前轮次结束，轮次加 1，序号重置为 1
                                new_key = f'{key}_{round_num}_{item_num}'
                                merged_dict[new_key] = value
                                round_num += 1
                                item_num = 1
                            elif key_name in key:
                                # 查找键中的数字序号
                                match = re.search(r'\d+', key)
                                if match:
                                    original_num = int(match.group())
                                    new_key = f'{key.replace(str(original_num), "")}_{round_num}_{item_num}'
                                    merged_dict[new_key] = value
                                else:
                                    new_key = f'{key}_{round_num}_{item_num}'
                                    merged_dict[new_key] = value
                                item_num += 1
                            else:
                                new_key = f'{key}_{round_num}_{item_num}'
                                merged_dict[new_key] = value
                                item_num += 1

                    return merged_dict
                except AttributeError as attr_error:
                    # 处理属性错误，例如键不是字符串类型，无法调用 replace 方法
                    print(f"Attribute error occurred: {attr_error}. Please check the key types.")
                except ValueError as value_error:
                    # 处理值错误，例如从字符串中提取的不是有效的数字
                    print(f"Value error occurred: {value_error}. Please check the key format.")
                except KeyError as key_error:
                    # 处理键错误，例如尝试访问字典中不存在的键
                    print(f"Key error occurred: {key_error}. Please check the dictionary structure.")
                except Exception as e:
                    # 处理其他未知异常
                    print(f"An unexpected error occurred: {e}")
                return None

            def parse_merge_and_modify_dicts_cal2_tx(self,
                                                     parsed_test_process_cal_container: object) -> object:
                """
                该函数用于合并并修改 parsed_test_process_cal_container 字典中的子字典。
                它会对特定的键进行重命名和序号更新操作，最终返回一个更新后的合并字典。
                针对校准内容，一般要进行多个轮次的，所以将校准项目名称更改为：校准项目名称_轮次_序号。

                参数:
                parsed_test_process_cal_container (dict): 一个包含多个子字典的字典，函数将处理除第一个子字典之外的其他子字典。

                返回:
                dict or None: 如果处理过程中没有发生异常，返回一个更新后的合并字典；
                              如果发生异常，返回 None，并打印相应的错误信息。
                """
                try:
                    # 初始化一个空字典，用于存储合并和修改后的结果
                    merged_dict = {}
                    # 获取除第一个字典表外的其他字典表
                    dict_list = list(parsed_test_process_cal_container.values())[1:]

                    round_num = 1
                    item_num = 1
                    for sub_dict in dict_list:
                        for key, value in sub_dict.items():
                            if key == 'Final measurement':
                                # 遇到 Final measurement 表示当前轮次结束，轮次加 1，序号重置为 1
                                new_key = f'{key}_{round_num}_{item_num}'
                                merged_dict[new_key] = value
                                round_num += 1
                                item_num = 1
                            elif 'Measure Process\tTX_POWER Reading ' in key:
                                # 查找键中的数字序号
                                match = re.search(r'\d+', key)
                                if match:
                                    original_num = int(match.group())
                                    new_key = f'{key.replace(str(original_num), "")}_{round_num}_{item_num}'
                                    merged_dict[new_key] = value
                                else:
                                    new_key = f'{key}_{round_num}_{item_num}'
                                    merged_dict[new_key] = value
                                item_num += 1
                            else:
                                new_key = f'{key}_{round_num}_{item_num}'
                                merged_dict[new_key] = value
                                item_num += 1

                    return merged_dict
                except AttributeError as attr_error:
                    # 处理属性错误，例如键不是字符串类型，无法调用 replace 方法
                    print(f"Attribute error occurred: {attr_error}. Please check the key types.")
                except ValueError as value_error:
                    # 处理值错误，例如从字符串中提取的不是有效的数字
                    print(f"Value error occurred: {value_error}. Please check the key format.")
                except KeyError as key_error:
                    # 处理键错误，例如尝试访问字典中不存在的键
                    print(f"Key error occurred: {key_error}. Please check the dictionary structure.")
                except Exception as e:
                    # 处理其他未知异常
                    print(f"An unexpected error occurred: {e}")
                return None

            def parse_merge_and_modify_dicts_cal2_rx(self,
                                                     parsed_test_process_cal_container: object) -> object:
                """
                该函数用于合并并修改 parsed_test_process_cal_container 字典中的子字典。
                它会对特定的键进行重命名和序号更新操作，最终返回一个更新后的合并字典。
                针对校准内容，一般要进行多个轮次的，所以将校准项目名称更改为：校准项目名称_轮次_序号。

                参数:
                parsed_test_process_cal_container (dict): 一个包含多个子字典的字典，函数将处理除第一个子字典之外的其他子字典。

                返回:
                dict or None: 如果处理过程中没有发生异常，返回一个更新后的合并字典；
                              如果发生异常，返回 None，并打印相应的错误信息。
                """
                try:
                    # 初始化一个空字典，用于存储合并和修改后的结果
                    merged_dict = {}
                    # 获取除第一个字典表外的其他字典表
                    dict_list = list(parsed_test_process_cal_container.values())[1:]

                    round_num = 1
                    item_num = 1
                    for sub_dict in dict_list:
                        for key, value in sub_dict.items():
                            if key == 'Final measurement':
                                # 遇到 Final measurement 表示当前轮次结束，轮次加 1，序号重置为 1
                                new_key = f'{key}_{round_num}_{item_num}'
                                merged_dict[new_key] = value
                                round_num += 1
                                item_num = 1
                            elif 'Measure Process\tSIGNAL_LEVEL Reading ' in key:
                                # 查找键中的数字序号
                                match = re.search(r'\d+', key)
                                if match:
                                    original_num = int(match.group())
                                    new_key = f'{key.replace(str(original_num), "")}_{round_num}_{item_num}'
                                    merged_dict[new_key] = value
                                else:
                                    new_key = f'{key}_{round_num}_{item_num}'
                                    merged_dict[new_key] = value
                                item_num += 1
                            else:
                                new_key = f'{key}_{round_num}_{item_num}'
                                merged_dict[new_key] = value
                                item_num += 1

                    return merged_dict
                except AttributeError as attr_error:
                    # 处理属性错误，例如键不是字符串类型，无法调用 replace 方法
                    print(f"Attribute error occurred: {attr_error}. Please check the key types.")
                except ValueError as value_error:
                    # 处理值错误，例如从字符串中提取的不是有效的数字
                    print(f"Value error occurred: {value_error}. Please check the key format.")
                except KeyError as key_error:
                    # 处理键错误，例如尝试访问字典中不存在的键
                    print(f"Key error occurred: {key_error}. Please check the dictionary structure.")
                except Exception as e:
                    # 处理其他未知异常
                    print(f"An unexpected error occurred: {e}")
                return None

            def parse_lte_route_info(self,
                                     route_container,
                                     target_str='MTK_MMRF_LTE_BC05_TX_20DB_V7_MCH20525'):
                result = {}
                # target_str = 'MTK_MMRF_LTE_BC05_TX_20DB_V7_MCH20525'
                for item in route_container:
                    if '=' in item:
                        key, value = item.split('=', 1)
                        key = key.replace(target_str, '').replace(' ', '').replace('\t', ' ').strip()
                        result[key] = value.strip()
                    elif ':' in item:
                        key, value = item.split(':', 1)
                        key = key.replace(target_str, '').replace(' ', '').replace('\t', ' ').strip()
                        result[key] = value.strip()
                return result

            def get_absolute_file_path(self,
                                       response_data_decoded):
                # """
                # 将响应中返回的相对文件路径转换为系统无关的绝对路径
                #
                # 参数:
                #     response_data_decoded (str): 响应中解码后的路径字符串，通常包含"FilePath"前缀和相对路径
                #
                # 返回:
                #     Path: 转换后的绝对路径对象
                #
                # 功能说明:
                #     1. 从输入字符串中提取实际的文件路径（移除"FilePath"前缀）
                #     2. 根据当前操作系统类型自动处理路径分隔符差异
                #     3. 将相对路径转换为基于项目根目录的绝对路径
                #     4. 规范化路径格式，确保在不同系统上的一致性
                #
                # 示例:
                #     输入: "FilePath../uploads\\test.txt" (Windows响应格式)
                #     输出: /home/user/project/uploads/test.txt (Linux绝对路径)
                #
                #     输入: "FilePath../uploads/test.txt" (Linux响应格式)
                #     输出: C:\Users\user\project\uploads\test.txt (Windows绝对路径)
                #
                # 注意事项:
                #     - 函数假设web_log_server2.py位于项目根目录下的一级目录中
                #     - 如果项目结构不同，需要调整project_root的计算方式
                #     - 路径中的"FilePath"前缀会被自动移除
                # """

                # 提取实际路径并去除空白字符
                file_path = response_data_decoded.strip().replace('FilePath', '')

                # 根据操作系统类型处理路径分隔符
                if os.name == 'nt':  # Windows系统
                    # 规范化路径（处理反斜杠和点号等）
                    normalized_path = os.path.normpath(file_path)
                else:  # Linux/Unix/Mac系统
                    # 将所有分隔符转换为正斜杠
                    normalized_path = file_path.replace(os.sep, '/')

                # 计算项目根目录（假设web_log_server2.py位于项目根目录的一级子目录中）
                project_root = Path(__file__).parent.parent

                # 构建并解析绝对路径
                absolute_file_path = (project_root / normalized_path).resolve()
                print(f"绝对路径: {absolute_file_path}")

                return absolute_file_path

            def find_project_root(self) -> Path:
                """向上查找，直到找到包含项目特征文件的目录"""
                current = Path.cwd().resolve()
                for _ in range(10):
                    if (current / "pyproject.toml").exists():
                        return current
                    if (current / ".git").exists():
                        return current
                    if (current / "docs").exists():
                        return current
                    current = current.parent
                raise RuntimeError("未找到项目根目录！")

            def parse_exception_errors(self, exception_error_container):
                """
                Parse the exception error list and convert it into a dictionary

                Args:
                    exception_error_container (list): List containing exception error messages

                Returns:
                    dict: Parsed exception error dictionary
                """
                exception_error_container_parse = {}

                for error_str in exception_error_container:
                    # Split the string to extract key and value
                    parts = error_str.split('\t', 1)

                    # If there is no tab, only the key exists
                    if len(parts) == 1:
                        key = parts[0]
                        value = None
                    else:
                        key, value = parts

                    # If the key is 'Exception error' and the value exists, update the dictionary
                    if key == 'Exception error' and value:
                        # Process additional information that may be contained in the value
                        if value.startswith('Details:'):
                            value = value[8:].strip()
                        elif value.startswith('Error code:'):
                            continue  # Skip error code information

                        # Update the dictionary, keeping only the last non-empty value
                        if value:
                            exception_error_container_parse[key] = value

                return exception_error_container_parse

            def parse_exception_errors_for_basic_band(self, exception_error_container):
                """
                解析基础频段的异常错误列表并转换为字典，将每个Details组的内容作为列表存入字典

                参数:
                    exception_error_container (list): 包含异常错误信息的列表

                返回:
                    dict: 解析后的异常错误字典，键为错误类型，值为对应Details组的错误信息列表
                """
                exception_parse_result = {}
                current_details = []  # 用于收集当前Details下的错误信息
                details_index = 0  # 用于区分不同的Details组

                for error_str in exception_error_container:
                    # 跳过标题行
                    if error_str.startswith('#'):
                        continue

                    # 分割错误字符串为键和值
                    parts = error_str.split('\t', 1)
                    key = parts[0] if len(parts) > 0 else ''
                    value = parts[1].strip() if len(parts) > 1 else ''

                    # 只处理Exception error类型
                    if key == 'Exception error':
                        # 遇到新的Details时，处理上一组（如果有）并重置当前收集列表
                        if value.startswith('Details:'):
                            # 如果存在上一组未保存的详情，先保存
                            if current_details:
                                details_key = f"{key}_details_{details_index}"
                                exception_parse_result[details_key] = current_details.copy()
                                details_index += 1
                            current_details = []
                        # 跳过错误代码信息
                        elif value.startswith('Error code:'):
                            continue
                        # 空值情况（仅Exception error标签）
                        elif not value:
                            # 如果有收集的详情，保存并重置索引
                            if current_details:
                                details_key = f"{key}_details_{details_index}"
                                exception_parse_result[details_key] = current_details.copy()
                                current_details = []
                                details_index += 1
                        # 收集Details下的具体错误信息
                        else:
                            current_details.append(value)

                # 处理最后一组未保存的详情
                if current_details:
                    details_key = f"{key}_details_{details_index}"
                    exception_parse_result[details_key] = current_details

                return exception_parse_result

            def translate_exception_message(self, error_code, lang='zh'):
                """
                根据语言参数翻译异常错误信息

                参数:
                    error_code (str): 错误代码，如 'FAILED_LIMITS_CHECK'
                    lang (str): 目标语言，'zh' 为中文，'en' 为英文，默认为中文

                返回:
                    str: 翻译后的错误信息
                """
                # 中英文错误信息对照表
                error_message_mapping = {
                    'FAILED_LIMITS_CHECK': {
                        'zh': '超出限制检查失败',
                        'en': 'Failed limits check'
                    },
                    'INVALID_PARAMETER': {
                        'zh': '无效参数',
                        'en': 'Invalid parameter'
                    },
                    'CONNECTION_ERROR': {
                        'zh': '连接错误',
                        'en': 'Connection error'
                    },
                    'AUTHENTICATION_FAILED': {
                        'zh': '认证失败',
                        'en': 'Authentication failed'
                    },
                    'TIMEOUT_ERROR': {
                        'zh': '超时错误',
                        'en': 'Timeout error'
                    }
                    # 可以继续添加更多错误代码和对应的翻译
                }

                # 获取错误代码对应的翻译
                if error_code in error_message_mapping and lang in error_message_mapping[error_code]:
                    return error_message_mapping[error_code][lang]
                else:
                    # 如果找不到对应的翻译，返回原始错误代码
                    return error_code

            # 修改函数以直接处理字典输入
            def translate_exception_dict(self, exception_dict, lang='zh'):
                """
                翻译异常错误字典

                参数:
                    exception_dict (dict): 包含异常错误信息的字典
                    lang (str): 目标语言，默认为中文'zh'

                返回:
                    dict: 翻译后的异常错误字典
                """
                # 检查输入是否为字典
                if not isinstance(exception_dict, dict):
                    print(f"错误: 输入不是字典类型 - {type(exception_dict)}")
                    return exception_dict

                # 创建翻译后的字典副本
                translated_dict = exception_dict.copy()

                # 检查是否包含 'Exception error' 键
                if 'Exception error' in translated_dict:
                    error_code = translated_dict['Exception error']
                    # 获取翻译后的错误信息
                    translated_value = self.translate_exception_message(error_code, lang)
                    # 更新字典中的值
                    translated_dict['Exception error'] = translated_value

                return translated_dict

            def parse_mic_test_purpose2items(self, param: str) -> dict:
                """
                解析MIC测试参数，生成中英文测试说明

                参数:
                    param: MIC测试参数（如：AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 定义MIC测试的正则表达式模式
                MIC_TEST_PATTERNS = [
                    r'AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_CONTIGUOUS_SPKR(?P<spkr_id>\d+)_(?P<freq_range>\d+-\d+)(?:_ASYNC_(?P<async_mode>START|WAIT))?',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_DFT_(?P<freq_khz>\d+)KHZ_(?P<dft_id>\d+)_(?P<dft_param>\d+)_L2SPK(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$'
                ]

                # 尝试匹配每个模式
                match = None
                pattern_type = 0  # 记录匹配的模式类型

                for i, pattern in enumerate(MIC_TEST_PATTERNS):
                    match = re.match(pattern, param.upper())
                    if match:
                        pattern_type = i + 1
                        break

                if not match:
                    raise ValueError(f"无效的MIC测试参数格式: {param}")

                # 解析通用参数
                mic_id = match.group('mic_id')
                spkr_id = match.group('spkr_id')

                # 根据匹配的模式类型解析特定参数
                if pattern_type == 1:  # CONTIGUOUS模式
                    freq_range = match.group('freq_range')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}与扬声器SPKR{spkr_id}在{freq_range}Hz频率范围内的连续采样性能",
                        "test_items_zh": [
                            f"1. MIC{mic_id}在{freq_range}Hz范围内的灵敏度响应",
                            f"2. 与扬声器SPKR{spkr_id}的同步性和连续性",
                            f"3. 采样数据的完整性和噪声水平"
                        ],
                        "test_purpose_en": f"Verify continuous sampling performance of MIC{mic_id} with speaker SPKR{spkr_id} in {freq_range}Hz frequency range",
                        "test_items_en": [
                            f"1. Sensitivity response of MIC{mic_id} in {freq_range}Hz range",
                            f"2. Synchronization and continuity with speaker SPKR{spkr_id}",
                            f"3. Integrity and noise level of sampled data"
                        ]
                    }

                    if async_mode == "START":
                        desc["test_purpose_zh"] += "（异步启动模式）"
                        desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                        desc["test_items_zh"].append("4. 异步启动的时间精度")
                        desc["test_items_en"].append("4. Time accuracy of asynchronous start")

                    elif async_mode == "WAIT":
                        desc["test_purpose_zh"] += "（异步等待模式）"
                        desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                        desc["test_items_zh"].append("4. 异步等待的响应时间")
                        desc["test_items_en"].append("4. Response time of asynchronous wait")

                elif pattern_type == 2:  # FFT模式
                    fft_id = match.group('fft_id')
                    freq_low = match.group('freq_low')
                    freq_high = match.group('freq_high')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}在{freq_low}-{freq_high}kHz频率范围内的FFT频谱分析性能（ID:{fft_id}）",
                        "test_items_zh": [
                            f"1. MIC{mic_id}在{freq_low}-{freq_high}kHz范围内的频率响应",
                            f"2. FFT算法（ID:{fft_id}）的精度和分辨率",
                            f"3. 与扬声器SPKR{spkr_id}的声学耦合性能"
                        ],
                        "test_purpose_en": f"Verify FFT spectral analysis performance of MIC{mic_id} in {freq_low}-{freq_high}kHz frequency range (ID:{fft_id})",
                        "test_items_en": [
                            f"1. Frequency response of MIC{mic_id} in {freq_low}-{freq_high}kHz range",
                            f"2. Accuracy and resolution of FFT algorithm (ID:{fft_id})",
                            f"3. Acoustic coupling performance with speaker SPKR{spkr_id}"
                        ]
                    }

                    if async_mode:
                        desc["test_purpose_zh"] += f"（{async_mode}模式）"
                        desc["test_purpose_en"] += f" ({async_mode} Mode)"

                elif pattern_type == 3:  # DFT模式
                    freq_khz = match.group('freq_khz')
                    dft_id = match.group('dft_id')
                    dft_param = match.group('dft_param')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}在{dft_id}DFT算法下对{freq_khz}kHz信号的处理性能（参数:{dft_param}）",
                        "test_items_zh": [
                            f"1. MIC{mic_id}对{dft_id}kHz信号的灵敏度",
                            f"2. DFT算法（ID:{dft_id}）的计算精度",
                            f"3. 与扬声器SPKR{spkr_id}的声学匹配度"
                        ],
                        "test_purpose_en": f"Verify processing performance of MIC{mic_id} for {freq_khz}kHz signal under DFT algorithm {dft_id} (Parameter:{dft_param})",
                        "test_items_en": [
                            f"1. Sensitivity of MIC{mic_id} to {freq_khz}kHz signal",
                            f"2. Calculation accuracy of DFT algorithm (ID:{dft_id})",
                            f"3. Acoustic matching with speaker SPKR{spkr_id}"
                        ]
                    }

                    if async_mode:
                        desc["test_purpose_zh"] += f"（{async_mode}模式）"
                        desc["test_purpose_en"] += f" ({async_mode} Mode)"

                return desc

            def parse_mic_test_purpose2items2(self, param: str) -> dict:
                """
                解析MIC测试参数，生成中英文测试说明

                参数:
                    param: MIC测试参数（如：AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 定义MIC测试的正则表达式模式
                MIC_TEST_PATTERNS = [
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_CONTIGUOUS_SPKR(?P<spkr_id>\d+)_(?P<freq_range>\d+-\d+)(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_DFT_(?P<freq_khz>\d+)KHZ_(?P<dft_id>\d+)_(?P<dft_param>\d+)_L2SPK(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<low_freq>\d+)HZ_TO_(?P<high_freq>\d+)HZ_MIC(?P<mic_num>\d+)(?:_(?P<product>\w+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$'
                    # r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<low_freq>\d+)Hz_TO_(?P<high_freq>\d+)Hz_MIC(?P<mic_num>\d+)_(?P<product>\w+)(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    # r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<low_freq>\d+)Hz_TO_(?P<high_freq>\d+)Hz_MIC(?P<mic_num>\d+)(?:_(?P<product>\w+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    # r'^AUDIO_L2AR_EAR_\d+_\d+Hz_TO_\d+Hz_MIC1(?:_KANSA(?:_ASYNC_(?:START|WAIT))?)?'
                ]

                # 打印调试信息
                print(f"测试字符串: {param}")
                print(f"转换为大写后: {param.upper()}")
                print("-" * 80)

                # 尝试匹配每个模式
                match = None
                pattern_type = 0  # 记录匹配的模式类型

                for i, pattern in enumerate(MIC_TEST_PATTERNS):
                    # 打印当前匹配的模式
                    print(f"模式{i + 1}: {pattern}")
                    # match = re.match(pattern, param)
                    # match = re.match(pattern,'AUDIO_L2AR_EAR_14705_140Hz_TO_7100Hz_MIC1_KANSA')
                    match = re.match(pattern, param.upper())
                    print(f"模式{i + 1}匹配结果: {match}")

                    # 如果匹配成功，显示捕获的组
                    if match:
                        print(f"模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    # 更详细的错误信息
                    raise ValueError(
                        f"无效的MIC测试参数格式: {param}\n"
                        f"参数结构应为: AUDIO_L2AR_EAR_<ear_id>_<low_freq>Hz_TO_<high_freq>Hz_MIC<mic_num>_<product>(可选)_ASYNC_<mode>(可选)"
                    )

                # 根据匹配的模式类型解析特定参数
                if pattern_type == 1:  # CONTIGUOUS模式
                    mic_id = match.group('mic_id')
                    spkr_id = match.group('spkr_id')
                    freq_range = match.group('freq_range')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}与扬声器SPKR{spkr_id}在{freq_range}Hz频率范围内的连续采样性能",
                        "test_items_zh": [
                            f"1. MIC{mic_id}在{freq_range}Hz范围内的灵敏度响应",
                            f"2. 与扬声器SPKR{spkr_id}的同步性和连续性",
                            f"3. 采样数据的完整性和噪声水平"
                        ],
                        "test_purpose_en": f"Verify continuous sampling performance of MIC{mic_id} with speaker SPKR{spkr_id} in {freq_range}Hz frequency range",
                        "test_items_en": [
                            f"1. Sensitivity response of MIC{mic_id} in {freq_range}Hz range",
                            f"2. Synchronization and continuity with speaker SPKR{spkr_id}",
                            f"3. Integrity and noise level of sampled data"
                        ]
                    }

                    if async_mode == "START":
                        desc["test_purpose_zh"] += "（异步启动模式）"
                        desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                        desc["test_items_zh"].append("4. 异步启动的时间精度")
                        desc["test_items_en"].append("4. Time accuracy of asynchronous start")

                    elif async_mode == "WAIT":
                        desc["test_purpose_zh"] += "（异步等待模式）"
                        desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                        desc["test_items_zh"].append("4. 异步等待的响应时间")
                        desc["test_items_en"].append("4. Response time of asynchronous wait")

                elif pattern_type == 2:  # FFT模式
                    mic_id = match.group('mic_id')
                    fft_id = match.group('fft_id')
                    freq_low = match.group('freq_low')
                    freq_high = match.group('freq_high')
                    spkr_id = match.group('spkr_id')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}在{freq_low}-{freq_high}kHz频率范围内的FFT频谱分析性能（ID:{fft_id}）",
                        "test_items_zh": [
                            f"1. MIC{mic_id}在{freq_low}-{freq_high}kHz范围内的频率响应",
                            f"2. FFT算法（ID:{fft_id}）的精度和分辨率",
                            f"3. 与扬声器SPKR{spkr_id}的声学耦合性能"
                        ],
                        "test_purpose_en": f"Verify FFT spectral analysis performance of MIC{mic_id} in {freq_low}-{freq_high}kHz frequency range (ID:{fft_id})",
                        "test_items_en": [
                            f"1. Frequency response of MIC{mic_id} in {freq_low}-{freq_high}kHz range",
                            f"2. Accuracy and resolution of FFT algorithm (ID:{fft_id})",
                            f"3. Acoustic coupling performance with speaker SPKR{spkr_id}"
                        ]
                    }

                    if async_mode:
                        desc["test_purpose_zh"] += f"（{async_mode}模式）"
                        desc["test_purpose_en"] += f" ({async_mode} Mode)"

                elif pattern_type == 3:  # DFT模式
                    mic_id = match.group('mic_id')
                    freq_khz = match.group('freq_khz')
                    dft_id = match.group('dft_id')
                    dft_param = match.group('dft_param')
                    spkr_id = match.group('spkr_id')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}在{dft_id}DFT算法下对{freq_khz}kHz信号的处理性能（参数:{dft_param}）",
                        "test_items_zh": [
                            f"1. MIC{mic_id}对{dft_id}kHz信号的灵敏度",
                            f"2. DFT算法（ID:{dft_id}）的计算精度",
                            f"3. 与扬声器SPKR{spkr_id}的声学匹配度"
                        ],
                        "test_purpose_en": f"Verify processing performance of MIC{mic_id} for {freq_khz}kHz signal under DFT algorithm {dft_id} (Parameter:{dft_param})",
                        "test_items_en": [
                            f"1. Sensitivity of MIC{mic_id} to {freq_khz}kHz signal",
                            f"2. Calculation accuracy of DFT algorithm (ID:{dft_id})",
                            f"3. Acoustic matching with speaker SPKR{spkr_id}"
                        ]
                    }

                    if async_mode:
                        desc["test_purpose_zh"] += f"（{async_mode}模式）"
                        desc["test_purpose_en"] += f" ({async_mode} Mode)"

                elif pattern_type == 4:  # EAR测试模式（修复部分）
                    low_freq = match.group('low_freq')
                    high_freq = match.group('high_freq')
                    mic_num = match.group('mic_num')  # 获取MIC编号（之前硬编码为1）
                    product = match.group('product')  # 这里修复了分组名称，从kansa改为product
                    async_mode = match.group('async_mode') or "同步"
                    # 基础描述（使用动态获取的mic_num，而非硬编码的1）
                    desc = {
                        "test_purpose_zh": f"验证EAR在{low_freq}Hz至{high_freq}Hz频率范围内与MIC{mic_num}的协同工作性能",
                        "test_items_zh": [
                            f"1. EAR在{low_freq}Hz至{high_freq}Hz范围内的灵敏度响应",
                            f"2. 与MIC{mic_num}的音频信号同步性能",
                            f"3. 频率响应的线性度和稳定性"
                        ],
                        "test_purpose_en": f"Verify cooperative performance of EAR with MIC{mic_num} in {low_freq}Hz to {high_freq}Hz frequency range",
                        "test_items_en": [
                            f"1. Sensitivity response of EAR in {low_freq}Hz to {high_freq}Hz range",
                            f"2. Audio signal synchronization performance with MIC{mic_num}",
                            f"3. Linearity and stability of frequency response"
                        ]
                    }

                    # 添加产品名称相关描述（不再局限于KANSA）
                    if product:
                        desc["test_purpose_zh"] += f"（{product}产品）"
                        desc["test_purpose_en"] += f" ({product} product)"
                        desc["test_items_zh"].append(f"4. 与{product}产品的兼容性验证")
                        desc["test_items_en"].append(f"4. Compatibility verification with {product} product")

                    # 添加异步模式描述（保持不变）
                    if async_mode == "START":
                        desc["test_purpose_zh"] += "（异步启动模式）"
                        desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                        desc["test_items_zh"].append("5. 异步启动的时序精度验证")
                        desc["test_items_en"].append("5. Timing accuracy verification of asynchronous start")

                    elif async_mode == "WAIT":
                        desc["test_purpose_zh"] += "（异步等待模式）"
                        desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                        desc["test_items_zh"].append("5. 异步等待的响应延迟测试")
                        desc["test_items_en"].append("5. Response delay test of asynchronous wait")

                return desc

            def parse_mic_test_purpose2items3(self, param: str) -> dict:
                """
                解析MIC测试参数，生成中英文测试说明

                参数:
                    param: MIC测试参数（如：AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200）

                返回:
                    dict: 包含中英文测试目的和测试项的结构化说明
                """
                # 定义MIC测试的正则表达式模式
                MIC_TEST_PATTERNS = [
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_CONTIGUOUS_SPKR(?P<spkr_id>\d+)_(?P<freq_range>\d+-\d+)(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_DFT_(?P<freq_khz>\d+)KHZ_(?P<dft_id>\d+)_(?P<dft_param>\d+)_L2SPK(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<low_freq>\d+)HZ_TO_(?P<high_freq>\d+)HZ_MIC(?P<mic_num>\d+)(?:_(?P<product>\w+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    # 新增的ALERT模式正则表达式，包含命名捕获组
                    r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Za-z]+)\d?_(?P<id>\d+)_(?P<start_freq>\d+K?HZ|\d+)_TO_(?P<end_freq>\d+HZ)_MIC(?P<mic_id>[\w-]+)(?:_(?P<product>[\w-]+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$'
                ]

                # 打印调试信息
                print(f"测试字符串: {param}")
                print(f"转换为大写后: {param.upper()}")
                print("-" * 80)

                # 尝试匹配每个模式
                match = None
                pattern_type = 0  # 记录匹配的模式类型

                for i, pattern in enumerate(MIC_TEST_PATTERNS):
                    # 打印当前匹配的模式
                    print(f"模式{i + 1}: {pattern}")
                    match = re.match(pattern, param.upper())
                    print(f"模式{i + 1}匹配结果: {match}")

                    # 如果匹配成功，显示捕获的组
                    if match:
                        print(f"模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    # 更详细的错误信息
                    raise ValueError(
                        f"无效的MIC测试参数格式: {param}\n"
                        f"参数结构应为以下之一:\n"
                        f"1. AUDIO_SAMPLE_MIC_<mic_id>_CONTIGUOUS_SPKR<spkr_id>_<freq_range>(_ASYNC_(START|WAIT))?\n"
                        f"2. AUDIO_SAMPLE_MIC_<mic_id>_FFT_<fft_id>_<freq_low>K-<freq_high>K_SPKR<spkr_id>_MILOS(_ASYNC_(START|WAIT))?\n"
                        f"3. AUDIO_SAMPLE_MIC_<mic_id>_DFT_<freq_khz>KHZ_<dft_id>_<dft_param>_L2SPK<spkr_id>_MILOS(_ASYNC_(START|WAIT))?\n"
                        f"4. AUDIO_L2AR_EAR_<ear_id>_<low_freq>HZ_TO_<high_freq>HZ_MIC<mic_num>(_<product>)?(_ASYNC_(START|WAIT))?\n"
                        f"5. AUDIO_L2AR_ALERT_<direction>_<id>_<start_freq>_TO_<end_freq>_MIC<mic_id>(_<product>)?(_ASYNC_(START|WAIT))?"
                    )

                # 根据匹配的模式类型解析特定参数
                if pattern_type == 1:  # CONTIGUOUS模式
                    mic_id = match.group('mic_id')
                    spkr_id = match.group('spkr_id')
                    freq_range = match.group('freq_range')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}与扬声器SPKR{spkr_id}在{freq_range}Hz频率范围内的连续采样性能",
                        "test_items_zh": [
                            f"1. MIC{mic_id}在{freq_range}Hz范围内的灵敏度响应",
                            f"2. 与扬声器SPKR{spkr_id}的同步性和连续性",
                            f"3. 采样数据的完整性和噪声水平"
                        ],
                        "test_purpose_en": f"Verify continuous sampling performance of MIC{mic_id} with speaker SPKR{spkr_id} in {freq_range}Hz frequency range",
                        "test_items_en": [
                            f"1. Sensitivity response of MIC{mic_id} in {freq_range}Hz range",
                            f"2. Synchronization and continuity with speaker SPKR{spkr_id}",
                            f"3. Integrity and noise level of sampled data"
                        ]
                    }

                    if async_mode == "START":
                        desc["test_purpose_zh"] += "（异步启动模式）"
                        desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                        desc["test_items_zh"].append("4. 异步启动的时间精度")
                        desc["test_items_en"].append("4. Time accuracy of asynchronous start")

                    elif async_mode == "WAIT":
                        desc["test_purpose_zh"] += "（异步等待模式）"
                        desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                        desc["test_items_zh"].append("4. 异步等待的响应时间")
                        desc["test_items_en"].append("4. Response time of asynchronous wait")

                elif pattern_type == 2:  # FFT模式
                    mic_id = match.group('mic_id')
                    fft_id = match.group('fft_id')
                    freq_low = match.group('freq_low')
                    freq_high = match.group('freq_high')
                    spkr_id = match.group('spkr_id')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}在{freq_low}-{freq_high}kHz频率范围内的FFT频谱分析性能（ID:{fft_id}）",
                        "test_items_zh": [
                            f"1. MIC{mic_id}在{freq_low}-{freq_high}kHz范围内的频率响应",
                            f"2. FFT算法（ID:{fft_id}）的精度和分辨率",
                            f"3. 与扬声器SPKR{spkr_id}的声学耦合性能"
                        ],
                        "test_purpose_en": f"Verify FFT spectral analysis performance of MIC{mic_id} in {freq_low}-{freq_high}kHz frequency range (ID:{fft_id})",
                        "test_items_en": [
                            f"1. Frequency response of MIC{mic_id} in {freq_low}-{freq_high}kHz range",
                            f"2. Accuracy and resolution of FFT algorithm (ID:{fft_id})",
                            f"3. Acoustic coupling performance with speaker SPKR{spkr_id}"
                        ]
                    }

                    if async_mode:
                        desc["test_purpose_zh"] += f"（{async_mode}模式）"
                        desc["test_purpose_en"] += f" ({async_mode} Mode)"

                elif pattern_type == 3:  # DFT模式
                    mic_id = match.group('mic_id')
                    freq_khz = match.group('freq_khz')
                    dft_id = match.group('dft_id')
                    dft_param = match.group('dft_param')
                    spkr_id = match.group('spkr_id')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证MIC{mic_id}在{dft_id}DFT算法下对{freq_khz}kHz信号的处理性能（参数:{dft_param}）",
                        "test_items_zh": [
                            f"1. MIC{mic_id}对{dft_id}kHz信号的灵敏度",
                            f"2. DFT算法（ID:{dft_id}）的计算精度",
                            f"3. 与扬声器SPKR{spkr_id}的声学匹配度"
                        ],
                        "test_purpose_en": f"Verify processing performance of MIC{mic_id} for {freq_khz}kHz signal under DFT algorithm {dft_id} (Parameter:{dft_param})",
                        "test_items_en": [
                            f"1. Sensitivity of MIC{mic_id} to {freq_khz}kHz signal",
                            f"2. Calculation accuracy of DFT algorithm (ID:{dft_id})",
                            f"3. Acoustic matching with speaker SPKR{spkr_id}"
                        ]
                    }

                    if async_mode:
                        desc["test_purpose_zh"] += f"（{async_mode}模式）"
                        desc["test_purpose_en"] += f" ({async_mode} Mode)"

                elif pattern_type == 4:  # EAR测试模式
                    low_freq = match.group('low_freq')
                    high_freq = match.group('high_freq')
                    mic_num = match.group('mic_num')
                    product = match.group('product')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证EAR在{low_freq}Hz至{high_freq}Hz频率范围内与MIC{mic_num}的协同工作性能",
                        "test_items_zh": [
                            f"1. EAR在{low_freq}Hz至{high_freq}Hz范围内的灵敏度响应",
                            f"2. 与MIC{mic_num}的音频信号同步性能",
                            f"3. 频率响应的线性度和稳定性"
                        ],
                        "test_purpose_en": f"Verify cooperative performance of EAR with MIC{mic_num} in {low_freq}Hz to {high_freq}Hz frequency range",
                        "test_items_en": [
                            f"1. Sensitivity response of EAR in {low_freq}Hz to {high_freq}Hz range",
                            f"2. Audio signal synchronization performance with MIC{mic_num}",
                            f"3. Linearity and stability of frequency response"
                        ]
                    }

                    if product:
                        desc["test_purpose_zh"] += f"（{product}产品）"
                        desc["test_purpose_en"] += f" ({product} product)"
                        desc["test_items_zh"].append(f"4. 与{product}产品的兼容性验证")
                        desc["test_items_en"].append(f"4. Compatibility verification with {product} product")

                    if async_mode == "START":
                        desc["test_purpose_zh"] += "（异步启动模式）"
                        desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                        desc["test_items_zh"].append("5. 异步启动的时序精度验证")
                        desc["test_items_en"].append("5. Timing accuracy verification of asynchronous start")

                    elif async_mode == "WAIT":
                        desc["test_purpose_zh"] += "（异步等待模式）"
                        desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                        desc["test_items_zh"].append("5. 异步等待的响应延迟测试")
                        desc["test_items_en"].append("5. Response delay test of asynchronous wait")

                elif pattern_type == 5:  # 新增的ALERT模式解析
                    direction = match.group('direction')
                    alert_id = match.group('id')
                    start_freq = match.group('start_freq')
                    # 处理可能没有单位的起始频率
                    if not re.search(r'Hz$', start_freq, re.IGNORECASE):
                        start_freq += "Hz"
                    end_freq = match.group('end_freq')
                    mic_id = match.group('mic_id')
                    product = match.group('product')
                    async_mode = match.group('async_mode') or "同步"

                    desc = {
                        "test_purpose_zh": f"验证{direction}方向的ALERT功能在{start_freq}至{end_freq}频率范围内与MIC{mic_id}的协同性能（ID:{alert_id}）",
                        "test_items_zh": [
                            f"1. {direction}方向ALERT信号的检测灵敏度",
                            f"2. MIC{mic_id}在{start_freq}至{end_freq}范围内的响应特性",
                            f"3. 警报信号处理的准确性和及时性"
                        ],
                        "test_purpose_en": f"Verify {direction} direction ALERT function performance with MIC{mic_id} in {start_freq} to {end_freq} range (ID:{alert_id})",
                        "test_items_en": [
                            f"1. Detection sensitivity of {direction} direction ALERT signal",
                            f"2. Response characteristics of MIC{mic_id} in {start_freq} to {end_freq} range",
                            f"3. Accuracy and timeliness of alert signal processing"
                        ]
                    }

                    if product:
                        desc["test_purpose_zh"] += f"（{product}产品）"
                        desc["test_purpose_en"] += f" ({product} product)"
                        desc["test_items_zh"].append(f"4. 与{product}产品的兼容性测试")
                        desc["test_items_en"].append(f"4. Compatibility test with {product} product")

                    if async_mode == "START":
                        desc["test_purpose_zh"] += "（异步启动模式）"
                        desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                        desc["test_items_zh"].append("5. 异步启动的响应时间测试")
                        desc["test_items_en"].append("5. Response time test of asynchronous start")

                    elif async_mode == "WAIT":
                        desc["test_purpose_zh"] += "（异步等待模式）"
                        desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                        desc["test_items_zh"].append("5. 异步等待状态的稳定性测试")
                        desc["test_items_en"].append("5. Stability test of asynchronous wait state")

                return desc

            def parse_mic_test_purpose2items4(self, param: str, test_patterns: list) -> dict:
                """主函数：根据参数类型路由到相应的解析函数"""
                param_upper = param.upper()

                # 打印调试信息
                print(f"测试字符串: {param}")
                print(f"转换为大写后: {param_upper}")
                print("-" * 80)

                # 判断参数类型并路由
                if param_upper.startswith("AUDIO_SAMPLE_MIC") or param_upper.startswith("AUDIO_MIC"):
                    return self.parse_mic_test3(param, test_patterns)
                elif param_upper.startswith("AUDIO_L2AR_ALERT"):
                    return self.parse_speaker_test3(param, test_patterns)
                elif param_upper.startswith("AUDIO_L2AR_EAR"):
                    return self.parse_ear_test3(param, test_patterns)
                else:
                    raise ValueError(f"无效的音频测试参数格式: {param}")

            def parse_mic_test(self, param: str) -> dict:
                """解析MIC相关的测试参数（3个指定模式）"""
                # 明确属于MIC的3个测试模式
                MIC_TEST_PATTERNS = [
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_CONTIGUOUS_SPKR(?P<spkr_id>\d+)_(?P<freq_range>\d+-\d+)(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_DFT_(?P<freq_khz>\d+)KHZ_(?P<dft_id>\d+)_(?P<dft_param>\d+)_L2SPK(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$'
                ]

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(MIC_TEST_PATTERNS):
                    print(f"MIC模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"MIC模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"MIC模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的MIC测试参数格式: {param}\n"
                        f"参数结构应为以下之一:\n"
                        f"1. AUDIO_SAMPLE_MIC_<mic_id>_CONTIGUOUS_SPKR<spkr_id>_<freq_range>(_ASYNC_(START|WAIT))?\n"
                        f"2. AUDIO_SAMPLE_MIC_<mic_id>_FFT_<fft_id>_<freq_low>K-<freq_high>K_SPKR<spkr_id>_MILOS(_ASYNC_(START|WAIT))?\n"
                        f"3. AUDIO_SAMPLE_MIC_<mic_id>_DFT_<freq_khz>KHZ_<dft_id>_<dft_param>_L2SPK<spkr_id>_MILOS(_ASYNC_(START|WAIT))?"
                    )

                # 根据匹配的模式生成描述
                # CONTIGUOUS模式
                if pattern_type == 1:
                    return self._parse_mic_contiguous2(match)
                # FFT模式
                elif pattern_type == 2:
                    return self._parse_mic_fft2(match)
                # DFT模式
                elif pattern_type == 3:
                    return self._parse_mic_dft2(match)
                else:
                    return None

            def parse_mic_test2(self, param: str) -> dict:
                """解析MIC相关的测试参数（4个指定模式）"""
                # 明确属于MIC的4个测试模式，新增了AUDIO_MIC开头的模式
                MIC_TEST_PATTERNS = [
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_CONTIGUOUS_SPKR(?P<spkr_id>\d+)_(?P<freq_range>\d+-\d+)(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_(?P<suffix>[A-Za-z]+)$',
                    r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_DFT_(?P<freq_khz>\d+)KHZ_(?P<dft_id>\d+)_(?P<dft_param>\d+)_L2SPK(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_MIC(?P<mic_id>\d+)_SPKR(?P<spkr_id>\d+)_(?P<param1>\d+)-(?P<param2>\d+)K(?P<param3>\d+)HZ_VS_SEAL_(?P<suffix>.+)$'
                ]

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(MIC_TEST_PATTERNS):
                    print(f"MIC模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"MIC模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"MIC模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的MIC测试参数格式: {param}\n"
                        f"参数结构应为以下之一:\n"
                        f"1. AUDIO_SAMPLE_MIC_<mic_id>_CONTIGUOUS_SPKR<spkr_id>_<freq_range>(_ASYNC_(START|WAIT))?\n"
                        f"2. AUDIO_SAMPLE_MIC_<mic_id>_FFT_<fft_id>_<freq_low>K-<freq_high>K_SPKR<spkr_id>_MILOS(_ASYNC_(START|WAIT))?\n"
                        f"3. AUDIO_SAMPLE_MIC_<mic_id>_DFT_<freq_khz>KHZ_<dft_id>_<dft_param>_L2SPK<spkr_id>_MILOS(_ASYNC_(START|WAIT))?\n"
                        f"4. AUDIO_MIC<mic_id>_SPKR<spkr_id>_<param1>-<param2>K<param3>Hz_VS_SEAL_<suffix>"
                    )

                # 根据匹配的模式生成描述
                # CONTIGUOUS模式
                if pattern_type == 1:
                    return self._parse_mic_contiguous2(match)
                # FFT模式
                elif pattern_type == 2:
                    return self._parse_mic_fft2(match)
                # FFT模式
                elif pattern_type == 3:
                    return self._parse_mic_fft_suffix(match)
                # DFT模式
                elif pattern_type == 4:
                    return self._parse_mic_dft2(match)
                # 新增的AUDIO_MIC模式
                elif pattern_type == 5:
                    return self._parse_audio_mic(match)
                else:
                    return None

            def parse_mic_test3(self, param: str, test_patterns: list) -> dict:
                """解析MIC相关的测试参数（包括新增的EQ模式）"""
                # # 明确属于MIC的测试模式，新增了带EQ后缀的模式
                # MIC_TEST_PATTERNS = [
                #     r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_CONTIGUOUS_SPKR(?P<spkr_id>\d+)_(?P<freq_range>\d+-\d+)(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                #     r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                #     r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_FFT_(?P<fft_id>\d+)_(?P<freq_low>\d+)K-(?P<freq_high>\d+)K_SPKR(?P<spkr_id>\d+)_(?P<suffix>[A-Za-z]+)$',
                #     r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_DFT_(?P<freq_khz>\d+)KHZ_(?P<dft_id>\d+)_(?P<dft_param>\d+)_L2SPK(?P<spkr_id>\d+)_MILOS(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                #     r'^AUDIO_MIC(?P<mic_id>\d+)_SPKR(?P<spkr_id>\d+)_(?P<param1>\d+)-(?P<param2>\d+)K(?P<param3>\d+)HZ_VS_SEAL_(?P<suffix>.+)$',
                #     # 新增模式：匹配带有EQ后缀的CONTIGUOUS模式
                #     r'^AUDIO_SAMPLE_MIC_(?P<mic_id>\d+)_CONTIGUOUS_SPKR(?P<spkr_id>\d+)_(?P<freq_range>\d+-\d+)_EQ$'
                # ]
                MIC_TEST_PATTERNS = test_patterns

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(MIC_TEST_PATTERNS):
                    print(f"MIC模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"MIC模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"MIC模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的MIC测试参数格式: {param}\n"
                        f"参数结构应为以下之一:\n"
                        f"1. AUDIO_SAMPLE_MIC_<mic_id>_CONTIGUOUS_SPKR<spkr_id>_<freq_range>(_ASYNC_(START|WAIT))?\n"
                        f"2. AUDIO_SAMPLE_MIC_<mic_id>_FFT_<fft_id>_<freq_low>K-<freq_high>K_SPKR<spkr_id>_MILOS(_ASYNC_(START|WAIT))?\n"
                        f"3. AUDIO_SAMPLE_MIC_<mic_id>_DFT_<freq_khz>KHZ_<dft_id>_<dft_param>_L2SPK<spkr_id>_MILOS(_ASYNC_(START|WAIT))?\n"
                        f"4. AUDIO_MIC<mic_id>_SPKR<spkr_id>_<param1>-<param2>K<param3>Hz_VS_SEAL_<suffix>\n"
                        f"5. AUDIO_SAMPLE_MIC_<mic_id>_CONTIGUOUS_SPKR<spkr_id>_<freq_range>_EQ"  # 新增模式说明
                    )

                # 根据匹配的模式生成描述
                if pattern_type == 1:
                    return self._parse_mic_contiguous2(match)
                elif pattern_type == 2:
                    return self._parse_mic_fft2(match)
                elif pattern_type == 3:
                    return self._parse_mic_fft_suffix(match)
                elif pattern_type == 4:
                    return self._parse_mic_dft2(match)
                elif pattern_type == 5:
                    return self._parse_audio_mic(match)
                # 处理新增的EQ模式
                elif pattern_type == 6:
                    return self._parse_mic_contiguous3(match)
                elif pattern_type == 7:
                    return self._parse_mic_dft_block(match)
                else:
                    return None

            def parse_speaker_test(self, param: str) -> dict:
                """解析扬声器相关的测试参数（仅保留指定的ALERT模式）"""
                # 仅保留指定的ALERT模式
                SPEAKER_TEST_PATTERNS = [
                    r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Za-z]+)\d?_(?P<id>\d+)_(?P<start_freq>\d+K?HZ|\d+)_TO_(?P<end_freq>\d+HZ)_MIC(?P<mic_id>[\w-]+)(?:_(?P<product>[\w-]+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Z]+)$'
                ]

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(SPEAKER_TEST_PATTERNS):
                    print(f"扬声器模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"扬声器模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"扬声器模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的扬声器测试参数格式: {param}\n"
                        f"参数结构应为:\n"
                        f"AUDIO_L2AR_ALERT_<direction>_<id>_<start_freq>_TO_<end_freq>_MIC<mic_id>(_<product>)?(_ASYNC_(START|WAIT))?"
                    )

                # 解析ALERT模式
                direction = match.group('direction')
                alert_id = match.group('id')
                start_freq = match.group('start_freq')
                # 处理可能没有单位的起始频率
                if not re.search(r'Hz$', start_freq, re.IGNORECASE):
                    start_freq += "Hz"
                end_freq = match.group('end_freq')
                mic_id = match.group('mic_id')
                product = match.group('product')
                async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"验证{direction}方向的ALERT功能在{start_freq}至{end_freq}频率范围内与扬声器的协同性能（ID:{alert_id}，关联MIC{mic_id}）",
                    "test_items_zh": [
                        f"1. {direction}方向ALERT信号的检测灵敏度",
                        f"2. 扬声器在{start_freq}至{end_freq}范围内的响应特性",
                        f"3. 与MIC{mic_id}的协同工作性能",
                        f"4. 警报信号处理的准确性和及时性"
                    ],
                    "test_purpose_en": f"Verify {direction} direction ALERT function performance with speaker in {start_freq} to {end_freq} range (ID:{alert_id}, associated MIC{mic_id})",
                    "test_items_en": [
                        f"1. Detection sensitivity of {direction} direction ALERT signal",
                        f"2. Speaker response characteristics in {start_freq} to {end_freq} range",
                        f"3. Cooperative performance with MIC{mic_id}",
                        f"4. Accuracy and timeliness of alert signal processing"
                    ]
                }

                if product:
                    desc["test_purpose_zh"] += f"（{product}产品）"
                    desc["test_purpose_en"] += f" ({product} product)"
                    desc["test_items_zh"].append(f"5. 与{product}产品的兼容性测试")
                    desc["test_items_en"].append(f"5. Compatibility test with {product} product")

                if async_mode == "START":
                    desc["test_purpose_zh"] += "（异步启动模式）"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("6. 异步启动的响应时间测试")
                    desc["test_items_en"].append("6. Response time test of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "（异步等待模式）"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append("6. 异步等待状态的稳定性测试")
                    desc["test_items_en"].append("6. Stability test of asynchronous wait state")

                return desc

            def parse_speaker_test2(self, param: str) -> dict:
                """解析扬声器相关的测试参数（仅保留指定的ALERT模式）"""
                # 仅保留指定的ALERT模式
                SPEAKER_TEST_PATTERNS = [
                    r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Za-z]+)\d?_(?P<id>\d+)_(?P<start_freq>\d+K?HZ|\d+)_TO_(?P<end_freq>\d+HZ)_MIC(?P<mic_id>[\w-]+)(?:_(?P<product>[\w-]+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                    r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Z]+)$',
                    r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+[A-Z]+)_(?P<version>V\d+)_(?P<product>[A-Z]+)$'
                ]

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(SPEAKER_TEST_PATTERNS):
                    print(f"扬声器模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"扬声器模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"扬声器模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的扬声器测试参数格式: {param}\n"
                        f"参数结构应为:\n"
                        f"AUDIO_L2AR_ALERT_<direction>_<id>_<start_freq>_TO_<end_freq>_MIC<mic_id>(_<product>)?(_ASYNC_(START|WAIT))?"
                    )

                # 解析ALERT模式
                direction = match.group('direction')
                alert_id = match.group('id')
                start_freq = match.group('start_freq')
                # 处理可能没有单位的起始频率
                if not re.search(r'Hz$', start_freq, re.IGNORECASE):
                    start_freq += "Hz"
                end_freq = match.group('end_freq')
                mic_id = match.group('mic_id')
                product = match.group('product')

                # 兼容处理：检查分组是否存在，不存在则设为默认值
                async_mode = "同步"  # 默认值
                if 'async_mode' in match.groupdict():
                    async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"验证{direction}方向的ALERT功能在{start_freq}至{end_freq}频率范围内与扬声器的协同性能（ID:{alert_id}，关联MIC{mic_id}）",
                    "test_items_zh": [
                        f"1. {direction}方向ALERT信号的检测灵敏度",
                        f"2. 扬声器在{start_freq}至{end_freq}范围内的响应特性",
                        f"3. 与MIC{mic_id}的协同工作性能",
                        f"4. 警报信号处理的准确性和及时性"
                    ],
                    "test_purpose_en": f"Verify {direction} direction ALERT function performance with speaker in {start_freq} to {end_freq} range (ID:{alert_id}, associated MIC{mic_id})",
                    "test_items_en": [
                        f"1. Detection sensitivity of {direction} direction ALERT signal",
                        f"2. Speaker response characteristics in {start_freq} to {end_freq} range",
                        f"3. Cooperative performance with MIC{mic_id}",
                        f"4. Accuracy and timeliness of alert signal processing"
                    ]
                }

                if product:
                    desc["test_purpose_zh"] += f"（{product}产品）"
                    desc["test_purpose_en"] += f" ({product} product)"
                    desc["test_items_zh"].append(f"5. 与{product}产品的兼容性测试")
                    desc["test_items_en"].append(f"5. Compatibility test with {product} product")

                if async_mode == "START":
                    desc["test_purpose_zh"] += "（异步启动模式）"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("6. 异步启动的响应时间测试")
                    desc["test_items_en"].append("6. Response time test of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "（异步等待模式）"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append("6. 异步等待状态的稳定性测试")
                    desc["test_items_en"].append("6. Stability test of asynchronous wait state")

                return desc

            def parse_speaker_test3(self, param: str, test_patterns: list) -> dict:
                """解析扬声器相关的测试参数（包含EQ模式）"""
                # # 包含EQ模式的扬声器测试模式
                # SPEAKER_TEST_PATTERNS = [
                #     r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Za-z]+)\d?_(?P<id>\d+)_(?P<start_freq>\d+K?HZ|\d+)_TO_(?P<end_freq>\d+HZ)_MIC(?P<mic_id>[\w-]+)(?:_(?P<product>[\w-]+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                #     r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Z]+)$',
                #     r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+[A-Z]+)_(?P<version>V\d+)_(?P<product>[A-Z]+)$',
                #     # 新增支持EQ后缀的模式
                #     r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Z]+)_EQ$',
                #     # 修正支持EQ后缀的模式，允许mic_id包含数字和字母
                #     r'^AUDIO_L2AR_ALERT_(?P<direction>[A-Z]+)_(?P<id>\d+)_(?P<start_freq>\d+KHZ)_TO_(?P<end_freq>\d+KHZ)_MIC(?P<mic_id>[\dA-Za-z]+)_(?P<product>[A-Z]+)_EQ$'
                # ]
                SPEAKER_TEST_PATTERNS = test_patterns

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(SPEAKER_TEST_PATTERNS):
                    print(f"扬声器模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"扬声器模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"扬声器模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的扬声器测试参数格式: {param}\n"
                        f"参数结构应为以下之一:\n"
                        f"1. AUDIO_L2AR_ALERT_<direction>_<id>_<start_freq>_TO_<end_freq>_MIC<mic_id>(_<product>)?(_ASYNC_(START|WAIT))?\n"
                        f"2. AUDIO_L2AR_ALERT_<direction>_<id>_<start_freq>KHZ_TO_<end_freq>KHZ_MIC<mic_id>_<product>\n"
                        f"3. AUDIO_L2AR_ALERT_<direction>_<id>_<start_freq>KHZ_TO_<end_freq>KHZ_MIC<mic_id>_<version>_<product>\n"
                        f"4. AUDIO_L2AR_ALERT_<direction>_<id>_<start_freq>KHZ_TO_<end_freq>KHZ_MIC<mic_id>_<product>_EQ"
                        # 新增模式说明
                    )

                # 解析ALERT模式
                direction = match.group('direction')
                alert_id = match.group('id')
                start_freq = match.group('start_freq')
                # 处理可能没有单位的起始频率
                if not re.search(r'Hz$', start_freq, re.IGNORECASE):
                    start_freq += "Hz"
                end_freq = match.group('end_freq')
                mic_id = match.group('mic_id')
                product = match.group('product')

                # 兼容处理：检查分组是否存在，不存在则设为默认值
                async_mode = "同步"  # 默认值
                if 'async_mode' in match.groupdict():
                    async_mode = match.group('async_mode') or "同步"

                # 判断是否为EQ模式
                is_eq_mode = (pattern_type == 4)

                desc = {
                    "test_purpose_zh": f"验证{direction}方向的ALERT功能在{start_freq}至{end_freq}频率范围内与扬声器的协同性能（ID:{alert_id}，关联MIC{mic_id}）" +
                                       ("，并启用均衡器(EQ)" if is_eq_mode else ""),
                    "test_items_zh": [
                        f"1. {direction}方向ALERT信号的检测灵敏度",
                        f"2. 扬声器在{start_freq}至{end_freq}范围内的响应特性",
                        f"3. 与MIC{mic_id}的协同工作性能",
                        f"4. 警报信号处理的准确性和及时性"
                    ],
                    "test_purpose_en": f"Verify {direction} direction ALERT function performance with speaker in {start_freq} to {end_freq} range (ID:{alert_id}, associated MIC{mic_id})" +
                                       (" with EQ (Equalizer) enabled" if is_eq_mode else ""),
                    "test_items_en": [
                        f"1. Detection sensitivity of {direction} direction ALERT signal",
                        f"2. Speaker response characteristics in {start_freq} to {end_freq} range",
                        f"3. Cooperative performance with MIC{mic_id}",
                        f"4. Accuracy and timeliness of alert signal processing"
                    ]
                }

                # EQ模式添加专门测试项
                if is_eq_mode:
                    desc["test_items_zh"].insert(2, f"2.1 扬声器在EQ模式下的频率均衡性测试")
                    desc["test_items_en"].insert(2, f"2.1 Speaker frequency balance test in EQ mode")

                if product:
                    desc["test_purpose_zh"] += f"（{product}产品）"
                    desc["test_purpose_en"] += f" ({product} product)"
                    desc["test_items_zh"].append(f"5. 与{product}产品的兼容性测试")
                    desc["test_items_en"].append(f"5. Compatibility test with {product} product")

                if async_mode == "START":
                    desc["test_purpose_zh"] += "（异步启动模式）"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("6. 异步启动的响应时间测试")
                    desc["test_items_en"].append("6. Response time test of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "（异步等待模式）"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append("6. 异步等待状态的稳定性测试")
                    desc["test_items_en"].append("6. Stability test of asynchronous wait state")

                return desc

            def parse_ear_test(self, param: str) -> dict:
                """解析EAR相关的测试参数（指定的1个模式）"""
                # 明确属于EAR的测试模式
                EAR_TEST_PATTERNS = [
                    r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<low_freq>\d+)HZ_TO_(?P<high_freq>\d+)HZ_MIC(?P<mic_num>\d+)(?:_(?P<product>\w+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$'
                ]

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(EAR_TEST_PATTERNS):
                    print(f"EAR模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"EAR模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"EAR模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的EAR测试参数格式: {param}\n"
                        f"参数结构应为:\n"
                        f"AUDIO_L2AR_EAR_<ear_id>_<low_freq>HZ_TO_<high_freq>HZ_MIC<mic_num>(_<product>)?(_ASYNC_(START|WAIT))?"
                    )

                # 解析EAR测试参数
                ear_id = match.group('ear_id')
                low_freq = match.group('low_freq')
                high_freq = match.group('high_freq')
                mic_num = match.group('mic_num')
                product = match.group('product')
                async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"验证EAR{ear_id}在{low_freq}Hz至{high_freq}Hz频率范围内与MIC{mic_num}的协同工作性能",
                    "test_items_zh": [
                        f"1. EAR{ear_id}在{low_freq}Hz至{high_freq}Hz范围内的灵敏度响应",
                        f"2. 与MIC{mic_num}的音频信号同步性能",
                        f"3. 频率响应的线性度和稳定性"
                    ],
                    "test_purpose_en": f"Verify cooperative performance of EAR{ear_id} with MIC{mic_num} in {low_freq}Hz to {high_freq}Hz frequency range",
                    "test_items_en": [
                        f"1. Sensitivity response of EAR{ear_id} in {low_freq}Hz to {high_freq}Hz range",
                        f"2. Audio signal synchronization performance with MIC{mic_num}",
                        f"3. Linearity and stability of frequency response"
                    ]
                }

                if product:
                    desc["test_purpose_zh"] += f"（{product}产品）"
                    desc["test_purpose_en"] += f" ({product} product)"
                    desc["test_items_zh"].append(f"4. 与{product}产品的兼容性验证")
                    desc["test_items_en"].append(f"4. Compatibility verification with {product} product")

                if async_mode == "START":
                    desc["test_purpose_zh"] += "（异步启动模式）"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("5. 异步启动的时序精度验证")
                    desc["test_items_en"].append("5. Timing accuracy verification of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "（异步等待模式）"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append("5. 异步等待的响应延迟测试")
                    desc["test_items_en"].append("5. Response delay test of asynchronous wait")

                return desc

            def parse_ear_test2(self, param: str) -> dict:
                """解析EAR相关的测试参数（指定的1个模式）"""
                # 明确属于EAR的测试模式
                EAR_TEST_PATTERNS = [
                    r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<low_freq>\d+)HZ_TO_(?P<high_freq>\d+)HZ_MIC(?P<mic_num>\d+)(?:_(?P<product>\w+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$'
                ]

                param_upper = param.upper()
                match = None
                pattern_type = 0

                for i, pattern in enumerate(EAR_TEST_PATTERNS):
                    print(f"EAR模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"EAR模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"EAR模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的EAR测试参数格式: {param}\n"
                        f"参数结构应为:\n"
                        f"AUDIO_L2AR_EAR_<ear_id>_<low_freq>HZ_TO_<high_freq>HZ_MIC<mic_num>(_<product>)?(_ASYNC_(START|WAIT))?"
                    )

                # 解析EAR测试参数
                ear_id = match.group('ear_id')
                low_freq = match.group('low_freq')
                high_freq = match.group('high_freq')
                mic_num = match.group('mic_num')
                product = match.group('product')
                async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"测试编号为{ear_id}的EAR设备，在{low_freq}赫兹到{high_freq}赫兹的声音频率范围内，和编号为{mic_num}的麦克风一起工作时的表现如何",
                    "test_items_zh": [
                        f"1. 检查编号{ear_id}的EAR设备，在{low_freq}赫兹到{high_freq}赫兹这个频率范围内，对声音的敏感程度和反应情况",
                        f"2. 观察EAR{ear_id}和麦克风{mic_num}之间，声音信号的传递是否能保持同步，不会出现时间差",
                        f"3. 测试在整个{low_freq}赫兹到{high_freq}赫兹的频率范围内，EAR{ear_id}的反应是否稳定，性能是否一致"
                    ],
                    "test_purpose_en": f"Verify cooperative performance of EAR{ear_id} with MIC{mic_num} in {low_freq}Hz to {high_freq}Hz frequency range",
                    "test_items_en": [
                        f"1. Sensitivity response of EAR{ear_id} in {low_freq}Hz to {high_freq}Hz range",
                        f"2. Audio signal synchronization performance with MIC{mic_num}",
                        f"3. Linearity and stability of frequency response"
                    ]
                }

                if product:
                    desc["test_purpose_zh"] += f"，特别是针对{product}这款产品的适配情况"
                    desc["test_purpose_en"] += f" ({product} product)"
                    desc["test_items_zh"].append(f"4. 检查EAR{ear_id}和{product}产品连接使用时，是否能正常配合工作")
                    desc["test_items_en"].append(f"4. Compatibility verification with {product} product")

                if async_mode == "START":
                    desc["test_purpose_zh"] += "，采用异步启动的方式进行测试"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("5. 测试在异步启动模式下，EAR设备开始工作的时间是否准确，是否符合预期")
                    desc["test_items_en"].append(f"5. Timing accuracy verification of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "，采用异步等待的方式进行测试"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append(
                        "5. 测试在异步等待模式下，EAR设备收到信号后，反应速度有多快，会不会延迟太久")
                    desc["test_items_en"].append(f"5. Response delay test of asynchronous wait")

                return desc

            def parse_ear_test3(self, param: str, test_patterns: list) -> dict:
                """解析EAR相关的测试参数（支持5种指定模式，正则表达式为全大写）"""
                # # 明确属于EAR的测试模式，均使用命名捕获组，且为全大写格式
                # EAR_TEST_PATTERNS = [
                #     # 0. 基础频率模式（无单位变化）
                #     # 匹配格式: AUDIO_L2AR_EAR_<ear_id>_<low_freq>HZ_TO_<high_freq>HZ_MIC<mic_num>(_<product>)?(_ASYNC_(START|WAIT))?
                #     # 示例: AUDIO_L2AR_EAR_123_4500HZ_TO_8000HZ_MIC2_TESTPROD_ASYNC_START
                #     # 捕获组说明:
                #     #   ear_id: EAR设备编号（数字）
                #     #   low_freq: 低频频率值（仅数字，无单位，单位固定为HZ）
                #     #   high_freq: 高频频率值（仅数字，无单位，单位固定为HZ）
                #     #   mic_num: 麦克风编号（数字）
                #     #   product: 产品名称（可选，字母数字组合）
                #     #   async_mode: 异步模式（可选，固定值START或WAIT）
                #     r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<low_freq>\d+)HZ_TO_(?P<high_freq>\d+)HZ_MIC(?P<mic_num>\d+)(?:_(?P<product>\w+))?(?:_ASYNC_(?P<async_mode>START|WAIT))?$',
                #
                #     # 1. 带异步模式和产品名的完整模式（全大写）
                #     # 匹配格式: AUDIO_L2AR_EAR_<ear_id>_<start_freq>_TO_<end_freq>_MIC<mic_id>_<product>_ASYNC_<async_mode>
                #     # 示例: AUDIO_L2AR_EAR_14705_140HZ_TO_7100HZ_MIC1_KANSA_ASYNC_START
                #     # 捕获组说明:
                #     #   ear_id: EAR设备编号（数字）
                #     #   start_freq: 起始频率（支持HZ和KHZ单位，如140HZ、8KHZ）
                #     #   end_freq: 结束频率（支持HZ和KHZ单位，如7100HZ、140HZ）
                #     #   mic_id: 麦克风编号（数字）
                #     #   product: 产品名称（字母组合）
                #     #   async_mode: 异步模式（固定值START或WAIT）
                #     r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<start_freq>\d+K?HZ)_TO_(?P<end_freq>\d+K?HZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Za-z]+)_ASYNC_(?P<async_mode>START|WAIT)$',
                #
                #     # 2. 带产品名但无异步模式（全大写）
                #     # 匹配格式: AUDIO_L2AR_EAR_<ear_id>_<start_freq>_TO_<end_freq>_MIC<mic_id>_<product>
                #     # 示例: AUDIO_L2AR_EAR_14705_140HZ_TO_7100HZ_MIC1_KANSA
                #     # 捕获组说明:
                #     #   ear_id: EAR设备编号（数字）
                #     #   start_freq: 起始频率（支持HZ和KHZ单位）
                #     #   end_freq: 结束频率（支持HZ和KHZ单位）
                #     #   mic_id: 麦克风编号（数字）
                #     #   product: 产品名称（字母组合）
                #     r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<start_freq>\d+K?HZ)_TO_(?P<end_freq>\d+K?HZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Za-z]+)$',
                #
                #     # 3. 带EQ模式和产品名（全大写）
                #     # 匹配格式: AUDIO_L2AR_EAR_<ear_id>_<start_freq>_TO_<end_freq>_MIC<mic_id>_<product>_EQ
                #     # 示例: AUDIO_L2AR_EAR_25000_8KHZ_TO_140HZ_MIC1_PORTO_EQ
                #     # 捕获组说明:
                #     #   ear_id: EAR设备编号（数字）
                #     #   start_freq: 起始频率（支持HZ和KHZ单位）
                #     #   end_freq: 结束频率（支持HZ和KHZ单位）
                #     #   mic_id: 麦克风编号（数字）
                #     #   product: 产品名称（字母组合）
                #     r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<start_freq>\d+K?HZ)_TO_(?P<end_freq>\d+K?HZ)_MIC(?P<mic_id>\d+)_(?P<product>[A-Za-z]+)_EQ$',
                #
                #     # 4. 仅带MIC ID，无其他附加信息（全大写）
                #     # 匹配格式: AUDIO_L2AR_EAR_<ear_id>_<start_freq>_TO_<end_freq>_MIC<mic_id>
                #     # 示例: AUDIO_L2AR_EAR_14705_140HZ_TO_7100HZ_MIC1、AUDIO_L2AR_EAR_14705_140HZ_TO_7100HZ_MIC2
                #     # 捕获组说明:
                #     #   ear_id: EAR设备编号（数字）
                #     #   start_freq: 起始频率（支持HZ和KHZ单位）
                #     #   end_freq: 结束频率（支持HZ和KHZ单位）
                #     #   mic_id: 麦克风编号（数字）
                #     r'^AUDIO_L2AR_EAR_(?P<ear_id>\d+)_(?P<start_freq>\d+K?HZ)_TO_(?P<end_freq>\d+K?HZ)_MIC(?P<mic_id>\d+)$'
                # ]

                EAR_TEST_PATTERNS = test_patterns

                param_upper = param.upper()  # 将输入参数转为大写，确保匹配一致性
                match = None
                pattern_type = 0

                for i, pattern in enumerate(EAR_TEST_PATTERNS):
                    print(f"EAR模式{i + 1}: {pattern}")
                    match = re.match(pattern, param_upper)
                    print(f"EAR模式{i + 1}匹配结果: {match}")

                    if match:
                        print(f"EAR模式{i + 1}捕获的组:")
                        for group_name, value in match.groupdict().items():
                            print(f"  {group_name}: {value}")
                        pattern_type = i + 1
                        break
                    print("-" * 80)

                if not match:
                    raise ValueError(
                        f"无效的EAR测试参数格式: {param}\n"
                        f"参数结构应为以下之一:\n"
                        f"0. AUDIO_L2AR_EAR_<ear_id>_<low_freq>HZ_TO_<high_freq>HZ_MIC<mic_num>(_<product>)?(_ASYNC_(START|WAIT))?\n"
                        f"1. AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>_<产品名>_ASYNC_(START|WAIT)\n"
                        f"2. AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>_<产品名>\n"
                        f"3. AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>_<产品名>_EQ\n"
                        f"4. AUDIO_L2AR_EAR_<数字ID>_<起始频率>_TO_<结束频率>_MIC<麦克风ID>"
                    )

                # 根据不同模式解析参数
                if pattern_type == 1:
                    ear_id = match.group('ear_id')
                    start_freq = f"{match.group('low_freq')}HZ"
                    end_freq = f"{match.group('high_freq')}HZ"
                    mic_id = match.group('mic_num')
                    product = match.group('product')
                    async_mode = match.group('async_mode') or "同步"
                    is_eq_mode = False
                else:
                    ear_id = match.group('ear_id')
                    start_freq = match.group('start_freq')
                    end_freq = match.group('end_freq')
                    mic_id = match.group('mic_id')
                    product = match.group('product') if pattern_type in [2, 3, 4] else None
                    async_mode = match.group('async_mode') if pattern_type == 2 else "同步"
                    is_eq_mode = (pattern_type == 4)

                desc = {
                    "test_purpose_zh": f"测试编号为{ear_id}的EAR设备，在{start_freq}到{end_freq}的声音频率范围内，和编号为{mic_id}的麦克风一起工作时的表现如何" +
                                       ("，并启用均衡器(EQ)功能" if is_eq_mode else ""),
                    "test_items_zh": [
                        f"1. 检查编号{ear_id}的EAR设备，在{start_freq}到{end_freq}这个频率范围内，对声音的敏感程度和反应情况",
                        f"2. 观察EAR{ear_id}和麦克风{mic_id}之间，声音信号的传递是否能保持同步，不会出现时间差",
                        f"3. 测试在整个{start_freq}到{end_freq}的频率范围内，EAR{ear_id}的反应是否稳定，性能是否一致"
                    ],
                    "test_purpose_en": f"Verify cooperative performance of EAR{ear_id} with MIC{mic_id} in {start_freq} to {end_freq} frequency range" +
                                       (" with EQ enabled" if is_eq_mode else ""),
                    "test_items_en": [
                        f"1. Sensitivity response of EAR{ear_id} in {start_freq} to {end_freq} range",
                        f"2. Audio signal synchronization performance with MIC{mic_id}",
                        f"3. Linearity and stability of frequency response"
                    ]
                }

                if is_eq_mode:
                    desc["test_items_zh"].insert(2, f"2.1 测试EQ模式下EAR{ear_id}对不同频率的均衡处理效果")
                    desc["test_items_en"].insert(2, f"2.1 Frequency balance verification of EAR{ear_id} under EQ mode")

                if product:
                    desc["test_purpose_zh"] += f"，特别是针对{product}这款产品的适配情况"
                    desc["test_purpose_en"] += f" ({product} product)"
                    desc["test_items_zh"].append(f"4. 检查EAR{ear_id}和{product}产品连接使用时，是否能正常配合工作")
                    desc["test_items_en"].append(f"4. Compatibility verification with {product} product")

                if async_mode in ["START", "WAIT"]:
                    mode_text = "异步启动" if async_mode == "START" else "异步等待"
                    desc["test_purpose_zh"] += f"，采用{mode_text}的方式进行测试"
                    desc["test_purpose_en"] += f" (Asynchronous {async_mode} Mode)"
                    desc["test_items_zh"].append(f"5. 测试在{mode_text}模式下，EAR设备的响应时间和同步准确性")
                    desc["test_items_en"].append(
                        f"5. Response time and synchronization test for asynchronous {async_mode.lower()} mode")

                return desc

            def _parse_mic_contiguous(self, match):
                """解析MIC CONTIGUOUS模式"""
                mic_id = match.group('mic_id')
                spkr_id = match.group('spkr_id')
                freq_range = match.group('freq_range')
                async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"验证MIC{mic_id}与扬声器SPKR{spkr_id}在{freq_range}Hz频率范围内的连续采样性能",
                    "test_items_zh": [
                        f"1. MIC{mic_id}在{freq_range}Hz范围内的灵敏度响应",
                        f"2. 与扬声器SPKR{spkr_id}的同步性和连续性",
                        f"3. 采样数据的完整性和噪声水平"
                    ],
                    "test_purpose_en": f"Verify continuous sampling performance of MIC{mic_id} with speaker SPKR{spkr_id} in {freq_range}Hz frequency range",
                    "test_items_en": [
                        f"1. Sensitivity response of MIC{mic_id} in {freq_range}Hz range",
                        f"2. Synchronization and continuity with speaker SPKR{spkr_id}",
                        f"3. Integrity and noise level of sampled data"
                    ]
                }

                if async_mode == "START":
                    desc["test_purpose_zh"] += "（异步启动模式）"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("4. 异步启动的时间精度")
                    desc["test_items_en"].append("4. Time accuracy of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "（异步等待模式）"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append("4. 异步等待的响应时间")
                    desc["test_items_en"].append("4. Response time of asynchronous wait")

                return desc

            def _parse_mic_contiguous2(self, match):
                """解析MIC CONTIGUOUS模式"""
                mic_id = match.group('mic_id')
                spkr_id = match.group('spkr_id')
                freq_range = match.group('freq_range')
                async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"检查麦克风MIC{mic_id}和扬声器SPKR{spkr_id}，在{freq_range}赫兹的频率范围内，连续采集声音的效果怎么样",
                    "test_items_zh": [
                        f"1. 看看麦克风MIC{mic_id}在{freq_range}赫兹范围内，对声音敏感不敏感，反应快不快",
                        f"2. 检查麦克风MIC{mic_id}和扬声器SPKR{spkr_id}配合工作时，会不会有卡顿或不同步的情况",
                        f"3. 测试采集到的声音是不是完整的，有没有太多杂音或断档"
                    ],
                    "test_purpose_en": f"Verify continuous sampling performance of MIC{mic_id} with speaker SPKR{spkr_id} in {freq_range}Hz frequency range",
                    "test_items_en": [
                        f"1. Sensitivity response of MIC{mic_id} in {freq_range}Hz range",
                        f"2. Synchronization and continuity with speaker SPKR{spkr_id}",
                        f"3. Integrity and noise level of sampled data"
                    ]
                }

                if async_mode == "START":
                    desc["test_purpose_zh"] += "，用异步启动的方式进行测试"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("4. 测试异步启动时，麦克风开始工作的时间准不准，会不会延迟")
                    desc["test_items_en"].append("4. Time accuracy of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "，用异步等待的方式进行测试"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append("4. 测试异步等待时，麦克风接到指令后多久能响应，反应速度快不快")
                    desc["test_items_en"].append("4. Response time of asynchronous wait")

                return desc

            def _parse_mic_contiguous3(self, match):
                """解析MIC CONTIGUOUS模式（专门处理EQ后缀模式）"""
                mic_id = match.group('mic_id')
                spkr_id = match.group('spkr_id')
                freq_range = match.group('freq_range')
                # EQ模式不包含异步模式，直接设为同步
                async_mode = "同步"

                # 基础描述，已包含EQ模式说明
                desc = {
                    "test_purpose_zh": f"检查麦克风MIC{mic_id}和扬声器SPKR{spkr_id}，在{freq_range}赫兹的频率范围内，连续采集声音的效果怎么样，并启用均衡器(EQ)进行音效调节",
                    "test_items_zh": [
                        f"1. 看看麦克风MIC{mic_id}在{freq_range}赫兹范围内，对声音敏感不敏感，反应快不快",
                        f"1.1 测试在EQ模式下，麦克风MIC{mic_id}对不同频率声音的采集效果是否均衡",
                        f"2. 检查麦克风MIC{mic_id}和扬声器SPKR{spkr_id}配合工作时，会不会有卡顿或不同步的情况",
                        f"3. 测试采集到的声音是不是完整的，有没有太多杂音或断档"
                    ],
                    "test_purpose_en": f"Verify continuous sampling performance of MIC{mic_id} with speaker SPKR{spkr_id} in {freq_range}Hz frequency range with EQ (Equalizer) enabled",
                    "test_items_en": [
                        f"1. Sensitivity response of MIC{mic_id} in {freq_range}Hz range",
                        f"1.1 Frequency balance check under EQ mode for MIC{mic_id}",
                        f"2. Synchronization and continuity with speaker SPKR{spkr_id}",
                        f"3. Integrity and noise level of sampled data"
                    ]
                }

                # 由于EQ模式正则表达式中没有异步模式，这里可以省略异步处理
                # 保留兼容代码，防止意外情况
                if async_mode == "START":
                    desc["test_purpose_zh"] += "，用异步启动的方式进行测试"
                    desc["test_purpose_en"] += " (Asynchronous Start Mode)"
                    desc["test_items_zh"].append("4. 测试异步启动时，麦克风开始工作的时间准不准，会不会延迟")
                    desc["test_items_en"].append("4. Time accuracy of asynchronous start")

                elif async_mode == "WAIT":
                    desc["test_purpose_zh"] += "，用异步等待的方式进行测试"
                    desc["test_purpose_en"] += " (Asynchronous Wait Mode)"
                    desc["test_items_zh"].append("4. 测试异步等待时，麦克风接到指令后多久能响应，反应速度快不快")
                    desc["test_items_en"].append("4. Response time of asynchronous wait")

                return desc

            def _parse_mic_dft_block(self, match):
                """解析MIC DFT/FFT BLOCK模式（处理带位置和块类型的变换测试）"""
                # 提取正则表达式捕获的参数
                mic_id = match.group('mic_id')
                transform_type = match.group('transform_type')
                freq_khz = match.group('freq_khz')
                param1 = match.group('param1')
                param2 = match.group('param2')
                position = match.group('position')
                pos_num = match.group('pos_num')
                spkr_id = match.group('spkr_id')
                block_type = match.group('block_type')

                # 位置标识中文映射
                position_map = {
                    'L': '左侧',
                    'R': '右侧',
                    'M': '中间'
                }
                position_zh = position_map.get(position, position)

                # 基础描述信息
                desc = {
                    "test_purpose_zh": f"检查麦克风MIC{mic_id}在{freq_khz}KHz频率下，使用{transform_type}变换算法，配合{position_zh}{pos_num}位置的扬声器SPKR{spkr_id}进行的{block_type}块测试性能",
                    "test_items_zh": [
                        f"1. 验证MIC{mic_id}在{freq_khz}KHz频率下的{transform_type}变换精度（参数范围：{param1}-{param2}）",
                        f"1.1 检查{block_type}块数据处理的完整性和时效性",
                        f"2. 测试{position_zh}{pos_num}位置的SPKR{spkr_id}与MIC{mic_id}的信号同步性",
                        f"3. 验证不同信号强度下{transform_type}变换结果的稳定性",
                        f"4. 检查{block_type}块数据传输过程中的丢包率和错误率"
                    ],
                    "test_purpose_en": f"Verify performance of MIC{mic_id} with {transform_type} transform algorithm at {freq_khz}KHz frequency, working with {position}{pos_num} speaker SPKR{spkr_id} in {block_type} block test",
                    "test_items_en": [
                        f"1. {transform_type} transform accuracy of MIC{mic_id} at {freq_khz}KHz (parameter range: {param1}-{param2})",
                        f"1.1 Integrity and timeliness check of {block_type} block data processing",
                        f"2. Signal synchronization test between {position}{pos_num} SPKR{spkr_id} and MIC{mic_id}",
                        f"3. Stability verification of {transform_type} results under different signal strengths",
                        f"4. Packet loss and error rate check during {block_type} block data transmission"
                    ]
                }

                # 根据变换类型添加专项测试项
                if transform_type == "FFT":
                    desc["test_items_zh"].insert(2, f"2.1 验证快速傅里叶变换的频谱分辨率是否符合设计要求")
                    desc["test_items_en"].insert(2, f"2.1 Verify FFT spectrum resolution meets design requirements")
                elif transform_type == "DFT":
                    desc["test_items_zh"].insert(2, f"2.1 验证离散傅里叶变换的计算精度和资源占用率")
                    desc["test_items_en"].insert(2, f"2.1 Verify DFT calculation accuracy and resource utilization")

                return desc

            def _parse_audio_mic(self, match):
                """解析AUDIO_MIC模式（对应第4种参数格式）"""
                # 从匹配结果中提取参数
                mic_id = match.group('mic_id')
                spkr_id = match.group('spkr_id')
                param1 = match.group('param1')
                param2 = match.group('param2')
                param3 = match.group('param3')
                suffix = match.group('suffix')

                # 构建频率范围描述
                freq_desc = f"{param1}-{param2}K{param3}Hz"

                # 基础描述字典
                desc = {
                    "test_purpose_zh": f"检查麦克风MIC{mic_id}和扬声器SPKR{spkr_id}在{freq_desc}频率下，与密封性(SEAL)相关的音频性能表现",
                    "test_items_zh": [
                        f"1. 评估麦克风MIC{mic_id}在{freq_desc}频率范围内的收音灵敏度和准确性",
                        f"2. 检查扬声器SPKR{spkr_id}在{freq_desc}频率下的输出特性与密封状态的关系",
                        f"3. 测试不同密封条件（{suffix}）对MIC{mic_id}和SPKR{spkr_id}音频交互的影响",
                        f"4. 验证在{freq_desc}频率下，密封性能变化时的音频信号完整性"
                    ],
                    "test_purpose_en": f"Verify audio performance related to seal for MIC{mic_id} and SPKR{spkr_id} at {freq_desc} frequency",
                    "test_items_en": [
                        f"1. Evaluate收音灵敏度 and accuracy of MIC{mic_id} in {freq_desc} range",
                        f"2. Check output characteristics of SPKR{spkr_id} at {freq_desc} related to seal status",
                        f"3. Test impact of different seal conditions ({suffix}) on audio interaction between MIC{mic_id} and SPKR{spkr_id}",
                        f"4. Verify audio signal integrity with varying seal performance at {freq_desc}"
                    ]
                }

                # 处理英文翻译中的未翻译部分
                desc["test_items_en"][0] = desc["test_items_en"][0].replace("收音灵敏度", "sensitivity")

                # 根据suffix添加特定测试项（模拟异步模式的条件处理）
                if "HIGH" in suffix.upper():
                    desc["test_purpose_zh"] += "，重点测试高密封状态下的性能"
                    desc["test_purpose_en"] += " (High Seal Condition Focus)"
                    desc["test_items_zh"].append(f"5. 验证MIC{mic_id}在高密封压力下的稳定性")
                    desc["test_items_en"].append(f"5. Verify stability of MIC{mic_id} under high seal pressure")
                elif "LOW" in suffix.upper():
                    desc["test_purpose_zh"] += "，重点测试低密封状态下的性能"
                    desc["test_purpose_en"] += " (Low Seal Condition Focus)"
                    desc["test_items_zh"].append(f"5. 评估SPKR{spkr_id}在低密封条件下的音质保持能力")
                    desc["test_items_en"].append(
                        f"5. Evaluate sound quality retention of SPKR{spkr_id} under low seal condition")

                return desc

            def _parse_mic_fft(self, match):
                """解析MIC FFT模式"""
                mic_id = match.group('mic_id')
                fft_id = match.group('fft_id')
                freq_low = match.group('freq_low')
                freq_high = match.group('freq_high')
                spkr_id = match.group('spkr_id')
                async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"验证MIC{mic_id}在{freq_low}-{freq_high}kHz频率范围内的FFT频谱分析性能（ID:{fft_id}）",
                    "test_items_zh": [
                        f"1. MIC{mic_id}在{freq_low}-{freq_high}kHz范围内的频率响应",
                        f"2. FFT算法（采样率:{fft_id}）的精度和分辨率",
                        f"3. 与扬声器SPKR{spkr_id}的声学耦合性能"
                    ],
                    "test_purpose_en": f"Verify FFT spectral analysis performance of MIC{mic_id} in {freq_low}-{freq_high}kHz frequency range (ID:{fft_id})",
                    "test_items_en": [
                        f"1. Frequency response of MIC{mic_id} in {freq_low}-{freq_high}kHz range",
                        f"2. Accuracy and resolution of FFT algorithm (sampling rate:{fft_id})",
                        f"3. Acoustic coupling performance with speaker SPKR{spkr_id}"
                    ]
                }

                if async_mode:
                    desc["test_purpose_zh"] += f"（{async_mode}模式）"
                    desc["test_purpose_en"] += f" ({async_mode} Mode)"

                return desc

            def _parse_mic_fft2(self, match):
                """解析MIC FFT模式"""
                mic_id = match.group('mic_id')
                fft_id = match.group('fft_id')
                freq_low = match.group('freq_low')
                freq_high = match.group('freq_high')
                spkr_id = match.group('spkr_id')
                async_mode = match.group('async_mode') or "同步"

                # FFT算法通俗解释：快速傅里叶变换，像"声音的彩虹分光镜"，能快速把混合声音拆成不同频率的成分（比如把音乐拆成各个乐器的声音）
                desc = {
                    "test_purpose_zh": f"检查麦克风MIC{mic_id}，在{freq_low}到{freq_high}千赫兹的频率范围内，用FFT频谱分析（编号:{fft_id}，一种快速拆分声音频率的技术）的效果怎么样",
                    "test_items_zh": [
                        f"1. 看看麦克风MIC{mic_id}在{freq_low}到{freq_high}千赫兹范围内，对不同频率声音的反应如何",
                        f"2. 测试FFT算法（采样率:{fft_id}）拆分声音的准不准，能不能分辨出很接近的频率（比如同时听到的钢琴和小提琴声音）",
                        f"3. 检查麦克风MIC{mic_id}和扬声器SPKR{spkr_id}之间，声音传递配合得好不好"
                    ],
                    "test_purpose_en": f"Verify FFT spectral analysis performance of MIC{mic_id} in {freq_low}-{freq_high}kHz frequency range (ID:{fft_id})",
                    "test_items_en": [
                        f"1. Frequency response of MIC{mic_id} in {freq_low}-{freq_high}kHz range",
                        f"2. Accuracy and resolution of FFT algorithm (sampling rate:{fft_id})",
                        f"3. Acoustic coupling performance with speaker SPKR{spkr_id}"
                    ]
                }

                if async_mode:
                    desc["test_purpose_zh"] += f"，用{async_mode}模式进行测试"
                    desc["test_purpose_en"] += f" ({async_mode} Mode)"

                return desc

            def _parse_mic_fft_suffix(self, match):
                """解析带产品名称后缀的MIC FFT模式（针对ORION产品添加专项测试）"""
                mic_id = match.group('mic_id')
                fft_id = match.group('fft_id')
                freq_low = match.group('freq_low')
                freq_high = match.group('freq_high')
                spkr_id = match.group('spkr_id')
                product_name = match.group('suffix')  # 后缀为产品名称

                # 基础描述框架
                desc = {
                    "test_purpose_zh": f"针对{product_name}产品，检查麦克风MIC{mic_id}在{freq_low}-{freq_high}kHz范围内的FFT频谱分析（编号:{fft_id}）性能",
                    "test_items_zh": [
                        f"1. 评估{product_name}产品中MIC{mic_id}在{freq_low}-{freq_high}kHz频段的频率响应特性",
                        f"2. 验证{product_name}产品专用FFT算法（ID:{fft_id}）的频率解析精度",
                        f"3. 测试{product_name}产品中SPKR{spkr_id}与MIC{mic_id}的声学匹配度",
                        f"4. 确认{product_name}产品在目标频段的音频信号完整性"
                    ],
                    "test_purpose_en": f"Verify FFT spectral analysis performance for {product_name} product, MIC{mic_id} in {freq_low}-{freq_high}kHz range (ID:{fft_id})",
                    "test_items_en": [
                        f"1. Frequency response characteristics of MIC{mic_id} in {product_name} product ({freq_low}-{freq_high}kHz)",
                        f"2. Frequency resolution accuracy of {product_name} dedicated FFT algorithm (ID:{fft_id})",
                        f"3. Acoustic matching between SPKR{spkr_id} and MIC{mic_id} in {product_name}",
                        f"4. Audio signal integrity verification for {product_name} in target frequency band"
                    ]
                }

                return desc

            def _parse_mic_dft(self, match):
                """解析MIC DFT模式"""
                mic_id = match.group('mic_id')
                freq_khz = match.group('freq_khz')
                dft_id = match.group('dft_id')
                dft_param = match.group('dft_param')
                spkr_id = match.group('spkr_id')
                async_mode = match.group('async_mode') or "同步"

                desc = {
                    "test_purpose_zh": f"验证MIC{mic_id}在{dft_id}DFT算法下对{freq_khz}kHz信号的处理性能（参数:{dft_param}）",
                    "test_items_zh": [
                        f"1. MIC{mic_id}对{dft_id}kHz信号的灵敏度",
                        f"2. DFT算法（ID:{dft_id}）的计算精度",
                        f"3. 与扬声器SPKR{spkr_id}的声学匹配度"
                    ],
                    "test_purpose_en": f"Verify processing performance of MIC{mic_id} for {freq_khz}kHz signal under DFT algorithm {dft_id} (Parameter:{dft_param})",
                    "test_items_en": [
                        f"1. Sensitivity of MIC{mic_id} to {freq_khz}kHz signal",
                        f"2. Calculation accuracy of DFT algorithm (ID:{dft_id})",
                        f"3. Acoustic matching with speaker SPKR{spkr_id}"
                    ]
                }

                if async_mode:
                    desc["test_purpose_zh"] += f"（{async_mode}模式）"
                    desc["test_purpose_en"] += f" ({async_mode} Mode)"

                return desc

            def _parse_mic_dft2(self, match):
                """解析MIC DFT模式"""
                mic_id = match.group('mic_id')
                freq_khz = match.group('freq_khz')
                dft_id = match.group('dft_id')
                dft_param = match.group('dft_param')
                spkr_id = match.group('spkr_id')
                async_mode = match.group('async_mode') or "同步"

                # DFT算法通俗解释：离散傅里叶变换，像"声音的拆解器"，能把混合声音拆成不同频率的成分，FFT是它的快速版本
                desc = {
                    "test_purpose_zh": f"检查麦克风MIC{mic_id}，用{dft_id}号DFT算法（一种拆分声音频率的技术）处理{freq_khz}千赫兹信号的效果（参数:{dft_param}）",
                    "test_items_zh": [
                        f"1. 看看麦克风MIC{mic_id}对{dft_id}千赫兹的信号敏感不敏感",
                        f"2. 测试DFT算法（编号:{dft_id}）拆分和计算声音频率的准不准",
                        f"3. 检查麦克风MIC{mic_id}和扬声器SPKR{spkr_id}之间，声音匹配得好不好"
                    ],
                    "test_purpose_en": f"Verify processing performance of MIC{mic_id} for {freq_khz}kHz signal under DFT algorithm {dft_id} (Parameter:{dft_param})",
                    "test_items_en": [
                        f"1. Sensitivity of MIC{mic_id} to {freq_khz}kHz signal",
                        f"2. Calculation accuracy of DFT algorithm (ID:{dft_id})",
                        f"3. Acoustic matching with speaker SPKR{spkr_id}"
                    ]
                }

                if async_mode:
                    desc["test_purpose_zh"] += f"，用{async_mode}模式进行测试"
                    desc["test_purpose_en"] += f" ({async_mode} Mode)"

                return desc

            def filter_mic_async_items(self, grouped_dict):
                """
                遍历嵌套字典，过滤掉所有包含 '_ASYNC_START' 或 '_ASYNC_WAIT' 的键

                参数:
                grouped_dict (dict): 嵌套字典结构

                返回:
                dict: 过滤后的新字典
                """
                result = {}

                for key, value in grouped_dict.items():
                    if isinstance(value, dict):
                        # 递归处理子字典
                        filtered_value = self.filter_mic_async_items(value)
                        # 仅当子字典不为空时保留
                        if filtered_value:
                            result[key] = filtered_value
                    elif isinstance(value, list):
                        # 处理列表中的元素（如果是字典）
                        new_list = []
                        for item in value:
                            if isinstance(item, dict):
                                # 递归处理列表中的字典
                                filtered_item = self.filter_mic_async_items(item)
                                if filtered_item:
                                    new_list.append(filtered_item)
                            else:
                                # 非字典元素直接保留
                                new_list.append(item)
                        # 仅当列表不为空时保留
                        if new_list:
                            result[key] = new_list
                    else:
                        # 非字典和列表的元素直接保留
                        result[key] = value

                # 过滤当前层级的键
                return {k: v for k, v in result.items()
                        if '_ASYNC_START' not in k and '_ASYNC_WAIT' not in k}

            def extract_mic_failed_logs(self, filtered_dict):
                """
                遍历过滤后的字典，提取所有包含 'EvalAndLogResults' 和 '* FAILED *' 的行

                参数:
                filtered_dict (dict): 过滤后的嵌套字典结构

                返回:
                list: 包含所有匹配行的列表
                """
                results = []

                def _recursive_search(obj):
                    if isinstance(obj, dict):
                        # 遍历字典的所有值
                        for value in obj.values():
                            _recursive_search(value)
                    elif isinstance(obj, list):
                        # 遍历列表中的每个元素
                        for item in obj:
                            if isinstance(item, str):
                                # 检查字符串是否同时包含两个关键词
                                if 'EvalAndLogResults' in item and '* FAILED *' in item:
                                    results.append(item)
                            else:
                                # 递归处理非字符串元素
                                _recursive_search(item)

                # 从根字典开始递归搜索
                _recursive_search(filtered_dict)
                return results

            def generic_mic_failed_logs_dict(self, filtered_dict, failed_logs):
                """
                处理过滤后的字典，将包含失败日志的列表重命名并更新内容

                参数:
                filtered_dict (dict): 过滤后的嵌套字典结构
                failed_logs (list): 包含所有失败日志的列表

                返回:
                dict: 处理后的字典副本
                """
                from copy import deepcopy

                # 创建字典的深拷贝，避免修改原始数据
                result_dict = deepcopy(filtered_dict)

                def _recursive_process(obj):
                    if isinstance(obj, dict):
                        # 用于存储需要重命名的键值对
                        items_to_rename = []

                        # 遍历字典中的每个键值对
                        for key, value in obj.items():
                            if isinstance(value, list):
                                # 检查列表中是否包含失败日志
                                has_failed_logs = any(
                                    isinstance(item, str) and
                                    'EvalAndLogResults' in item and
                                    '* FAILED *' in item
                                    for item in value
                                )

                                if has_failed_logs:
                                    # 记录需要重命名的键和原始值
                                    items_to_rename.append((key, value))

                            # 递归处理嵌套的字典或列表
                            _recursive_process(value)

                        # 重命名列表并更新内容
                        for old_key, old_value in items_to_rename:
                            # 构建新键名
                            new_key = f"{old_key}_FAILED"
                            # 清空原列表并添加失败日志
                            old_value.clear()
                            old_value.extend(failed_logs)
                            # 从字典中删除旧键
                            obj.pop(old_key)
                            # 添加新键
                            obj[new_key] = old_value

                    elif isinstance(obj, list):
                        # 递归处理列表中的元素
                        for item in obj:
                            _recursive_process(item)

                # 从根字典开始处理
                _recursive_process(result_dict)
                return result_dict

            def filter_mic_duplicate_logs_in_dict(self, data_dict):
                """
                递归过滤字典中所有列表的重复日志项

                参数:
                data_dict (dict): 包含嵌套列表的字典

                返回:
                dict: 处理后的字典副本
                """
                from copy import deepcopy

                # 创建字典的深拷贝，避免修改原始数据
                result_dict = deepcopy(data_dict)

                def _recursive_process(obj):
                    if isinstance(obj, dict):
                        # 递归处理字典的值
                        for key, value in obj.items():
                            obj[key] = _recursive_process(value)
                        return obj

                    elif isinstance(obj, list):
                        # 处理列表中的重复项
                        unique_items = []
                        seen = set()

                        for item in obj:
                            if isinstance(item, str):
                                # 提取关键信息用于判断重复
                                parts = item.split()
                                if len(parts) >= 4:
                                    # 提取关键标识: 通常是第四个部分和最后一个部分
                                    key_part = parts[3]
                                    last_part = parts[-1] if parts else ""
                                    log_id = f"{key_part}_{last_part}"

                                    # 检查是否已存在
                                    if log_id not in seen:
                                        seen.add(log_id)
                                        unique_items.append(item)
                                else:
                                    # 格式不完整的日志，直接保留
                                    unique_items.append(item)
                            else:
                                # 非字符串项，递归处理
                                processed_item = _recursive_process(item)
                                unique_items.append(processed_item)

                        return unique_items

                    else:
                        # 其他类型的数据直接返回
                        return obj

                # 从根字典开始处理
                return _recursive_process(result_dict)

            def extract_mic_log_data(self, cleaned_dict):
                """
                从cleaned_dict中提取日志数据并结构化

                参数:
                cleaned_dict (dict): 已清理的字典数据

                返回:
                dict: 结构化后的字典数据
                """
                result = {}

                def _process_item(item):
                    """处理单个日志条目，提取关键信息"""
                    if not isinstance(item, str):
                        return item

                    parts = item.strip().split('\t')
                    if len(parts) < 12:  # 确保数据至少包含必要的字段
                        return item

                    try:
                        return {
                            'Item': parts[3],
                            'lowlimit': parts[4],
                            'uplimit': parts[5],
                            'data': parts[6],
                            'unit': parts[7],
                            'state': parts[10].strip()
                        }
                    except IndexError:
                        return item  # 处理格式异常的数据，保持原样

                def _recursive_extract(obj):
                    """递归处理字典和列表"""
                    if isinstance(obj, dict):
                        new_dict = {}
                        for key, value in obj.items():
                            new_dict[key] = _recursive_extract(value)
                        return new_dict

                    elif isinstance(obj, list):
                        new_list = []
                        for item in obj:
                            if isinstance(item, str) and 'EvalAndLogResults' in item:
                                new_list.append(_process_item(item))
                            else:
                                new_list.append(_recursive_extract(item))
                        return new_list

                    else:
                        return obj

                return _recursive_extract(cleaned_dict)

            def analyze_mic_test_position(self, nested_dict):
                """
                分析嵌套字典中的数据点位置，仅返回位置分析结果

                参数:
                nested_dict (dict): 嵌套字典结构，包含需要分析的数据列表

                返回:
                dict: 包含位置分析结果的新字典
                """
                from copy import deepcopy

                def determine_position(data_list):
                    """判断数据点在区间中的位置，仅返回位置分析结果"""
                    results = []

                    for item in data_list:
                        try:
                            data = float(item['data'])
                            low = float(item['lowlimit'])
                            high = float(item['uplimit'])

                            # 计算相对位置：0.0（等于下限）到 1.0（等于上限）
                            if high == low:
                                position = 0.5 if data == low else (0.0 if data < low else 1.0)
                            else:
                                position = (data - low) / (high - low)

                            # 根据相对位置分类
                            if position < 0.33:
                                position_class_cn = "偏下"
                                position_class_en = "Below"
                            elif position > 0.67:
                                position_class_cn = "偏上"
                                position_class_en = "Above"
                            else:
                                position_class_cn = "居中"
                                position_class_en = "Middle"

                            results.append({
                                'position': position,  # 相对位置比例
                                'position_cn': position_class_cn,  # 中文位置分类
                                'position_en': position_class_en  # 英文位置分类
                            })
                        except (KeyError, ValueError, TypeError) as e:
                            results.append({
                                'position_error': f"位置分析失败: {str(e)}"
                            })
                    return results

                def process_value(value):
                    """递归处理字典值"""
                    if isinstance(value, dict):
                        return {k: process_value(v) for k, v in value.items()}
                    elif isinstance(value, list) and value and isinstance(value[0], dict):
                        # 处理包含字典的列表
                        return determine_position(value)
                    else:
                        return value  # 其他类型的值保持不变

                # 创建深拷贝，避免修改原始数据
                return deepcopy({k: process_value(v) for k, v in nested_dict.items()})

            def merge_mic_test_position_v1(self, structured_failed_logs_dict, mic_test_position):
                """
                将位置分析结果合并到原始结构化日志数据中

                参数:
                structured_failed_logs_dict (dict): 原始结构化失败日志数据
                mic_test_position (dict): 位置分析结果

                返回:
                dict: 合并后的新字典
                """
                from copy import deepcopy

                # 创建深拷贝，避免修改原始数据
                merged_dict = deepcopy(structured_failed_logs_dict)

                # 遍历位置分析结果的每个键
                for key, value in mic_test_position.items():
                    # 检查原始数据中是否存在相同的键
                    if key in merged_dict:
                        # 遍历位置分析结果的子键
                        for sub_key, position_list in value.items():
                            # 检查原始数据中是否存在相同的子键
                            if sub_key in merged_dict[key]:
                                # 获取原始数据中的项目列表
                                item_list = merged_dict[key][sub_key]

                                # 确保两个列表长度相同
                                if len(item_list) == len(position_list):
                                    # 合并每个项目的位置分析结果
                                    for i in range(len(item_list)):
                                        # 添加位置分析结果到原始数据中
                                        item_list[i].update(position_list[i])
                                else:
                                    print(f"警告: 键 '{sub_key}' 的项目数量不匹配，无法合并位置分析结果")
                            else:
                                print(f"警告: 原始数据中不存在子键 '{sub_key}'，跳过位置分析结果")
                    else:
                        print(f"警告: 原始数据中不存在键 '{key}'，跳过位置分析结果")

                return merged_dict

            def merge_mic_test_position(self, structured_failed_logs_dict, mic_test_position):
                """
                将位置分析结果合并到原始结构化日志数据中

                参数:
                structured_failed_logs_dict (dict): 原始结构化失败日志数据（一层字典）
                mic_test_position (dict): 位置分析结果（一层字典）

                返回:
                dict: 合并后的新字典
                """
                from copy import deepcopy

                # 创建深拷贝，避免修改原始数据
                merged_dict = deepcopy(structured_failed_logs_dict)

                # 遍历位置分析结果的每个键（由于是一层字典，直接处理键值对）
                for key, value in mic_test_position.items():
                    # 检查原始数据中是否存在相同的键
                    if key in merged_dict:
                        # 对于一层字典，直接合并值
                        # 如果原始值是字典，进行更新；如果是其他类型，直接覆盖
                        if isinstance(merged_dict[key], dict) and isinstance(value, dict):
                            merged_dict[key].update(value)
                        else:
                            # 非字典类型直接赋值（可根据实际需求调整此逻辑）
                            merged_dict[key] = value
                    else:
                        # 原始数据中不存在该键，直接添加
                        merged_dict[key] = value

                return merged_dict

            def merge_mic_test_purpose2items(self, structured_failed_logs_dict, mic_test_purpose2items, second_key):
                """
                将测试目的和测试项信息添加到结构化失败日志字典中

                参数:
                structured_failed_logs_dict (dict): 原始结构化失败日志数据
                mic_test_purpose2items (dict): 测试目的和测试项信息

                返回:
                dict: 合并后的新字典
                """
                from copy import deepcopy

                # 创建深拷贝，避免修改原始数据
                merged_dict = deepcopy(structured_failed_logs_dict)

                # 查找目标键
                target_key = None
                for key in merged_dict.keys():
                    if second_key in merged_dict[key]:
                        target_key = key
                        break

                if target_key:
                    # 获取目标字典
                    target_dict = merged_dict[target_key][second_key]

                    # 检查目标字典是否为列表
                    if isinstance(target_dict, list):
                        # 将测试目的和测试项信息作为新的键添加到目标层级
                        merged_dict[target_key][second_key] = {
                            'purpose2items': mic_test_purpose2items,
                            'data_items': target_dict  # 保留原始数据列表
                        }
                    else:
                        print("警告: 目标键下不是有效的数据列表")
                else:
                    print("警告: 未找到目标键 'AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200_FAILED'")

                return merged_dict

            def analyze_mic_failure_reasons_suggestion(self, structured_failed_logs_dict,
                                                       language='zh',
                                                       first_key=r'AUDIO_SAMPLE_MIC_\\d+_CONTIGUOUS_SPKR\\d+_\\d+-\\d+(?:_ASYNC_(START|WAIT))?.*FAILED'):
                """
                分析AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200_FAILED的失败原因并提供建议
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_MIC_后跟数字，然后是任意内容和FAILED
                mic_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        # 使用正则表达式进行匹配
                        if mic_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "未找到AUDIO_SAMPLE_MIC_1相关的失败测试项"
                    return error_msg if language == 'zh' else "No AUDIO_SAMPLE_MIC_1 failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # 解析XML模板
                try:
                    xml_path = Path(".") / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 编译用于查找test_type的正则表达式
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None

                    # 遍历所有test_type元素，使用正则表达式匹配name属性
                    for elem in root.findall(".//test_type"):
                        name_attr = elem.get('name', '')
                        if test_type_pattern.search(name_attr):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")

                    # 获取模板内容并替换变量格式（关键修复）
                    template_content = desc_elem.text.strip()
                    # 将{{变量名}}格式转换为${变量名}格式，适配Python Template
                    template_content = template_content.replace('{{', '${').replace('}}', '}')

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"XML解析错误: {str(e)}" if language == 'zh' else f"XML parsing error: {str(e)}"

                # 处理灵敏度异常信息（保持不变）
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0

                    freq_info = []
                    for freq, value in freq_values:
                        if freq is not None:
                            freq_info.append(f"{freq}Hz: {value:.2f}dB" if language == 'zh'
                                             else f"{freq}Hz: {value:.2f}dB")

                    if language == 'zh':
                        level_spec_text = (f"{test_items[0]}: 麦克风灵敏度响应超出上限\n"
                                           f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，上限: {upper_limit:.1f} dB\n")
                    else:
                        level_spec_text = (f"{test_items[0]}: Microphone sensitivity response exceeds the upper limit\n"
                                           f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, Upper limit: {upper_limit:.1f} dB\n")
                    if freq_info:
                        level_spec_text += f"  {'频率点测量' if language == 'zh' else 'Frequency measurements'}: {', '.join(freq_info)}\n"

                # 处理状态异常信息（保持不变）
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if language == 'zh':
                        status_text = (f"{test_items[2]}: 采样数据状态异常\n"
                                       f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                    else:
                        status_text = (f"{test_items[2]}: Abnormal sampling data status\n"
                                       f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")

                # 综合分析（保持不变）
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if language == 'zh':
                        comprehensive_text = "- 所有测试项均失败，表明MIC1与SPKR1在300-5200Hz范围内的整体性能不达标\n"
                    else:
                        comprehensive_text = "- All test items failed, indicating that the overall performance of MIC1 and SPKR1 in the 300-5200Hz range does not meet the standard\n"

                # 填充模板
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=target_key,
                        problem_desc=f"{'音频采样测试失败' if language == 'zh' else 'Audio sampling test failed'}",
                        test_purpose=test_purpose,
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text
                    )
                    return report
                except KeyError as e:
                    return f"模板中存在未定义的变量: {str(e)}" if language == 'zh' else f"Undefined variable in template: {str(e)}"
                except Exception as e:
                    return f"生成报告时出错: {str(e)}" if language == 'zh' else f"Error generating report: {str(e)}"

            def analyze_mic_failure_reasons_suggestion2(self, structured_failed_logs_dict,
                                                        language='zh',
                                                        first_key=r'AUDIO_SAMPLE_MIC_\d+_(?:CONTIGUOUS|FFT|DFT)_(?:\d+K?HZ?_|)(?:\d+K?-\d+K?|\d+-\d+)_SPKR\d+[A-Z0-9_]*(?:_ASYNC_(?:START|WAIT))?.*FAILED'):
                """
                Analyze failure reasons and provide suggestions for MIC related test failures
                """
                # Dynamically find target test item key
                target_key = None
                target_entry = None

                # Compile regex pattern - match MIC test patterns
                mic_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        # Use regex for matching
                        if mic_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "未找到AUDIO_SAMPLE_MIC相关的失败测试项"
                    return error_msg if language == 'zh' else "No AUDIO_SAMPLE_MIC failure test item found"

                # Extract test data and purpose
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # Analyze data items
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # Parse XML template
                try:
                    # Set base path according to the operating system
                    if os.name == 'posix':  # Linux/Mac system
                        base_path = Path("/opt/xiejun4/pro_PathFinder")
                    else:  # Windows system
                        base_path = Path(".")  # Keep current directory as base

                    xml_path = base_path / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # Compile regex for finding test_type
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None

                    # Iterate through all test_type elements, match name attribute with regex
                    for elem in root.findall(".//test_type"):
                        name_attr = elem.get('name', '')
                        if test_type_pattern.search(name_attr):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")

                    # Get template content and replace variable format
                    template_content = desc_elem.text.strip()
                    # Convert {{variable}} format to ${variable} format for Python Template
                    template_content = template_content.replace('{{', '${').replace('}}', '}')

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"XML解析错误: {str(e)}" if language == 'zh' else f"XML parsing error: {str(e)}"

                # Extract variables from target_key using regex
                # Pattern to match different MIC test formats
                key_patterns = [
                    # For FFT format: AUDIO_SAMPLE_MIC_1_FFT_44100_4K-16K_SPKR1_MILOS
                    r'AUDIO_SAMPLE_MIC_(\d+)_FFT_(\d+)_([\dK-]+)_([A-Z0-9]+)',
                    # For DFT format: AUDIO_SAMPLE_MIC_2_DFT_8KHZ_200_5000_L2SPK2_MILOS
                    r'AUDIO_SAMPLE_MIC_(\d+)_DFT_(\d+K?HZ?)_(\d+)_(\d+)_([A-Z0-9]+)',
                    # For CONTIGUOUS format: AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200
                    r'AUDIO_SAMPLE_MIC_(\d+)_CONTIGUOUS_([A-Z0-9]+)_([\d-]+)'
                    # New pattern for AUDIO_MIC format: AUDIO_MIC1_SPKR1_300-5K2Hz_VS_SEAL_PORTO_FAILED
                    r'AUDIO_MIC(\d+)_SPKR(\d+)_([\d-]+)K(\d+)Hz_VS_SEAL_([A-Z0-9_]+)'
                ]

                mic_number = ""
                sampling_rate = ""
                freq_range = ""
                spkr_name = ""
                mic_name = ""
                # 新增AUDIO_MIC模式专用变量
                is_audio_mic_pattern = False

                for pattern in key_patterns:
                    match = re.search(pattern, target_key)
                    if match:
                        if 'FFT' in pattern:
                            mic_number = match.group(1)
                            sampling_rate = match.group(2)
                            freq_range = match.group(3).replace('K', 'K')  # Preserve K notation
                            spkr_name = match.group(4).split('_')[0]  # Get base speaker name
                        elif 'DFT' in pattern:
                            mic_number = match.group(1)
                            sampling_rate = match.group(2).replace('KHZ', '000').replace('HZ', '')
                            freq_range = f"{match.group(3)}-{match.group(4)}Hz"
                            spkr_name = match.group(5).split('_')[0]
                        elif 'CONTIGUOUS' in pattern:
                            mic_number = match.group(1)
                            spkr_name = match.group(2)
                            freq_range = match.group(3) + "Hz"
                        # 新增AUDIO_MIC模式解析逻辑
                        elif 'AUDIO_MIC' in pattern:
                            is_audio_mic_pattern = True
                            mic_number = match.group(1)
                            spkr_number = match.group(2)
                            # 构建频率范围（如300-5K2Hz）
                            freq_part = match.group(3)
                            freq_suffix = match.group(4)
                            freq_range = f"{freq_part}K{freq_suffix}Hz"
                            # 设置扬声器名称和麦克风名称
                            spkr_name = f"SPKR{spkr_number}"
                            # 为AUDIO_MIC模式设置默认采样率（如有需要可从其他位置获取）
                            sampling_rate = "48000"

                        mic_name = f"MIC{mic_number}"
                        break

                # Set default values if no pattern matched
                if not mic_name:
                    mic_name = "MIC1"
                    spkr_name = "SPKR1"
                    freq_range = "300-5200Hz"
                    sampling_rate = "44100"

                # Process frequency response abnormal information
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0

                    freq_info = []
                    for freq, value in freq_values:
                        if freq is not None:
                            freq_info.append(f"{freq}Hz: {value:.2f}dB" if language == 'zh'
                                             else f"{freq}Hz: {value:.2f}dB")

                    # 为AUDIO_MIC模式定制化描述
                    if is_audio_mic_pattern:
                        if language == 'zh':
                            level_spec_text = (f"{test_items[0]}: 密封性相关音频电平超出规格\n"
                                               f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，上限: {upper_limit:.1f} dB\n")
                        else:
                            level_spec_text = (f"{test_items[0]}: Seal-related audio level exceeds specification\n"
                                               f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, Upper limit: {upper_limit:.1f} dB\n")
                    else:
                        if language == 'zh':
                            level_spec_text = (f"{test_items[0]}: 麦克风灵敏度响应超出上限\n"
                                               f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，上限: {upper_limit:.1f} dB\n")
                        else:
                            level_spec_text = (f"{test_items[0]}: Microphone sensitivity response exceeds the upper limit\n"
                                               f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, Upper limit: {upper_limit:.1f} dB\n")
                    if freq_info:
                        level_spec_text += f"  {'频率点测量' if language == 'zh' else 'Frequency measurements'}: {', '.join(freq_info)}\n"

                # Process status abnormal information
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if is_audio_mic_pattern:  # AUDIO_MIC模式状态异常描述
                        if language == 'zh':
                            status_text = (f"{test_items[2]}: 密封性能测试状态异常\n"
                                           f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                        else:
                            status_text = (f"{test_items[2]}: Abnormal seal performance test status\n"
                                           f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")
                    else:  # 原有状态异常描述
                        if language == 'zh':
                            status_text = (f"{test_items[2]}: 采样数据状态异常\n"
                                           f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                        else:
                            status_text = (f"{test_items[2]}: Abnormal sampling data status\n"
                                           f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")

                # Comprehensive analysis
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if is_audio_mic_pattern:  # AUDIO_MIC模式综合分析
                        if language == 'zh':
                            comprehensive_text = f"- 所有测试项均失败，表明{mic_name}与{spkr_name}在{freq_range}下的密封性能不达标\n"
                        else:
                            comprehensive_text = f"- All test items failed, indicating that the seal performance of {mic_name} and {spkr_name} at {freq_range} is not up to standard\n"
                    else:  # 原有综合分析
                        if language == 'zh':
                            comprehensive_text = f"- 所有测试项均失败，表明{mic_name}与{spkr_name}在{freq_range}范围内的整体性能不达标\n"
                        else:
                            comprehensive_text = f"- All test items failed, indicating that the overall performance of {mic_name} and {spkr_name} in the {freq_range} range does not meet the standard\n"

                # Fill template with extracted variables
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=target_key,
                        problem_desc=f"{'音频采样测试失败' if language == 'zh' else 'Audio sampling test failed'}",
                        test_purpose=test_purpose,
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text,
                        mic_name=mic_name,
                        spkr_name=spkr_name,
                        freq_range=freq_range,
                        sampling_rate=sampling_rate
                    )
                    return report
                except KeyError as e:
                    return f"模板中存在未定义的变量: {str(e)}" if language == 'zh' else f"Undefined variable in template: {str(e)}"
                except Exception as e:
                    return f"生成报告时出错: {str(e)}" if language == 'zh' else f"Error generating report: {str(e)}"

            def analyze_mic_failure_reasons_suggestion3(self, structured_failed_logs_dict,
                                                        language='zh',
                                                        first_key=r'AUDIO_SAMPLE_MIC_\d+_(?:CONTIGUOUS|FFT|DFT)_(?:\d+K?HZ?_|)(?:\d+K?-\d+K?|\d+-\d+)_SPKR\d+[A-Z0-9_]*(?:_ASYNC_(?:START|WAIT))?.*FAILED'):
                """
                分析麦克风相关测试失败原因并提供建议，生成Markdown格式报告
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None

                # 编译正则表达式模式 - 匹配麦克风测试模式
                mic_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        # 使用正则表达式进行匹配
                        if mic_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "## 未找到AUDIO_SAMPLE_MIC相关的失败测试项"
                    return error_msg if language == 'zh' else "## No AUDIO_SAMPLE_MIC failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # 解析XML模板
                try:
                    # 根据操作系统设置基础路径
                    if os.name == 'posix':  # Linux/Mac系统
                        base_path = Path("/opt/xiejun4/pro_PathFinder")
                    else:  # Windows系统
                        base_path = Path(".")  # 保持当前目录为基础路径

                    xml_path = base_path / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 编译用于查找test_type的正则表达式
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None

                    # 遍历所有test_type元素，用正则匹配name属性
                    for elem in root.findall(".//test_type"):
                        name_attr = elem.get('name', '')
                        if test_type_pattern.search(name_attr):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"## 未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"## No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")

                    # 获取模板内容并替换变量格式
                    template_content = desc_elem.text.strip()
                    # 将{{variable}}格式转换为Python Template的${variable}格式
                    template_content = template_content.replace('{{', '${').replace('}}', '}')

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"## XML解析错误\n- {str(e)}" if language == 'zh' else f"## XML parsing error\n- {str(e)}"

                # 使用正则表达式从target_key提取变量
                # 匹配不同麦克风测试格式的模式
                # key_patterns = [
                #     # 新增带BLOCK的FFT/DFT格式: AUDIO_SAMPLE_MIC_1_DFT_8KHZ_300_5200_L2SPK1_BLOCK_equator_FAILED
                #     r'^AUDIO_SAMPLE_MIC_(\d+)_(FFT|DFT)_(\d+)KHZ_(\d+)_(\d+)_(L|R|M)\d+SPK(\d+)_BLOCK_[a-z]+',
                #     # 用于FFT格式: AUDIO_SAMPLE_MIC_1_FFT_44100_4K-16K_SPKR1_MILOS
                #     r'AUDIO_SAMPLE_MIC_(\d+)_FFT_(\d+)_([\dK-]+)_([A-Z0-9]+)',
                #     # 用于DFT格式: AUDIO_SAMPLE_MIC_2_DFT_8KHZ_200_5000_L2SPK2_MILOS
                #     r'AUDIO_SAMPLE_MIC_(\d+)_DFT_(\d+K?HZ?)_(\d+)_(\d+)_([A-Z0-9]+)',
                #     # 用于CONTIGUOUS格式: AUDIO_SAMPLE_MIC_1_CONTIGUOUS_SPKR1_300-5200
                #     r'AUDIO_SAMPLE_MIC_(\d+)_CONTIGUOUS_([A-Z0-9]+)_([\d-]+)',
                #     # 用于AUDIO_MIC格式: AUDIO_MIC1_SPKR1_300-5K2Hz_VS_SEAL_PORTO_FAILED
                #     r'AUDIO_MIC(\d+)_SPKR(\d+)_([\d-]+)K(\d+)Hz_VS_SEAL_([A-Z0-9_]+)'
                # ]
                def load_patterns_from_json(json_file='clean_filter_data_entity.json'):
                    """从JSON文件加载模式列表"""
                    try:
                        # 根据操作系统设置基础路径
                        if os.name == 'posix':  # Linux/Mac系统
                            json_path = Path(f"/opt/xiejun4/pro_PathFinder/config/{json_file}")
                        else:  # Windows系统
                            # Windows系统保持原有路径不变
                            current_dir = os.path.dirname(__file__)
                            parent_dir = os.path.dirname(current_dir)
                            json_path = os.path.join(parent_dir, f"config/{json_file}")

                        # 读取JSON文件内容
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # 提取BasicBandPatterns下的L2AR_BASIC_BAND模式列表
                        return data.get('Patterns', {}).get('GenericPatterns', {}).get('MIC_TEST_GROUP2', [])

                    except FileNotFoundError:
                        print(f"错误: 找不到文件 {json_path}")
                        return []
                    except json.JSONDecodeError:
                        print(f"错误: {json_path} 不是有效的JSON文件")
                        return []
                    except Exception as e:
                        print(f"加载模式时发生错误: {str(e)}")
                        return []

                key_patterns = load_patterns_from_json()

                mic_number = ""
                sampling_rate = ""
                freq_range = ""
                spkr_name = ""
                mic_name = ""
                # 新增AUDIO_MIC模式专用变量
                is_audio_mic_pattern = False
                # 新增BLOCK模式标识
                is_block_pattern = False

                for pattern in key_patterns:
                    match = re.search(pattern, target_key)
                    if match:
                        # 处理新增的带BLOCK的FFT/DFT模式
                        if 'BLOCK' in pattern:
                            is_block_pattern = True
                            mic_number = match.group(1)
                            signal_type = match.group(2)  # FFT或DFT
                            # 处理采样率 (如8KHZ -> 8000)
                            sampling_rate = f"{match.group(3)}000"
                            # 处理频率范围
                            freq_start = match.group(4)
                            freq_end = match.group(5)
                            freq_range = f"{freq_start}-{freq_end}Hz"
                            # 处理扬声器名称 (如L2SPK1)
                            channel = match.group(6)  # L/R/M
                            spkr_num = match.group(7)
                            spkr_name = f"{channel}SPK{spkr_num}"

                        elif 'FFT' in pattern:
                            mic_number = match.group(1)
                            sampling_rate = match.group(2)
                            freq_range = match.group(3).replace('K', 'K')  # 保留K符号
                            spkr_name = match.group(4).split('_')[0]  # 获取基础扬声器名称

                        elif 'DFT' in pattern:
                            mic_number = match.group(1)
                            sampling_rate = match.group(2).replace('KHZ', '000').replace('HZ', '')
                            freq_range = f"{match.group(3)}-{match.group(4)}Hz"
                            spkr_name = match.group(5).split('_')[0]

                        elif 'CONTIGUOUS' in pattern:
                            mic_number = match.group(1)
                            spkr_name = match.group(2)
                            freq_range = match.group(3) + "Hz"

                        # 处理AUDIO_MIC模式
                        elif 'AUDIO_MIC' in pattern:
                            is_audio_mic_pattern = True
                            mic_number = match.group(1)
                            spkr_number = match.group(2)
                            # 构建频率范围（如300-5K2Hz）
                            freq_part = match.group(3)
                            freq_suffix = match.group(4)
                            freq_range = f"{freq_part}K{freq_suffix}Hz"
                            # 设置扬声器名称和麦克风名称
                            spkr_name = f"SPKR{spkr_number}"
                            # 为AUDIO_MIC模式设置默认采样率
                            sampling_rate = "48000"

                        mic_name = f"MIC{mic_number}"
                        break

                # 如果没有匹配到模式，设置默认值
                if not mic_name:
                    mic_name = "MIC1"
                    spkr_name = "SPKR1"
                    freq_range = "300-5200Hz"
                    sampling_rate = "44100"

                # 处理频率响应异常信息（Markdown列表格式）
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0

                    # 频率测量值用列表展示
                    freq_info = []
                    for i, (freq, value) in enumerate(freq_values, 1):
                        if freq is not None:
                            freq_info.append(f"{i}. {freq}Hz: {value:.2f}dB")

                    # 为不同模式定制化描述
                    if is_audio_mic_pattern:
                        if language == 'zh':
                            level_spec_text = (f"### 密封性相关电平异常\n"
                                               f"- {test_items[0]}: 密封性相关音频电平超出规格\n"
                                               f"- 测量值范围: {min_value:.2f} 至 {max_value:.2f} dB\n"
                                               f"- 上限标准: {upper_limit:.1f} dB\n")
                        else:
                            level_spec_text = (f"### Seal-related Level Anomaly\n"
                                               f"- {test_items[0]}: Seal-related audio level exceeds specification\n"
                                               f"- Measured range: {min_value:.2f} to {max_value:.2f} dB\n"
                                               f"- Upper limit: {upper_limit:.1f} dB\n")
                    elif is_block_pattern:
                        if language == 'zh':
                            level_spec_text = (f"### 区块测试电平异常\n"
                                               f"- {test_items[0]}: 区块测试中音频电平超出规格\n"
                                               f"- 测量值范围: {min_value:.2f} 至 {max_value:.2f} dB\n"
                                               f"- 上限标准: {upper_limit:.1f} dB\n")
                        else:
                            level_spec_text = (f"### Block Test Level Anomaly\n"
                                               f"- {test_items[0]}: Audio level exceeds specification in block test\n"
                                               f"- Measured range: {min_value:.2f} to {max_value:.2f} dB\n"
                                               f"- Upper limit: {upper_limit:.1f} dB\n")
                    else:
                        if language == 'zh':
                            level_spec_text = (f"### 灵敏度响应异常\n"
                                               f"- {test_items[0]}: 麦克风灵敏度响应超出上限\n"
                                               f"- 测量值范围: {min_value:.2f} 至 {max_value:.2f} dB\n"
                                               f"- 上限标准: {upper_limit:.1f} dB\n")
                        else:
                            level_spec_text = (f"### Sensitivity Response Anomaly\n"
                                               f"- {test_items[0]}: Microphone sensitivity response exceeds the upper limit\n"
                                               f"- Measured range: {min_value:.2f} to {max_value:.2f} dB\n"
                                               f"- Upper limit: {upper_limit:.1f} dB\n")

                    if freq_info:
                        level_spec_text += f"- {'频率点测量值' if language == 'zh' else 'Frequency measurements'}:\n  " + "\n  ".join(
                            freq_info) + "\n"

                # 处理状态异常信息（Markdown格式）
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    # 为BLOCK模式定制状态异常描述
                    if is_block_pattern:
                        if language == 'zh':
                            status_text = (f"### 区块测试状态异常\n"
                                           f"- {test_items[2]}: 区块采样数据状态异常\n"
                                           f"- 状态值: {status_fails[0]['data']}\n"
                                           f"- 预期值: {status_fails[0]['lowlimit']}\n")
                        else:
                            status_text = (f"### Block Test Status Anomaly\n"
                                           f"- {test_items[2]}: Abnormal block sampling data status\n"
                                           f"- Status value: {status_fails[0]['data']}\n"
                                           f"- Expected value: {status_fails[0]['lowlimit']}\n")
                    # AUDIO_MIC模式状态异常描述
                    elif is_audio_mic_pattern:
                        if language == 'zh':
                            status_text = (f"### 密封性能状态异常\n"
                                           f"- {test_items[2]}: 密封性能测试状态异常\n"
                                           f"- 状态值: {status_fails[0]['data']}\n"
                                           f"- 预期值: {status_fails[0]['lowlimit']}\n")
                        else:
                            status_text = (f"### Seal Performance Status Anomaly\n"
                                           f"- {test_items[2]}: Abnormal seal performance test status\n"
                                           f"- Status value: {status_fails[0]['data']}\n"
                                           f"- Expected value: {status_fails[0]['lowlimit']}\n")
                    # 原有状态异常描述
                    else:
                        if language == 'zh':
                            status_text = (f"### 采样数据状态异常\n"
                                           f"- {test_items[2]}: 采样数据状态异常\n"
                                           f"- 状态值: {status_fails[0]['data']}\n"
                                           f"- 预期值: {status_fails[0]['lowlimit']}\n")
                        else:
                            status_text = (f"### Sampling Data Status Anomaly\n"
                                           f"- {test_items[2]}: Abnormal sampling data status\n"
                                           f"- Status value: {status_fails[0]['data']}\n"
                                           f"- Expected value: {status_fails[0]['lowlimit']}\n")

                # 综合分析（Markdown加粗重点）
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    # AUDIO_MIC模式综合分析
                    if is_audio_mic_pattern:
                        if language == 'zh':
                            comprehensive_text = (f"### 综合分析\n"
                                                  f"- 所有测试项均失败，表明**{mic_name}**与**{spkr_name}**在"
                                                  f"**{freq_range}**下的密封性能不达标\n")
                        else:
                            comprehensive_text = (f"### Comprehensive Analysis\n"
                                                  f"- All test items failed, indicating that the seal performance of "
                                                  f"**{mic_name}** and **{spkr_name}** at **{freq_range}** "
                                                  f"does not meet the standard\n")
                    # BLOCK模式综合分析
                    elif is_block_pattern:
                        if language == 'zh':
                            comprehensive_text = (f"### 综合分析\n"
                                                  f"- 所有测试项均失败，表明**{mic_name}**与**{spkr_name}**在"
                                                  f"**{freq_range}**频率范围内的区块测试性能不达标\n")
                        else:
                            comprehensive_text = (f"### Comprehensive Analysis\n"
                                                  f"- All test items failed, indicating that the block test performance of "
                                                  f"**{mic_name}** and **{spkr_name}** in the **{freq_range}** range "
                                                  f"does not meet the standard\n")
                    # 原有综合分析
                    else:
                        if language == 'zh':
                            comprehensive_text = (f"### 综合分析\n"
                                                  f"- 所有测试项均失败，表明**{mic_name}**与**{spkr_name}**在"
                                                  f"**{freq_range}**范围内的整体性能不达标\n")
                        else:
                            comprehensive_text = (f"### Comprehensive Analysis\n"
                                                  f"- All test items failed, indicating that the overall performance of "
                                                  f"**{mic_name}** and **{spkr_name}** in the **{freq_range}** range "
                                                  f"does not meet the standard\n")

                # 填充模板并生成最终Markdown报告
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=f"## {target_key}",
                        problem_desc=f"### {'音频采样测试失败' if language == 'zh' else 'Audio sampling test failed'}",
                        test_purpose=f"### {'测试目的' if language == 'zh' else 'Test Purpose'}\n{test_purpose}",
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text,
                        mic_name=mic_name,
                        spkr_name=spkr_name,
                        freq_range=freq_range,
                        sampling_rate=sampling_rate
                    )
                    return report
                except KeyError as e:
                    return f"## 模板变量错误\n- 未定义的变量: {str(e)}" if language == 'zh' else f"## Template Variable Error\n- Undefined variable: {str(e)}"
                except Exception as e:
                    return f"## 报告生成错误\n- {str(e)}" if language == 'zh' else f"## Report Generation Error\n- {str(e)}"

            def analyze_speaker_failure_reasons_suggestion(self, structured_failed_logs_dict,
                                                           language='zh',
                                                           first_key=r'^AUDIO_L2AR_ALERT_[A-Za-z]+\d?_\d+_(?:\d+K?Hz|\d+)_TO_\d+Hz_MIC[\w-]+(?:_[\w-]+)?(?:_ASYNC_(?:START|WAIT))?.*FAILED'):
                """
                分析AUDIO_SAMPLE_SPKR_1_CONTIGUOUS_MIC1_300-5200_FAILED的失败原因并提供建议
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_SPKR_后跟数字，然后是任意内容和FAILED
                speaker_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        # 使用正则表达式进行匹配
                        if speaker_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "未找到AUDIO_SAMPLE_SPKR_1相关的失败测试项"
                    return error_msg if language == 'zh' else "No AUDIO_SAMPLE_SPKR_1 failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # 解析XML模板
                try:
                    xml_path = Path(".") / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 编译用于查找test_type的正则表达式
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None

                    # 遍历所有test_type元素，使用正则表达式匹配name属性
                    for elem in root.findall(".//test_type"):
                        name_attr = elem.get('name', '')
                        if test_type_pattern.search(name_attr):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")

                    # 获取模板内容并替换变量格式
                    template_content = desc_elem.text.strip()
                    # 将{{变量名}}格式转换为${变量名}格式，适配Python Template
                    template_content = template_content.replace('{{', '${').replace('}}', '}')

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"XML解析错误: {str(e)}" if language == 'zh' else f"XML parsing error: {str(e)}"

                # 处理扬声器输出电平异常信息
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0
                    lower_limit = float(level_spec_fails[0]['lowlimit']) if level_spec_fails else 0

                    freq_info = []
                    for freq, value in freq_values:
                        if freq is not None:
                            freq_info.append(f"{freq}Hz: {value:.2f}dB" if language == 'zh'
                                             else f"{freq}Hz: {value:.2f}dB")

                    if language == 'zh':
                        level_spec_text = (f"{test_items[0]}: 扬声器输出电平超出规格范围\n"
                                           f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，"
                                           f"标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                    else:
                        level_spec_text = (f"{test_items[0]}: Speaker output level exceeds specification range\n"
                                           f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, "
                                           f"Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")
                    if freq_info:
                        level_spec_text += f"  {'频率点测量' if language == 'zh' else 'Frequency measurements'}: {', '.join(freq_info)}\n"

                # 处理扬声器状态异常信息
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if language == 'zh':
                        status_text = (f"{test_items[2]}: 扬声器驱动状态异常\n"
                                       f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                    else:
                        status_text = (f"{test_items[2]}: Abnormal speaker driver status\n"
                                       f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")

                # 综合分析
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if language == 'zh':
                        comprehensive_text = "- 所有测试项均失败，表明SPKR1与MIC1在300-5200Hz范围内的整体性能不达标\n"
                    else:
                        comprehensive_text = "- All test items failed, indicating that the overall performance of SPKR1 and MIC1 in the 300-5200Hz range does not meet the standard\n"

                # 填充模板
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=target_key,
                        problem_desc=f"{'音频输出测试失败' if language == 'zh' else 'Audio output test failed'}",
                        test_purpose=test_purpose,
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text
                    )
                    return report
                except KeyError as e:
                    return f"模板中存在未定义的变量: {str(e)}" if language == 'zh' else f"Undefined variable in template: {str(e)}"
                except Exception as e:
                    return f"生成报告时出错: {str(e)}" if language == 'zh' else f"Error generating report: {str(e)}"

            def analyze_speaker_failure_reasons_suggestion2(self, structured_failed_logs_dict,
                                                            language='zh',
                                                            first_key=r'^AUDIO_L2AR_ALERT_[A-Za-z0-9]+_\d+_(?:\d+K?Hz|\d+)_TO_\d+Hz_MIC[\w-]+(?:_[\w-]+)?(?:_ASYNC_(?:START|WAIT))?.*FAILED'):
                """
                分析音频测试失败原因并提供建议，支持动态提取传感器、麦克风和频率参数
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None
                speaker_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        if speaker_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "未找到AUDIO_L2AR_ALERT相关的失败测试项"
                    return error_msg if language == 'zh' else "No AUDIO_L2AR_ALERT failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # 从目标键中提取传感器、麦克风和频率信息
                # 正则模式：匹配ALERT_后的传感器名、高频、低频和MIC后的麦克风名
                sensor_freq_mic_pattern = re.compile(
                    r'^AUDIO_L2AR_ALERT_([A-Za-z0-9]+)_\d+_(\d+K?Hz|\d+)_TO_(\d+Hz)_MIC([\w-]+)',
                )
                match = sensor_freq_mic_pattern.search(target_key)

                # 初始化提取的变量，设置默认值
                sensor = "ALERT_UNKNOWN"
                high_freq = "unknown"
                low_freq = "unknown"
                mic = "MIC_UNKNOWN"

                if match:
                    # 提取传感器名称（如LEFT2 → ALERT_LEFT2）
                    sensor = f"ALERT_{match.group(1)}"

                    # 提取高频值（处理带Hz和不带Hz的情况）
                    high_freq_part = match.group(2)
                    high_freq = f"{high_freq_part}Hz" if not high_freq_part.endswith('Hz') else high_freq_part

                    # 提取低频值
                    low_freq = match.group(3)

                    # 提取麦克风名称（如1LEFT → MIC1LEFT）
                    mic = f"MIC{match.group(4)}"

                # 解析XML模板
                try:
                    # Set base path according to the operating system
                    if os.name == 'posix':  # Linux/Mac system
                        base_path = Path("/opt/xiejun4/pro_PathFinder")
                    else:  # Windows system
                        base_path = Path(".")  # Keep current directory as base

                    # Concatenate complete XML file path
                    xml_path = base_path / "docs" / "issue_suggestions.xml"
                    # xml_path = Path(".") / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 查找匹配的test_type元素
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None
                    for elem in root.findall(".//test_type"):
                        # 使用elem.get('name')完整匹配，避免部分匹配遗漏
                        if test_type_pattern.fullmatch(elem.get('name', '')):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")
                    template_content = desc_elem.text.strip()

                    # 模板变量替换：先转换{{}}为${}，再替换固定变量为动态变量
                    template_content = (template_content
                                        .replace('{{', '${')
                                        .replace('}}', '}')
                                        .replace('ALERT_LEFT2', '${sensor}')
                                        .replace('MIC1LEFT', '${mic}')
                                        .replace('1000Hz', '${low_freq}')
                                        .replace('7100Hz', '${high_freq}'))

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"XML解析错误: {str(e)}" if language == 'zh' else f"XML parsing error: {str(e)}"

                # 处理扬声器输出电平异常信息
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0
                    lower_limit = float(level_spec_fails[0]['lowlimit']) if level_spec_fails else 0

                    freq_info = []
                    for freq, value in freq_values:
                        if freq is not None:
                            freq_info.append(f"{freq}Hz: {value:.2f}dB" if language == 'zh'
                                             else f"{freq}Hz: {value:.2f}dB")

                    if language == 'zh':
                        level_spec_text = (f"{test_items[0]}: 扬声器输出电平超出规格范围\n"
                                           f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，"
                                           f"标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                    else:
                        level_spec_text = (f"{test_items[0]}: Speaker output level exceeds specification range\n"
                                           f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, "
                                           f"Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")
                    if freq_info:
                        level_spec_text += f"  {'频率点测量' if language == 'zh' else 'Frequency measurements'}: {', '.join(freq_info)}\n"

                # 处理扬声器状态异常信息
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if language == 'zh':
                        status_text = (f"{test_items[2]}: 扬声器驱动状态异常\n"
                                       f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                    else:
                        status_text = (f"{test_items[2]}: Abnormal speaker driver status\n"
                                       f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")

                # 综合分析
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if language == 'zh':
                        comprehensive_text = f"- 所有测试项均失败，表明{sensor}与{mic}在{low_freq}至{high_freq}范围内的整体性能不达标\n"
                    else:
                        comprehensive_text = f"- All test items failed, indicating that the overall performance of {sensor} and {mic} in the {low_freq} to {high_freq} range does not meet the standard\n"

                # 填充模板
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=target_key,
                        problem_desc=f"{'音频输出测试失败' if language == 'zh' else 'Audio output test failed'}",
                        test_purpose=test_purpose,
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text,
                        sensor=sensor,
                        mic=mic,
                        low_freq=low_freq,
                        high_freq=high_freq
                    )
                    return report
                except KeyError as e:
                    return f"模板中存在未定义的变量: {str(e)}" if language == 'zh' else f"Undefined variable in template: {str(e)}"
                except Exception as e:
                    return f"生成报告时出错: {str(e)}" if language == 'zh' else f"Error generating report: {str(e)}"

            def analyze_speaker_failure_reasons_suggestion3(self, structured_failed_logs_dict,
                                                            language='zh',
                                                            first_key=r'^AUDIO_L2AR_ALERT_[A-Za-z0-9]+_\d+_(?:\d+K?Hz|\d+)_TO_\d+Hz_MIC[\w-]+(?:_[\w-]+)?(?:_ASYNC_(?:START|WAIT))?.*FAILED'):
                """
                分析音频测试失败原因并提供建议，支持动态提取传感器、麦克风和频率参数
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None
                speaker_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        if speaker_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "未找到AUDIO_L2AR_ALERT相关的失败测试项"
                    return error_msg if language == 'zh' else "No AUDIO_L2AR_ALERT failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # Extract sensor, microphone and frequency information from the target key
                # Regular expression pattern list: contains multiple multiple patterns to match different formats of keys
                sensor_freq_mic_patterns = [
                    # Original pattern
                    re.compile(r'^AUDIO_L2AR_ALERT_([A-Za-z0-9]+)_\d+_(\d+K?Hz|\d+)_TO_(\d+Hz)_MIC([\w-]+)'),
                    # Added pattern 1
                    re.compile(
                        r'^AUDIO_L2AR_ALERT_([A-Za-z]+\d?)_\d+_(?:(\d+K?Hz|\d+))_TO_(\d+Hz)_MIC([\w-]+(?:_[\w-]+)?)(?:_ASYNC_(?:START|WAIT))?'),
                    # Added pattern 2
                    re.compile(
                        r'^AUDIO_L2AR_ALERT_([A-Za-z]+)_\d+_(\d+(?:KHz)?)\_TO\_(\d+(?:KHz)?)_MIC([\w_]+)(?:_ASYNC_(?:START|WAIT))?'),
                    # Added pattern 3
                    re.compile(
                        r'AUDIO_SAMPLE_MIC_(\d+)_FFT_(\d+)_([\dK-]+)_([\w]+)_.+_FAILED'
                    )
                ]

                # 尝试匹配所有模式
                match = None
                for pattern in sensor_freq_mic_patterns:
                    match = pattern.search(target_key)
                    if match:
                        break

                # 初始化提取的变量，设置默认值
                sensor = "ALERT_UNKNOWN"
                high_freq = "unknown"
                low_freq = "unknown"
                mic = "MIC_UNKNOWN"

                if match:
                    # 提取传感器名称（如LEFT2 → ALERT_LEFT2）
                    sensor = f"ALERT_{match.group(1)}"

                    # 提取高频值（处理带Hz和不带Hz的情况）
                    high_freq_part = match.group(2)
                    high_freq = f"{high_freq_part}Hz" if not high_freq_part.endswith(('Hz', 'KHz')) else high_freq_part

                    # 提取低频值
                    low_freq_part = match.group(3)
                    low_freq = f"{low_freq_part}Hz" if not low_freq_part.endswith(('Hz', 'KHz')) else low_freq_part

                    # 提取麦克风名称（如1LEFT → MIC1LEFT）
                    mic = f"MIC{match.group(4)}"

                # 解析XML模板
                try:
                    # Set base path according to the operating system
                    if os.name == 'posix':  # Linux/Mac system
                        base_path = Path("/opt/xiejun4/pro_PathFinder")
                    else:  # Windows system
                        base_path = Path(".")  # Keep current directory as base

                    # Concatenate complete XML file path
                    xml_path = base_path / "docs" / "issue_suggestions.xml"
                    # xml_path = Path(".") / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 查找匹配的test_type元素
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None
                    for elem in root.findall(".//test_type"):
                        # 使用elem.get('name')完整匹配，避免部分匹配遗漏
                        if test_type_pattern.fullmatch(elem.get('name', '')):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")
                    template_content = desc_elem.text.strip()

                    # 模板变量替换：先转换{{}}为${}，再替换固定变量为动态变量
                    template_content = (template_content
                                        .replace('{{', '${')
                                        .replace('}}', '}')
                                        .replace('ALERT_LEFT2', '${sensor}')
                                        .replace('MIC1LEFT', '${mic}')
                                        .replace('1000Hz', '${low_freq}')
                                        .replace('7100Hz', '${high_freq}'))

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"XML解析错误: {str(e)}" if language == 'zh' else f"XML parsing error: {str(e)}"

                # 处理扬声器输出电平异常信息
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0
                    lower_limit = float(level_spec_fails[0]['lowlimit']) if level_spec_fails else 0

                    freq_info = []
                    for freq, value in freq_values:
                        if freq is not None:
                            freq_info.append(f"{freq}Hz: {value:.2f}dB" if language == 'zh'
                                             else f"{freq}Hz: {value:.2f}dB")

                    if language == 'zh':
                        level_spec_text = (f"{test_items[0]}: 扬声器输出电平超出规格范围\n"
                                           f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，"
                                           f"标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                    else:
                        level_spec_text = (f"{test_items[0]}: Speaker output level exceeds specification range\n"
                                           f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, "
                                           f"Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")
                    if freq_info:
                        level_spec_text += f"  {'频率点测量' if language == 'zh' else 'Frequency measurements'}: {', '.join(freq_info)}\n"

                # 处理扬声器状态异常信息
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if language == 'zh':
                        status_text = (f"{test_items[2]}: 扬声器驱动状态异常\n"
                                       f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                    else:
                        status_text = (f"{test_items[2]}: Abnormal speaker driver status\n"
                                       f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")

                # 综合分析
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if language == 'zh':
                        comprehensive_text = f"- 所有测试项均失败，表明{sensor}与{mic}在{low_freq}至{high_freq}范围内的整体性能不达标\n"
                    else:
                        comprehensive_text = f"- All test items failed, indicating that the overall performance of {sensor} and {mic} in the {low_freq} to {high_freq} range does not meet the standard\n"

                # 填充模板
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=target_key,
                        problem_desc=f"{'音频输出测试失败' if language == 'zh' else 'Audio output test failed'}",
                        test_purpose=test_purpose,
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text,
                        sensor=sensor,
                        mic=mic,
                        low_freq=low_freq,
                        high_freq=high_freq
                    )
                    return report
                except KeyError as e:
                    return f"模板中存在未定义的变量: {str(e)}" if language == 'zh' else f"Undefined variable in template: {str(e)}"
                except Exception as e:
                    return f"生成报告时出错: {str(e)}" if language == 'zh' else f"Error generating report: {str(e)}"

            def analyze_speaker_failure_reasons_suggestion4(self, structured_failed_logs_dict,
                                                            language='zh',
                                                            first_key=r'^AUDIO_L2AR_ALERT_[A-Za-z0-9]+_\d+_(?:\d+K?Hz|\d+)_TO_\d+Hz_MIC[\w-]+(?:_[\w-]+)?(?:_ASYNC_(?:START|WAIT))?.*FAILED'):
                """
                分析音频测试失败原因并提供建议，支持动态提取传感器、麦克风和频率参数，生成Markdown格式报告
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None
                speaker_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        if speaker_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "## 未找到AUDIO_L2AR_ALERT相关的失败测试项"
                    return error_msg if language == 'zh' else "## No AUDIO_L2AR_ALERT failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # 提取传感器、麦克风和频率信息
                # sensor_freq_mic_patterns = [
                #     re.compile(r'^AUDIO_L2AR_ALERT_([A-Za-z0-9]+)_\d+_(\d+K?Hz|\d+)_TO_(\d+Hz)_MIC([\w-]+)'),
                #     re.compile(r'^AUDIO_L2AR_ALERT_([A-Za-z]+\d?)_\d+_(?:(\d+K?Hz|\d+))_TO_(\d+Hz)_MIC([\w-]+(?:_[\w-]+)?)(?:_ASYNC_(?:START|WAIT))?'),
                #     re.compile(r'^AUDIO_L2AR_ALERT_([A-Za-z]+)_\d+_(\d+(?:KHz)?)\_TO\_(\d+(?:KHz)?)_MIC([\w_]+)(?:_ASYNC_(?:START|WAIT))?'),
                #     re.compile(r'AUDIO_SAMPLE_MIC_(\d+)_FFT_(\d+)_([\dK-]+)_([\w]+)_.+_FAILED')
                # ]
                def load_patterns_from_json(json_file='clean_filter_data_entity.json'):
                    """从JSON文件加载模式列表"""
                    try:
                        # 根据操作系统设置基础路径
                        if os.name == 'posix':  # Linux/Mac系统
                            json_path = Path(f"/opt/xiejun4/pro_PathFinder/config/{json_file}")
                        else:  # Windows系统
                            # Windows系统保持原有路径不变
                            current_dir = os.path.dirname(__file__)
                            parent_dir = os.path.dirname(current_dir)
                            json_path = os.path.join(parent_dir, f"config/{json_file}")

                        # 读取JSON文件内容
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # 提取BasicBandPatterns下的L2AR_BASIC_BAND模式列表
                        return data.get('Patterns', {}).get('GenericPatterns', {}).get('SPEAKER_TEST_GROUP2', [])

                    except FileNotFoundError:
                        print(f"错误: 找不到文件 {json_path}")
                        return []
                    except json.JSONDecodeError:
                        print(f"错误: {json_path} 不是有效的JSON文件")
                        return []
                    except Exception as e:
                        print(f"加载模式时发生错误: {str(e)}")
                        return []

                sensor_freq_mic_patterns = load_patterns_from_json()

                # 尝试匹配所有模式
                match = None
                for pattern in sensor_freq_mic_patterns:
                    match = re.search(pattern, target_key)
                    if match:
                        break

                # 初始化提取的变量
                sensor = "ALERT_UNKNOWN"
                high_freq = "unknown"
                low_freq = "unknown"
                mic = "MIC_UNKNOWN"

                if match:
                    sensor = f"ALERT_{match.group(1)}"

                    high_freq_part = match.group(2)
                    high_freq = f"{high_freq_part}Hz" if not high_freq_part.endswith(('Hz', 'KHz')) else high_freq_part

                    low_freq_part = match.group(3)
                    low_freq = f"{low_freq_part}Hz" if not low_freq_part.endswith(('Hz', 'KHz')) else low_freq_part

                    mic = f"MIC{match.group(4)}"

                # 解析XML模板
                try:
                    # 设置基础路径
                    if os.name == 'posix':  # Linux/Mac系统
                        base_path = Path("/opt/xiejun4/pro_PathFinder")
                    else:  # Windows系统
                        base_path = Path(".")

                    xml_path = base_path / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 查找匹配的test_type元素
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None
                    for elem in root.findall(".//test_type"):
                        if test_type_pattern.fullmatch(elem.get('name', '')):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"## 未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"## No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")
                    template_content = desc_elem.text.strip()

                    # 模板变量替换（确保符合Markdown格式）
                    template_content = (template_content
                                        .replace('{{', '${')
                                        .replace('}}', '}')
                                        .replace('ALERT_LEFT2', '**${sensor}**')
                                        .replace('MIC1LEFT', '**${mic}**')
                                        .replace('1000Hz', '**${low_freq}**')
                                        .replace('7100Hz', '**${high_freq}**'))

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"## XML解析错误\n- {str(e)}" if language == 'zh' else f"## XML parsing error\n- {str(e)}"

                # 处理扬声器输出电平异常信息（Markdown列表格式）
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0
                    lower_limit = float(level_spec_fails[0]['lowlimit']) if level_spec_fails else 0

                    # 频率测量值用列表展示
                    freq_info = []
                    for i, (freq, value) in enumerate(freq_values, 1):
                        if freq is not None:
                            freq_info.append(f"{i}. {freq}Hz: {value:.2f}dB")

                    if language == 'zh':
                        level_spec_text = (f"### 输出电平异常\n"
                                           f"- {test_items[0]}: 扬声器输出电平超出规格范围\n"
                                           f"- 测量值范围: {min_value:.2f} 至 {max_value:.2f} dB\n"
                                           f"- 标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                    else:
                        level_spec_text = (f"### Output Level Anomaly\n"
                                           f"- {test_items[0]}: Speaker output level exceeds specification range\n"
                                           f"- Measured range: {min_value:.2f} to {max_value:.2f} dB\n"
                                           f"- Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")

                    if freq_info:
                        level_spec_text += f"- {'频率点测量值' if language == 'zh' else 'Frequency measurements'}:\n  " + "\n  ".join(
                            freq_info) + "\n"

                # 处理扬声器状态异常信息（Markdown格式）
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if language == 'zh':
                        status_text = (f"### 驱动状态异常\n"
                                       f"- {test_items[2]}: 扬声器驱动状态异常\n"
                                       f"- 状态值: {status_fails[0]['data']}\n"
                                       f"- 预期值: {status_fails[0]['lowlimit']}\n")
                    else:
                        status_text = (f"### Driver Status Anomaly\n"
                                       f"- {test_items[2]}: Abnormal speaker driver status\n"
                                       f"- Status value: {status_fails[0]['data']}\n"
                                       f"- Expected value: {status_fails[0]['lowlimit']}\n")

                # 综合分析（Markdown加粗重点）
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if language == 'zh':
                        comprehensive_text = (f"### 综合分析\n"
                                              f"- 所有测试项均失败，表明**{sensor}**与**{mic}**在"
                                              f"**{low_freq}至{high_freq}**范围内的整体性能不达标\n")
                    else:
                        comprehensive_text = (f"### Comprehensive Analysis\n"
                                              f"- All test items failed, indicating that the overall performance of "
                                              f"**{sensor}** and **{mic}** in the **{low_freq} to {high_freq}** range "
                                              f"does not meet the standard\n")

                # 填充模板并生成最终Markdown报告
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=f"## {target_key}",
                        problem_desc=f"### {'音频输出测试失败' if language == 'zh' else 'Audio output test failed'}",
                        test_purpose=f"### {'测试目的' if language == 'zh' else 'Test Purpose'}\n{test_purpose}",
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text,
                        sensor=sensor,
                        mic=mic,
                        low_freq=low_freq,
                        high_freq=high_freq
                    )
                    return report
                except KeyError as e:
                    return f"## 模板变量错误\n- 未定义的变量: {str(e)}" if language == 'zh' else f"## Template Variable Error\n- Undefined variable: {str(e)}"
                except Exception as e:
                    return f"## 报告生成错误\n- {str(e)}" if language == 'zh' else f"## Report Generation Error\n- {str(e)}"

            def analyze_ear_failure_reasons_suggestion(self, structured_failed_logs_dict,
                                                       language='zh',
                                                       first_key=r'^AUDIO_L2AR_EAR_\d+_\d+Hz_TO_\d+Hz_MIC1(?:_KANSA(?:_ASYNC_(?:START|WAIT))?)?.*FAILED'):
                """
                分析AUDIO_SAMPLE_EAR_1_CONTIGUOUS_MIC1_300-5200_FAILED的失败原因并提供建议
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_EAR_后跟数字，然后是任意内容和FAILED
                ear_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        # 使用正则表达式进行匹配
                        if ear_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "未找到AUDIO_SAMPLE_EAR_1相关的失败测试项"
                    return error_msg if language == 'zh' else "No AUDIO_SAMPLE_EAR_1 failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # 解析XML模板
                try:
                    xml_path = Path(".") / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 编译用于查找test_type的正则表达式
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None

                    # 遍历所有test_type元素，使用正则表达式匹配name属性
                    for elem in root.findall(".//test_type"):
                        name_attr = elem.get('name', '')
                        if test_type_pattern.search(name_attr):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")

                    # 获取模板内容并替换变量格式
                    template_content = desc_elem.text.strip()
                    # 将{{变量名}}格式转换为${变量名}格式，适配Python Template
                    template_content = template_content.replace('{{', '${').replace('}}', '}')

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"XML解析错误: {str(e)}" if language == 'zh' else f"XML parsing error: {str(e)}"

                # 处理EAR输出电平异常信息
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0
                    lower_limit = float(level_spec_fails[0]['lowlimit']) if level_spec_fails else 0

                    freq_info = []
                    for freq, value in freq_values:
                        if freq is not None:
                            freq_info.append(f"{freq}Hz: {value:.2f}dB" if language == 'zh'
                                             else f"{freq}Hz: {value:.2f}dB")

                    if language == 'zh':
                        level_spec_text = (f"{test_items[0]}: 耳机输出电平超出规格范围\n"
                                           f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，"
                                           f"标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                    else:
                        level_spec_text = (f"{test_items[0]}: Earphone output level exceeds specification range\n"
                                           f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, "
                                           f"Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")
                    if freq_info:
                        level_spec_text += f"  {'频率点测量' if language == 'zh' else 'Frequency measurements'}: {', '.join(freq_info)}\n"

                # 处理EAR状态异常信息
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if language == 'zh':
                        status_text = (f"{test_items[2]}: 耳机驱动状态异常\n"
                                       f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                    else:
                        status_text = (f"{test_items[2]}: Abnormal earphone driver status\n"
                                       f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")

                # 综合分析
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if language == 'zh':
                        comprehensive_text = "- 所有测试项均失败，表明EAR1与MIC1在300-5200Hz范围内的整体性能不达标\n"
                    else:
                        comprehensive_text = "- All test items failed, indicating that the overall performance of EAR1 and MIC1 in the 300-5200Hz range does not meet the standard\n"

                # 填充模板
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=target_key,
                        problem_desc=f"{'耳机音频输出测试失败' if language == 'zh' else 'Earphone audio output test failed'}",
                        test_purpose=test_purpose,
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text
                    )
                    return report
                except KeyError as e:
                    return f"模板中存在未定义的变量: {str(e)}" if language == 'zh' else f"Undefined variable in template: {str(e)}"
                except Exception as e:
                    return f"生成报告时出错: {str(e)}" if language == 'zh' else f"Error generating report: {str(e)}"

            def analyze_ear_failure_reasons_suggestion2(self, structured_failed_logs_dict,
                                                        language='zh',
                                                        first_key=r'^AUDIO_L2AR_EAR_\d+_\d+Hz_TO_\d+Hz_MIC1(?:_KANSA(?:_ASYNC_(?:START|WAIT))?)?.*FAILED'):
                """
                Analyze failure reasons and provide suggestions for AUDIO_SAMPLE_EAR_1_CONTIGUOUS_MIC1_300-5200_FAILED
                """
                # Dynamically find target test item key
                target_key = None
                target_entry = None

                # Compile regex pattern - match AUDIO_SAMPLE_EAR_ followed by numbers, then any content and FAILED
                ear_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        # Use regex for matching
                        if ear_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "未找到AUDIO_SAMPLE_EAR_1相关的失败测试项"
                    return error_msg if language == 'zh' else "No AUDIO_SAMPLE_EAR_1 failure test item found"

                # Extract test data and purpose
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # Analyze data items
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # Parse XML template
                try:
                    # Set base path according to the operating system
                    if os.name == 'posix':  # Linux/Mac system
                        base_path = Path("/opt/xiejun4/pro_PathFinder")
                    else:  # Windows system
                        base_path = Path(".")  # Keep current directory as base

                    xml_path = base_path / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # Compile regex for finding test_type
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None

                    # Iterate through all test_type elements, match name attribute with regex
                    for elem in root.findall(".//test_type"):
                        name_attr = elem.get('name', '')
                        if test_type_pattern.search(name_attr):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")

                    # Get template content and replace variable format
                    template_content = desc_elem.text.strip()
                    # Convert {{variable}} format to ${variable} format for Python Template
                    template_content = template_content.replace('{{', '${').replace('}}', '}')

                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"XML解析错误: {str(e)}" if language == 'zh' else f"XML parsing error: {str(e)}"

                # Extract variables from target_key using regex
                # Pattern: AUDIO_L2AR_EAR_<number>_<low>Hz_TO_<high>Hz_<mic>
                key_pattern = r'AUDIO_L2AR_EAR_\d+_(\d+)Hz_TO_(\d+)Hz_([A-Z0-9_]+)'
                match = re.search(key_pattern, target_key)

                if match:
                    low_freq = match.group(1) + "Hz"
                    high_freq = match.group(2) + "Hz"
                    mic_name = match.group(3).split('_')[0]  # Get base MIC name without suffixes

                    # If MIC name contains LEFT/RIGHT or other suffixes, extract full name
                    if any(suffix in match.group(3) for suffix in ['LEFT', 'RIGHT']):
                        mic_name = match.group(3).split('_KANSA')[0]
                else:
                    # Default values if pattern doesn't match
                    low_freq = "140Hz"
                    high_freq = "7100Hz"
                    mic_name = "MIC1"

                # Process EAR output level abnormal information
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0
                    lower_limit = float(level_spec_fails[0]['lowlimit']) if level_spec_fails else 0

                    freq_info = []
                    for freq, value in freq_values:
                        if freq is not None:
                            freq_info.append(f"{freq}Hz: {value:.2f}dB" if language == 'zh'
                                             else f"{freq}Hz: {value:.2f}dB")

                    if language == 'zh':
                        level_spec_text = (f"{test_items[0]}: 耳机输出电平超出规格范围\n"
                                           f"  测量值范围: {min_value:.2f} 至 {max_value:.2f} dB，"
                                           f"标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                    else:
                        level_spec_text = (f"{test_items[0]}: Earphone output level exceeds specification range\n"
                                           f"  Measured values: {min_value:.2f} to {max_value:.2f} dB, "
                                           f"Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")
                    if freq_info:
                        level_spec_text += f"  {'频率点测量' if language == 'zh' else 'Frequency measurements'}: {', '.join(freq_info)}\n"

                # Process EAR status abnormal information
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    if language == 'zh':
                        status_text = (f"{test_items[2]}: 耳机驱动状态异常\n"
                                       f"  状态值: {status_fails[0]['data']}，预期: {status_fails[0]['lowlimit']}\n")
                    else:
                        status_text = (f"{test_items[2]}: Abnormal earphone driver status\n"
                                       f"  Status value: {status_fails[0]['data']}, Expected: {status_fails[0]['lowlimit']}\n")

                # Comprehensive analysis
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if language == 'zh':
                        comprehensive_text = f"- 所有测试项均失败，表明EAR与{mic_name}在{low_freq}至{high_freq}范围内的整体性能不达标\n"
                    else:
                        comprehensive_text = f"- All test items failed, indicating that the overall performance of EAR and {mic_name} in the {low_freq} to {high_freq} range does not meet the standard\n"

                # Fill template with extracted variables
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=target_key,
                        problem_desc=f"{'耳机音频输出测试失败' if language == 'zh' else 'Earphone audio output test failed'}",
                        test_purpose=test_purpose,
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text,
                        mic_name=mic_name,
                        low_freq=low_freq,
                        high_freq=high_freq
                    )
                    return report
                except KeyError as e:
                    return f"模板中存在未定义的变量: {str(e)}" if language == 'zh' else f"Undefined variable in template: {str(e)}"
                except Exception as e:
                    return f"生成报告时出错: {str(e)}" if language == 'zh' else f"Error generating report: {str(e)}"

            def analyze_ear_failure_reasons_suggestion3(self, structured_failed_logs_dict,
                                                        language='zh',
                                                        first_key=r'^AUDIO_L2AR_EAR_\d+_\d+Hz_TO_\d+Hz_MIC1(?:_KANSA(?:_ASYNC_(?:START|WAIT))?)?.*FAILED'):
                """
                分析耳机相关测试失败原因并提供建议，生成Markdown格式报告
                """
                # 动态查找目标测试项键
                target_key = None
                target_entry = None

                # 编译正则表达式模式 - 匹配耳机测试模式
                ear_failed_pattern = re.compile(first_key)

                for pattern_key, pattern_value in structured_failed_logs_dict.items():
                    for test_key, test_value in pattern_value.items():
                        # 使用正则表达式进行匹配
                        if ear_failed_pattern.search(test_key):
                            target_key = test_key
                            target_entry = test_value
                            break
                    if target_entry:
                        break

                if not target_entry:
                    error_msg = "## 未找到AUDIO_SAMPLE_EAR_1相关的失败测试项"
                    return error_msg if language == 'zh' else "## No AUDIO_SAMPLE_EAR_1 failure test item found"

                # 提取测试数据和目的
                data_items = target_entry.get('data_items', [])
                purpose2items = target_entry.get('purpose2items', {})

                test_purpose = purpose2items.get(f'test_purpose_{language}',
                                                 '未知测试目的' if language == 'zh' else 'Unknown test purpose')
                test_items = purpose2items.get(f'test_items_{language}', [])

                # 分析数据项
                failed_items = [item for item in data_items if item.get('state') == '* FAILED *']

                # 解析XML模板
                try:
                    # 根据操作系统设置基础路径
                    if os.name == 'posix':  # Linux/Mac系统
                        base_path = Path("/opt/xiejun4/pro_PathFinder")
                    else:  # Windows系统
                        base_path = Path(".")  # 保持当前目录为基础路径

                    xml_path = base_path / "docs" / "issue_suggestions.xml"
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # 编译用于查找test_type的正则表达式
                    test_type_pattern = re.compile(first_key)
                    test_type_elem = None

                    # 遍历所有test_type元素，用正则匹配name属性
                    for elem in root.findall(".//test_type"):
                        name_attr = elem.get('name', '')
                        if test_type_pattern.search(name_attr):
                            test_type_elem = elem
                            break

                    if not test_type_elem:
                        return f"## 未找到匹配的test_type元素: {first_key}" if language == 'zh' else f"## No matching test_type element found: {first_key}"

                    desc_elem = test_type_elem.find(f".//description[@language='{language}']")

                    # 获取模板内容并替换变量格式
                    template_content = desc_elem.text.strip()
                    # 将{{variable}}格式转换为Python Template的${variable}格式
                    template_content = template_content.replace('{{', '${').replace('}}', '}')
                except (ET.ParseError, FileNotFoundError, AttributeError) as e:
                    return f"## XML解析错误\n- {str(e)}" if language == 'zh' else f"## XML parsing error\n- {str(e)}"

                # 使用正则表达式从target_key提取变量
                # 模式: AUDIO_L2AR_EAR_<number>_<low>Hz_TO_<high>Hz_<mic>
                # key_patterns = r'AUDIO_L2AR_EAR_\d+_(\d+)Hz_TO_(\d+)Hz_([A-Z0-9_]+)'
                def load_patterns_from_json(json_file='clean_filter_data_entity.json'):
                    """从JSON文件加载模式列表"""
                    try:
                        # 根据操作系统设置基础路径
                        if os.name == 'posix':  # Linux/Mac系统
                            json_path = Path(f"/opt/xiejun4/pro_PathFinder/config/{json_file}")
                        else:  # Windows系统
                            # Windows系统保持原有路径不变
                            current_dir = os.path.dirname(__file__)
                            parent_dir = os.path.dirname(current_dir)
                            json_path = os.path.join(parent_dir, f"config/{json_file}")

                        # 读取JSON文件内容
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # 提取BasicBandPatterns下的L2AR_BASIC_BAND模式列表
                        return data.get('Patterns', {}).get('GenericPatterns', {}).get('EAR_TEST_GROUP2', [])

                    except FileNotFoundError:
                        print(f"错误: 找不到文件 {json_path}")
                        return []
                    except json.JSONDecodeError:
                        print(f"错误: {json_path} 不是有效的JSON文件")
                        return []
                    except Exception as e:
                        print(f"加载模式时发生错误: {str(e)}")
                        return []

                key_patterns = load_patterns_from_json()

                # 尝试匹配所有模式
                match = None
                for pattern in key_patterns:
                    match = re.search(pattern, target_key)
                    if match:
                        break

                # 初始化变量
                low_freq = ""
                high_freq = ""
                mic_name = ""
                is_l2ar_pattern = False  # 标识是否匹配L2AR模式

                if match:
                    is_l2ar_pattern = True
                    # 提取频率范围（注意原正则分组索引调整）
                    # 从示例'AUDIO_L2AR_EAR_10000_8KHz_TO_140Hz_MIC1_PORTO_EQ'解析：
                    # group1: 10000（额外参数）
                    # group2: 8KHz（高频）
                    # group3: 140Hz（低频）
                    # group4: 1（麦克风编号）
                    # group5: PORTO_EQ（后缀）

                    # 修正频率范围提取逻辑（根据示例调整高低频对应关系）
                    high_freq = match.group(2)  # 8KHz
                    low_freq = match.group(3)  # 140Hz

                    # 构建麦克风名称
                    mic_number = match.group(4)
                    mic_name = f"MIC{mic_number}"

                    # 处理可能的特殊后缀（如果需要）
                    suffix = match.group(5)
                    if suffix:
                        mic_name += f"_{suffix}"
                else:
                    # 模式不匹配时使用默认值
                    low_freq = "140Hz"
                    high_freq = "7100Hz"
                    mic_name = "MIC1"

                # 处理耳机输出电平异常信息（Markdown列表格式）
                level_spec_fails = [item for item in failed_items if 'LEVEL_SPEC' in item['Item']]
                level_spec_text = ""
                if level_spec_fails:
                    freq_values = []
                    for item in level_spec_fails:
                        freq_part = item['Item'].split('_')[-1]
                        try:
                            freq_hz = int(freq_part)
                            freq_values.append((freq_hz, float(item['data'])))
                        except ValueError:
                            freq_values.append((None, float(item['data'])))

                    freq_values.sort(key=lambda x: x[0] if x[0] is not None else 0)
                    values = [v for _, v in freq_values]
                    min_value = min(values) if values else 0
                    max_value = max(values) if values else 0
                    upper_limit = float(level_spec_fails[0]['uplimit']) if level_spec_fails else 0
                    lower_limit = float(level_spec_fails[0]['lowlimit']) if level_spec_fails else 0

                    # 频率测量值用列表展示
                    freq_info = []
                    for i, (freq, value) in enumerate(freq_values, 1):
                        if freq is not None:
                            freq_info.append(f"{i}. {freq}Hz: {value:.2f}dB")

                    # 为L2AR模式定制描述
                    if is_l2ar_pattern:
                        if language == 'zh':
                            level_spec_text = (f"### 输出电平异常\n"
                                               f"- {test_items[0]}: L2AR耳机输出电平超出规格范围\n"
                                               f"- 测量值范围: {min_value:.2f} 至 {max_value:.2f} dB\n"
                                               f"- 标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                        else:
                            level_spec_text = (f"### Output Level Anomaly\n"
                                               f"- {test_items[0]}: L2AR earphone output level exceeds specification range\n"
                                               f"- Measured range: {min_value:.2f} to {max_value:.2f} dB\n"
                                               f"- Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")
                    else:
                        if language == 'zh':
                            level_spec_text = (f"### 输出电平异常\n"
                                               f"- {test_items[0]}: 耳机输出电平超出规格范围\n"
                                               f"- 测量值范围: {min_value:.2f} 至 {max_value:.2f} dB\n"
                                               f"- 标准范围: {lower_limit:.1f} 至 {upper_limit:.1f} dB\n")
                        else:
                            level_spec_text = (f"### Output Level Anomaly\n"
                                               f"- {test_items[0]}: Earphone output level exceeds specification range\n"
                                               f"- Measured range: {min_value:.2f} to {max_value:.2f} dB\n"
                                               f"- Specification range: {lower_limit:.1f} to {upper_limit:.1f} dB\n")

                    if freq_info:
                        level_spec_text += f"- {'频率点测量值' if language == 'zh' else 'Frequency measurements'}:\n  " + "\n  ".join(
                            freq_info) + "\n"

                # 处理耳机状态异常信息（Markdown格式）
                status_fails = [item for item in failed_items if 'STATUS' in item['Item']]
                status_text = ""
                if status_fails:
                    # 为L2AR模式定制状态描述
                    if is_l2ar_pattern:
                        if language == 'zh':
                            status_text = (f"### 驱动状态异常\n"
                                           f"- {test_items[2]}: L2AR耳机驱动状态异常\n"
                                           f"- 状态值: {status_fails[0]['data']}\n"
                                           f"- 预期值: {status_fails[0]['lowlimit']}\n")
                        else:
                            status_text = (f"### Driver Status Anomaly\n"
                                           f"- {test_items[2]}: Abnormal L2AR earphone driver status\n"
                                           f"- Status value: {status_fails[0]['data']}\n"
                                           f"- Expected value: {status_fails[0]['lowlimit']}\n")
                    else:
                        if language == 'zh':
                            status_text = (f"### 驱动状态异常\n"
                                           f"- {test_items[2]}: 耳机驱动状态异常\n"
                                           f"- 状态值: {status_fails[0]['data']}\n"
                                           f"- 预期值: {status_fails[0]['lowlimit']}\n")
                        else:
                            status_text = (f"### Driver Status Anomaly\n"
                                           f"- {test_items[2]}: Abnormal earphone driver status\n"
                                           f"- Status value: {status_fails[0]['data']}\n"
                                           f"- Expected value: {status_fails[0]['lowlimit']}\n")

                # 综合分析（Markdown加粗重点）
                comprehensive_text = ""
                if len(failed_items) == len(data_items):
                    if is_l2ar_pattern:
                        if language == 'zh':
                            comprehensive_text = (f"### 综合分析\n"
                                                  f"- 所有测试项均失败，表明**L2AR EAR**与**{mic_name}**在"
                                                  f"**{low_freq}至{high_freq}**范围内的整体性能不达标\n")
                        else:
                            comprehensive_text = (f"### Comprehensive Analysis\n"
                                                  f"- All test items failed, indicating that the overall performance of "
                                                  f"**L2AR EAR** and **{mic_name}** in the **{low_freq} to {high_freq}** range "
                                                  f"does not meet the standard\n")
                    else:
                        if language == 'zh':
                            comprehensive_text = (f"### 综合分析\n"
                                                  f"- 所有测试项均失败，表明**EAR**与**{mic_name}**在"
                                                  f"**{low_freq}至{high_freq}**范围内的整体性能不达标\n")
                        else:
                            comprehensive_text = (f"### Comprehensive Analysis\n"
                                                  f"- All test items failed, indicating that the overall performance of "
                                                  f"**EAR** and **{mic_name}** in the **{low_freq} to {high_freq}** range "
                                                  f"does not meet the standard\n")

                # 填充模板并生成最终Markdown报告
                try:
                    template = Template(template_content)
                    report = template.substitute(
                        test_item_desc=f"## {target_key}",
                        problem_desc=f"### {'L2AR耳机音频输出测试失败' if is_l2ar_pattern else '耳机音频输出测试失败' if language == 'zh' else 'L2AR earphone audio output test failed' if is_l2ar_pattern else 'Earphone audio output test failed'}",
                        test_purpose=f"### {'测试目的' if language == 'zh' else 'Test Purpose'}\n{test_purpose}",
                        level_spec_fails=level_spec_text,
                        status_fails=status_text,
                        comprehensive_analysis=comprehensive_text,
                        mic_name=mic_name,
                        low_freq=low_freq,
                        high_freq=high_freq
                    )
                    return report
                except KeyError as e:
                    return f"## 模板变量错误\n- 未定义的变量: {str(e)}" if language == 'zh' else f"## Template Variable Error\n- Undefined variable: {str(e)}"
                except Exception as e:
                    return f"## 报告生成错误\n- {str(e)}" if language == 'zh' else f"## Report Generation Error\n- {str(e)}"

            def merge_mic_failure_reasons_suggestion(self, structured_failed_logs_dict,
                                                     chinese_failure_reasons_suggestion,
                                                     english_failure_reasons_suggestion,
                                                     first_key=r'AUDIO_SAMPLE_MIC_\\d+_CONTIGUOUS_SPKR\\d+_\\d+-\\d+(?:_ASYNC_(START|WAIT))?.*FAILED'):
                """
                将中英文分析报告添加到结构化失败日志字典中

                参数:
                structured_failed_logs_dict (dict): 包含测试数据的结构化字典
                chinese_report (str): 中文分析报告内容
                english_failure_reasons_suggestion (str): 英文分析报告内容

                返回:
                dict: 更新后的结构化字典，包含中英文分析报告
                """
                # 查找目标测试项
                target_pattern_key = None
                target_test_key = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_MIC_后跟数字，然后是任意内容和FAILED
                mic_failed_pattern = re.compile(first_key)

                for pattern_key in structured_failed_logs_dict:
                    for test_key in structured_failed_logs_dict[pattern_key]:
                        # 使用正则表达式进行匹配
                        if mic_failed_pattern.search(test_key):
                            target_pattern_key = pattern_key
                            target_test_key = test_key
                            break
                    if target_test_key:
                        break

                if not target_test_key:
                    print("警告：未找到目标测试项")
                    return structured_failed_logs_dict

                # 获取目标测试项的字典
                test_dict = structured_failed_logs_dict[target_pattern_key][target_test_key]

                # 创建报告字典
                report_items = {
                    'chinese_failure_reasons_suggestion': chinese_failure_reasons_suggestion,
                    'english_failure_reasons_suggestion': english_failure_reasons_suggestion
                }

                # 添加到字典中，与data_items同级
                test_dict['report_items'] = report_items

                return structured_failed_logs_dict

            def plot_mic_test_results(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存

                参数:
                data_dict (dict): 包含测试数据的字典
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {}

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                if not data_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 提取第一个数据点的单位和测试项
                unit = data_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据
                x_labels = [item['Item'] for item in data_items]
                y_values = np.array([float(item['data']) for item in data_items], dtype=np.float64)

                # 提取上下限数据（假设所有数据的上下限相同）
                low_limit = float(data_items[0]['lowlimit'])
                up_limit = float(data_items[0]['uplimit'])

                # 创建图表
                plt.figure(figsize=(10, 6))
                plt.plot(x_labels, y_values, marker='o', label='Test Data', linewidth=2)
                plt.axhline(y=low_limit, color='#dc2626', linestyle='--', linewidth=2.5,
                            label=f'Low Limit: {low_limit:.1f}{unit}')
                plt.axhline(y=up_limit, color='#dc2626', linestyle='--', linewidth=2.5,
                            label=f'Up Limit: {up_limit:.1f}{unit}')

                # 添加平均值线
                avg_value = np.mean(y_values)
                plt.axhline(y=avg_value, color='#2563eb', linestyle='-.', linewidth=2,
                            label=f'Avg Value: {avg_value:.1f}{unit}')

                # 添加状态信息
                state = data_items[0].get('state', 'Unknown')
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color='green', ha='left', va='top', fontsize=9)

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(rotation=90)
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    # 确保文件夹存在
                    os.makedirs(folder_path, exist_ok=True)

                    # 保存图表
                    if os.name == 'nt':  # Windows系统
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:  # Linux/Unix系统
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    # 读取并返回base64编码内容
                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                # 根据参数决定是否显示图片
                if show_image:
                    plt.show()

                # 关闭绘图工具
                plt.close()

                # 构建返回结果
                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results2(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存

                参数:
                data_dict (dict): 包含测试数据的字典
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {}

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"MIC_1_STATUS"的无关项
                data_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not data_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 提取第一个数据点的单位和测试项
                unit = data_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态
                x_labels = []
                y_values = []
                is_abnormal = []  # 记录每个数据点是否异常

                for item in data_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    # 判断是否异常（超出上下限）
                    val = float(item['data'])
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)

                # 提取上下限数据
                low_limit = float(data_items[0]['lowlimit'])
                up_limit = float(data_items[0]['uplimit'])

                # 创建图表
                plt.figure(figsize=(10, 6))

                # 绘制数据点，根据是否异常设置不同颜色
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_labels[i], y_values[i], marker='o', color=color, markersize=8)

                # 绘制连接线（使用绿色作为基础连接线）
                plt.plot(x_labels, y_values, color='green', linewidth=2, label='Test Data')

                # 绘制上下限线（黑色）
                plt.axhline(y=low_limit, color='black', linestyle='--', linewidth=2.5,
                            label=f'Low Limit: {low_limit:.1f}{unit}')
                plt.axhline(y=up_limit, color='black', linestyle='--', linewidth=2.5,
                            label=f'Up Limit: {up_limit:.1f}{unit}')

                # 添加平均值线
                avg_value = np.mean(y_values)
                plt.axhline(y=avg_value, color='#2563eb', linestyle='-.', linewidth=2,
                            label=f'Avg Value: {avg_value:.1f}{unit}')

                # 添加状态信息，根据状态设置不同颜色
                state = data_items[0].get('state', 'Unknown')
                # 判断状态是否合格，合格用绿色，不合格用红色
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(rotation=90)
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    # 确保文件夹存在
                    os.makedirs(folder_path, exist_ok=True)

                    # 保存图表
                    if os.name == 'nt':  # Windows系统
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:  # Linux/Unix系统
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    # 读取并返回base64编码内容
                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                # 根据参数决定是否显示图片
                if show_image:
                    plt.show()

                # 关闭绘图工具
                plt.close()

                # 构建返回结果
                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results3(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存

                参数:
                data_dict (dict): 包含测试数据的字典
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {}

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"MIC_1_STATUS"的无关项
                data_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not data_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 提取第一个数据点的单位和测试项
                unit = data_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []  # 记录每个数据点是否异常
                low_limits = []  # 记录每个数据点的下限
                up_limits = []  # 记录每个数据点的上限

                for item in data_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    # 提取当前数据点的上下限并存储
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    # 判断是否异常（超出当前数据点的上下限）
                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)

                # 创建图表
                plt.figure(figsize=(10, 6))

                # 绘制数据点，根据是否异常设置不同颜色
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_labels[i], y_values[i], marker='o', color=color, markersize=8)

                # 绘制连接线（使用绿色作为基础连接线）
                plt.plot(x_labels, y_values, color='green', linewidth=2, label='Test Data')

                # 绘制每个数据点对应的上下限线（黑色虚线）
                for i in range(len(x_labels)):
                    # 下限线
                    plt.axhline(y=low_limits[i], color='black', linestyle='--', linewidth=1.5)
                    # 上限线
                    plt.axhline(y=up_limits[i], color='black', linestyle='--', linewidth=1.5)

                # 添加整体上下限标签（使用第一个数据点的上下限作为参考）
                plt.axhline(y=low_limits[0], color='black', linestyle='--', linewidth=2.5,
                            label=f'Low Limit Range: {min(low_limits):.1f}-{max(low_limits):.1f}{unit}')
                plt.axhline(y=up_limits[0], color='black', linestyle='--', linewidth=2.5,
                            label=f'Up Limit Range: {min(up_limits):.1f}-{max(up_limits):.1f}{unit}')

                # 添加平均值线
                avg_value = np.mean(y_values)
                plt.axhline(y=avg_value, color='#2563eb', linestyle='-.', linewidth=2,
                            label=f'Avg Value: {avg_value:.1f}{unit}')

                # 添加状态信息，根据状态设置不同颜色
                state = data_items[0].get('state', 'Unknown')
                # 判断状态是否合格，合格用绿色，不合格用红色
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(rotation=90)
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    # 确保文件夹存在
                    os.makedirs(folder_path, exist_ok=True)

                    # 保存图表
                    if os.name == 'nt':  # Windows系统
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:  # Linux/Unix系统
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    # 读取并返回base64编码内容
                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                # 根据参数决定是否显示图片
                if show_image:
                    plt.show()

                # 关闭绘图工具
                plt.close()

                # 构建返回结果
                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results4(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存

                参数:
                data_dict (dict): 包含测试数据的字典
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {}

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"MIC_1_STATUS"的无关项
                data_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not data_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 提取第一个数据点的单位和测试项
                unit = data_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []  # 记录每个数据点是否异常
                low_limits = []  # 记录每个数据点的下限
                up_limits = []  # 记录每个数据点的上限

                for item in data_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    # 提取当前数据点的上下限并存储
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    # 判断是否异常（超出当前数据点的上下限）
                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)

                # 创建图表
                plt.figure(figsize=(10, 6))

                # 获取x轴坐标位置（用于绘制小段线）
                x_positions = range(len(x_labels))

                # 绘制数据点，根据是否异常设置不同颜色
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_positions[i], y_values[i], marker='o', color=color, markersize=8)

                # 绘制连接线（使用绿色作为基础连接线）
                plt.plot(x_positions, y_values, color='green', linewidth=2, label='Test Data')

                # 绘制每个数据点对应的上下限小段线（黑色虚线）
                # 计算线段长度（使用数据范围的5%作为线段长度）
                data_range = max(y_values) - min(y_values) if len(y_values) > 0 else 10
                segment_length = data_range * 0.05  # 线段长度为数据范围的5%

                for i in range(len(x_labels)):
                    # 下限小段线（在x位置绘制垂直短线）
                    plt.plot(
                        [x_positions[i] - 0.1, x_positions[i] + 0.1],  # x轴范围（左右各延伸0.1）
                        [low_limits[i], low_limits[i]],  # y轴固定为下限值
                        color='black', linestyle='-', linewidth=1.5
                    )

                    # 上限小段线
                    plt.plot(
                        [x_positions[i] - 0.1, x_positions[i] + 0.1],  # x轴范围
                        [up_limits[i], up_limits[i]],  # y轴固定为上限值
                        color='black', linestyle='-', linewidth=1.5
                    )

                # # 添加整体上下限标签
                # plt.axhline(y=low_limits[0], color='black', linestyle='--', linewidth=2.5,
                #             label=f'Low Limit Range: {min(low_limits):.1f}-{max(low_limits):.1f}{unit}')
                # plt.axhline(y=up_limits[0], color='black', linestyle='--', linewidth=2.5,
                #             label=f'Up Limit Range: {min(up_limits):.1f}-{max(up_limits):.1f}{unit}')

                # # 添加平均值线
                # avg_value = np.mean(y_values)
                # plt.axhline(y=avg_value, color='#2563eb', linestyle='-.', linewidth=2,
                #             label=f'Avg Value: {avg_value:.1f}{unit}')

                # 添加状态信息，根据状态设置不同颜色
                state = data_items[0].get('state', 'Unknown')
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(x_positions, x_labels, rotation=90)  # 使用实际x位置设置刻度
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)

                    if os.name == 'nt':
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                if show_image:
                    plt.show()

                plt.close()

                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results5(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存

                参数:
                data_dict (dict): 包含测试数据的字典
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {}

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"MIC_1_STATUS"的无关项
                data_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not data_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 提取第一个数据点的单位和测试项
                unit = data_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []  # 记录每个数据点是否异常
                low_limits = []  # 记录每个数据点的下限
                up_limits = []  # 记录每个数据点的上限

                for item in data_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    # 提取当前数据点的上下限并存储
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    # 判断是否异常（超出当前数据点的上下限）
                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)

                # 创建图表
                plt.figure(figsize=(10, 6))

                # 获取x轴坐标位置（用于绘制线段）
                x_positions = range(len(x_labels))

                # 绘制数据点，根据是否异常设置不同颜色
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_positions[i], y_values[i], marker='o', color=color, markersize=8)

                # 绘制连接线（使用绿色作为基础连接线）
                plt.plot(x_positions, y_values, color='green', linewidth=2, label='Test Data')

                # 绘制上下限线：先连接所有点的上下限，再在每个点添加垂直短线
                # 1. 连接所有点的下限形成一条连续线
                plt.plot(x_positions, low_limits, color='black', linestyle='-', linewidth=1.5, label='Low Limits')

                # 2. 连接所有点的上限形成一条连续线
                plt.plot(x_positions, up_limits, color='black', linestyle='-', linewidth=1.5, label='Up Limits')

                # 3. 在每个数据点位置添加垂直短线，增强上下限与数据点的关联视觉效果
                for i in range(len(x_labels)):
                    # 下限垂直短线
                    plt.plot(
                        [x_positions[i], x_positions[i]],  # x轴位置固定
                        [low_limits[i] - 0.1, low_limits[i] + 0.1],  # y轴上下延伸一小段
                        color='black', linestyle='-', linewidth=0.1
                    )

                    # 上限垂直短线
                    plt.plot(
                        [x_positions[i], x_positions[i]],  # x轴位置固定
                        [up_limits[i] - 0.1, up_limits[i] + 0.1],  # y轴上下延伸一小段
                        color='black', linestyle='-', linewidth=0.1
                    )

                # 添加状态信息，根据状态设置不同颜色
                state = data_items[0].get('state', 'Unknown')
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(x_positions, x_labels, rotation=90)  # 使用实际x位置设置刻度
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)

                    if os.name == 'nt':
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                if show_image:
                    plt.show()

                plt.close()

                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results6(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存

                参数:
                data_dict (dict): 包含测试数据的字典
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {
                    "chart_name": '',
                    "image_path": '',
                    "base64_content": ''
                }

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"MIC_1_STATUS"的无关项
                data_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not data_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 提取第一个数据点的单位和测试项
                unit = data_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []  # 记录每个数据点是否异常
                low_limits = []  # 记录每个数据点的下限
                up_limits = []  # 记录每个数据点的上限

                for item in data_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    # 提取当前数据点的上下限并存储
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    # 判断是否异常（超出当前数据点的上下限）
                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)
                num_points = len(x_labels)  # 获取数据点数量

                # 创建图表
                plt.figure(figsize=(10, 6))

                # 获取x轴坐标位置（用于绘制线段）
                x_positions = range(len(x_labels))

                # 绘制数据点，根据是否异常设置不同颜色
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_positions[i], y_values[i], marker='o', color=color, markersize=8)

                # 仅当有多个数据点时才绘制连接线
                if num_points > 1:
                    plt.plot(x_positions, y_values, color='green', linewidth=2, label='Test Data')
                else:
                    # 单个数据点时不绘制连接线，仅显示数据点
                    plt.scatter(x_positions, y_values, color='green', label='Test Data')

                # 绘制上下限线：单个点时绘制两条独立线，多个点时绘制连接线
                if num_points == 1:
                    # 单个数据点时，绘制两条独立的上下限指标线
                    x = x_positions[0]
                    # 扩展x轴范围，使线条更明显（左右各延伸0.2单位）
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [low_limits[0], low_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Low Limit'
                    )
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [up_limits[0], up_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Up Limit'
                    )
                else:
                    # 多个数据点时，连接所有点的上下限形成连续线
                    plt.plot(x_positions, low_limits, color='black', linestyle='-', linewidth=1.5, label='Low Limits')
                    plt.plot(x_positions, up_limits, color='black', linestyle='-', linewidth=1.5, label='Up Limits')

                    # 在每个数据点位置添加垂直短线，增强关联视觉效果
                    for i in range(len(x_labels)):
                        # 下限垂直短线
                        plt.plot(
                            [x_positions[i], x_positions[i]],  # x轴位置固定
                            [low_limits[i] - 0.1, low_limits[i] + 0.1],  # y轴上下延伸
                            color='black', linestyle='-', linewidth=1.5
                        )

                        # 上限垂直短线
                        plt.plot(
                            [x_positions[i], x_positions[i]],  # x轴位置固定
                            [up_limits[i] - 0.1, up_limits[i] + 0.1],  # y轴上下延伸
                            color='black', linestyle='-', linewidth=1.5
                        )

                # 添加状态信息，根据状态设置不同颜色
                state = data_items[0].get('state', 'Unknown')
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(x_positions, x_labels, rotation=90)  # 使用实际x位置设置刻度
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)

                    if os.name == 'nt':
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                if show_image:
                    plt.show()

                plt.close()

                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results7(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存，数据超过20个时使用最差20个数据

                参数:
                data_dict (dict): 包含测试数据的字典
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {
                    "chart_name": '',
                    "image_path": '',
                    "base64_content": ''
                }

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"MIC_1_STATUS"的无关项
                data_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not data_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 计算每个数据点的偏离程度（用于判断"最差"数据）
                # 偏离程度 = 超出上限的值 + 低于下限的值（取绝对值）
                for item in data_items:
                    val = float(item['data'])
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])

                    if val > up:
                        deviation = val - up  # 超出上限的部分
                    elif val < low:
                        deviation = low - val  # 低于下限的部分
                    else:
                        deviation = 0  # 正常范围内偏离度为0
                    item['deviation'] = deviation

                # 如果数据超过20个，选取偏离度最大的20个（最差的20个）
                if len(data_items) > 20:
                    # 按偏离度降序排序，取前20个
                    data_items = sorted(data_items, key=lambda x: x['deviation'], reverse=True)[:20]
                    print(f"数据点超过20个，选取偏离度最大的20个数据进行绘图")

                # 提取第一个数据点的单位和测试项
                unit = data_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []  # 记录每个数据点是否异常
                low_limits = []  # 记录每个数据点的下限
                up_limits = []  # 记录每个数据点的上限

                for item in data_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    # 提取当前数据点的上下限并存储
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    # 判断是否异常（超出当前数据点的上下限）
                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)
                num_points = len(x_labels)  # 获取数据点数量

                # 创建图表
                plt.figure(figsize=(10, 6))

                # 获取x轴坐标位置（用于绘制线段）
                x_positions = range(len(x_labels))

                # 绘制数据点，根据是否异常设置不同颜色
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_positions[i], y_values[i], marker='o', color=color, markersize=8)

                # 仅当有多个数据点时才绘制连接线
                if num_points > 1:
                    plt.plot(x_positions, y_values, color='green', linewidth=2, label='Test Data')
                else:
                    # 单个数据点时不绘制连接线，仅显示数据点
                    plt.scatter(x_positions, y_values, color='green', label='Test Data')

                # 绘制上下限线：单个点时绘制两条独立线，多个点时绘制连接线
                if num_points == 1:
                    # 单个数据点时，绘制两条独立的上下限指标线
                    x = x_positions[0]
                    # 扩展x轴范围，使线条更明显（左右各延伸0.2单位）
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [low_limits[0], low_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Low Limit'
                    )
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [up_limits[0], up_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Up Limit'
                    )
                else:
                    # 多个数据点时，连接所有点的上下限形成连续线
                    plt.plot(x_positions, low_limits, color='black', linestyle='-', linewidth=1.5, label='Low Limits')
                    plt.plot(x_positions, up_limits, color='black', linestyle='-', linewidth=1.5, label='Up Limits')

                    # 在每个数据点位置添加垂直短线，增强关联视觉效果
                    for i in range(len(x_labels)):
                        # 下限垂直短线
                        plt.plot(
                            [x_positions[i], x_positions[i]],  # x轴位置固定
                            [low_limits[i] - 0.1, low_limits[i] + 0.1],  # y轴上下延伸
                            color='black', linestyle='-', linewidth=1.5
                        )

                        # 上限垂直短线
                        plt.plot(
                            [x_positions[i], x_positions[i]],  # x轴位置固定
                            [up_limits[i] - 0.1, up_limits[i] + 0.1],  # y轴上下延伸
                            color='black', linestyle='-', linewidth=1.5
                        )

                # 添加状态信息，根据状态设置不同颜色
                state = data_items[0].get('state', 'Unknown')
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 添加数据量说明（如果进行了数据筛选）
                if len(data_items) == 20 and len(test_data.get('data_items', [])) > 20:
                    plt.text(0.05, 0.85, 'Displaying top 20 worst results', transform=plt.gca().transAxes,
                             color='orange', ha='left', va='top', fontsize=8, style='italic')

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(x_positions, x_labels, rotation=90)  # 使用实际x位置设置刻度
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)

                    if os.name == 'nt':
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                if show_image:
                    plt.show()

                plt.close()

                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results8(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存，数据超过20个时使用最差20个数据，同时同步更新原始数据

                参数:
                data_dict (dict): 包含测试数据的字典，将被同步更新
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {
                    "chart_name": '',
                    "image_path": '',
                    "base64_content": ''
                }

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"STATUS"的无关项
                filtered_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not filtered_items:
                    print("警告：无有效数据可绘制图表")
                    return result

                # 计算每个数据点的偏离程度（用于判断"最差"数据）
                # 偏离程度 = 超出上限的值 + 低于下限的值（取绝对值）
                for item in filtered_items:
                    val = float(item['data'])
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])

                    if val > up:
                        deviation = val - up  # 超出上限的部分
                    elif val < low:
                        deviation = low - val  # 低于下限的部分
                    else:
                        deviation = 0  # 正常范围内偏离度为0
                    item['deviation'] = deviation

                # 数据筛选：如果超过20个，选取偏离度最大的20个（最差的20个）
                if len(filtered_items) > 20:
                    # 按偏离度降序排序，取前20个
                    selected_items = sorted(filtered_items, key=lambda x: x['deviation'], reverse=True)[:20]
                    print(f"数据点超过20个，选取偏离度最大的20个数据进行绘图并更新原始数据")
                else:
                    selected_items = filtered_items
                    print(f"数据点不足20个，使用全部{len(selected_items)}个数据点")

                # 同步更新原始数据字典中的data_items
                # 保存未过滤的STATUS项，仅替换有效测试数据项
                status_items = [item for item in data_items if "STATUS" in item.get('Item', '')]
                updated_items = selected_items + status_items  # 合并筛选后的测试项和状态项
                data_dict[pattern_key][test_key]['data_items'] = updated_items  # 更新原始数据
                print(f"已同步更新原始数据，保留{len(updated_items)}个数据项（含状态项）")

                # 提取第一个数据点的单位和测试项
                unit = selected_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []  # 记录每个数据点是否异常
                low_limits = []  # 记录每个数据点的下限
                up_limits = []  # 记录每个数据点的上限

                for item in selected_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    # 提取当前数据点的上下限并存储
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    # 判断是否异常（超出当前数据点的上下限）
                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)
                num_points = len(x_labels)  # 获取数据点数量

                # 创建图表
                plt.figure(figsize=(10, 6))

                # 获取x轴坐标位置（用于绘制线段）
                x_positions = range(len(x_labels))

                # 绘制数据点，根据是否异常设置不同颜色
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_positions[i], y_values[i], marker='o', color=color, markersize=8)

                # 仅当有多个数据点时才绘制连接线
                if num_points > 1:
                    plt.plot(x_positions, y_values, color='green', linewidth=2, label='Test Data')
                else:
                    # 单个数据点时不绘制连接线，仅显示数据点
                    plt.scatter(x_positions, y_values, color='green', label='Test Data')

                # 绘制上下限线：单个点时绘制两条独立线，多个点时绘制连接线
                if num_points == 1:
                    # 单个数据点时，绘制两条独立的上下限指标线
                    x = x_positions[0]
                    # 扩展x轴范围，使线条更明显（左右各延伸0.2单位）
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [low_limits[0], low_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Low Limit'
                    )
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [up_limits[0], up_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Up Limit'
                    )
                else:
                    # 多个数据点时，连接所有点的上下限形成连续线
                    plt.plot(x_positions, low_limits, color='black', linestyle='-', linewidth=1.5, label='Low Limits')
                    plt.plot(x_positions, up_limits, color='black', linestyle='-', linewidth=1.5, label='Up Limits')

                    # 在每个数据点位置添加垂直短线，增强关联视觉效果
                    for i in range(len(x_labels)):
                        # 下限垂直短线
                        plt.plot(
                            [x_positions[i], x_positions[i]],  # x轴位置固定
                            [low_limits[i] - 0.1, low_limits[i] + 0.1],  # y轴上下延伸
                            color='black', linestyle='-', linewidth=1.5
                        )

                        # 上限垂直短线
                        plt.plot(
                            [x_positions[i], x_positions[i]],  # x轴位置固定
                            [up_limits[i] - 0.1, up_limits[i] + 0.1],  # y轴上下延伸
                            color='black', linestyle='-', linewidth=1.5
                        )

                # 添加状态信息，根据状态设置不同颜色
                state = selected_items[0].get('state', 'Unknown')
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 添加数据量说明（如果进行了数据筛选）
                if len(selected_items) == 20 and len(filtered_items) > 20:
                    plt.text(0.05, 0.85, 'Displaying top 20 worst results', transform=plt.gca().transAxes,
                             color='orange', ha='left', va='top', fontsize=8, style='italic')

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(x_positions, x_labels, rotation=90)  # 使用实际x位置设置刻度
                plt.legend()
                plt.tight_layout()

                image_path = None
                base64_content = None

                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)

                    if os.name == 'nt':
                        image_path = f'{folder_path}\\{test_item}.png'
                    else:
                        image_path = f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                if show_image:
                    plt.show()

                plt.close()

                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results9(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存，数据超过20个时使用最差20个数据，同步更新原始数据（不保留状态项）

                参数:
                data_dict (dict): 包含测试数据的字典，将被同步更新
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {
                    "chart_name": '',
                    "image_path": '',
                    "base64_content": ''
                }

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"STATUS"的项，只保留有效测试数据项
                filtered_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not filtered_items:
                    print("警告：无有效测试数据可绘制图表（已过滤所有状态项）")
                    return result

                # 计算每个数据点的偏离程度（用于判断"最差"数据）
                for item in filtered_items:
                    val = float(item['data'])
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])

                    if val > up:
                        deviation = val - up  # 超出上限的部分
                    elif val < low:
                        deviation = low - val  # 低于下限的部分
                    else:
                        deviation = 0  # 正常范围内偏离度为0
                    item['deviation'] = deviation

                # 数据筛选：如果超过20个，选取偏离度最大的20个（最差的20个）
                if len(filtered_items) > 20:
                    selected_items = sorted(filtered_items, key=lambda x: x['deviation'], reverse=True)[:20]
                    print(f"数据点超过20个，选取偏离度最大的20个测试数据进行绘图并更新原始数据")
                else:
                    selected_items = filtered_items
                    print(f"数据点不足20个，使用全部{len(selected_items)}个测试数据点")

                # 同步更新原始数据字典中的data_items（仅保留筛选后的测试数据项，不保留状态项）
                data_dict[pattern_key][test_key]['data_items'] = selected_items
                print(f"已同步更新原始数据，仅保留{len(selected_items)}个有效测试数据项（已移除所有状态项）")

                # 提取第一个数据点的单位和测试项
                unit = selected_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []
                low_limits = []
                up_limits = []

                for item in selected_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)
                num_points = len(x_labels)

                # 创建图表
                plt.figure(figsize=(10, 6))
                x_positions = range(len(x_labels))

                # 绘制数据点
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_positions[i], y_values[i], marker='o', color=color, markersize=8)

                # 绘制连接线（多个数据点时）
                if num_points > 1:
                    plt.plot(x_positions, y_values, color='green', linewidth=2, label='Test Data')
                else:
                    plt.scatter(x_positions, y_values, color='green', label='Test Data')

                # 绘制上下限线
                if num_points == 1:
                    x = x_positions[0]
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [low_limits[0], low_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Low Limit'
                    )
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [up_limits[0], up_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Up Limit'
                    )
                else:
                    plt.plot(x_positions, low_limits, color='black', linestyle='-', linewidth=1.5, label='Low Limits')
                    plt.plot(x_positions, up_limits, color='black', linestyle='-', linewidth=1.5, label='Up Limits')

                    # 添加垂直短线增强关联
                    for i in range(len(x_labels)):
                        plt.plot([x_positions[i], x_positions[i]],
                                 [low_limits[i] - 0.1, low_limits[i] + 0.1],
                                 color='black', linestyle='-', linewidth=1.5)
                        plt.plot([x_positions[i], x_positions[i]],
                                 [up_limits[i] - 0.1, up_limits[i] + 0.1],
                                 color='black', linestyle='-', linewidth=1.5)

                # 添加状态信息（从第一个测试项获取）
                state = selected_items[0].get('state', 'Unknown')
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 添加数据筛选说明
                if len(selected_items) == 20 and len(filtered_items) > 20:
                    plt.text(0.05, 0.85, 'Displaying top 20 worst results', transform=plt.gca().transAxes,
                             color='orange', ha='left', va='top', fontsize=8, style='italic')

                # 设置图表属性
                plt.xlabel('Test Item')
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(x_positions, x_labels, rotation=90)
                plt.legend()
                plt.tight_layout()

                # 保存图片和处理base64编码
                image_path = None
                base64_content = None

                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)
                    image_path = f'{folder_path}\\{test_item}.png' if os.name == 'nt' else f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                if show_image:
                    plt.show()

                plt.close()

                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def plot_mic_test_results10(self, data_dict, title=None, folder_path=None, test_index=1, show_image=True):
                """
                绘制音频测试结果的折线图并保存，数据超过20个时使用最差20个数据，按频率从低到高排序，同步更新原始数据（不保留状态项）

                参数:
                data_dict (dict): 包含测试数据的字典，将被同步更新
                title (str, optional): 图表标题，如果未提供则使用数据键名
                folder_path (str, optional): 图表保存路径
                test_index (int, optional): 测试索引，用于生成文件名
                show_image (bool, optional): 是否显示图像

                返回:
                dict: 包含图表名称、图片路径和base64编码内容的结果字典
                """

                result = {
                    "chart_name": '',
                    "image_path": '',
                    "base64_content": ''
                }

                # 从数据字典中提取数据
                pattern_key = next(iter(data_dict))  # 获取第一个键 (正则表达式模式)
                test_key = next(iter(data_dict[pattern_key]))  # 获取测试项键

                # 提取数据项和测试目的
                test_data = data_dict[pattern_key][test_key]
                data_items = test_data.get('data_items', [])
                purpose2items = test_data.get('purpose2items', {})

                # 过滤掉包含"STATUS"的项，只保留有效测试数据项
                filtered_items = [item for item in data_items if "STATUS" not in item.get('Item', '')]

                if not filtered_items:
                    print("警告：无有效测试数据可绘制图表（已过滤所有状态项）")
                    return result

                # 计算每个数据点的偏离程度（用于判断"最差"数据）
                for item in filtered_items:
                    val = float(item['data'])
                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])

                    # 提取频率值（假设Item格式如"XXX_100Hz"，从Item中提取数字部分）
                    try:
                        # 从Item中提取频率数值（如从"LEVEL_100Hz"中提取100）
                        freq_str = item['Item'].split('_')[-1].replace('Hz', '')
                        item['frequency'] = int(freq_str)
                    except (IndexError, ValueError):
                        # 如果提取失败，设置一个默认频率（放在最前面）
                        item['frequency'] = 0

                    if val > up:
                        deviation = val - up  # 超出上限的部分
                    elif val < low:
                        deviation = low - val  # 低于下限的部分
                    else:
                        deviation = 0  # 正常范围内偏离度为0
                    item['deviation'] = deviation

                # 数据筛选：如果超过20个，选取偏离度最大的20个（最差的20个）
                if len(filtered_items) > 20:
                    selected_items = sorted(filtered_items, key=lambda x: x['deviation'], reverse=True)[:20]
                    print(f"数据点超过20个，选取偏离度最大的20个测试数据进行绘图并更新原始数据")
                else:
                    selected_items = filtered_items
                    print(f"数据点不足20个，使用全部{len(selected_items)}个测试数据点")

                # 按频率从低到高排序选中的数据点
                selected_items.sort(key=lambda x: x['frequency'])
                print(f"已按频率从低到高对{len(selected_items)}个测试数据点进行排序")

                # 同步更新原始数据字典中的data_items（仅保留筛选后的测试数据项，不保留状态项）
                data_dict[pattern_key][test_key]['data_items'] = selected_items
                print(f"已同步更新原始数据，仅保留{len(selected_items)}个有效测试数据项（已移除所有状态项）")

                # 提取第一个数据点的单位和测试项
                unit = selected_items[0].get('unit', 'dB')
                test_item = title or test_key

                # 提取x轴和y轴数据，同时记录正常/异常状态和每个数据点的上下限
                x_labels = []
                y_values = []
                is_abnormal = []
                low_limits = []
                up_limits = []

                for item in selected_items:
                    x_labels.append(item['Item'])
                    y_values.append(float(item['data']))

                    low = float(item['lowlimit'])
                    up = float(item['uplimit'])
                    low_limits.append(low)
                    up_limits.append(up)

                    val = float(item['data'])
                    is_abnormal.append(val < low or val > up)

                y_values = np.array(y_values, dtype=np.float64)
                num_points = len(x_labels)

                # 创建图表
                plt.figure(figsize=(10, 6))
                x_positions = range(len(x_labels))

                # 绘制数据点
                for i in range(len(x_labels)):
                    color = 'red' if is_abnormal[i] else 'green'
                    plt.plot(x_positions[i], y_values[i], marker='o', color=color, markersize=8)

                # 绘制连接线（多个数据点时）
                if num_points > 1:
                    plt.plot(x_positions, y_values, color='green', linewidth=2, label='Test Data')
                else:
                    plt.scatter(x_positions, y_values, color='green', label='Test Data')

                # 绘制上下限线
                if num_points == 1:
                    x = x_positions[0]
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [low_limits[0], low_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Low Limit'
                    )
                    plt.plot(
                        [x - 0.2, x + 0.2],
                        [up_limits[0], up_limits[0]],
                        color='black', linestyle='--', linewidth=1.5, label='Up Limit'
                    )
                else:
                    plt.plot(x_positions, low_limits, color='black', linestyle='-', linewidth=1.5, label='Low Limits')
                    plt.plot(x_positions, up_limits, color='black', linestyle='-', linewidth=1.5, label='Up Limits')

                    # 添加垂直短线增强关联
                    for i in range(len(x_labels)):
                        plt.plot([x_positions[i], x_positions[i]],
                                 [low_limits[i] - 0.1, low_limits[i] + 0.1],
                                 color='black', linestyle='-', linewidth=1.5)
                        plt.plot([x_positions[i], x_positions[i]],
                                 [up_limits[i] - 0.1, up_limits[i] + 0.1],
                                 color='black', linestyle='-', linewidth=1.5)

                # 添加状态信息（从第一个测试项获取）
                state = selected_items[0].get('state', 'Unknown')
                state_color = 'green' if state == '合格' else 'red'
                plt.text(0.05, 0.9, f'State: {state}', transform=plt.gca().transAxes,
                         color=state_color, ha='left', va='top', fontsize=9)

                # 添加数据筛选和排序说明
                sort_info = 'sorted by frequency (low to high)'
                if len(selected_items) == 20 and len(filtered_items) > 20:
                    plt.text(0.05, 0.85, f'Displaying top 20 worst results ({sort_info})',
                             transform=plt.gca().transAxes,
                             color='orange', ha='left', va='top', fontsize=8, style='italic')
                else:
                    plt.text(0.05, 0.85, f'Data {sort_info}', transform=plt.gca().transAxes,
                             color='blue', ha='left', va='top', fontsize=8, style='italic')

                # 设置图表属性
                plt.xlabel('Test Item (Frequency)')  # 明确x轴为频率相关
                plt.ylabel(f'Values ({unit})')
                plt.title(f'{test_item}_Chart{test_index}')
                plt.xticks(x_positions, x_labels, rotation=90)
                plt.legend()
                plt.tight_layout()

                # 保存图片和处理base64编码
                image_path = None
                base64_content = None

                if folder_path:
                    os.makedirs(folder_path, exist_ok=True)
                    image_path = f'{folder_path}\\{test_item}.png' if os.name == 'nt' else f'{folder_path}/{test_item}.png'

                    plt.savefig(image_path)
                    print(f"图片：{image_path}保存成功。")

                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_bytes = base64.b64encode(image_file.read())
                            base64_content = encoded_bytes.decode('utf-8')
                        print(f"成功获取图片的base64编码内容")
                    except Exception as e:
                        print(f"错误：无法读取图片文件并生成base64编码: {e}")

                if show_image:
                    plt.show()

                plt.close()

                result = {
                    "chart_name": f'{test_item}_Chart{test_index}',
                    "image_path": image_path,
                    "base64_content": base64_content
                }

                return result

            def merge_mic_test_results_to_dict(self, structured_failed_logs_dict,
                                               chart_items,
                                               second_key):
                """
                将图表结果添加到结构化失败日志字典中

                参数:
                structured_failed_logs_dict (dict): 结构化失败日志字典
                result (dict): 包含图表信息的结果字典

                返回:
                dict: 更新后的结构化失败日志字典
                """
                from copy import deepcopy

                # 创建深拷贝，避免修改原始数据
                updated_dict = deepcopy(structured_failed_logs_dict)

                # 查找目标键
                target_key = None
                for key in updated_dict.keys():
                    if second_key in updated_dict[key]:
                        target_key = key
                        break

                if target_key:
                    # 获取目标字典
                    target_entry = updated_dict[target_key][second_key]

                    # 添加chart_items
                    target_entry['chart_items'] = chart_items

                    print("成功添加chart_items到字典中")
                else:
                    print(f"警告: 未找到目标键 {0}", second_key)

                return updated_dict

            def update_mic_report_v1(self, report,
                                     structured_failed_logs_dict,
                                     first_key=r'AUDIO_SAMPLE_MIC_\\d+_CONTIGUOUS_SPKR\\d+_\\d+-\\d+(?:_ASYNC_(START|WAIT))?.*FAILED'):
                """
                将结构化失败日志字典中的数据映射到测试报告的测试项目结果中

                参数:
                report (Report): 包含测试结果的Report对象
                structured_failed_logs_dict (dict): 包含详细测试数据的字典

                返回:
                Report: 更新后的Report对象
                """
                # 查找目标测试项
                target_pattern_key = None
                target_test_key = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_MIC_后跟数字，然后是任意内容和FAILED
                mic_failed_pattern = re.compile(first_key)

                for pattern_key in structured_failed_logs_dict:
                    for test_key in structured_failed_logs_dict[pattern_key]:
                        # 使用正则表达式进行匹配
                        if mic_failed_pattern.search(test_key):
                            target_pattern_key = pattern_key
                            target_test_key = test_key
                            break
                    if target_test_key:
                        break

                if not target_test_key:
                    print("警告：未找到目标测试项")
                    return report

                # 获取测试数据
                test_data = structured_failed_logs_dict[target_pattern_key][target_test_key]

                # 获取Report中的测试项目结果列表
                test_project_results = report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results

                # 如果列表为空，添加一个新的TestProjectResult
                if not test_project_results:
                    empty_result = report.Modular_Test_Results_Display.Test_Analysis.TestProjectResult(
                        Test_Project='',
                        Meaning='',
                        Indicator='',
                        Test_Value='',
                        Range='',
                        Test_Result='',
                        Trend_Analysis='',
                        Implied_Problem_Possibility='',
                        Chart_Name='',
                        Chart_Content=''
                    )
                    test_project_results.append(empty_result)
                else:
                    empty_result = test_project_results[0]

                # 1. 填充Chart_Name和Chart_Content
                chart_items = test_data.get('chart_items', {})
                empty_result.Chart_Name = chart_items.get('chart_name', '')
                empty_result.Chart_Content = chart_items.get('base64_content', '')

                # 2. 填充Meaning和Indicator
                purpose2items = test_data.get('purpose2items', {})
                test_items_en = purpose2items.get('test_items_en', [])
                test_purpose_en = purpose2items.get('test_purpose_en', '')

                # 3. 填充Implied_Problem_Possibility
                issue_suggestions_items = test_data.get('report_items', {})
                issue_suggestions_items_zh = issue_suggestions_items.get('chinese_failure_reasons_suggestion', '')
                issue_suggestions_items_en = issue_suggestions_items.get('english_failure_reasons_suggestion', '')

                # 将test_items_en合并为字符串
                meaning_text = "\n".join(test_items_en) if test_items_en else ''

                empty_result.Meaning = meaning_text
                empty_result.Indicator = test_purpose_en
                empty_result.Implied_Problem_Possibility = issue_suggestions_items_en

                # 3. 处理data_items，排除最后一个无效项
                data_items = test_data.get('data_items', [])

                # 排除最后一个无效项（如果有多个项）
                if len(data_items) > 1:
                    valid_items = data_items[:-1]
                else:
                    valid_items = data_items

                # 提取并组合lowlimit和uplimit为Range
                ranges = []
                for item in valid_items:
                    low = item.get('lowlimit', '')
                    up = item.get('uplimit', '')
                    if low and up:
                        ranges.append(f"{low},{up}")
                    elif low:
                        ranges.append(f"{low},")
                    elif up:
                        ranges.append(f",{up}")

                empty_result.Range = " | ".join(ranges)

                # 提取并组合data为Test_Value
                values = [item.get('data', '') for item in valid_items]
                empty_result.Test_Value = " | ".join(values)

                # 提取并组合position_en为Trend_Analysis
                trends = [item.get('position_en', '') for item in valid_items]
                empty_result.Trend_Analysis = " | ".join(trends)

                # 设置其他必要字段
                empty_result.Test_Project = target_test_key
                empty_result.Test_Result = "FAILED"  # 明确标记为失败

                return report

            def update_mic_report(self, report,
                                  structured_failed_logs_dict,
                                  first_key=r'AUDIO_SAMPLE_MIC_\\d+_CONTIGUOUS_SPKR\\d+_\\d+-\\d+(?:_ASYNC_(START|WAIT))?.*FAILED',
                                  language='en'):
                """
                将结构化失败日志字典中的数据映射到测试报告的测试项目结果中

                参数:
                report (Report): 包含测试结果的Report对象
                structured_failed_logs_dict (dict): 包含详细测试数据的字典
                first_key (str): 用于匹配测试项的正则表达式
                language (str): 语言选择，默认'en'（英文），可传入'zh'使用中文

                返回:
                Report: 更新后的Report对象
                """
                # 查找目标测试项
                target_pattern_key = None
                target_test_key = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_MIC_后跟数字，然后是任意内容和FAILED
                mic_failed_pattern = re.compile(first_key)

                for pattern_key in structured_failed_logs_dict:
                    for test_key in structured_failed_logs_dict[pattern_key]:
                        # 使用正则表达式进行匹配
                        if mic_failed_pattern.search(test_key):
                            target_pattern_key = pattern_key
                            target_test_key = test_key
                            break
                    if target_test_key:
                        break

                if not target_test_key:
                    print("警告：未找到目标测试项")
                    return report

                # 获取测试数据
                test_data = structured_failed_logs_dict[target_pattern_key][target_test_key]

                # 获取Report中的测试项目结果列表
                test_project_results = report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results

                # 如果列表为空，添加一个新的TestProjectResult
                if not test_project_results:
                    empty_result = report.Modular_Test_Results_Display.Test_Analysis.TestProjectResult(
                        Test_Project='',
                        Meaning='',
                        Indicator='',
                        Test_Value='',
                        Range='',
                        Test_Result='',
                        Trend_Analysis='',
                        Implied_Problem_Possibility='',
                        Chart_Name='',
                        Chart_Content=''
                    )
                    test_project_results.append(empty_result)
                else:
                    empty_result = test_project_results[0]

                # 1. 填充Chart_Name和Chart_Content
                chart_items = test_data.get('chart_items', {})
                empty_result.Chart_Name = chart_items.get('chart_name', '')
                empty_result.Chart_Content = chart_items.get('base64_content', '')

                # 2. 填充Meaning和Indicator，根据语言参数选择对应数据
                purpose2items = test_data.get('purpose2items', {})
                if language == 'zh':
                    test_items = purpose2items.get('test_items_zh', [])
                    test_purpose = purpose2items.get('test_purpose_zh', '')
                else:  # 默认英文
                    test_items = purpose2items.get('test_items_en', [])
                    test_purpose = purpose2items.get('test_purpose_en', '')

                # 3. 填充Implied_Problem_Possibility，根据语言参数选择对应数据
                issue_suggestions_items = test_data.get('report_items', {})
                if language == 'zh':
                    issue_suggestion = issue_suggestions_items.get('chinese_failure_reasons_suggestion', '')
                else:  # 默认英文
                    issue_suggestion = issue_suggestions_items.get('english_failure_reasons_suggestion', '')

                # 将测试项合并为字符串
                meaning_text = "\n".join(test_items) if test_items else ''

                empty_result.Meaning = meaning_text
                empty_result.Indicator = test_purpose
                empty_result.Implied_Problem_Possibility = issue_suggestion

                # 4. 处理data_items，排除最后一个无效项
                data_items = test_data.get('data_items', [])

                # 排除最后一个无效项（如果有多个项）
                if len(data_items) > 1:
                    valid_items = data_items[:-1]
                else:
                    valid_items = data_items

                # 提取并组合lowlimit和uplimit为Range
                ranges = []
                for item in valid_items:
                    low = item.get('lowlimit', '')
                    up = item.get('uplimit', '')
                    if low and up:
                        ranges.append(f"{low},{up}")
                    elif low:
                        ranges.append(f"{low},")
                    elif up:
                        ranges.append(f",{up}")

                empty_result.Range = " | ".join(ranges)

                # 提取并组合data为Test_Value
                values = [item.get('data', '') for item in valid_items]
                empty_result.Test_Value = " | ".join(values)

                # 提取并组合position_en为Trend_Analysis
                trends = [item.get('position_en', '') for item in valid_items]
                empty_result.Trend_Analysis = " | ".join(trends)

                # 设置其他必要字段
                empty_result.Test_Project = target_test_key
                empty_result.Test_Result = "FAILED"  # 明确标记为失败

                return report

            def update_mic_report2(self, report,
                                   structured_failed_logs_dict,
                                   first_key=r'AUDIO_SAMPLE_MIC_\\d+_CONTIGUOUS_SPKR\\d+_\\d+-\\d+(?:_ASYNC_(START|WAIT))?.*FAILED',
                                   language='en',
                                   is_clear=False):
                """
                将结构化失败日志字典中的数据映射到测试报告的测试项目结果中

                参数:
                report (Report): 包含测试结果的Report对象
                structured_failed_logs_dict (dict): 包含详细测试数据的字典
                first_key (str): 用于匹配测试项的正则表达式
                language (str): 语言选择，默认'en'（英文），可传入'zh'使用中文
                is_clear (bool): 是否清空现有结果，True表示清空后添加，False表示在现有结果后新增

                返回:
                Report: 更新后的Report对象
                """
                # 查找目标测试项
                target_pattern_key = None
                target_test_key = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_MIC_后跟数字，然后是任意内容和FAILED
                mic_failed_pattern = re.compile(first_key)

                for pattern_key in structured_failed_logs_dict:
                    for test_key in structured_failed_logs_dict[pattern_key]:
                        if mic_failed_pattern.search(test_key):
                            target_pattern_key = pattern_key
                            target_test_key = test_key
                            break
                    if target_test_key:
                        break

                if not target_test_key:
                    print("警告：未找到目标测试项")
                    return report

                # 获取测试数据
                test_data = structured_failed_logs_dict[target_pattern_key][target_test_key]

                # 获取Report中的测试项目结果列表（包含TestProjectResult对象）
                test_project_results = report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results

                # 创建新的TestProjectResult对象（基于列表中已有对象的类型）
                def create_new_result():
                    return TestProjectResult(
                        Test_Project='',
                        Meaning='',
                        Indicator='',
                        Test_Value='',
                        Range='',
                        Test_Result='',
                        Trend_Analysis='',
                        Implied_Problem_Possibility='',
                        Chart_Name='',
                        Chart_Content=''
                    )

                # 根据is_clear参数处理结果列表
                if is_clear:
                    # 清空现有结果并添加新结果
                    test_project_results.clear()
                    new_result = create_new_result()
                    test_project_results.append(new_result)
                    print("已清空现有测试项目结果并添加新结果")
                else:
                    # 在现有结果后新增
                    new_result = create_new_result()
                    test_project_results.append(new_result)

                # 填充新结果的数据
                chart_items = test_data.get('chart_items', {})
                new_result.Chart_Name = chart_items.get('chart_name', '')
                new_result.Chart_Content = chart_items.get('base64_content', '')

                purpose2items = test_data.get('purpose2items', {})
                if language == 'zh':
                    test_items = purpose2items.get('test_items_zh', [])
                    test_purpose = purpose2items.get('test_purpose_zh', '')
                else:
                    test_items = purpose2items.get('test_items_en', [])
                    test_purpose = purpose2items.get('test_purpose_en', '')

                issue_suggestions_items = test_data.get('report_items', {})
                new_result.Implied_Problem_Possibility = (
                    issue_suggestions_items.get('chinese_failure_reasons_suggestion', '')
                    if language == 'zh'
                    else issue_suggestions_items.get('english_failure_reasons_suggestion', '')
                )

                new_result.Meaning = "\n".join(test_items) if test_items else ''
                new_result.Indicator = test_purpose

                # 处理数据项
                data_items = test_data.get('data_items', [])
                valid_items = data_items[:-1] if len(data_items) > 1 else data_items

                ranges = []
                for item in valid_items:
                    low, up = item.get('lowlimit', ''), item.get('uplimit', '')
                    if low and up:
                        ranges.append(f"{low},{up}")
                    elif low:
                        ranges.append(f"{low},")
                    elif up:
                        ranges.append(f",{up}")

                new_result.Range = " | ".join(ranges)
                new_result.Test_Value = " | ".join([item.get('data', '') for item in valid_items])
                new_result.Trend_Analysis = " | ".join([item.get('position_en', '') for item in valid_items])

                # 设置基本信息
                new_result.Test_Project = target_test_key
                new_result.Test_Result = "FAILED"

                return report

            def update_mic_report3(self, report,
                                   structured_failed_logs_dict,
                                   first_key=r'AUDIO_SAMPLE_MIC_\\d+_CONTIGUOUS_SPKR\\d+_\\d+-\\d+(?:_ASYNC_(START|WAIT))?.*FAILED',
                                   language='en',
                                   is_clear=False):
                """
                将结构化失败日志字典中的数据映射到测试报告的测试项目结果中

                参数:
                report (Report): 包含测试结果的Report对象
                structured_failed_logs_dict (dict): 包含详细测试数据的字典
                first_key (str): 用于匹配测试项的正则表达式
                language (str): 语言选择，默认'en'（英文），可传入'zh'使用中文
                is_clear (bool): 是否清空现有结果，True表示清空后添加，False表示在现有结果后新增

                返回:
                Report: 更新后的Report对象
                """
                # 查找目标测试项
                target_pattern_key = None
                target_test_key = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_MIC_后跟数字，然后是任意内容和FAILED
                mic_failed_pattern = re.compile(first_key)

                for pattern_key in structured_failed_logs_dict:
                    for test_key in structured_failed_logs_dict[pattern_key]:
                        if mic_failed_pattern.search(test_key):
                            target_pattern_key = pattern_key
                            target_test_key = test_key
                            break
                    if target_test_key:
                        break

                if not target_test_key:
                    print("警告：未找到目标测试项")
                    return report

                # 获取测试数据
                test_data = structured_failed_logs_dict[target_pattern_key][target_test_key]

                # 处理StatusIndicators（与TestProjectResult逻辑保持一致）
                # 获取Report中的状态指示器列表
                status_indicators = report.Global_Overview.Status_Indicators.Status_Indicators

                # 创建新的StatusIndicatorItem对象
                def create_new_status_item():
                    return StatusIndicatorItem(
                        item='',
                        state='',
                        color='',
                        show=True
                    )

                # 根据is_clear参数处理状态指示器列表
                if is_clear:
                    # 清空现有状态指示器并添加新项
                    status_indicators.clear()
                    new_status_item = create_new_status_item()
                    status_indicators.append(new_status_item)
                    print("已清空现有状态指示器并添加新项")
                else:
                    # 在现有状态指示器后新增
                    new_status_item = create_new_status_item()
                    status_indicators.append(new_status_item)

                # 填充新状态指示器的数据
                # 从测试数据中提取状态相关信息
                status_info = test_data.get('data_items', {})
                new_status_item.item = target_test_key  # 使用测试项作为状态名称
                # 判断状态：如果包含'FAILED'则返回'FAILED'，否则返回'PASS'
                state_value = status_info[0]['state'] if status_info else ''
                new_status_item.state = "FAILED" if 'FAILED' in state_value else "PASS"
                # 同步更新颜色
                new_status_item.color = "Red" if new_status_item.state == "FAILED" else "Green"
                new_status_item.show = True

                # 获取Report中的测试项目结果列表（包含TestProjectResult对象）
                test_project_results = report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results

                # 创建新的TestProjectResult对象（基于列表中已有对象的类型）
                def create_new_result():
                    return TestProjectResult(
                        Test_Project='',
                        Meaning='',
                        Indicator='',
                        Test_Value='',
                        Range='',
                        Test_Result='',
                        Trend_Analysis='',
                        Implied_Problem_Possibility='',
                        Chart_Name='',
                        Chart_Content=''
                    )

                # 根据is_clear参数处理结果列表
                if is_clear:
                    # 清空现有结果并添加新结果
                    test_project_results.clear()
                    new_result = create_new_result()
                    test_project_results.append(new_result)
                    print("已清空现有测试项目结果并添加新结果")
                else:
                    # 在现有结果后新增
                    new_result = create_new_result()
                    test_project_results.append(new_result)

                # 填充新结果的数据
                chart_items = test_data.get('chart_items', {})
                new_result.Chart_Name = chart_items.get('chart_name', '')
                new_result.Chart_Content = chart_items.get('base64_content', '')

                purpose2items = test_data.get('purpose2items', {})
                if language == 'zh':
                    test_items = purpose2items.get('test_items_zh', [])
                    test_purpose = purpose2items.get('test_purpose_zh', '')
                else:
                    test_items = purpose2items.get('test_items_en', [])
                    test_purpose = purpose2items.get('test_purpose_en', '')

                issue_suggestions_items = test_data.get('report_items', {})
                new_result.Implied_Problem_Possibility = (
                    issue_suggestions_items.get('chinese_failure_reasons_suggestion', '')
                    if language == 'zh'
                    else issue_suggestions_items.get('english_failure_reasons_suggestion', '')
                )

                new_result.Meaning = "\n".join(test_items) if test_items else ''
                new_result.Indicator = test_purpose

                # 处理数据项
                data_items = test_data.get('data_items', [])
                valid_items = data_items[:-1] if len(data_items) > 1 else data_items

                ranges = []
                for item in valid_items:
                    low, up = item.get('lowlimit', ''), item.get('uplimit', '')
                    if low and up:
                        ranges.append(f"{low},{up}")
                    elif low:
                        ranges.append(f"{low},")
                    elif up:
                        ranges.append(f",{up}")

                new_result.Range = " | ".join(ranges)
                new_result.Test_Value = " | ".join([item.get('data', '') for item in valid_items])
                new_result.Trend_Analysis = " | ".join([item.get('position_en', '') for item in valid_items])

                # 设置基本信息
                new_result.Test_Project = target_test_key
                new_result.Test_Result = "FAILED"

                return report

            def update_mic_report4(self, report,
                                   structured_failed_logs_dict,
                                   first_key=r'AUDIO_SAMPLE_MIC_\\d+_CONTIGUOUS_SPKR\\d+_\\d+-\\d+(?:_ASYNC_(START|WAIT))?.*FAILED',
                                   language='en',
                                   is_clear=False):
                """
                将结构化失败日志字典中的数据映射到测试报告的测试项目结果中

                参数:
                report (Report): 包含测试结果的Report对象
                structured_failed_logs_dict (dict): 包含详细测试数据的字典
                first_key (str): 用于匹配测试项的正则表达式
                language (str): 语言选择，默认'en'（英文），可传入'zh'使用中文
                is_clear (bool): 是否清空现有结果，True表示清空后添加，False表示在现有结果后新增

                返回:
                Report: 更新后的Report对象
                """
                # 查找目标测试项
                target_pattern_key = None
                target_test_key = None

                # 编译正则表达式模式 - 匹配AUDIO_SAMPLE_MIC_后跟数字，然后是任意内容和FAILED
                mic_failed_pattern = re.compile(first_key)

                for pattern_key in structured_failed_logs_dict:
                    for test_key in structured_failed_logs_dict[pattern_key]:
                        if mic_failed_pattern.search(test_key):
                            target_pattern_key = pattern_key
                            target_test_key = test_key
                            break
                    if target_test_key:
                        break

                if not target_test_key:
                    print("警告：未找到目标测试项")
                    return report

                # 获取测试数据
                test_data = structured_failed_logs_dict[target_pattern_key][target_test_key]

                # 处理StatusIndicators（与TestProjectResult逻辑保持一致）
                # 获取Report中的状态指示器列表，兼容两种JSON结构
                status_indicators_parent = report.Global_Overview.Status_Indicators
                # 检查父对象是列表还是包含列表的对象
                if isinstance(status_indicators_parent, list):
                    status_indicators = status_indicators_parent
                else:
                    # 如果是对象类型，则获取其内部的Status_Indicators列表
                    status_indicators = status_indicators_parent.Status_Indicators

                # 创建新的StatusIndicatorItem对象
                def create_new_status_item():
                    return StatusIndicatorItem(
                        item='',
                        state='',
                        color='',
                        show=True
                    )

                # 根据is_clear参数处理状态指示器列表
                if is_clear:
                    # 清空现有状态指示器并添加新项
                    status_indicators.clear()
                    new_status_item = create_new_status_item()
                    status_indicators.append(new_status_item)
                    print("已清空现有状态指示器并添加新项")
                else:
                    # 在现有状态指示器后新增
                    new_status_item = create_new_status_item()
                    status_indicators.append(new_status_item)

                # 填充新状态指示器的数据
                # 从测试数据中提取状态相关信息
                status_info = test_data.get('data_items', {})
                new_status_item.item = target_test_key  # 使用测试项作为状态名称
                # 判断状态：如果包含'FAILED'则返回'FAILED'，否则返回'PASS'
                state_value = status_info[0]['state'] if status_info else ''
                new_status_item.state = "FAILED" if 'FAILED' in state_value else "PASS"
                # 同步更新颜色
                new_status_item.color = "Red" if new_status_item.state == "FAILED" else "Green"
                new_status_item.show = True

                # 获取Report中的测试项目结果列表（包含TestProjectResult对象）
                test_project_results = report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results

                # 创建新的TestProjectResult对象（基于列表中已有对象的类型）
                def create_new_result():
                    return TestProjectResult(
                        Test_Project='',
                        Meaning='',
                        Indicator='',
                        Test_Value='',
                        Range='',
                        Test_Result='',
                        Trend_Analysis='',
                        Implied_Problem_Possibility='',
                        Chart_Name='',
                        Chart_Content=''
                    )

                # 根据is_clear参数处理结果列表
                if is_clear:
                    # 清空现有结果并添加新结果
                    test_project_results.clear()
                    new_result = create_new_result()
                    test_project_results.append(new_result)
                    print("已清空现有测试项目结果并添加新结果")
                else:
                    # 在现有结果后新增
                    new_result = create_new_result()
                    test_project_results.append(new_result)

                # 填充新结果的数据
                chart_items = test_data.get('chart_items', {})
                new_result.Chart_Name = chart_items.get('chart_name', '')
                new_result.Chart_Content = chart_items.get('base64_content', '')

                purpose2items = test_data.get('purpose2items', {})
                if language == 'zh':
                    test_items = purpose2items.get('test_items_zh', [])
                    test_purpose = purpose2items.get('test_purpose_zh', '')
                else:
                    test_items = purpose2items.get('test_items_en', [])
                    test_purpose = purpose2items.get('test_purpose_en', '')

                issue_suggestions_items = test_data.get('report_items', {})
                new_result.Implied_Problem_Possibility = (
                    issue_suggestions_items.get('chinese_failure_reasons_suggestion', '')
                    if language == 'zh'
                    else issue_suggestions_items.get('english_failure_reasons_suggestion', '')
                )

                # 1. 判断test_items是否为列表类型
                if isinstance(test_items, list):
                    # 若为列表：非空则用换行符连接所有元素，为空则赋值空字符串
                    new_result.Meaning = "\n".join(test_items) if test_items else ""
                else:
                    # 若不为列表（如字符串、数字、None等）：直接赋值原内容
                    new_result.Meaning = test_items
                new_result.Indicator = test_purpose

                # 处理数据项
                data_items = test_data.get('data_items', [])
                valid_items = data_items[:-1] if len(data_items) > 1 else data_items

                ranges = []
                for item in valid_items:
                    low, up = item.get('lowlimit', ''), item.get('uplimit', '')
                    if low and up:
                        ranges.append(f"{low},{up}")
                    elif low:
                        ranges.append(f"{low},")
                    elif up:
                        ranges.append(f",{up}")

                new_result.Range = " | ".join(ranges)
                new_result.Test_Value = " | ".join([item.get('data', '') for item in valid_items])
                new_result.Trend_Analysis = " | ".join([item.get('position_en', '') for item in valid_items])

                # 设置基本信息
                new_result.Test_Project = target_test_key
                new_result.Test_Result = "FAILED"

                return report


if __name__ == "__main__":
    # # debug:pass
    # # 创建 DataCleaner 实例，使用默认参数（这里实际不会初始化属性）
    # cleaner1 = DataCleaningAndFiltering.L2AR.DataCleaner()
    # mtk_comprehensive_patterns1 = cleaner1.get_patterns(TestSites.L2AR, Platforms.MTK, TestTypes.COMPREHENSIVE_TEST)
    #
    # # 创建 DataCleaner 实例，传入具体的参数
    # cleaner2 = DataCleaningAndFiltering.L2AR.DataCleaner(TestSites.L2AR, Platforms.MTK, TestTypes.COMPREHENSIVE_TEST)
    # mtk_comprehensive_patterns2 = cleaner2.get_patterns()

    # debug:pass
    cleaner1 = DataCleaningAndFiltering.L2AR.DataCleaner()

    # 现在 exception_error_container 是一个字典
    exception_error_container = {
        'Exception error': 'FAILED_LIMITS_CHECK',
        'Error code': '1',
        'Details': 'Additional information about the error'
    }

    # 获取中文翻译
    chinese_result = cleaner1.translate_exception_dict(exception_error_container, lang='zh')
    print("中文翻译结果:", chinese_result)
    # 输出: {'Exception error': '超出限制检查失败', 'Error code': '1', 'Details': 'Additional information about the error'}

    # 获取英文翻译
    english_result = cleaner1.translate_exception_dict(exception_error_container, lang='en')
    print("英文翻译结果:", english_result)
    # 输出: {'Exception error': 'Failed limits check', 'Error code': '1', 'Details': 'Additional information about the error'}
