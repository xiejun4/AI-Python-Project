import zipfile
import os
import shutil
from collections import namedtuple
import time
# from pro_PathFinder.functions.web_log_client import download_log_file

# 定义结果容器（建议放在文件顶部）
FilterResult = namedtuple('FilterResult', ['filtered_files', 'renamed_files', 'errors'])

def unzip_otplus_helper_unzip_file(
        zip_file_path: str,
        folder_in_zip: str,
        dest_path: str,
        overwrite: bool = True
) -> tuple:  # 移除泛型，或改为 (bool, str)（3.10+支持）
    """
    解压zip中指定目录下的所有文件到目标路径（支持覆盖）

    参数:
        zip_file_path: zip文件路径
        folder_in_zip: zip内待解压的目录（如"prod/log"）
        dest_path: 目标解压路径
        overwrite: 是否覆盖已存在文件（默认True）
    """
    try:

        # 1.如果目标目录存在，先删除目录下的文件，然后删除目录
        if os.path.exists(dest_path):
            for root, dirs, files in os.walk(dest_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"🗑️ 删除文件: {file_path}")
                    except PermissionError:
                        return False, f"❌ 权限错误: 无法删除 {file_path}"
                    except Exception as e:
                        return False, f"❌ 删除文件失败: {e}"
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                        print(f"🗑️ 删除目录: {dir_path}")
                    except PermissionError:
                        return False, f"❌ 权限错误: 无法删除 {dir_path}"
                    except Exception as e:
                        return False, f"❌ 删除目录失败: {e}"
            try:
                os.rmdir(dest_path)
                print(f"🗑️ 删除目录: {dest_path}")
            except PermissionError:
                return False, f"❌ 权限错误: 无法删除 {dest_path}"
            except Exception as e:
                return False, f"❌ 删除目录失败: {e}"
        # 如果目标目录不存在，先创建目录
        os.makedirs(dest_path, exist_ok=True)


        # 2.解压文件
        # 标准化路径格式（保持不变）
        folder_in_zip = folder_in_zip.rstrip('/') + '/'
        dest_path = os.path.abspath(dest_path)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # 筛选文件（保持不变）
            target_files = [f for f in zip_ref.namelist()
                            if f.startswith(folder_in_zip) and not f.endswith('/')]

            if not target_files:
                return False, f"⚠️ 未找到任何文件: {folder_in_zip}"

            os.makedirs(dest_path, exist_ok=True)

            for file_in_zip in target_files:
                # 文件覆盖逻辑（保持不变）
                file_name = os.path.basename(file_in_zip)
                dest_file = os.path.join(dest_path, file_name)

                if os.path.exists(dest_file):
                    if overwrite:
                        try:
                            os.remove(dest_file)
                            print(f"🗑️ 删除已存在文件: {dest_file}")
                        except PermissionError:
                            return False, f"❌ 权限错误: 无法删除 {dest_file}"
                        except Exception as e:
                            return False, f"❌ 删文件失败: {e}"
                    else:
                        print(f"⚠️ 跳过已存在文件: {dest_file}")
                        continue

                # 解压&清理目录（保持不变）
                zip_ref.extract(file_in_zip, dest_path)
                temp_path = os.path.join(dest_path, file_in_zip)
                os.rename(temp_path, dest_file)

                dir_to_clean = os.path.dirname(temp_path)
                while dir_to_clean != dest_path:
                    try:
                        os.rmdir(dir_to_clean)
                        dir_to_clean = os.path.dirname(dir_to_clean)
                    except OSError:
                        break

            return True, f"✅ 成功解压 {len(target_files)} 个文件到: {dest_path}"

    # 异常处理（保持不变）
    except FileNotFoundError:
        return False, f"❌ 找不到文件: {zip_file_path}"
    except zipfile.BadZipFile:
        return False, f"❌ 无效的zip文件: {zip_file_path}"
    except Exception as e:
        return False, f"❌ 未知错误: {str(e)}"

def unzip_otplus_helper_filter_files(dest_path: str):
    """
    过滤掉目标路径中文件名包含指定关键字的文件
    """
    keywords = {"_startup", "resourceHistory.xml.txt", ".txt"}
    for root, dirs, files in os.walk(dest_path):
        for file in files:
            for keyword in keywords:
                if keyword in file:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"🗑️ 删除文件: {file_path}")
                    except PermissionError:
                        return False, f"❌ 权限错误: 无法删除 {file_path}"
                    except Exception as e:
                        return False, f"❌ 删除文件失败: {e}"

    return True

