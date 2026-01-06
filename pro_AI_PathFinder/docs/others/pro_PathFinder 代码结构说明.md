pro_PathFinder 代码结构说明

1.# check site and platform

获取当前站点和平台

2.unzip_otplus_helper_rename_log_zip

对OT+log进行重命名，变成可以直接处理的zip文件

3.# 解压 log_zip文件

将有效的log文件加压到指定的upload目录下。

4.cleaner.remove_timestamp2log_level

清除文件中不参加数据处理的字段，如：time,stamp

5.process_log_file

执行处理log文件，这里面包含将log文件转换成json文件整个过程。

6.get_platform_patterns

获取平台的正则表达式

7.get_patterns_grouped_dic

使用正则表达式过滤log中的测试项，然后将其分组。

8.filter_async_items

过滤掉async_items

9.extract_failed_logs

提取出异常log

10.generic_failed_logs_dict

生成异常log字典表

11.filter_duplicate_logs_in_dict

去重

12.extract_log_data

结构化异常log



13.parse_mic_test_position2

测试数据分布趋势（中英文）

14.merge_position_analysis

合入测试数据分布趋势（中英文）



15.parse_mic_test_purpose2items

测试项解释与进一步说明

16.merge_test_purpose2items

合入测试项解释与进一步说明



17.analyze_failure_reasons4

分析异常原因与建议

18.add_analysis_reports

合入分析异常原因与建议



19.plot_audio_test_results3

绘制Speaker的图形

20.add_chart_items_to_dict

合入绘制Speaker的图形



21.convert_json_to_object

将json模版转成object

22.map_logs_to_test_results2

将structured_failed_logs_dict插入json的object对象

23.save_json

保持json文件

24.read_json_file

读取json文件内容



25.cleanup_uploads_directory

清空uploads下面的log文件。







# CleanFilterDataEntity_L2AR.py
## 1.这里面包含MTK，高通的WCN，LTE，Speaker，Mic，Ear 等正则表达式，目的是从log中获取对应的测试项。

# mian_test.py

## 4-5.解析 测试目的和测试项说明
    # 1.将CleanFilterDataEntity_L2AR.py中的正则表达式添加到这里。 
    elif re.match(
        r'^(QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RADIATED_RX_C\d+_(M|L)CH_EQ|'
        r'QC_WLAN_5\.0GHz_\d+[a-zA-Z]_RADIATED_RX_C\d+_(M|L)CH(\d*?)_-?\d+|'
        r'QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RADIATED_RX_C\d+_(M|L)CH_EQ|'
        r'QC_WLAN_2\.4GHz_\d+[a-zA-Z]_RAD_RX_C\d+_CAL_POWER_(M|L)CH)',
        second_key
    ):
        # 2.将CleanFilterDataEntity_L2AR.py的正则表达式添加到下面的函数里。 
        # 处理匹配到的逻辑
        result = cleaner.parse_wifi_rx_test_description3_for_qc(second_key)

# 4-6.解析 "趋势分析": "值集中在中位区（稳定）",
    # 1.这里生成issue_suggestion,MTK,高通的WCN，LTE是代码生成的。Speaker，Mic，Ear是从.\doc\issue_suggestions.xml
    # 中加载的

