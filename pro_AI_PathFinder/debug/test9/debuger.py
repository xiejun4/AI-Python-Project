from json_filter import do_json_filter_process, do_find_matching_info_process
from json_add import add_test_item_to_json
from parse import do_parse_process
from zip_helper import do_unzip_process
from excel_reader import do_excel_reader
from group_data import do_group_data
from add_properties import do_add_properties
from write_to_excel import do_write_json_to_excel


def excel_to_json_to_excel_new(station):
    """主函数"""
    print("开始调试excel_reader和group_data模块\n")

    # 调试ExcelReader类
    do_excel_reader(station)

    # 调试group_data模块
    do_group_data(station)

    # 调试add_properties模块
    do_add_properties(station)

    # 调试write_to_excel模块
    do_write_json_to_excel(station)

    print("所有调试完成")


if __name__ == "__main__":
    # 1 - 将excel转成新的excel文件
    stations = ['JOTSLIM+L2VISION', 'Audio(AR&ACT)+ANT']
    for station in stations:
        excel_to_json_to_excel_new(station)

    # 2 - 解压zip文件
    file_name = 'NexTestLogs_L2VISION_LAGOS25_EUROPE_L2_VISION_BE37-LVISION14_Failed_ADB_input keyevent 223_ZY32M2F9WB_2025-09-15_T13-09-57~22.log_zip'
    file_path, file_dir, file_name, file_ext, file_name_without_ext = do_unzip_process(file_name)

    # 3 - 生成 parsed_log_output_fixed.json
    output_json_path, parsed_data = do_parse_process(file_path=file_path)

    # 定义一个函数来处理日志过滤、匹配和添加操作
    def process_logs(print_msg, json_path, log_type, status):
        print(print_msg)
        items = do_json_filter_process(
            json_path=json_path,
            log_type=log_type,
            status=status
        )
        
        results = None
        if items:
            results = []
            for item in items:
                # 对每个 item 调用 do_find_matching_info_process 函数
                result = do_find_matching_info_process(item,
                                                    finder_file_path=r"debug\\test9\\docs\\JOTSLIM+L2VISION_grouped_output_with_properties.json")
                if result:
                    results.append(result)
                else:
                    # 若未找到匹配信息，则添加测试项到 JSON 文件
                    add_test_item_to_json(item,
                                        finder_file_path=r"debug\\test9\\docs\\JOTSLIM+L2VISION_grouped_output_with_properties.json")

    # 定义参数列表
    process_params = [
        {
            "print_msg": "=== 系统级日志 ===",
            "json_path": r"debug\\test9\\logs\\extracted_logs\\parsed_log_output_fixed.json",
            "log_type": "系统级",
            "status": "失败"
        },
        {
            "print_msg": "\n=== 失败的测试项 ===",
            "json_path": r"debug\\test9\\logs\\extracted_logs\\parsed_log_output_fixed.json",
            "log_type": "测试项",
            "status": "失败"
        }
    ]

    # 循环执行 process_logs 函数
    for params in process_params:
        process_logs(**params)
