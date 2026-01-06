import os

# 定义要创建的文件夹名称列表
folder_names=[
"9999-临时+待处理",
"快速笔记",
"QuickNotes",
"谢军-2024-物联网",
"谢军-2024-汽车",
"谢军-2024-洋葱英语",
"谢军-2024-英语流利说-笔记",
"谢军-2024-新概念英语语法-初中版",
"谢军-2024-操作系统",
"谢军-2024-数学",
"谢军-2024-英语",
"谢军-2024-语文",
"谢军-2024-测评师",
"谢军-2024-无线电通讯",
"谢军-2024-AI人工智能-百战程序员",
"谢军-2024-LibLibAI哩布哩布AI在线生图良心总结帖-十分钟了解Pandas核心内容",
"谢军-2024-LibLibAI哩布哩布AI在线生图",
"谢军-2024-Pandas",
"谢军-2024-Python",
"谢军-2024-自然语言",
"谢军-2024-深度学习保姆级教学",
"谢军-2024-PyTorch深度学习快速入门教程（绝对通俗易懂！）【小土堆】"
]

# 假设要在 D:/my_folders 路径下创建
base_path = "D:/99-个人知识图谱"
for folder in folder_names:
    valid_folder_name = folder.replace(" ", "_")
    full_path = os.path.join(base_path, valid_folder_name)
    try:
        os.mkdir(full_path)
        print(f"成功创建文件夹: {full_path}")
    except FileExistsError:
        print(f"文件夹 {full_path} 已存在，跳过创建")
    except Exception as e:
        print(f"创建文件夹 {full_path} 时出错: {e}")