## 5.----------------------- json 文件处理 -------------------------
### 5-2.更新 Status_Indicators 对象
    # jsoner.update_status_indicators3会去调用JsonDataEntity_L2AR.py里面的正则表达式表。
        report = jsoner.update_status_indicators3(
            report,
            parsed_eval_and_log_results_container['test_item'],
            parsed_eval_and_log_results_container['state'])

    JsonDataEntity_L2AR.py
        'lte_tx': [
            r'LTE_BC\d+_TX',
            r'LTE_(TDD|FDD)_TX',
            r'^QC_LTE_BC\d+_QRRFR_TX_POWER_(M|L)CH_\d+_V\d+',

## 说明：OT+的log中的测试项名称与高通和MTK的原生log中的测试项名称不一致。
### 1.一个是用户手动编写，会参考上一代或者类似产品的测试项； - all station owners
### 2.原生log会根据DLL的更新而有所变化。 - zhurui3 and other developer



## 向代码中添加基带测试项
## execute_abnormal_log_of_basic_band
### 1.check_file_info
    # check site and platform
    site, platform,base_band_test_item = check_file_info(zip_path)

### 2.execute_abnormal_log_of_basic_band
    # 3.获取原始数据
    # eval_and_log_results_container 测试结果的数据容器
    # exception_error_container 测试异常数据的数据容器
    # folder_path
    # TODO:这里添加正则表达式
### 3. 4-5.解析 测试目的和测试项说明
### 4. 4-6.生成错误分析与建议"
### 5. 5-2.更新 Status_Indicators 对象

### 6. JsonDataEntity_L2AR.py
    #1. 定义json文件结构
    #2. 汇总所有正则表达式模式
    # REGEX_PATTERNS_For_Status_Indicators
    # TODO：这里添加各个测试项的正则表达式表
### 7.JsonUtil_L2AR.py
    #1.定义了处理json文件的各种方法


### 7. CleanFilterDataEntity_L2AR.py
    #1.这里定义的是从过滤后日志文件匹配测试项的正则表达式表

### 8. CleanFilterDataUtil_L2AR.py
    #1.定义了清洗，过滤日志数据的方法。
    #关键：测试项的解释方法、异常数据分析与建议的方法。




    在 VS Code 中，代码折叠相关的常用快捷键如下：

- 折叠当前代码块：`Ctrl + Shift + [ `（Windows/Linux）或 `Cmd + Shift + [ `（Mac）
- 展开当前代码块：`Ctrl + Shift + ] `（Windows/Linux）或 `Cmd + Shift + ] `（Mac）
- 折叠所有代码块：`Ctrl + K, Ctrl + 0 `（先按 Ctrl+K，再按 Ctrl+0，Windows/Linux）或 `Cmd + K, Cmd + 0 `（Mac）
- 展开所有代码块：`Ctrl + K, Ctrl + J `（先按 Ctrl+K，再按 Ctrl+J，Windows/Linux）或 `Cmd + K, Cmd + J `（Mac）
- 折叠当前层级的代码：`Ctrl + K, Ctrl + [ `（Windows/Linux）或 `Cmd + K, Cmd + [ `（Mac）
- 展开当前层级的代码：`Ctrl + K, Ctrl + ] `（Windows/Linux）或 `Cmd + K, Cmd + ] `（Mac）

这些快捷键可以帮助你快速折叠或展开代码块，提高代码阅读和编辑效率。如果快捷键不起作用，可能是与其他快捷键冲突，可以在 VS Code 的「文件 > 首选项 > 键盘快捷方式」中搜索 "fold" 相关命令进行查看和修改。

2025-9-9
1.在 file_info_rules.json 里面添加xxx测试项的平台和类型
2.在 clean_filter_data_entity.json 里面添加测试项的正则表达式，用来获取测试记录
3.在 basic_band_test_purpose2items.json 里面添加测试项中测试子项正则表达式与的说明
注明：如果测试子项一个正则表达式没法表示，那就写2个。
4.在生成json文件部分中
需要将测试项的正则表达式内容添加到：regex_patterns_for_status_indicators.json 中的指定节点内。
因为 report = jsoner.update_status_indicators4 这个函数调用 regex_patterns_for_status_indicators.json 里面的内容生成以下内容
        "Status_Indicators": [
            {
                "item": "ANDROID_CQATEST_CFG_MA_DATABASE_RESULTS",
                "state": "FAILED",
                "color": "red",
                "show": true
            }

2025-9-10
1.在Issue_Suggestion_DataUtil_L2AR.py中添加了LTE的Tx/Rx的异常分析与建议函数
lte_tx_issue_suggestion_add_more_fields
lte_rx_issue_suggestion_add_more_fields
