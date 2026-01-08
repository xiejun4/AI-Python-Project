#!/usr/bin/env python3
"""
ModelInfo XML 验证工具后端
提供 API 接口用于验证 XML 文件
"""

import xml.etree.ElementTree as ET
import json
import sys
import os

def parse_xml(xml_content):
    """解析 XML 内容并返回根元素"""
    try:
        tree = ET.ElementTree(ET.fromstring(xml_content))
        return tree.getroot(), None
    except Exception as e:
        return None, str(e)

def get_namespace(element):
    """获取 XML 元素的命名空间"""
    if element.tag.startswith('{'):
        return element.tag.split('}')[0][1:]
    return ''

def extract_bands(root):
    """从 XML 根元素提取所有 Band 元素"""
    namespace = get_namespace(root)
    products = {}
    
    # 查找所有 Product 元素
    product_elements = root.findall(f'.//{{{namespace}}}Product')
    for product_elem in product_elements:
        product_name = product_elem.get('name')
        models = {}
        
        # 查找当前 Product 下的所有 Model 元素
        model_elements = product_elem.findall(f'.//{{{namespace}}}Model')
        for model_elem in model_elements:
            model_name = model_elem.get('name')
            bands = []
            
            # 查找当前 Model 下的所有 Band 元素
            band_elements = model_elem.findall(f'.//{{{namespace}}}Band')
            for band_elem in band_elements:
                band_name = band_elem.get('name')
                rfpath = band_elem.get('Rfpath_name')
                device_path = band_elem.get('device_path')
                
                if band_name and rfpath:
                    bands.append({
                        'name': band_name,
                        'rfpath': rfpath,
                        'device_path': device_path
                    })
            
            models[model_name] = bands
        
        products[product_name] = models
    
    return products

def define_rules():
    """定义验证规则"""
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
    
    for i in range(100, 1000, 100):
        base_connectors[i] = f'UUT_RF_CONN{i}_TO_TESTSET_DIRECT_RF'
    
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
    
    return rules

def validate_rfpath_format(rfpath):
    """验证 Rfpath_name 格式"""
    try:
        conn_part = rfpath.split('CONN')[1].split('_TO_TESTSET')[0]
        conn_number = int(conn_part)
        
        rf_type = ''
        if 'MAIN_RF' in rfpath:
            rf_type = 'MAIN_RF'
        elif 'ALT1_RF' in rfpath:
            rf_type = 'ALT1_RF'
        elif 'DIRECT_RF' in rfpath:
            rf_type = 'DIRECT_RF'
        else:
            return {
                'valid': False,
                'errorParts': [rfpath.split('_TO_TESTSET')[1] or rfpath],
                'correctHint': 'RF 类型必须是 MAIN_RF、ALT1_RF 或 DIRECT_RF'
            }
        
        if rf_type == 'MAIN_RF':
            allowed_conn = {1, 3, 4, 6, 7, 8, 11, 12, 13, 14, 15}
            if conn_number not in allowed_conn:
                return {
                    'valid': False,
                    'errorParts': [f'CONN{conn_number}', 'MAIN_RF'],
                    'correctHint': 'MAIN_RF 的 CONN 数值必须在 {1, 3, 4, 6, 7, 8, 11, 12, 13, 14, 15} 中'
                }
        elif rf_type == 'ALT1_RF':
            allowed_conn = {2, 5, 9, 10}
            if conn_number not in allowed_conn:
                return {
                    'valid': False,
                    'errorParts': [f'CONN{conn_number}', 'ALT1_RF'],
                    'correctHint': 'ALT1_RF 的 CONN 数值必须在 {2, 5, 9, 10} 中'
                }
        elif rf_type == 'DIRECT_RF':
            allowed_conn = set()
            for i in range(100, 1000, 100):
                allowed_conn.add(i)
            if conn_number not in allowed_conn:
                return {
                    'valid': False,
                    'errorParts': [f'CONN{conn_number}', 'DIRECT_RF'],
                    'correctHint': 'DIRECT_RF 的 CONN 数值必须是 100, 200, ..., 900'
                }
        
        return {
            'valid': True,
            'errorParts': [],
            'correctHint': ''
        }
    except Exception as e:
        return {
            'valid': False,
            'errorParts': [rfpath],
            'correctHint': 'Rfpath_name 格式无效'
        }

