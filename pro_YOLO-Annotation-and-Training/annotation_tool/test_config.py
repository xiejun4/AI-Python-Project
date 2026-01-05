#!/usr/bin/env python3
"""
测试配置文件加载功能
"""

import sys
import os

sys.path.append('.')

# 模拟AnnotationTool类的load_default_classes方法
import json

def test_load_default_classes():
    """
    测试从配置文件加载默认类别
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, "config.json")
    default_classes = ["马叔", "桂英"]
    
    print("=== 测试配置文件加载功能 ===")
    print(f"配置文件路径: {config_file}")
    print(f"配置文件存在: {os.path.exists(config_file)}")
    
    # 读取配置文件
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"配置内容: {config}")
                if "default_classes" in config and isinstance(config["default_classes"], list):
                    default_classes = config["default_classes"]
                    if not default_classes:
                        default_classes = ["马叔", "桂英"]
        print(f"加载的默认类别: {default_classes}")
        print("✅ 配置文件加载成功！")
        return default_classes
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return ["马叔", "桂英"]
    except Exception as e:
        print(f"❌ 读取配置文件时出错: {e}")
        return ["马叔", "桂英"]

if __name__ == "__main__":
    test_load_default_classes()