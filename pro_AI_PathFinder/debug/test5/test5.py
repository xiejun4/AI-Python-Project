import os
import shutil


def delete_temp_files(directory):
    """
    删除指定目录下的temp文件夹，t_json.json文件和.log_zip文件

    参数:
        directory (str): 要清理的目录路径

    返回:
        tuple: (成功删除的文件/文件夹数量, 错误信息列表)
    """
    deleted_count = 0
    errors = []

    # 检查目录是否存在
    if not os.path.exists(directory):
        errors.append(f"目录不存在: {directory}")
        return (deleted_count, errors)

    if not os.path.isdir(directory):
        errors.append(f"{directory} 不是一个有效的目录")
        return (deleted_count, errors)

    try:
        # 处理temp文件夹
        temp_dir = os.path.join(directory, "temp")
        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
            deleted_count += 1

        # 遍历目录中的所有文件
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            # 处理t_json.json文件
            if filename == "t_json.json" and os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1

            # 处理.log_zip文件
            if filename.endswith(".log_zip") and os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1

    except Exception as e:
        errors.append(f"处理过程中发生错误: {str(e)}")

    return (deleted_count, errors)


# 使用示例
if __name__ == "__main__":
    if os.name == 'posix':  # Linux
        target_directory = r'/opt/xiejun4/pro_PathFinder/uploads'
    else:  # windows
        target_directory = r'D:\PythonProject\pro_PathFinder\uploads'
    count, errors = delete_temp_files(target_directory)

    if errors:
        print("清理过程中出现以下错误:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"成功删除了 {count} 个文件/文件夹")
