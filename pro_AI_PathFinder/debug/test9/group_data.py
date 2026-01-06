import json
from collections import defaultdict


def group_data_by_test_group_and_key_parts(json_file_path):
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 创建一个嵌套的defaultdict来存储分组结果
    grouped_data = defaultdict(lambda: defaultdict(list))

    # 遍历数据并按"Test Group"和"Key parts"分组
    for item in data:
        test_group = item.get("Test Group", "Unknown")
        key_parts = item.get("Key parts", "None")

        # 将数据项添加到相应的分组中
        grouped_data[test_group][key_parts].append(item)

    # 将defaultdict转换为普通字典以便JSON序列化
    result = {test_group: dict(key_parts_data) for test_group, key_parts_data in grouped_data.items()}

    return result


def save_grouped_data(grouped_data, output_file_path):
    # 将分组后的数据保存到新的JSON文件
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(grouped_data, f, ensure_ascii=False, indent=2)

    print(f"分组后的数据已保存到 {output_file_path}")


def do_group_data(station):
    # 输入文件路径
    input_file_path = rf".\debug\test9\docs\{station}_output.json"

    # 输出文件路径
    output_file_path = rf".\debug\test9\docs\{station}_grouped_output.json"

    # 按"Test Group"和"Key parts"分组数据
    grouped_data = group_data_by_test_group_and_key_parts(input_file_path)

    # 保存分组后的数据
    save_grouped_data(grouped_data, output_file_path)

    # 打印分组结果的摘要
    print("数据分组完成。分组摘要：")
    for test_group, key_parts_data in grouped_data.items():
        print(f"  {test_group} 组:")
        for key_parts, items in key_parts_data.items():
            print(f"    {key_parts}: {len(items)} 项")


if __name__ == "__main__":
    do_group_data()
