#!/usr/bin/env python3
"""
ModelInfo XML 验证工具
验证 ModelInfoFile_Beryl.xml 文件中的 RF 连接配置是否符合指定规则

功能说明：
- 解析 XML 文件，提取所有 Model 和 Band 元素
- 根据预定义规则验证每个 Band 的 Rfpath_name 配置
- 生成详细的验证报告，显示有效和无效的配置
- 支持命令行指定 XML 文件路径

使用方法：
1. 默认使用 D:\\PythonProject\\pro_python\\pro_debug\\test6\\ModelInfoFile_Beryl.xml
   python validate_modelinfo.py
   
2. 指定其他 XML 文件
   python validate_modelinfo.py <path_to_xml_file>
"""

# 导入必要的模块
import xml.etree.ElementTree as ET  # 用于解析 XML 文件
import argparse  # 用于处理命令行参数
import os  # 用于文件路径操作

def parse_xml(file_path):
    """
    解析 XML 文件并返回根元素
    
    参数：
        file_path: XML 文件的路径
        
    返回：
        成功：返回 XML 根元素
        失败：返回 None 并打印错误信息
    """
    try:
        # 使用 ElementTree 解析 XML 文件
        tree = ET.parse(file_path)
        # 获取根元素
        return tree.getroot()
    except Exception as e:
        # 打印错误信息
        print(f"Error parsing XML file: {e}")
        return None

def get_namespace(element):
    """
    获取 XML 元素的命名空间
    
    参数：
        element: XML 元素
        
    返回：
        元素的命名空间字符串，如果没有则返回空字符串
    """
    # 检查元素标签是否以 { 开头（XML 命名空间格式）
    if element.tag.startswith('{'):
        # 提取命名空间部分
        return element.tag.split('}')[0][1:]
    # 没有命名空间则返回空字符串
    return ''

def extract_bands(root):
    """
    从 XML 根元素提取所有 Band 元素
    
    参数：
        root: XML 根元素
        
    返回：
        字典，键为 Product 名称，值为该 Product 下的 Model 信息字典
        Model 信息字典的键为 Model 名称，值为该 Model 下的所有 Band 信息列表
    """
    # 获取 XML 命名空间
    namespace = get_namespace(root)
    # 存储所有 Product 的信息
    products = {}
    
    # 查找所有 Product 元素
    product_elements = root.findall(f'.//{{{namespace}}}Product')
    for product_elem in product_elements:
        # 获取 Product 名称
        product_name = product_elem.get('name')
        # 存储当前 Product 的 Model 信息
        models = {}
        
        # 查找当前 Product 下的所有 Model 元素
        model_elements = product_elem.findall(f'.//{{{namespace}}}Model')
        for model_elem in model_elements:
            # 获取 Model 名称
            model_name = model_elem.get('name')
            # 存储当前 Model 的 Band 信息
            bands = []
            
            # 查找当前 Model 下的所有 Band 元素
            band_elements = model_elem.findall(f'.//{{{namespace}}}Band')
            for band_elem in band_elements:
                # 获取 Band 名称
                band_name = band_elem.get('name')
                # 获取 RF 路径
                rfpath = band_elem.get('Rfpath_name')
                # 获取设备路径
                device_path = band_elem.get('device_path')
                
                # 确保 Band 名称和 RF 路径都存在
                if band_name and rfpath:
                    bands.append({
                        'name': band_name,
                        'rfpath': rfpath,
                        'device_path': device_path
                    })
            
            # 将当前 Model 的 Band 信息添加到字典
            models[model_name] = bands
        
        # 将当前 Product 的 Model 信息添加到字典
        products[product_name] = models
    
    return products

