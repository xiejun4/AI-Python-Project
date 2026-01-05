#!/usr/bin/env python3
"""
图片排序与重命名脚本

功能：
1. 读取指定目录的PNG图片
2. 按照文件名中的特定数字（如_64_中的64）排序
3. 按照1,2,3...依次递增重命名文件

使用说明：
- 直接运行脚本，无需参数
- 脚本会自动处理目标目录中的PNG图片
- 处理结果会输出到控制台
"""

import os
import re

def sort_and_rename_images():
    """
    排序并重新命名图片文件
    """
    # 目标目录
    target_dir = r"D:\PythonProject\pro_PathFinder\debug\YOLO\xunlian\images\train"
    
    print("=== 图片排序与重命名脚本 ===")
    print(f"目标目录: {target_dir}")
    
    # 检查目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误：目录 {target_dir} 不存在")
        return
    
    # 获取目录下所有PNG图片文件
    png_files = [f for f in os.listdir(target_dir) if f.lower().endswith(".png")]
    
    if not png_files:
        print("错误：目录中没有PNG图片文件")
        return
    
    print(f"找到 {len(png_files)} 个PNG图片文件")
    
    # 定义正则表达式，用于提取文件名中的特定数字（如_64_中的64）
    pattern = r"_(\d+)_"
    
    # 提取文件名和对应的排序数字
    file_with_number = []
    for filename in png_files:
        # 提取数字
        match = re.search(pattern, filename)
        if match:
            # 获取匹配到的数字
            number = int(match.group(1))
            file_with_number.append((filename, number))
        else:
            print(f"警告：文件名 {filename} 中未找到符合规则的数字，跳过该文件")
    
    if not file_with_number:
        print("错误：没有符合规则的图片文件")
        return
    
    # 按照提取的数字进行排序
    file_with_number.sort(key=lambda x: x[1])
    
    print("\n排序后的文件列表：")
    for i, (filename, number) in enumerate(file_with_number, 1):
        print(f"{i}. {filename} (排序数字: {number})")
    
    # 依次重命名文件
    print("\n开始重命名文件...")
    success_count = 0
    fail_count = 0
    
    for i, (old_filename, _) in enumerate(file_with_number, 1):
        # 构建新旧文件路径
        old_path = os.path.join(target_dir, old_filename)
        new_filename = f"{i}.png"
        new_path = os.path.join(target_dir, new_filename)
        
        try:
            # 重命名文件
            os.rename(old_path, new_path)
            print(f"成功：{old_filename} -> {new_filename}")
            success_count += 1
        except Exception as e:
            print(f"失败：{old_filename} -> {new_filename}，错误：{e}")
            fail_count += 1
    
    print(f"\n重命名完成！")
    print(f"成功：{success_count} 个文件")
    print(f"失败：{fail_count} 个文件")

if __name__ == "__main__":
    sort_and_rename_images()