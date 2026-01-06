import re
import json

def add_test_items_to_json(system_items, finder_file_path=r"debug\test9\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json"):
    """
    将system_items中不存在于finder_file_path指定的JSON文件中的异常测试项添加到JSON文件中
    
    参数:
        system_items: 系统级日志项列表
        finder_file_path: JSON文件路径
    """
    # 加载现有的JSON数据
    try:
        with open(finder_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {finder_file_path}")
        return
    except json.JSONDecodeError:
        print(f"错误: 文件 {finder_file_path} 不是有效的JSON格式")
        return
    
    # 创建一个集合来存储已存在的测试项名称
    existing_test_items = set()
    
    # 遍历JSON数据，收集所有已存在的测试项名称
    for test_group in json_data.values():
        for key_parts in test_group.values():
            for item in key_parts:
                if "TEST ITEMS" in item:
                    existing_test_items.add(item["TEST ITEMS"])
    
    # 收集需要添加的系统级异常测试项
    items_to_add = []
    for item in system_items:
        test_name = getattr(item, 'test_name', None)
        test_type = getattr(item, 'test_type', None)
        if test_name and test_name not in existing_test_items:
            # 创建新的测试项条目
            new_item = {
                "Test Group": f"{test_type}异常",  # 默认测试组
                "Key parts": f"{test_type}日志",   # 默认关键参数
                "TEST ITEMS": test_name,
                "Method": f"{test_type}日志分析",
                "Test detail information": f"{test_type}异常日志项: {test_name}",
                "Dependency": None,
                "Principle": f"{test_type}日志异常检测",
                "Impact": "未知",
                "Risk": "未知",
                "Owner": "system",
                "List of Regular Expressions": [f".*{re.escape(test_name)}.*"],
                "AI Prompt": {
                    "测试项解释": f"{test_type}异常日志项: {test_name}",
                    "异常日志分析与建议": f"需要进一步分析{test_type}异常日志项: {test_name}"
                },
                "analysis_suggest": {
                    "可能的失败原因": ["待分析"],
                    "建议的解决方案": ["待分析"],
                    "预防措施": ["待分析"]
                },
                "Status": "待加入"  # 添加状态字段
            }
            items_to_add.append(new_item)
            
            # 将测试项添加到JSON数据中
            test_group_name = f"{test_type}异常"
            key_parts_name = f"{test_type}日志"
            
            # 如果测试组不存在，创建它
            if test_group_name not in json_data:
                json_data[test_group_name] = {}
            
            # 如果关键参数组不存在，创建它
            if key_parts_name not in json_data[test_group_name]:
                json_data[test_group_name][key_parts_name] = []
            
            # 添加新项
            json_data[test_group_name][key_parts_name].append(new_item)
    
    # 保存更新后的JSON数据
    try:
        with open(finder_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"成功添加 {len(items_to_add)} 个新的系统级异常测试项到 {finder_file_path}")
    except Exception as e:
        print(f"保存文件时出错: {e}")

def add_test_item_to_json(system_item, finder_file_path=r"debug\test9\docs\JOTSLIM+L2VISION_grouped_output_with_properties.json"):
    """
    将单个system_item中不存在于finder_file_path指定的JSON文件中的异常测试项添加到JSON文件中
    
    参数:
        system_item: 单个系统级日志项
        finder_file_path: JSON文件路径
    """
    # 加载现有的JSON数据
    try:
        with open(finder_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {finder_file_path}")
        return
    except json.JSONDecodeError:
        print(f"错误: 文件 {finder_file_path} 不是有效的JSON格式")
        return
    
    # 创建一个集合来存储已存在的测试项名称
    existing_test_items = set()
    
    # 遍历JSON数据，收集所有已存在的测试项名称
    for test_group in json_data.values():
        for key_parts in test_group.values():
            for item in key_parts:
                if "TEST ITEMS" in item:
                    existing_test_items.add(item["TEST ITEMS"])
    
    test_name = getattr(system_item, 'test_name', None)
    log_details = getattr(system_item, 'log_details', None)
    if test_name and test_name not in existing_test_items:
        # 创建新的测试项条目
        new_item = {
            "Test Group": "待加入",  # 默认测试组
            "Key parts": "待加入",   # 默认关键参数
            "TEST ITEMS": test_name,
            "Method": "待加入",        
            "Test detail information": "待加入",
            "Dependency": "待加入",
            "Principle": "待加入",
            "Impact": "待加入",
            "Risk": "待加入",
            "Owner": "待加入",
            "List of Regular Expressions": [f".*{re.escape(test_name)}.*"],
            "AI Prompt": {
                "测试项解释": "待加入", 
                "异常日志分析与建议": "待加入"
            },
            "analysis_suggest": {
                "异常日志": [log_details.replace('"', '&quot;')] if isinstance(log_details, str) else [item.replace('"', '&quot;') if isinstance(item, str) else item for item in log_details],
                "可能的失败原因": ["待加入"],
                "建议的解决方案": ["待加入"],
                "预防措施": ["待加入"]
            },
            "Status": "待加入"  # 添加状态字段
        }
        
        # 将测试项添加到JSON数据中
        test_group_name = "待加入"
        key_parts_name = "待加入"
        
        # 如果测试组不存在，创建它
        if test_group_name not in json_data:
            json_data[test_group_name] = {}
        
        # 如果关键参数组不存在，创建它
        if key_parts_name not in json_data[test_group_name]:
            json_data[test_group_name][key_parts_name] = []
        
        # 添加新项
        json_data[test_group_name][key_parts_name].append(new_item)
        
        # 保存更新后的JSON数据
        try:
            with open(finder_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"成功添加 1 个新的系统级异常测试项到 {finder_file_path}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    else:
        print("未找到需要添加的测试项或测试项已存在")