def define_rules():
    """
    定义验证规则
    
    返回：
        字典，包含 WIFI、PRC、ROW 的连接器映射规则
    """
    # 定义基础连接器映射
    base_connectors = {
        1: 'UUT_RF_CONN1_TO_TESTSET_MAIN_RF',
        2: 'UUT_RF_CONN8_TO_TESTSET_MAIN_RF',
        6: 'UUT_RF_CONN6_TO_TESTSET_MAIN_RF',
        7: 'UUT_RF_CONN7_TO_TESTSET_MAIN_RF',
        4: 'UUT_RF_CONN2_TO_TESTSET_ALT1_RF',
        5: 'UUT_RF_CONN5_TO_TESTSET_ALT1_RF',
        9: 'UUT_RF_CONN9_TO_TESTSET_ALT1_RF',
        8: 'UUT_RF_CONN10_TO_TESTSET_ALT1_RF'
    }
    
    # 添加 DIRECT_RF 连接器（100, 200, ..., 900）
    for i in range(100, 1000, 100):
        base_connectors[i] = f'UUT_RF_CONN{i}_TO_TESTSET_DIRECT_RF'
    
    # 定义规则字典，按模型名称组织
    rules = {
        'ROW': {
            'connectors': base_connectors.copy()
        },
        'PRC': {
            'connectors': base_connectors.copy()
        },
        'WIFI': {
            'connectors': base_connectors.copy()
        }
    }
    
    # 验证端口号和 CONN 数值的有效性
    for model, model_rules in rules.items():
        for port, rfpath in model_rules['connectors'].items():
            # 检查端口号是否为整数
            if not isinstance(port, int):
                raise ValueError(f"端口号必须是整数: {port}")
            # 检查端口号是否为正数
            if port <= 0:
                raise ValueError(f"端口号必须是正数: {port}")
            
            # 提取 CONN 数值
            try:
                conn_part = rfpath.split('CONN')[1].split('_TO_TESTSET')[0]
                conn_number = int(conn_part)
            except (IndexError, ValueError):
                raise ValueError(f"无效的 Rfpath_name 格式: {rfpath}")
            
            # 根据 RF 类型验证 CONN 数值
            if 'MAIN_RF' in rfpath:
                allowed_conn = {1, 3, 4, 6, 7, 8, 11, 12, 13, 14, 15}
                if conn_number not in allowed_conn:
                    raise ValueError(f"MAIN_RF 的 CONN 数值必须在 {allowed_conn} 中: {conn_number}")
            elif 'ALT1_RF' in rfpath:
                allowed_conn = {2, 5, 9, 10}
                if conn_number not in allowed_conn:
                    raise ValueError(f"ALT1_RF 的 CONN 数值必须在 {allowed_conn} 中: {conn_number}")
            elif 'DIRECT_RF' in rfpath:
                allowed_conn = set(range(100, 1000, 100))
                if conn_number not in allowed_conn:
                    raise ValueError(f"DIRECT_RF 的 CONN 数值必须是 100, 200, ..., 900: {conn_number}")
            else:
                raise ValueError(f"无效的 RF 类型: {rfpath}")
    
    return rules

def define_rf_io_mapping():
    """
    定义 RF-IO 端口映射
    
    返回：
        字典，包含 MAIN_RF 和 ALT1_RF 对应的端口列表
    """
    return {
        'MAIN_RF': ['1', '3', '4', '6', '7', '8', '11', '12', '13', '14', '15'],
        'ALT1_RF': ['2', '5', '9', '10']
    }

def validate_model(model_name, bands, rules):
    """
    验证单个 Model 的配置
    
    参数：
        model_name: Model 名称
        bands: 该 Model 下的所有 Band 信息列表
        rules: 验证规则字典
        
    返回：
        字典，包含验证结果（有效和无效的配置）
    """
    # 初始化验证结果
    results = {
        'model': model_name,  # Model 名称
        'valid': [],  # 有效配置列表
        'invalid': []  # 无效配置列表
    }
    
    # 检查当前模型是否在规则中
    if model_name in rules:
        # 获取当前模型的连接器规则
        model_connectors = rules[model_name]['connectors']
        # 获取所有预期的 RF 路径
        expected_rfpaths = set(model_connectors.values())
        
        # 遍历每个 Band 进行验证
        for band in bands:
            # 验证 Rfpath_name 的格式是否符合规则
            if validate_rfpath_format(band['rfpath']):
                # 检查当前 Band 的 RF 路径是否在预期列表中
                if band['rfpath'] in expected_rfpaths:
                    # 添加到有效配置列表
                    results['valid'].append({
                        'band': band['name'],
                        'rfpath': band['rfpath'],
                        'device_path': band['device_path']
                    })
                else:
                    # 添加到无效配置列表
                    results['invalid'].append({
                        'band': band['name'],
                        'rfpath': band['rfpath'],
                        'device_path': band['device_path'],
                        'reason': f"Unexpected Rfpath_name: {band['rfpath']}"
                    })
            else:
                # 添加到无效配置列表
                results['invalid'].append({
                    'band': band['name'],
                    'rfpath': band['rfpath'],
                    'device_path': band['device_path'],
                    'reason': f"Invalid Rfpath_name format: {band['rfpath']}"
                })
    else:
        # 模型不在规则中，所有配置都标记为无效
        for band in bands:
            results['invalid'].append({
                'band': band['name'],
                'rfpath': band['rfpath'],
                'device_path': band['device_path'],
                'reason': f"Model '{model_name}' not found in rules"
            })
    
    return results

