# pip3 show lxml
#
# Name: lxml
# Version: 6.0.1
# Summary: Powerful and Pythonic XML processing library combining libxml2/libxslt with the ElementTree API.
# 这是联想笔记本上python的site-packages路径。
# Location: C:\Users\xiejun4\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages
from lxml import etree


def remove_pass_tests(xml_file_path, output_file_path):
    try:
        # 解析XML文件
        tree = etree.parse(xml_file_path)
    except etree.XMLSyntaxError as e:
        print(f"XML解析错误: {e}")
        return

    root = tree.getroot()

    # 定义命名空间（如果有）。如果没有命名空间，可以使用空字典或None
    # namespaces = {
    #    'ns': 'http://www.example.com/ns'  # 请根据实际命名空间修改
    # }
    namespaces = {
        'ns': ''  # 请根据实际命名空间修改
    }
    # 如果没有命名空间，可以省略namespaces参数
    # 查找所有 <Test> 节点
    # test_nodes = root.findall('.//ns:Test', namespaces) if 'ns' in namespaces else root.findall('.//Test')
    test_nodes = root.findall('.//Test')
    # 列表推导式收集所有需要删除的 <Test> 节点
    tests_to_remove = [
        test for test in test_nodes
        # if test.find('.//ns:PassFail/ns:DI[ns:N="Status"][ns:V="PASS"]', namespaces) is not None
        if test.find('.//PassFail/DI[N="Status"][V="FAIL"]') is None
    ]

    # 删除收集到的 <Test> 节点
    for test in tests_to_remove:
        parent = test.getparent()
        if parent is not None:
            parent.remove(test)
            print(f"已删除 <Test> 节点，因为 Status 为 PASS.")

    # 将修改后的XML写入新文件
    try:
        # 美化输出
        etree.indent(tree, space='    ')
        tree.write(output_file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        print(f"修改后的XML已保存到 {output_file_path}")
    except Exception as e:
        print(f"保存XML时出错: {e}")