def validate_model(model_name, bands, rules):
    """验证单个 Model 的配置"""
    results = {
        'model': model_name,
        'valid': [],
        'invalid': []
    }
    
    if model_name in rules:
        model_connectors = rules[model_name]['connectors']
        expected_rfpaths = set(model_connectors.values())
        
        for band in bands:
            format_result = validate_rfpath_format(band['rfpath'])
            
            if format_result['valid']:
                if band['rfpath'] in expected_rfpaths:
                    results['valid'].append({
                        'band': band['name'],
                        'rfpath': band['rfpath'],
                        'device_path': band['device_path']
                    })
                else:
                    results['invalid'].append({
                        'band': band['name'],
                        'rfpath': band['rfpath'],
                        'device_path': band['device_path'],
                        'reason': f'Unexpected Rfpath_name: {band["rfpath"]}',
                        'errorParts': [],
                        'correctHint': 'Rfpath_name 不在预期列表中'
                    })
            else:
                results['invalid'].append({
                    'band': band['name'],
                    'rfpath': band['rfpath'],
                    'device_path': band['device_path'],
                    'reason': f'Invalid Rfpath_name format: {band["rfpath"]}',
                    'errorParts': format_result['errorParts'],
                    'correctHint': format_result['correctHint']
                })
    else:
        for band in bands:
            results['invalid'].append({
                'band': band['name'],
                'rfpath': band['rfpath'],
                'device_path': band['device_path'],
                'reason': f'Model "{model_name}" not found in rules',
                'errorParts': [model_name],
                'correctHint': f'Model 名称必须是 {", ".join(rules.keys())} 之一'
            })
    
    return results

def validate_xml(xml_content):
    """验证 XML 内容"""
    root, error = parse_xml(xml_content)
    if error:
        return {
            'success': False,
            'error': error
        }
    
    products = extract_bands(root)
    if not products:
        return {
            'success': False,
            'error': 'No products found in XML file'
        }
    
    rules = define_rules()
    results_list = []
    all_valid = True
    
    for product_name, models in products.items():
        product_result = {
            'product': product_name,
            'results': []
        }
        
        for model_name, bands in models.items():
            model_result = validate_model(model_name, bands, rules)
            product_result['results'].append(model_result)
            
            if len(model_result['invalid']) > 0:
                all_valid = False
        
        results_list.append(product_result)
    
    return {
        'success': True,
        'data': {
            'results': results_list,
            'allValid': all_valid
        }
    }

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # 测试模式
        test_xml = """
        <ModelInfo xmlns="http://www.motorola-mobility.com/globaltest/nextest2010/modelinfo/">
            <Product name="TEST">
                <Model name="ROW">
                    <Band name="GSM_850" device_path="0" Rfpath_name="UUT_RF_CONN1_TO_TESTSET_MAIN_RF" />
                    <Band name="WLAN_80211_5G" device_path="1" Rfpath_name="UUT_RF_CONN9_TO_TESTSET_MAIN_RF" />
                </Model>
            </Product>
        </ModelInfo>
        """
        result = validate_xml(test_xml)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    elif len(sys.argv) > 1:
        # 从文件读取 XML 内容
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            result = validate_xml(xml_content)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        except Exception as e:
            print(json.dumps({
                'success': False,
                'error': f'Error reading file: {str(e)}'
            }, ensure_ascii=False))
            return
    
    # 从标准输入读取 XML 内容
    xml_content = sys.stdin.read()
    result = validate_xml(xml_content)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()