import json
import os
import re
import sys
from dataclasses import (
    dataclass, field, asdict, replace)

from functions.JsonDataEntity_L2AR import (
    StatusIndicatorItem,
    StatusIndicators,
    # KeyConclusionSummary,
    GlobalOverview,
    TestProjectResult,
    TestAnalysis,
    ModularTestResultsDisplay,
    # OptimizationSuggestionsOrSolutions,
    Report,
    REGEX_PATTERNS_For_Status_Indicators
)


class JsonUtil:
    class L2AR:

        def __init__(self):
            pass

        # 添加json_file_path属性
        json_template_file = "Pathfinder-TestReport-L2AR-Jason-En.json"

        def read_json_file(self, file_path):
            """读取JSON文件内容并返回解析后的字典或列表"""
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_content = json.load(file)
                    return json_content
            except FileNotFoundError:
                print(f"错误：文件 '{file_path}' 未找到")
                return None
            except json.JSONDecodeError:
                print(f"错误：文件 '{file_path}' 不是有效的JSON格式")
                return None
            except Exception as e:
                print(f"错误：读取文件时发生意外错误: {e}")
                return None

        def convert_json_to_object(self, file_path: str, is_clear=True) -> Report:
            """

            改函数将json文件序列化为report类

            :param json_file_path: json文件路径
            :return: report类

            """
            if is_clear:
                if os.name == 'nt': # Windows
                    temp_json_file_path = fr'.\uploads\{file_path}'
                else: # Linux
                    temp_json_file_path = f'/opt/xiejun4/pro_PathFinder/uploads/{file_path}'
            else:
                temp_json_file_path = file_path

            json_file_directory = os.path.dirname(temp_json_file_path)
            json_filename_with_ext = os.path.basename(file_path)
            json_filename, json_file_extension = os.path.splitext(json_filename_with_ext)
            # 根据操作系统使用不同的路径分隔符
            if os.name == 'nt':  # Windows
                json_file_full_path = f"{json_file_directory}\\{json_filename}{json_file_extension}"
            else:  # Linux 或其他类 Unix 系统
                json_file_full_path = f"{json_file_directory}/{json_filename}{json_file_extension}"

            with open(json_file_full_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            report_theme = data['Report_Theme']

            status_indicators = StatusIndicators(**data['Global_Overview']['Status_Indicators'])
            # key_conclusion_summary = KeyConclusionSummary(**data['Global_Overview']['Key_Conclusion_Summary'])
            # global_overview = GlobalOverview(status_indicators, key_conclusion_summary)
            global_overview = GlobalOverview(status_indicators)

            test_project_results = [TestProjectResult(**result) for result in
                                    data['Modular_Test_Results_Display']['Test_Analysis']['Test_Project_Results']]
            # test_project_results2analysis_logic_chain = TestAnalysis(test_project_results,
            #                                                          data['Modular_Test_Results_Display']['Test_Analysis']['Analysis_Logic_Chain'])
            # modular_test_results_display = ModularTestResultsDisplay(test_project_results2analysis_logic_chain)
            #
            # optimization_suggestions = OptimizationSuggestionsOrSolutions(
            #     data['Optimization_Suggestions_or_Solutions']['Emergency_Plan'],
            #     data['Optimization_Suggestions_or_Solutions']['Radical_Solution'])

            return Report(report_theme, global_overview, None, None)

        def convert_json_to_object2(self, file_path: str, is_clear=True) -> Report:
            """
            该函数将json文件序列化为Report类

            :param file_path: json文件路径
            :param is_clear: 是否使用默认路径处理
            :return: Report类实例
            """
            if is_clear:
                if os.name == 'nt':  # Windows
                    temp_json_file_path = fr'.\uploads\{file_path}'
                else:  # Linux
                    temp_json_file_path = f'/opt/xiejun4/pro_PathFinder/uploads/{file_path}'
            else:
                temp_json_file_path = file_path

            json_file_directory = os.path.dirname(temp_json_file_path)
            json_filename_with_ext = os.path.basename(file_path)
            json_filename, json_file_extension = os.path.splitext(json_filename_with_ext)

            # 根据操作系统使用不同的路径分隔符
            if os.name == 'nt':  # Windows
                json_file_full_path = f"{json_file_directory}\\{json_filename}{json_file_extension}"
            else:  # Linux 或其他类 Unix 系统
                json_file_full_path = f"{json_file_directory}/{json_filename}{json_file_extension}"

            with open(json_file_full_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            report_theme = data['Report_Theme']

            # 处理状态指示器列表 - 添加异常处理
            status_indicator_items = []
            required_fields = ['item', 'state', 'color', 'show']  # StatusIndicatorItem的必填字段

            try:
                # 获取状态指示器数据，兼容字典和列表类型
                status_indicators_data = data['Global_Overview']['Status_Indicators']

                # 如果是字典，获取第一个key对应的列表；如果是列表，直接使用
                if isinstance(status_indicators_data, dict):
                    # 获取第一个key对应的列表（按字典键的插入顺序）
                    first_key = next(iter(status_indicators_data.keys()))
                    indicators_data = status_indicators_data[first_key]
                    print(f"检测到Status_Indicators为字典类型，使用第一个键'{first_key}'对应的列表数据")
                elif isinstance(status_indicators_data, list):
                    indicators_data = status_indicators_data
                    print("检测到Status_Indicators为列表类型，直接使用列表数据")
                else:
                    raise TypeError(
                        f"Status_Indicators数据类型错误，期望dict或list，实际为{type(status_indicators_data)}")

                # 验证获取到的数据是否为列表
                if not isinstance(indicators_data, list):
                    raise TypeError(f"状态指示器数据应为列表类型，实际为{type(indicators_data)}")

                for item in indicators_data:
                    # 检查是否包含所有必填字段
                    missing_fields = [field for field in required_fields if field not in item]
                    if missing_fields:
                        raise ValueError(f"状态指示器项缺少必要字段: {', '.join(missing_fields)}")

                    # 检查show字段是否为布尔值
                    if not isinstance(item.get('show', False), bool):
                        raise TypeError(f"状态指示器项 '{item.get('item')}' 的show字段必须是布尔值")

                    # 创建StatusIndicatorItem实例
                    status_indicator_items.append(StatusIndicatorItem(**item))

            except KeyError as e:
                raise KeyError(f"JSON数据结构错误，缺少键: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"处理状态指示器时出错: {str(e)}")

            status_indicators = StatusIndicators(Status_Indicators=status_indicator_items)

            # 处理关键结论摘要
            # key_conclusion_summary = KeyConclusionSummary(
            #     **data['Global_Overview']['Key_Conclusion_Summary']
            # )
            # global_overview = GlobalOverview(
            #     Status_Indicators=status_indicators,
            #     Key_Conclusion_Summary=key_conclusion_summary
            # )
            global_overview = GlobalOverview(
                Status_Indicators=status_indicators
            )


            # 处理测试项目结果
            test_project_results = [
                TestProjectResult(**result)
                for result in data['Modular_Test_Results_Display']['Test_Analysis']['Test_Project_Results']
            ]
            # test_analysis = TestAnalysis(
            #     Test_Project_Results=test_project_results,
            #     Analysis_Logic_Chain=data['Modular_Test_Results_Display']['Test_Analysis']['Analysis_Logic_Chain']
            # )
            # modular_test_results_display = ModularTestResultsDisplay(
            #     Test_Analysis=test_analysis
            # )

            # # 处理优化建议
            # optimization_suggestions = OptimizationSuggestionsOrSolutions(
            #     Emergency_Plan=data['Optimization_Suggestions_or_Solutions']['Emergency_Plan'],
            #     Radical_Solution=data['Optimization_Suggestions_or_Solutions']['Radical_Solution']
            # )

            return Report(
                Report_Theme=report_theme,
                Global_Overview=global_overview,
                Modular_Test_Results_Display=None,
                Optimization_Suggestions_or_Solutions=None
            )

        def convert_json_to_object3(self, file_path: str, is_clear=True) -> Report:
            """
            该函数将json文件序列化为Report类，确保正确处理Status_Indicators结构，避免不必要的嵌套

            :param file_path: json文件路径
            :param is_clear: 是否使用默认路径处理
            :return: Report类实例
            """
            if is_clear:
                if os.name == 'nt':  # Windows
                    temp_json_file_path = fr'.\uploads\{file_path}'
                else:  # Linux
                    temp_json_file_path = f'/opt/xiejun4/pro_PathFinder/uploads/{file_path}'
            else:
                temp_json_file_path = file_path

            json_file_directory = os.path.dirname(temp_json_file_path)
            json_filename_with_ext = os.path.basename(file_path)
            json_filename, json_file_extension = os.path.splitext(json_filename_with_ext)

            # 根据操作系统使用不同的路径分隔符
            if os.name == 'nt':  # Windows
                json_file_full_path = f"{json_file_directory}\\{json_filename}{json_file_extension}"
            else:  # Linux 或其他类 Unix 系统
                json_file_full_path = f"{json_file_directory}/{json_filename}{json_file_extension}"

            with open(json_file_full_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            report_theme = data['Report_Theme']

            # 处理状态指示器列表 - 确保生成扁平结构
            status_indicator_items = []
            required_fields = ['item', 'state', 'color', 'show']  # StatusIndicatorItem的必填字段

            try:
                # 获取状态指示器数据
                status_indicators_data = data['Global_Overview']['Status_Indicators']
                indicators_data = []

                # 处理外层数据结构，确保最终得到扁平列表
                if isinstance(status_indicators_data, dict):
                    # 提取字典中所有可能的列表数据并合并
                    for key, value in status_indicators_data.items():
                        if isinstance(value, list):
                            indicators_data.extend(value)
                    print(f"检测到字典类型，合并所有列表数据，共{len(indicators_data)}项")
                elif isinstance(status_indicators_data, list):
                    indicators_data = status_indicators_data
                    print("检测到列表类型，直接使用")
                else:
                    raise TypeError(
                        f"Status_Indicators数据类型错误，期望dict或list，实际为{type(status_indicators_data)}")

                # 处理可能的嵌套结构，确保最终列表扁平
                flattened_indicators = []
                for item in indicators_data:
                    # 如果遇到嵌套的Status_Indicators列表则展开
                    if isinstance(item, dict) and 'Status_Indicators' in item and isinstance(item['Status_Indicators'],
                                                                                             list):
                        flattened_indicators.extend(item['Status_Indicators'])
                        print(f"展开嵌套的Status_Indicators，新增{len(item['Status_Indicators'])}项")
                    else:
                        flattened_indicators.append(item)

                # 验证并转换所有项
                for item in flattened_indicators:
                    # 检查是否为字典类型
                    if not isinstance(item, dict):
                        raise TypeError(f"状态指示器项必须是字典类型，实际为{type(item)}")

                    # 检查是否包含所有必填字段
                    missing_fields = [field for field in required_fields if field not in item]
                    if missing_fields:
                        raise ValueError(f"状态指示器项缺少必要字段: {', '.join(missing_fields)}")

                    # 检查show字段是否为布尔值
                    if not isinstance(item.get('show', False), bool):
                        raise TypeError(f"状态指示器项 '{item.get('item')}' 的show字段必须是布尔值")

                    # 创建StatusIndicatorItem实例
                    status_indicator_items.append(StatusIndicatorItem(**item))

            except KeyError as e:
                raise KeyError(f"JSON数据结构错误，缺少键: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"处理状态指示器时出错: {str(e)}")

            # 直接使用扁平列表，避免额外的StatusIndicators包装
            # 关键修复：移除多余的StatusIndicators层级包装
            status_indicators = status_indicator_items

            # # 处理关键结论摘要
            # key_conclusion_summary = KeyConclusionSummary(
            #     **data['Global_Overview']['Key_Conclusion_Summary']
            # )
            # global_overview = GlobalOverview(
            #     Status_Indicators=status_indicators,  # 使用扁平列表
            #     Key_Conclusion_Summary=key_conclusion_summary
            # )
            global_overview = GlobalOverview(
                Status_Indicators=status_indicators,  # 使用扁平列表
                Key_Conclusion_Summary=None
            )



            # 处理测试项目结果
            test_project_results = [
                TestProjectResult(**result)
                for result in data['Modular_Test_Results_Display']['Test_Analysis']['Test_Project_Results']
            ]
            # test_analysis = TestAnalysis(
            #     Test_Project_Results=test_project_results,
            #     Analysis_Logic_Chain=data['Modular_Test_Results_Display']['Test_Analysis']['Analysis_Logic_Chain']
            # )
            # modular_test_results_display = ModularTestResultsDisplay(
            #     Test_Analysis=test_analysis
            # )

            # # 处理优化建议
            # optimization_suggestions = OptimizationSuggestionsOrSolutions(
            #     Emergency_Plan=data['Optimization_Suggestions_or_Solutions']['Emergency_Plan'],
            #     Radical_Solution=data['Optimization_Suggestions_or_Solutions']['Radical_Solution']
            # )

            return Report(
                Report_Theme=report_theme,
                Global_Overview=global_overview,
                Modular_Test_Results_Display=None,
                Optimization_Suggestions_or_Solutions=None
            )

        def process_test_project_result(self, report, parsed_eval_and_log_results_container):
            """
            该函数用于向报告中添加新的测试项目结果。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            parsed_eval_and_log_results_container (dict): 包含新测试项目结果信息的字典。

            返回:
            Report: 更新后的报告对象。
            """
            try:
                # 1. 清空原有的 test_project_results 数据
                report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results = []

                # 2. 获取用户输入（赋值默认值用于调试）
                test_project = parsed_eval_and_log_results_container['test_item']
                meaning = parsed_eval_and_log_results_container['meaning']
                indicator = parsed_eval_and_log_results_container['indicator']
                test_value = parsed_eval_and_log_results_container['test_data']
                range_value = (f"{parsed_eval_and_log_results_container['low_limit']},"
                               f"{parsed_eval_and_log_results_container['up_limit']}")
                test_result = parsed_eval_and_log_results_container['state']
                trend_analysis = parsed_eval_and_log_results_container['trend_analysis']
                implied_problem_possibility = parsed_eval_and_log_results_container['implied_problem_possibility']
                chart_name = parsed_eval_and_log_results_container['chart_name']
                chart_content = parsed_eval_and_log_results_container['chart_content']

                # 3. 创建新的 TestProjectResult 对象
                new_test_project_result = TestProjectResult(
                    Test_Project=test_project,
                    Meaning=meaning,
                    Indicator=indicator,
                    Test_Value=test_value,
                    Range=range_value,
                    Test_Result=test_result,
                    Trend_Analysis=trend_analysis,
                    Implied_Problem_Possibility=implied_problem_possibility,
                    Chart_Name=chart_name,
                    Chart_Content=chart_content
                )

                # 4. 添加新的 TestProjectResult 对象到列表中
                report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results.append(new_test_project_result)

                return report
            except KeyError as e:
                print(f"解析 parsed_eval_and_log_results_container 时缺少必要的键: {e}")
            except Exception as e:
                print(f"处理新测试项目结果时出现未知错误: {e}")
            return report

        def process_test_project_result2(self, report, parsed_eval_and_log_results_container, is_clear=True):
            """
            该函数用于向报告中添加新的测试项目结果。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            parsed_eval_and_log_results_container (dict): 包含新测试项目结果信息的字典。
            is_clear (bool)：是否清空原有的 test_project_results 数据的标志。
            返回:
            Report: 更新后的报告对象。
            """
            try:
                if is_clear:
                    # 1. 清空原有的 test_project_results 数据
                    report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results = []

                # 2. 获取用户输入（赋值默认值用于调试）
                required_keys = [
                    'test_item', 'meaning', 'indicator', 'test_data',
                    'low_limit', 'up_limit', 'state', 'trend_analysis',
                    'implied_problem_possibility', 'chart_name', 'chart_content'
                ]
                for key in required_keys:
                    if key not in parsed_eval_and_log_results_container:
                        raise KeyError(f"parsed_eval_and_log_results_container 中缺少必要的键: {key}")

                test_project = parsed_eval_and_log_results_container['test_item']
                meaning = parsed_eval_and_log_results_container['meaning']
                indicator = parsed_eval_and_log_results_container['indicator']
                test_value = str(parsed_eval_and_log_results_container['test_data'])
                # 构建范围值，格式为 "low_limit,up_limit"
                range_value = f"{parsed_eval_and_log_results_container['low_limit']},{parsed_eval_and_log_results_container['up_limit']}"
                test_result = parsed_eval_and_log_results_container['state']
                trend_analysis = parsed_eval_and_log_results_container['trend_analysis']
                implied_problem_possibility = parsed_eval_and_log_results_container['implied_problem_possibility']
                chart_name = parsed_eval_and_log_results_container['chart_name']
                chart_content = parsed_eval_and_log_results_container['chart_content']

                # 3. 创建新的 TestProjectResult 对象
                new_test_project_result = TestProjectResult(
                    Test_Project=test_project,
                    Meaning=meaning,
                    Indicator=indicator,
                    Test_Value=test_value,
                    Range=range_value,
                    Test_Result=test_result,
                    Trend_Analysis=trend_analysis,
                    Implied_Problem_Possibility=implied_problem_possibility,
                    Chart_Name=chart_name,
                    Chart_Content=chart_content
                )

                # 4. 添加新的 TestProjectResult 对象到列表中
                report.Modular_Test_Results_Display.Test_Analysis.Test_Project_Results.append(new_test_project_result)

                return report
            except KeyError as e:
                print(f"解析 parsed_eval_and_log_results_container 时缺少必要的键: {e}")
                return report
            except Exception as e:
                print(f"处理新测试项目结果时出现未知错误: {e}")
                return report

        def save_json(self, report, file_path, is_clear=True):
            """
            该函数用于将报告对象保存为 JSON 文件。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            file_path：json文件模板。

            返回:
            str: 保存的 JSON 文件的路径。
            """


            if is_clear:
                temp_json_file_path = fr'.\uploads\{file_path}'
            else:
                temp_json_file_path = file_path

            json_file_directory = os.path.dirname(temp_json_file_path)
            json_filename_with_ext = os.path.basename(file_path)
            json_filename, json_file_extension = os.path.splitext(json_filename_with_ext)

            try:
                # 将 Report 对象转换为字典
                report_dict = asdict(report)

                if is_clear:
                    # 根据操作系统使用不同的路径分隔符
                    if os.name == 'nt':  # Windows
                        save_path = f"{json_file_directory}\\{json_filename}_Modify{json_file_extension}"
                    else:  # Linux 或其他类 Unix 系统
                        save_path = f"{json_file_directory}/{json_filename}_Modify{json_file_extension}"
                else:
                    save_path = file_path

                # 保存为 JSON 文件
                with open(save_path, 'w', encoding='utf-8') as file:
                    json.dump(report_dict, file, ensure_ascii=False, indent=4)
                print(f"JSON 文件已成功保存到 {save_path}")
                return save_path
            except FileNotFoundError:
                print(f"指定的文件夹路径 {json_file_directory} 不存在。")
            except PermissionError:
                print(f"没有权限在 {json_file_directory} 中保存文件。")
            except Exception as e:
                print(f"保存文件时出现未知错误: {e}")
            return save_path

        def save_json_old(self, report, file_path):
            """
            该函数用于将报告对象保存为 JSON 文件。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            file_path：json文件模板。

            返回:
            str: 保存的 JSON 文件的路径。
            """

            json_file_directory = os.path.dirname(file_path)
            json_filename_with_ext = os.path.basename(file_path)
            json_filename, json_file_extension = os.path.splitext(json_filename_with_ext)

            try:
                # 将 Report 对象转换为字典
                report_dict = asdict(report)

                # 根据操作系统使用不同的路径分隔符
                if os.name == 'nt':  # Windows
                    save_path = f"{json_file_directory}\\{json_filename}_修改后{json_file_extension}"
                else:  # Linux 或其他类 Unix 系统
                    save_path = f"{json_file_directory}/{json_filename}_修改后{json_file_extension}"

                # 保存为 JSON 文件
                with open(save_path, 'w', encoding='utf-8') as file:
                    json.dump(report_dict, file, ensure_ascii=False, indent=4)
                print(f"JSON 文件已成功保存到 {save_path}")
                return save_path
            except FileNotFoundError:
                print(f"指定的文件夹路径 {json_file_directory} 不存在。")
            except PermissionError:
                print(f"没有权限在 {json_file_directory} 中保存文件。")
            except Exception as e:
                print(f"保存文件时出现未知错误: {e}")
            return None

        def update_status_indicators(self, report, value, is_clear=True):
            """
            该函数用于清空StatusIndicators中指定字段内容，然后新增MTK_WLAN2.4G_TX_C0_HQA_15DB_MCH7字段。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            new_value (str): 新增字段MTK_WLAN2.4G_TX_C0_HQA_15DB_MCH7的值。
            is_clear (bool)：是否清空原有的 status_indicators 数据的标志。
            返回:
            Report: 更新后的报告对象。
            """
            try:
                if is_clear:
                    # 初始化 StatusIndicators
                    report.Global_Overview.Status_Indicators = StatusIndicators(
                        WiFi_2_4G_TX="",
                        WiFi_2_4G_RX="",
                        WiFi_5G_TX="",
                        WiFi_5G_RX="",
                        Bluetooth_TX="",
                        GPS_RX="",
                        LTE_TX="",
                        LTE_RX=""
                    )

                # 更新报告中的 StatusIndicators
                report.Global_Overview.Status_Indicators.WiFi_2_4G_TX = value

                return report
            except KeyError as e:
                print(f"解析新字段时缺少必要的键: {e}")
            except Exception as e:
                print(f"处理新字段内容时出现未知错误: {e}")
            return report

        def _match_any_pattern(self, string, patterns):
            """辅助方法：检查字符串是否匹配任意一个正则表达式模式"""
            for pattern in patterns:
                if re.search(pattern, string):
                    return True
            return False

        def update_status_indicators2(self, report, test_name, test_value, is_clear=True):
            """
            该函数用于清空StatusIndicators中指定字段内容，然后根据test_name更新相应字段。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            test_name (str): 测试名称，用于判断更新哪个字段。
            test_value (str): 测试值，用于更新相应字段。
            is_clear (bool)：是否清空原有的 status_indicators 数据的标志。
            返回:
            Report: 更新后的报告对象。
            """
            try:
                if is_clear:
                    # 初始化 StatusIndicators
                    report.Global_Overview.Status_Indicators = StatusIndicators(
                        WiFi_2_4G_TX="",
                        WiFi_2_4G_RX="",
                        WiFi_5G_TX="",
                        WiFi_5G_RX="",
                        Bluetooth_TX="",
                        GPS_RX="",
                        LTE_TX="",
                        LTE_RX=""
                    )

                # 使用统一的正则表达式匹配逻辑
                if self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['wifi_2_4g_tx']):
                    report.Global_Overview.Status_Indicators.WiFi_2_4G_TX = test_value

                elif self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['wifi_2_4g_rx']):
                    report.Global_Overview.Status_Indicators.WiFi_2_4G_RX = test_value

                elif self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['wifi_5g_tx']):
                    report.Global_Overview.Status_Indicators.WiFi_5G_TX = test_value

                elif self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['wifi_5g_rx']):
                    report.Global_Overview.Status_Indicators.WiFi_5G_RX = test_value

                elif self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['bluetooth_tx']):
                    report.Global_Overview.Status_Indicators.Bluetooth_TX = test_value

                elif self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['gps_rx']):
                    report.Global_Overview.Status_Indicators.GPS_RX = test_value

                elif self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['lte_tx']):
                    report.Global_Overview.Status_Indicators.LTE_TX = test_value

                elif self._match_any_pattern(test_name, REGEX_PATTERNS_For_Status_Indicators['lte_rx']):
                    report.Global_Overview.Status_Indicators.LTE_RX = test_value

                return report
            except KeyError as e:
                print(f"解析新字段时缺少必要的键: {e}")
            except Exception as e:
                print(f"处理新字段内容时出现未知错误: {e}")
            return report

        def update_status_indicators3(self, report, test_name, test_state, is_clear=True):
            """
            该函数用于处理StatusIndicators列表，根据is_clear标志决定是否清空列表，
            然后创建新的StatusIndicatorItem并添加到列表中。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            test_name (str): 测试名称，赋值给item。
            test_state (str): 测试值，赋值给state，用于判断color。
            is_clear (bool)：是否清空原有的 status_indicators 列表的标志。
            返回:
            Report: 更新后的报告对象。
            """
            try:
                # 定义字段与正则模式的映射关系
                field_patterns = {
                    'WiFi_2_4G_TX': REGEX_PATTERNS_For_Status_Indicators['wifi_2_4g_tx'],
                    'WiFi_2_4G_RX': REGEX_PATTERNS_For_Status_Indicators['wifi_2_4g_rx'],
                    'WiFi_5G_TX': REGEX_PATTERNS_For_Status_Indicators['wifi_5g_tx'],
                    'WiFi_5G_RX': REGEX_PATTERNS_For_Status_Indicators['wifi_5g_rx'],
                    'Bluetooth_TX': REGEX_PATTERNS_For_Status_Indicators['bluetooth_tx'],
                    'GPS_RX': REGEX_PATTERNS_For_Status_Indicators['gps_rx'],
                    'LTE_TX': REGEX_PATTERNS_For_Status_Indicators['lte_tx'],
                    'LTE_RX': REGEX_PATTERNS_For_Status_Indicators['lte_rx'],
                    'Basic_Band':REGEX_PATTERNS_For_Status_Indicators['basic_band'],
                    'NS_RX': REGEX_PATTERNS_For_Status_Indicators['ns_rx']
                }

                # 确保Status_Indicators是列表类型（关键修复）
                if not hasattr(report.Global_Overview, 'Status_Indicators'):
                    # 如果属性不存在，初始化为空列表
                    report.Global_Overview.Status_Indicators = []
                elif not isinstance(report.Global_Overview.Status_Indicators, list):
                    # 如果存在但不是列表类型
                    if is_clear:
                        # is_clear为True时，直接转换为空列表
                        report.Global_Overview.Status_Indicators = []
                    else:
                        # is_clear为False时，尝试保留所有原有数据并转换为列表
                        try:
                            # 处理可迭代对象的情况（如元组等）
                            if hasattr(report.Global_Overview.Status_Indicators, '__iter__'):
                                # 转换为列表保留所有元素
                                report.Global_Overview.Status_Indicators = list(
                                    report.Global_Overview.Status_Indicators)
                            else:
                                # 处理单个对象的情况，包装成列表
                                report.Global_Overview.Status_Indicators = [report.Global_Overview.Status_Indicators]
                        except Exception:
                            # 转换失败时使用空列表
                            report.Global_Overview.Status_Indicators = []

                # 如果需要清空列表
                if is_clear:
                    report.Global_Overview.Status_Indicators.clear()

                # 确定状态颜色 - 精确匹配Pass和Failed
                if test_state == "PASSED":
                    color = "blue"
                elif test_state == "FAILED":  # 保持与需求一致的拼写
                    color = "red"
                else:
                    color = ""  # 未知状态保持空值

                # 动态匹配并创建对应字段的StatusIndicatorItem
                matched_field = None
                for field, pattern in field_patterns.items():
                    if self._match_any_pattern(test_name, pattern):
                        matched_field = field
                        break  # 找到匹配项后退出循环

                if matched_field:
                    # 创建新的StatusIndicatorItem
                    new_item = StatusIndicatorItem(
                        item=test_name,  # 使用匹配到的字段名作为item
                        state=test_state,
                        color=color,
                        show=True
                    )
                    # 添加到列表中
                    report.Global_Overview.Status_Indicators.append(new_item)

                return report
            except KeyError as e:
                print(f"解析新字段时缺少必要的键: {e}")
            except Exception as e:
                print(f"处理新字段内容时出现未知错误: {e}")
            return report

        def update_status_indicators4(self, report, test_name, test_state, is_clear=True):
            """
            该函数用于处理StatusIndicators列表，根据is_clear标志决定是否清空列表，
            然后创建新的StatusIndicatorItem并添加到列表中。

            参数:
            report (Report): 报告对象，包含各种测试结果和分析信息。
            test_name (str): 测试名称，赋值给item。
            test_state (str): 测试值，赋值给state，用于判断color。
            is_clear (bool)：是否清空原有的 status_indicators 列表的标志。
            返回:
            Report: 更新后的报告对象。
            """
            # 假设正则表达式模式已保存到以下JSON文件
            REGEX_PATTERNS_JSON = "config/regex_patterns_for_status_indicators.json"
            # 拼接得到正确的JSON文件路径
            if sys.platform.startswith('linux'):
                # Linux系统使用指定路径
                REGEX_PATTERNS_JSON_PATH = '/opt/xiejun4/pro_PathFinder/config/regex_patterns_for_status_indicators.json'
            else:
                # Windows系统保持原有路径不变
                current_dir = os.path.dirname(__file__)
                parent_dir = os.path.dirname(current_dir)
                REGEX_PATTERNS_JSON_PATH = os.path.join(parent_dir, REGEX_PATTERNS_JSON)


            try:
                # 从JSON文件读取正则表达式模式
                field_patterns = {}
                if os.path.exists(REGEX_PATTERNS_JSON_PATH):
                    with open(REGEX_PATTERNS_JSON_PATH, 'r', encoding='utf-8') as f:
                        regex_patterns = json.load(f)

                        # 映射JSON中的键到字段名
                        field_mapping = {
                            'wifi_2_4g_tx': 'WiFi_2_4G_TX',
                            'wifi_2_4g_rx': 'WiFi_2_4G_RX',
                            'wifi_5g_tx': 'WiFi_5G_TX',
                            'wifi_5g_rx': 'WiFi_5G_RX',
                            'bluetooth_tx': 'Bluetooth_TX',
                            'gps_rx': 'GPS_RX',
                            'lte_tx': 'LTE_TX',
                            'lte_rx': 'LTE_RX',
                            'basic_band': 'Basic_Band',
                            'ns_rx': 'NS_RX'
                        }

                        # 构建字段与正则模式的映射关系
                        for json_key, field_name in field_mapping.items():
                            if json_key in regex_patterns:
                                field_patterns[field_name] = regex_patterns[json_key]
                else:
                    # 如果JSON文件不存在，使用默认模式作为 fallback
                    print(f"警告: 未找到正则表达式配置文件 {REGEX_PATTERNS_JSON_PATH}，使用默认模式")
                    # 添加默认模式，防止field_patterns为空
                    field_patterns = {
                        'WiFi_2_4G_TX': [r'MTK_WLAN_\d+\.\d+G_C\d+_TX_POWER_(H|M|L)CH\d+_ANT_CW']
                        # 可以根据需要添加其他默认模式
                    }

                # 确保Status_Indicators是列表类型
                if not hasattr(report.Global_Overview, 'Status_Indicators'):
                    report.Global_Overview.Status_Indicators = []
                elif not isinstance(report.Global_Overview.Status_Indicators, list):
                    if is_clear:
                        report.Global_Overview.Status_Indicators = []
                    else:
                        try:
                            if hasattr(report.Global_Overview.Status_Indicators, '__iter__'):
                                report.Global_Overview.Status_Indicators = list(report.Global_Overview.Status_Indicators)
                            else:
                                report.Global_Overview.Status_Indicators = [report.Global_Overview.Status_Indicators]
                        except Exception:
                            report.Global_Overview.Status_Indicators = []

                # 如果需要清空列表
                if is_clear:
                    report.Global_Overview.Status_Indicators.clear()

                # 确定状态颜色
                if test_state == "PASSED":
                    color = "blue"
                elif test_state == "FAILED":
                    color = "red"
                else:
                    color = ""

                # 动态匹配并创建对应字段的StatusIndicatorItem
                matched_field = None
                # 打印当前测试名称
                print(f"当前测试名称: {test_name}")
                for field, patterns in field_patterns.items():
                    # 打印当前字段及对应的正则模式列表
                    print(f"正在检查字段: {field}")
                    print(f"关联的正则模式列表: {patterns}")
                    if self._match_any_pattern(test_name, patterns):
                        matched_field = field
                        print(f"找到匹配字段: {matched_field}")
                        break
                if not matched_field:
                    print(f"未找到与测试名称 '{test_name}' 匹配的字段")

                if matched_field:
                    new_item = StatusIndicatorItem(
                        item=test_name,
                        state=test_state,
                        color=color,
                        show=True
                    )
                    # 将添加新项的操作放在if块内，避免未定义变量错误
                    report.Global_Overview.Status_Indicators.append(new_item)

            except Exception as e:
                print(f"处理状态指示器时发生错误: {e}")

            return report


# 使用示例
if __name__ == "__main__":
    # 1. 序列化 json 文件为 report 类
    # json_template_file = f"D:\\99999 - MTK log 分析\\extracted_logs\\Pathfinder-测试项报告Jason结构-英文_替换后_20250423.json"
    helper = JsonUtil.L2AR()
    report = helper.convert_json_to_object(helper.json_template_file)
    print(report)

    helper.update_status_indicators(report, "passed")

    # 新增 TestProjectResult 对象，并保存文件
    parsed_eval_and_log_results_container = {
        'test_item': 'test_item',
        'low_limit': 'low_limit',
        'up_limit': 'up_limit',
        'test_data': 'test_data',
        'unit': 'unit',
        'state': 'state',
        'meaning': 'meaning',
        'indicator': 'indicator',
        'trend_analysis': 'trend_analysis',
        'implied_problem_possibility': 'implied_problem_possibility',
        'chart_name': 'chart_name',
        'chart_content': 'chart_content'}
    report = helper.process_test_project_result2(report, parsed_eval_and_log_results_container)

    save_path = helper.save_json(report, helper.json_template_file)