def unzip_otplus_helper_filter_files2(
        dest_path: str,
        keywords: set
) -> FilterResult:
    """
    过滤并记录删除的文件（支持批量错误收集）

    返回:
        FilterResult(filter_files=List[str], renamed_files=List[str], errors=List[str])
    """
    # deleted_files = []
    filtered_files = []
    renamed_files = []
    errors = []

    # 标准化路径（避免多余斜杠）
    dest_path = os.path.normpath(dest_path)

    for root, _, files in os.walk(dest_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            # 1. 过滤含有关键字的文件（跳过删除）
            if any(kw in filename for kw in keywords):
                continue  # 跳过需要过滤的文件

            # 2. 检查并重命名.log扩展名
            base_name, ext = os.path.splitext(filename)
            if ext.lower() == ".log":
                new_filename = f"{base_name}.txt"
                new_filepath = os.path.join(root, new_filename)

                try:
                    # 处理同名文件（可选：覆盖或跳过）
                    if os.path.exists(new_filepath):
                        errors.append(f"跳过重命名: {file_path} → {new_filepath}（文件已存在）")
                        continue

                    os.rename(file_path, new_filepath)
                    renamed_files.append((file_path, new_filepath))
                    filtered_files.append(new_filepath)  # 记录新路径
                except PermissionError:
                    errors.append(f"权限错误: 无法重命名 {file_path}")
                except Exception as e:
                    errors.append(f"重命名失败: {file_path} → {str(e)}")
            else:
                # 保留其他扩展名的文件
                filtered_files.append(file_path)


    # 打印操作摘要（可选）
    print(f"📝 过滤结果：保留{len(filtered_files)}个文件，重命名{len(renamed_files)}个文件，发现{len(errors)}个异常")
    return FilterResult(filtered_files=filtered_files, renamed_files=renamed_files, errors=errors)

def unzip_otplus_helper_rename_log_zip(file_path):
    """
    将OT+的log文件复制一份，新文件名头部添加"new_"并将扩展名改为xxx.zip

    参数:
        file_path: OT+的log文件路径

    返回:
        bool: 操作是否成功
    """
    # 原文件名
    original_file = file_path  # 'C:\\Users\\xiaoxiang3\\Desktop\\99999 - MTK log 分析\\machuan_L2AR.log_zip'
    # 获取文件名和扩展名
    file_name, _ = os.path.splitext(original_file)
    # 新文件名
    new_file = f'new_{os.path.basename(file_name)}.zip'
    new_file_path = os.path.join(os.path.dirname(original_file), new_file)

    try:
        # 检查新文件是否存在，如果存在则删除
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        # 复制文件
        shutil.copy2(original_file, new_file_path)
        return True, f'已将 {original_file} 复制为 {new_file_path}', new_file_path
    except FileNotFoundError:
        return False, f'错误：未找到文件 {original_file}'
    except Exception as e:
        return False, f'错误：发生了一个未知错误 {e}'

def unzip_otplus_helper_delete_zip_files(directory_path):
    """
    删除指定目录下扩展名是.zip和.log_zip的文件

    参数:
        directory_path (str): 指定目录的路径，如 ".\\uploads"
    """
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"错误: 目录 '{directory_path}' 不存在")
        return False

    # 检查是否是目录
    if not os.path.isdir(directory_path):
        print(f"错误: '{directory_path}' 不是一个目录")
        return False

    # 遍历目录中的所有文件
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 检查文件扩展名是否为.zip或.log_zip
            if file.endswith(('.zip', '.log_zip')):
                try:
                    # 删除文件
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {e}")

    return True

def unzip_otplus_helper_rotate_log_file(log_path, max_size_mb=3):
    """
    监控日志文件大小，超过指定大小时按时间戳备份并创建新文件

    参数:
        log_path (str): 日志文件的完整路径
        max_size_mb (int): 最大文件大小(MB)，默认为3MB
    """
    # 转换为字节单位
    max_size_bytes = max_size_mb * 1024 * 1024

    # 检查文件是否存在
    if not os.path.exists(log_path):
        print(f"警告: 日志文件 '{log_path}' 不存在")
        return

    # 获取文件大小
    file_size = os.path.getsize(log_path)

    # 如果文件大小超过限制
    if file_size > max_size_bytes:
        # 生成备份文件名，使用时间戳
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = f"{log_path}.{timestamp}"

        try:
            # 备份原日志文件
            shutil.copy2(log_path, backup_path)
            print(f"已备份日志文件至: {backup_path}")

            # 创建新的空日志文件
            with open(log_path, 'w') as f:
                f.write('')
            print(f"已创建新的日志文件: {log_path}")

            return True
        except Exception as e:
            print(f"备份日志文件时出错: {e}")
            return False
    else:
        print(f"日志文件大小正常 ({file_size / 1024 / 1024:.2f}MB / {max_size_mb}MB)")
        return False

# 主程序（保持不变）
if __name__ == '__main__':

    # -------------------- client 调试 -------------------------
    # 请求的log文件
    log_filename = 'machuan_L2AR_pass.zip'

    # 构造请求的 URL
    url =  f'http://localhost:5000/get_log/{log_filename}'

    # 拼接完整的保存路径
    save_directory = "D:\\99999 - MTK log 分析\\"
    save_path = os.path.join(save_directory, f'received_{log_filename}')
    # zip_path,msg = download_log_file(url,save_path)

    # -------------------- unzip_otplus 调试 -------------------------

    # file_path = 'D:\\99999 - MTK log 分析\\machuan_L2AR_fail.log_zip1'
    file_path = 'D:\\99999 - MTK log 分析\\machuan_L2AR_pass.log_zip'
    res = unzip_otplus_helper_rename_log_zip(file_path)
    print(f'返回值：\n{res[0]} \n信息：\n{res[1]}')


    zip_path_rename = res[2]
    config = {
        "zip_file_path": zip_path_rename, # r"D:\99999 - MTK log 分析\received_machuan_L2AR_pass.zip",
        "folder_in_zip": "prod/log",
        "dest_path": r"D:\99999 - MTK log 分析\extracted_logs",
        "overwrite": True
    }

    success, msg = unzip_otplus_helper_unzip_file(**config)
    print(f"\n{'成功' if success else '失败'}: {msg}")
    if success:
        # success2, msg2 = filter_files(config["dest_path"])
        # print(f"\n{'成功' if success2 else '失败'}: {msg2}")

        keywords = {"_startup", "resourceHistory.xml.txt", ".txt"}
        filter_results = unzip_otplus_helper_filter_files2(config["dest_path"], keywords)

        print("\n过滤后保留的文件:")
        for file in filter_results.filtered_files:
            print(file)

        print("\n重命名的文件:")
        for file in filter_results.renamed_files:
            print(file)

        print("\n出现的错误:")
        for error in filter_results.errors:
            print(error)

    if not success:
        input("按任意键退出...")