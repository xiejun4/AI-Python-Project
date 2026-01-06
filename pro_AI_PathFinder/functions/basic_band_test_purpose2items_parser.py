import re
import json
import os
import sys
from typing import Dict, List, Any


class BasicBand_TestPurposeAndItems_parser:
    def __init__(self, config_file: str = "basic_band_test_purpose2items.json"):
        """
        初始化测试解析器，从当前项目的config目录加载合并后的JSON配置文件

        参数:
            config_file: 配置文件名称（默认：basic_band_test_purpose2items.json）
        """
        # 从项目的config文件夹加载配置文件
        config_path = self._get_config_path(config_file)
        self.config = self._load_config(config_path)
        self.all_pattern_configs = self.config.get("pattern_configs", [])
        self._init_param_extractors()

    # def _get_project_root(self) -> str:
    #     """获取当前文件所在的项目根目录"""
    #     current_file_path = os.path.abspath(__file__)
    #     current_dir = os.path.dirname(current_file_path)
    #
    #     # 项目根目录标志（可根据实际项目调整）
    #     project_markers = [".git", "requirements.txt", "setup.py", "pyproject.toml"]
    #
    #     while True:
    #         if any(os.path.exists(os.path.join(current_dir, marker)) for marker in project_markers):
    #             return current_dir
    #
    #         parent_dir = os.path.dirname(current_dir)
    #         if parent_dir == current_dir:  # 到达文件系统根目录
    #             return current_dir  # fallback
    #
    #         current_dir = parent_dir

    def _get_config_path(self, config_file: str) -> str:
        """构建项目根目录下config文件夹中配置文件的完整路径"""
        config_dir=None
        # 根据操作系统选择不同的配置路径
        if sys.platform.startswith('linux'):
            # Linux系统使用指定路径
            config_dir = os.path.join('/opt', 'xiejun4', 'pro_PathFinder', 'config')
        else:
            # Windows系统保持原有路径不变
            current_dir = os.path.dirname(__file__)
            parent_dir = os.path.dirname(current_dir)
            config_dir = os.path.join(parent_dir, "config")

        if not os.path.exists(config_dir):
            raise NotADirectoryError(f"项目的config目录不存在: {config_dir}")

        return os.path.join(config_dir, config_file)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载并解析JSON配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"未在config目录找到配置文件: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件格式错误: {config_path}")

    def _init_param_extractors(self):
        """初始化参数提取器映射，支持所有类型的参数提取"""
        self.param_extractors = {
            "basic": lambda match: {},
            "wattage_based": lambda match: {
                "wattage": match.group('wattage'),
                "wattage_unit": "W"
            },
            "subtype_based": lambda match: {
                "subtype": match.group('subtype')
            },
            "power_based": lambda match: {
                "spec_value": match.group('spec_value'),
                "spec_unit": "W"
            },
            "spec_based": lambda match: {
                "spec_value": match.group('spec_value')
            }
        }

    def _get_matched_config(self, normalized_param: str) -> Dict[str, Any]:
        """根据标准化参数查找匹配的配置"""
        for config in self.all_pattern_configs:
            if re.match(config["pattern"], normalized_param):
                return config
        # 未找到匹配配置时生成示例提示
        example_patterns = [config["pattern"].replace('^', '').replace('$', '')
                            for config in self.all_pattern_configs[:5]]  # 取前5个示例
        raise ValueError(
            f"无效的参数格式: {normalized_param}，示例：\n"
            + "\n".join([f"- {p}" for p in example_patterns])
        )

    def parse_test_parameters_v1(self, param: str) -> dict:
        """
        通用解析方法：根据输入参数自动匹配配置并生成测试说明
        当param与配置文件中的pattern匹配时，使用param中的参数或默认值处理相关字段
        """
        normalized_param = param.upper().replace(' ', '_')

        # 确定默认参数（覆盖所有可能的占位符，确保无遗漏）
        default_params = {
            "product": "未知产品",
            "device": "未知设备",
            "wattage": "默认",
            "wattage_unit": "",
            "subtype": "默认类型",
            "spec_value": "默认规格",
            "spec_unit": "",
            "param": normalized_param  # 保留原始参数作为备用
        }

        # 根据参数前缀优化默认设备/产品名称
        if normalized_param.startswith("QC_USIM"):
            default_params["device"] = "高通设备"
        elif normalized_param.startswith("ANDROID"):
            default_params["device"] = "Android设备"
        elif normalized_param.startswith(("MAGNETOMETER", "BATTERY", "CAP_SWITCH")):
            default_params["device"] = "移动设备"
        elif normalized_param.startswith(("SPK_INFO", "KEY_PART")):
            default_params["product"] = "音频设备"

        # 获取匹配的配置（核心：只要与pattern匹配就进行处理）
        config = self._get_matched_config(normalized_param)
        match = re.match(config["pattern"], normalized_param)
        if not match:
            raise ValueError(f"参数 {normalized_param} 与配置模式 {config['pattern']} 不匹配")

        # 提取参数（从正则匹配中获取所有命名分组）
        extracted_params = match.groupdict()

        # 补充单位参数（基于提取的参数和原始参数推断）
        if "wattage" in extracted_params:
            extracted_params["wattage_unit"] = "W"
        if "spec_value" in extracted_params and re.search(r'\d+W', normalized_param):
            extracted_params["spec_unit"] = "W"

        # 合并参数（提取的参数优先级高于默认值）
        params = {**default_params, **extracted_params}

        # 处理基础测试项（如果包含参数占位符则进行格式化）
        test_items_zh = [item.format(**params) for item in config["base_test_items_zh"].copy()]
        test_items_en = [item.format(**params) for item in config["base_test_items_en"].copy()]

        # 添加额外测试项（如有）
        if "additional_items" in config:
            try:
                add_items_zh = [item.format(**params) for item in config["additional_items"]["zh"]]
                add_items_en = [item.format(**params) for item in config["additional_items"]["en"]]
            except KeyError as e:
                raise ValueError(f"格式化额外测试项时缺少参数: {str(e)}, 参数: {params}")

            pos = config["additional_items"]["insert_pos"]
            if pos == -1:
                test_items_zh.extend(add_items_zh)
                test_items_en.extend(add_items_en)
            else:
                for i, item in enumerate(add_items_zh):
                    test_items_zh.insert(pos + i, item)
                for i, item in enumerate(add_items_en):
                    test_items_en.insert(pos + i, item)

        # 处理功率相关扩展测试项（SPK_INFO_PROGAMMING_POWER模式）
        if "power_based_items" in config and "spec_value" in params:
            try:
                power = int(params["spec_value"])
                power_level = "high" if power >= 5 else "low" if power < 1 else None
                if power_level:
                    items_zh = [item.format(**params) for item in config["power_based_items"][power_level]["zh"]]
                    items_en = [item.format(**params) for item in config["power_based_items"][power_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理充电功率相关扩展测试项（CAP_SWITCH_TURBO模式）
        if "wattage_based_items" in config and "wattage" in params:
            try:
                wattage = int(params["wattage"])
                watt_level = "high" if wattage >= 60 else "low" if wattage < 30 else None
                if watt_level:
                    items_zh = [item.format(**params) for item in config["wattage_based_items"][watt_level]["zh"]]
                    items_en = [item.format(**params) for item in config["wattage_based_items"][watt_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理规格相关扩展测试项（KEY_PART_MATCH_SPEC模式）
        if "spec_based_items" in config and "spec_value" in params:
            try:
                spec_val = params["spec_value"].lower()
                if spec_val in ["high", "low"]:
                    items_zh = [item.format(**params) for item in config["spec_based_items"][spec_val]["zh"]]
                    items_en = [item.format(**params) for item in config["spec_based_items"][spec_val]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except KeyError:
                pass  # 忽略格式错误，使用基础测试项

        # 生成并返回最终测试说明（确保所有占位符都被替换）
        try:
            return {
                "test_purpose_zh": config["test_purpose_zh"].format(**params),
                "test_items_zh": test_items_zh,
                "test_purpose_en": config["test_purpose_en"].format(**params),
                "test_items_en": test_items_en
            }
        except KeyError as e:
            raise ValueError(
                f"格式化测试目的时缺少参数: {str(e)}, "
                f"参数集合: {params}, "
                f"匹配模式: {config['pattern']}"
            )
    def parse_test_parameters_v2(self, param: str) -> dict:
        """
        通用解析方法：根据输入参数自动匹配配置并生成测试说明
        当param与配置文件中的pattern匹配时，使用param中的参数或默认值处理相关字段
        """
        normalized_param = param.upper().replace(' ', '_')

        # 确定默认参数（覆盖所有可能的占位符，确保无遗漏）
        default_params = {
            "product": "未知产品",
            "device": "未知设备",
            "wattage": "默认",
            "wattage_unit": "",
            "subtype": "默认类型",
            "spec_value": "默认规格",
            "spec_unit": "",
            "param": normalized_param  # 保留原始参数作为备用
        }

        # 根据参数前缀优化默认设备/产品名称
        if normalized_param.startswith("QC_USIM"):
            default_params["device"] = "高通设备"
        elif normalized_param.startswith("ANDROID"):
            default_params["device"] = "Android设备"
        elif normalized_param.startswith(("MAGNETOMETER", "BATTERY", "CAP_SWITCH", "CAP_SENSOR")):
            # 新增CAP_SENSOR前缀匹配，归类为移动设备
            default_params["device"] = "移动设备"
        elif normalized_param.startswith(("SPK_INFO", "KEY_PART")):
            default_params["product"] = "音频设备"

        # 针对CAP_SENSOR_DETECT_STATUS的特殊处理
        if normalized_param == "CAP_SENSOR_DETECT_STATUS":
            default_params["product"] = "电容传感器设备"
            default_params["subtype"] = "检测状态"

        # 获取匹配的配置（核心：只要与pattern匹配就进行处理）
        config = self._get_matched_config(normalized_param)
        match = re.match(config["pattern"], normalized_param)
        if not match:
            raise ValueError(f"参数 {normalized_param} 与配置模式 {config['pattern']} 不匹配")

        # 提取参数（从正则匹配中获取所有命名分组）
        extracted_params = match.groupdict()

        # 补充单位参数（基于提取的参数和原始参数推断）
        if "wattage" in extracted_params:
            extracted_params["wattage_unit"] = "W"
        if "spec_value" in extracted_params and re.search(r'\d+W', normalized_param):
            extracted_params["spec_unit"] = "W"

        # 合并参数（提取的参数优先级高于默认值）
        params = {**default_params, **extracted_params}

        # 处理基础测试项（如果包含参数占位符则进行格式化）
        test_items_zh = [item.format(**params) for item in config["base_test_items_zh"].copy()]
        test_items_en = [item.format(**params) for item in config["base_test_items_en"].copy()]

        # 添加额外测试项（如有）
        if "additional_items" in config:
            try:
                add_items_zh = [item.format(**params) for item in config["additional_items"]["zh"]]
                add_items_en = [item.format(**params) for item in config["additional_items"]["en"]]
            except KeyError as e:
                raise ValueError(f"格式化额外测试项时缺少参数: {str(e)}, 参数: {params}")

            pos = config["additional_items"]["insert_pos"]
            if pos == -1:
                test_items_zh.extend(add_items_zh)
                test_items_en.extend(add_items_en)
            else:
                for i, item in enumerate(add_items_zh):
                    test_items_zh.insert(pos + i, item)
                for i, item in enumerate(add_items_en):
                    test_items_en.insert(pos + i, item)

        # 处理功率相关扩展测试项（SPK_INFO_PROGAMMING_POWER模式）
        if "power_based_items" in config and "spec_value" in params:
            try:
                power = int(params["spec_value"])
                power_level = "high" if power >= 5 else "low" if power < 1 else None
                if power_level:
                    items_zh = [item.format(**params) for item in config["power_based_items"][power_level]["zh"]]
                    items_en = [item.format(**params) for item in config["power_based_items"][power_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理充电功率相关扩展测试项（CAP_SWITCH_TURBO模式）
        if "wattage_based_items" in config and "wattage" in params:
            try:
                wattage = int(params["wattage"])
                watt_level = "high" if wattage >= 60 else "low" if wattage < 30 else None
                if watt_level:
                    items_zh = [item.format(**params) for item in config["wattage_based_items"][watt_level]["zh"]]
                    items_en = [item.format(**params) for item in config["wattage_based_items"][watt_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理规格相关扩展测试项（KEY_PART_MATCH_SPEC模式）
        if "spec_based_items" in config and "spec_value" in params:
            try:
                spec_val = params["spec_value"].lower()
                if spec_val in ["high", "low"]:
                    items_zh = [item.format(**params) for item in config["spec_based_items"][spec_val]["zh"]]
                    items_en = [item.format(**params) for item in config["spec_based_items"][spec_val]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except KeyError:
                pass  # 忽略格式错误，使用基础测试项

        # 为CAP_SENSOR_DETECT_STATUS添加专用测试项
        if normalized_param == "CAP_SENSOR_DETECT_STATUS":
            # 添加传感器检测状态相关的测试项
            sensor_items_zh = [
                "验证传感器在不同环境条件下的检测准确性",
                "检查传感器状态报告的实时性和稳定性",
                "测试传感器在边缘条件下的响应能力"
            ]
            sensor_items_en = [
                "Verify the detection accuracy of the sensor under different environmental conditions",
                "Check the real-time performance and stability of sensor status reporting",
                "Test the response capability of the sensor under edge conditions"
            ]
            test_items_zh.extend(sensor_items_zh)
            test_items_en.extend(sensor_items_en)

        # 生成并返回最终测试说明（确保所有占位符都被替换）
        try:
            return {
                "test_purpose_zh": config["test_purpose_zh"].format(**params),
                "test_items_zh": test_items_zh,
                "test_purpose_en": config["test_purpose_en"].format(**params),
                "test_items_en": test_items_en
            }
        except KeyError as e:
            raise ValueError(
                f"格式化测试目的时缺少参数: {str(e)}, "
                f"参数集合: {params}, "
                f"匹配模式: {config['pattern']}"
            )
    def parse_test_parameters_v3(self, param: str) -> dict:
        """
        通用解析方法：根据输入参数自动匹配配置并生成测试说明
        当param与配置文件中的pattern匹配时，使用param中的参数或默认值处理相关字段
        """
        normalized_param = param.upper().replace(' ', '_')

        # 确定默认参数（覆盖所有可能的占位符，确保无遗漏）
        default_params = {
            "product": "未知产品",
            "device": "未知设备",
            "wattage": "默认",
            "wattage_unit": "",
            "subtype": "默认类型",
            "spec_value": "默认规格",
            "spec_unit": "",
            "code": "未知型号",  # 新增code参数默认值，用于匹配型号编码
            "param": normalized_param  # 保留原始参数作为备用
        }

        # 根据参数前缀优化默认设备/产品名称
        if normalized_param.startswith("QC_USIM"):
            default_params["device"] = "高通设备"
        elif normalized_param.startswith("ANDROID"):
            default_params["device"] = "Android设备"
        elif normalized_param.startswith(("MAGNETOMETER", "BATTERY", "CAP_SWITCH", "CAP_SENSOR", "CAP_COMP")):
            # 新增CAP_COMP前缀匹配，归类为移动设备
            default_params["device"] = "移动设备"
        elif normalized_param.startswith(("SPK_INFO", "KEY_PART")):
            default_params["product"] = "音频设备"

        # 针对电容组件相关参数的特殊处理
        if normalized_param.startswith("CAP_COMP"):
            default_params["product"] = "电容组件模块"
            # 根据具体参数类型设置更精确的子类型
            if normalized_param.startswith("CAP_COMP_ASM_VALUE"):
                default_params["subtype"] = "装配值检测"
            elif normalized_param.startswith("CAP_COMP_BRD_VS_ASM_VALUE"):
                default_params["subtype"] = "板载值与装配值对比"
            elif normalized_param.startswith("CAP_COMP_BRD_VALUE"):
                default_params["subtype"] = "板载值检测"
            elif normalized_param.startswith("CAP_COMP_DIFF_IDAC_VALUE"):
                default_params["subtype"] = "差分IDAC值检测"

        # 针对CAP_SENSOR_DETECT_STATUS的特殊处理
        if normalized_param == "CAP_SENSOR_DETECT_STATUS":
            default_params["product"] = "电容传感器设备"
            default_params["subtype"] = "检测状态"

        # 获取匹配的配置（核心：只要与pattern匹配就进行处理）
        config = self._get_matched_config(normalized_param)
        match = re.match(config["pattern"], normalized_param)
        if not match:
            raise ValueError(f"参数 {normalized_param} 与配置模式 {config['pattern']} 不匹配")

        # 提取参数（从正则匹配中获取所有命名分组）
        extracted_params = match.groupdict()

        # 从参数中提取型号编码（针对电容组件系列参数）
        if normalized_param.startswith("CAP_COMP"):
            # 提取末尾的型号编码（2位字母数字组合）
            code_match = re.search(r'[0-9A-Z]{2}$', normalized_param)
            if code_match:
                extracted_params["code"] = code_match.group()

        # 补充单位参数（基于提取的参数和原始参数推断）
        if "wattage" in extracted_params:
            extracted_params["wattage_unit"] = "W"
        if "spec_value" in extracted_params and re.search(r'\d+W', normalized_param):
            extracted_params["spec_unit"] = "W"
        # 为电容值相关参数添加单位推断
        if normalized_param.startswith("CAP_COMP") and "spec_value" in extracted_params:
            if not extracted_params.get("spec_unit"):
                extracted_params["spec_unit"] = "pF"  # 电容默认单位为皮法

        # 合并参数（提取的参数优先级高于默认值）
        params = {**default_params, **extracted_params}

        # 处理基础测试项（如果包含参数占位符则进行格式化）
        test_items_zh = [item.format(**params) for item in config["base_test_items_zh"].copy()]
        test_items_en = [item.format(**params) for item in config["base_test_items_en"].copy()]

        # 添加额外测试项（如有）
        if "additional_items" in config:
            try:
                add_items_zh = [item.format(**params) for item in config["additional_items"]["zh"]]
                add_items_en = [item.format(**params) for item in config["additional_items"]["en"]]
            except KeyError as e:
                raise ValueError(f"格式化额外测试项时缺少参数: {str(e)}, 参数: {params}")

            pos = config["additional_items"]["insert_pos"]
            if pos == -1:
                test_items_zh.extend(add_items_zh)
                test_items_en.extend(add_items_en)
            else:
                for i, item in enumerate(add_items_zh):
                    test_items_zh.insert(pos + i, item)
                for i, item in enumerate(add_items_en):
                    test_items_en.insert(pos + i, item)

        # 处理功率相关扩展测试项（SPK_INFO_PROGAMMING_POWER模式）
        if "power_based_items" in config and "spec_value" in params:
            try:
                power = int(params["spec_value"])
                power_level = "high" if power >= 5 else "low" if power < 1 else None
                if power_level:
                    items_zh = [item.format(**params) for item in config["power_based_items"][power_level]["zh"]]
                    items_en = [item.format(**params) for item in config["power_based_items"][power_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理充电功率相关扩展测试项（CAP_SWITCH_TURBO模式）
        if "wattage_based_items" in config and "wattage" in params:
            try:
                wattage = int(params["wattage"])
                watt_level = "high" if wattage >= 60 else "low" if wattage < 30 else None
                if watt_level:
                    items_zh = [item.format(**params) for item in config["wattage_based_items"][watt_level]["zh"]]
                    items_en = [item.format(**params) for item in config["wattage_based_items"][watt_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理规格相关扩展测试项（KEY_PART_MATCH_SPEC模式）
        if "spec_based_items" in config and "spec_value" in params:
            try:
                spec_val = params["spec_value"].lower()
                if spec_val in ["high", "low"]:
                    items_zh = [item.format(**params) for item in config["spec_based_items"][spec_val]["zh"]]
                    items_en = [item.format(**params) for item in config["spec_based_items"][spec_val]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except KeyError:
                pass  # 忽略格式错误，使用基础测试项

        # 为CAP_SENSOR_DETECT_STATUS添加专用测试项
        if normalized_param == "CAP_SENSOR_DETECT_STATUS":
            # 添加传感器检测状态相关的测试项
            sensor_items_zh = [
                "验证传感器在不同环境条件下的检测准确性",
                "检查传感器状态报告的实时性和稳定性",
                "测试传感器在边缘条件下的响应能力"
            ]
            sensor_items_en = [
                "Verify the detection accuracy of the sensor under different environmental conditions",
                "Check the real-time performance and stability of sensor status reporting",
                "Test the response capability of the sensor under edge conditions"
            ]
            test_items_zh.extend(sensor_items_zh)
            test_items_en.extend(sensor_items_en)

        # 生成并返回最终测试说明（确保所有占位符都被替换）
        try:
            return {
                "test_purpose_zh": config["test_purpose_zh"].format(**params),
                "test_items_zh": test_items_zh,
                "test_purpose_en": config["test_purpose_en"].format(**params),
                "test_items_en": test_items_en
            }
        except KeyError as e:
            raise ValueError(
                f"格式化测试目的时缺少参数: {str(e)}, "
                f"参数集合: {params}, "
                f"匹配模式: {config['pattern']}"
            )
    def parse_test_parameters(self, param: str) -> dict:
        """
        通用解析方法：根据输入参数自动匹配配置并生成测试说明
        当param与配置文件中的pattern匹配时，使用param中的参数或默认值处理相关字段
        """
        normalized_param = param.upper().replace(' ', '_')

        # 确定默认参数（覆盖所有可能的占位符，确保无遗漏）
        default_params = {
            "product": "未知产品",
            "device": "未知设备",
            "wattage": "默认",
            "wattage_unit": "",
            "subtype": "默认类型",
            "spec_value": "默认规格",
            "spec_unit": "",
            "code": "未知型号",  # 新增code参数默认值，用于匹配型号编码
            "param": normalized_param,  # 保留原始参数作为备用
            "mode_code": "默认模式",  # 新增：用于ONLINE_MODE的模式编码
            "verify_code": "默认验证"  # 新增：用于ONLINE_MODE_VERIFY的验证编码
        }

        # 根据参数前缀优化默认设备/产品名称
        if normalized_param.startswith("QC_USIM"):
            default_params["device"] = "高通设备"
        elif normalized_param.startswith("ANDROID"):
            default_params["device"] = "Android设备"
        elif normalized_param.startswith(("MAGNETOMETER", "BATTERY", "CAP_SWITCH", "CAP_SENSOR", "CAP_COMP")):
            # 新增CAP_COMP前缀匹配，归类为移动设备
            default_params["device"] = "移动设备"
        elif normalized_param.startswith(("SPK_INFO", "KEY_PART")):
            default_params["product"] = "音频设备"
        # 新增ONLINE_MODE相关参数的默认设备设置
        elif normalized_param.startswith("ONLINE_MODE"):
            default_params["device"] = "网络设备"
            default_params["product"] = "在线模式模块"

        # 针对电容组件相关参数的特殊处理
        if normalized_param.startswith("CAP_COMP"):
            default_params["product"] = "电容组件模块"
            # 根据具体参数类型设置更精确的子类型
            if normalized_param.startswith("CAP_COMP_ASM_VALUE"):
                default_params["subtype"] = "装配值检测"
            elif normalized_param.startswith("CAP_COMP_BRD_VS_ASM_VALUE"):
                default_params["subtype"] = "板载值与装配值对比"
            elif normalized_param.startswith("CAP_COMP_BRD_VALUE"):
                default_params["subtype"] = "板载值检测"
            elif normalized_param.startswith("CAP_COMP_DIFF_IDAC_VALUE"):
                default_params["subtype"] = "差分IDAC值检测"

        # 针对CAP_SENSOR_DETECT_STATUS的特殊处理
        if normalized_param == "CAP_SENSOR_DETECT_STATUS":
            default_params["product"] = "电容传感器设备"
            default_params["subtype"] = "检测状态"

        # 针对ONLINE_MODE相关参数的特殊处理
        if normalized_param.startswith("ONLINE_MODE"):
            default_params["subtype"] = "在线模式验证"
            # 提取模式编码（1-2位字母数字组合）
            mode_code_match = re.search(r'[0-9A-Z]{1,2}$', normalized_param)
            if mode_code_match:
                default_params["mode_code"] = mode_code_match.group()

            # 针对验证类型的特殊处理
            if normalized_param.startswith("ONLINE_MODE_VERIFY"):
                default_params["subtype"] = "在线模式验证检查"
                # 提取验证编码（1位字母数字）
                verify_code_match = re.search(r'[0-9A-Z]{1,2}$', normalized_param)
                if verify_code_match:
                    default_params["verify_code"] = verify_code_match.group()

        # 获取匹配的配置（核心：只要与pattern匹配就进行处理）
        config = self._get_matched_config(normalized_param)
        match = re.match(config["pattern"], normalized_param)
        if not match:
            raise ValueError(f"参数 {normalized_param} 与配置模式 {config['pattern']} 不匹配")

        # 提取参数（从正则匹配中获取所有命名分组）
        extracted_params = match.groupdict()

        # 从参数中提取型号编码（针对电容组件系列参数）
        if normalized_param.startswith("CAP_COMP"):
            # 提取末尾的型号编码（2位字母数字组合）
            code_match = re.search(r'[0-9A-Z]{1,2}$', normalized_param)
            if code_match:
                extracted_params["code"] = code_match.group()

        # 补充单位参数（基于提取的参数和原始参数推断）
        if "wattage" in extracted_params:
            extracted_params["wattage_unit"] = "W"
        if "spec_value" in extracted_params and re.search(r'\d+W', normalized_param):
            extracted_params["spec_unit"] = "W"
        # 为电容值相关参数添加单位推断
        if normalized_param.startswith("CAP_COMP") and "spec_value" in extracted_params:
            if not extracted_params.get("spec_unit"):
                extracted_params["spec_unit"] = "pF"  # 电容默认单位为皮法

        # 合并参数（提取的参数优先级高于默认值）
        params = {**default_params, **extracted_params}

        # 处理基础测试项（如果包含参数占位符则进行格式化）
        test_items_zh = [item.format(**params) for item in config["base_test_items_zh"].copy()]
        test_items_en = [item.format(**params) for item in config["base_test_items_en"].copy()]

        # 添加额外测试项（如有）
        if "additional_items" in config:
            try:
                add_items_zh = [item.format(**params) for item in config["additional_items"]["zh"]]
                add_items_en = [item.format(**params) for item in config["additional_items"]["en"]]
            except KeyError as e:
                raise ValueError(f"格式化额外测试项时缺少参数: {str(e)}, 参数: {params}")

            pos = config["additional_items"]["insert_pos"]
            if pos == -1:
                test_items_zh.extend(add_items_zh)
                test_items_en.extend(add_items_en)
            else:
                for i, item in enumerate(add_items_zh):
                    test_items_zh.insert(pos + i, item)
                for i, item in enumerate(add_items_en):
                    test_items_en.insert(pos + i, item)

        # 处理功率相关扩展测试项（SPK_INFO_PROGAMMING_POWER模式）
        if "power_based_items" in config and "spec_value" in params:
            try:
                power = int(params["spec_value"])
                power_level = "high" if power >= 5 else "low" if power < 1 else None
                if power_level:
                    items_zh = [item.format(**params) for item in config["power_based_items"][power_level]["zh"]]
                    items_en = [item.format(**params) for item in config["power_based_items"][power_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理充电功率相关扩展测试项（CAP_SWITCH_TURBO模式）
        if "wattage_based_items" in config and "wattage" in params:
            try:
                wattage = int(params["wattage"])
                watt_level = "high" if wattage >= 60 else "low" if wattage < 30 else None
                if watt_level:
                    items_zh = [item.format(**params) for item in config["wattage_based_items"][watt_level]["zh"]]
                    items_en = [item.format(**params) for item in config["wattage_based_items"][watt_level]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except (ValueError, KeyError):
                pass  # 忽略格式错误，使用基础测试项

        # 处理规格相关扩展测试项（KEY_PART_MATCH_SPEC模式）
        if "spec_based_items" in config and "spec_value" in params:
            try:
                spec_val = params["spec_value"].lower()
                if spec_val in ["high", "low"]:
                    items_zh = [item.format(**params) for item in config["spec_based_items"][spec_val]["zh"]]
                    items_en = [item.format(**params) for item in config["spec_based_items"][spec_val]["en"]]
                    test_items_zh.extend(items_zh)
                    test_items_en.extend(items_en)
            except KeyError:
                pass  # 忽略格式错误，使用基础测试项

        # 为CAP_SENSOR_DETECT_STATUS添加专用测试项
        if normalized_param == "CAP_SENSOR_DETECT_STATUS":
            # 添加传感器检测状态相关的测试项
            sensor_items_zh = [
                "验证传感器在不同环境条件下的检测准确性",
                "检查传感器状态报告的实时性和稳定性",
                "测试传感器在边缘条件下的响应能力"
            ]
            sensor_items_en = [
                "Verify the detection accuracy of the sensor under different environmental conditions",
                "Check the real-time performance and stability of sensor status reporting",
                "Test the response capability of the sensor under edge conditions"
            ]
            test_items_zh.extend(sensor_items_zh)
            test_items_en.extend(sensor_items_en)

        # 为ONLINE_MODE相关参数添加专用测试项
        if normalized_param.startswith("ONLINE_MODE"):
            online_items_zh = [
                f"验证{params['product']}在{params['mode_code']}模式下的在线连接稳定性",
                f"测试{params['device']}在网络波动时的模式切换能力",
                f"检查{params['mode_code']}模式下的功耗表现与设计规格的一致性"
            ]
            online_items_en = [
                f"Verify the online connection stability of {params['product']} in {params['mode_code']} mode",
                f"Test the mode switching capability of {params['device']} during network fluctuations",
                f"Check the consistency between power consumption performance and design specifications in {params['mode_code']} mode"
            ]

            # 为验证类型添加额外测试项
            if normalized_param.startswith("ONLINE_MODE_VERIFY"):
                verify_items_zh = [
                    f"验证{params['verify_code']}类型的在线模式切换指令响应时间",
                    f"测试异常网络环境下{params['verify_code']}验证机制的可靠性"
                ]
                verify_items_en = [
                    f"Verify the response time of {params['verify_code']} type online mode switching commands",
                    f"Test the reliability of {params['verify_code']} verification mechanism in abnormal network environments"
                ]
                online_items_zh.extend(verify_items_zh)
                online_items_en.extend(verify_items_en)

            test_items_zh.extend(online_items_zh)
            test_items_en.extend(online_items_en)

        # 生成并返回最终测试说明（确保所有占位符都被替换）
        try:
            return {
                "test_purpose_zh": config["test_purpose_zh"].format(**params),
                "test_items_zh": test_items_zh,
                "test_purpose_en": config["test_purpose_en"].format(**params),
                "test_items_en": test_items_en
            }
        except KeyError as e:
            raise ValueError(
                f"格式化测试目的时缺少参数: {str(e)}, "
                f"参数集合: {params}, "
                f"匹配模式: {config['pattern']}"
            )

# 使用示例
if __name__ == "__main__":
    try:
        parser = BasicBand_TestPurposeAndItems_parser()

        # 测试电容开关解析
        print("=== 电容开关测试 ===")
        cap_result = parser.parse_test_parameters("Cap_Switch_Turbo_Cap_Switch_Chg_Curr_65W")
        print("中文测试目的:")
        print(cap_result["test_purpose_zh"])
        print("\n中文测试项:")
        for item in cap_result["test_items_zh"]:
            print(item)

        # 测试first_vatt模式解析
        print("\n=== First VATT模式测试 ===")
        vatt_result = parser.parse_test_parameters("CAP_SWITCH_TURBO_CHARGER_FIRST_VATT_65W")
        print("中文测试目的:")
        print(vatt_result["test_purpose_zh"])
        print("\n中文测试项:")
        for item in vatt_result["test_items_zh"]:
            print(item)

        # 测试扬声器信息解析
        print("\n=== 扬声器信息测试 ===")
        spk_result = parser.parse_test_parameters("SPK_INFO_PROGAMMING_POWER_10W")
        print("中文测试目的:")
        print(spk_result["test_purpose_zh"])
        print("\n中文测试项:")
        for item in spk_result["test_items_zh"]:
            print(item)

        # 测试磁力计解析
        print("\n=== 磁力计测试 ===")
        mag_result = parser.parse_test_parameters("MAGNETOMETER_X_AXIS_ABSOLUTE_MAG_FIELD_APK")
        print("中文测试目的:")
        print(mag_result["test_purpose_zh"])
        print("\n中文测试项:")
        for item in mag_result["test_items_zh"]:
            print(item)

        # 测试电池状态解析
        print("\n=== 电池状态测试 ===")
        bat_result = parser.parse_test_parameters("GET_BATTERY_CHARGE_LEVEL_STATUS")
        print("中文测试目的:")
        print(bat_result["test_purpose_zh"])
        print("\n中文测试项:")
        for item in bat_result["test_items_zh"]:
            print(item)

    except (ValueError, NotADirectoryError) as e:
        print(e)