def validate_rfpath_format(rfpath):
    """
    验证 Rfpath_name 的格式是否符合规则
    
    参数：
        rfpath: Rfpath_name 字符串
        
    返回：
        布尔值，表示是否符合规则
    """
    try:
        # 提取 CONN 数值
        conn_part = rfpath.split('CONN')[1].split('_TO_TESTSET')[0]
        conn_number = int(conn_part)
        
        # 根据 RF 类型验证 CONN 数值
        if 'MAIN_RF' in rfpath:
            allowed_conn = {1, 3, 4, 6, 7, 8, 11, 12, 13, 14, 15}
            if conn_number not in allowed_conn:
                return False
        elif 'ALT1_RF' in rfpath:
            allowed_conn = {2, 5, 9, 10}
            if conn_number not in allowed_conn:
                return False
        elif 'DIRECT_RF' in rfpath:
            allowed_conn = set(range(100, 1000, 100))
            if conn_number not in allowed_conn:
                return False
        else:
            return False
        
        return True
    except (IndexError, ValueError):
        return False

def validate_rf_io_mapping(rfpath, rf_io_mapping):
    """
    验证 RF 路径是否符合 RF-IO 映射规则
    
    参数：
        rfpath: RF 路径字符串
        rf_io_mapping: RF-IO 映射字典
        
    返回：
        布尔值，表示是否符合规则
    """
    # 检查 RF 路径是否包含 MAIN_RF
    if 'MAIN_RF' in rfpath:
        # 检查 MAIN_RF 是否在映射字典中
        return 'MAIN_RF' in rf_io_mapping
    # 检查 RF 路径是否包含 ALT1_RF
    elif 'ALT1_RF' in rfpath:
        # 检查 ALT1_RF 是否在映射字典中
        return 'ALT1_RF' in rf_io_mapping
    # 既不是 MAIN_RF 也不是 ALT1_RF
    return False

def generate_report(results_list):
    """
    生成验证报告
    
    参数：
        results_list: 验证结果列表，每个元素是一个包含 Product 名称、Model 名称和验证结果的字典
        
    返回：
        布尔值，表示总体验证是否通过
    """
    # 打印报告标题
    print("\n" + "="*80)
    print("MODELINFO XML 验证报告")
    print("="*80)
    
    # 初始化总体验证状态
    all_valid = True
    
    # 遍历每个 Product 的验证结果
    for result in results_list:
        product_name = result['product']
        model_results = result['results']
        
        # 打印 Product 名称
        print(f"\nProduct: {product_name}")
        print("-" * 40)
        
        # 遍历每个 Model 的验证结果
        for model_result in model_results:
            # 打印 Model 名称
            print(f"\n  Model: {model_result['model']}")
            print("  " + "-" * 36)
            
            # 打印有效配置
            if model_result['valid']:
                print(f"  ✓ 有效配置 ({len(model_result['valid'])}):")
                for item in model_result['valid']:
                    print(f"    - Band: {item['band']}, Rfpath: {item['rfpath']}, Device Path: {item['device_path']}")
            else:
                print("  ✓ 有效配置: 无")
            
            # 打印无效配置
            if model_result['invalid']:
                # 发现无效配置，总体验证标记为失败
                all_valid = False
                print(f"  ✗ 无效配置 ({len(model_result['invalid'])}):")
                for item in model_result['invalid']:
                    print(f"    - Band: {item['band']}, Rfpath: {item['rfpath']}, Device Path: {item['device_path']}")
                    print(f"      原因: {item['reason']}")
            else:
                print("  ✗ 无效配置: 无")
    
    # 打印总体验证结果
    print("\n" + "="*80)
    if all_valid:
        print("✓ 总体验证: 通过")
    else:
        print("✗ 总体验证: 失败")
    print("="*80)
    
    return all_valid

def main():
    """
    主函数，程序的入口点
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='验证 ModelInfo XML 文件中的 RF 连接配置')
    # 添加 XML 文件路径参数，默认使用指定路径
    parser.add_argument('xml_file', help='XML 文件路径', nargs='?', 
                        default='D:\\PythonProject\\pro_python\\pro_debug\\test6\\ModelInfoFile_Beryl.xml')
    # 解析命令行参数
    args = parser.parse_args()
    
    # 获取 XML 文件路径
    xml_file = args.xml_file
    
    # 检查文件是否存在
    if not os.path.exists(xml_file):
        print(f"Error: File '{xml_file}' does not exist.")
        return
    
    # 解析 XML 文件
    root = parse_xml(xml_file)
    if not root:
        return
    
    # 提取 Band 元素
    products = extract_bands(root)
    if not products:
        print("Error: No products found in XML file.")
        return
    
    # 定义规则
    rules = define_rules()
    rf_io_mapping = define_rf_io_mapping()
    
    # 验证每个 Product 和 Model
    results_list = []
    for product_name, models in products.items():
        product_result = {
            'product': product_name,
            'results': []
        }
        
        # 验证每个 Model
        for model_name, bands in models.items():
            # 验证当前 Model
            model_result = validate_model(model_name, bands, rules)
            # 添加到 Product 结果中
            product_result['results'].append(model_result)
        
        # 添加到总结果列表
        results_list.append(product_result)
    
    # 生成报告
    generate_report(results_list)

# 如果直接运行此脚本，执行主函数
if __name__ == '__main__':
    main()