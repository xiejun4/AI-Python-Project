import shutil
import os
import zipfile
from pathlib import Path
from collections import namedtuple


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


FilterResult = namedtuple('FilterResult', ['filtered_files', 'renamed_files', 'errors'])


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


def extract_file_info(filter_results):
    """
    该函数用于从 filter_results 对象中提取第一个文件的相关信息。
    包括文件所在目录、文件名、文件扩展名以及不带扩展名的文件名。

    参数:
    filter_results (object): 包含 filtered_files 属性的对象，filtered_files 是一个文件路径列表。

    返回:
    tuple: 包含文件目录、文件名、文件扩展名和不带扩展名的文件名的元组。
           如果过程中出现异常，则返回 None。
    """
    try:
        # 尝试获取 filter_results 对象的 filtered_files 属性中的第一个文件路径
        # 若 filtered_files 列表为空或者 filter_results 没有该属性，会触发异常
        file_path = filter_results
        # 获取文件所在的目录
        file_dir = os.path.dirname(file_path)
        # 获取完整的文件名
        file_name = os.path.basename(file_path)
        # 获取文件的扩展名
        file_ext = os.path.splitext(file_name)[1]
        # 获取不带扩展名的文件名
        file_name_without_ext = os.path.splitext(file_name)[0]
        return file_path, file_dir, file_name, file_ext, file_name_without_ext
    except AttributeError:
        # 当 filter_results 对象没有 filtered_files 属性时触发此异常
        print("错误: 传入的对象没有 'filtered_files' 属性。")
    except IndexError:
        # 当 filtered_files 列表为空时触发此异常
        print("错误: 'filtered_files' 列表为空。")
    except Exception as e:
        # 捕获其他未知异常
        print(f"发生未知错误: {e}")
    return None


def delete_directory_contents(target_dir=r"C:\Users\xiejun4\Desktop\pro_PathFinder\debug\test9\logs"):
    """
    删除指定目录下的所有文件夹、子文件夹、文件以及.zip文件，
    但保留.log_zip类型的文件

    参数:
        target_dir: 要清理的目标目录路径
    """
    # 检查目标目录是否存在
    if not os.path.exists(target_dir):
        print(f"目录不存在: {target_dir}")
        return

    # 检查是否是一个目录
    if not os.path.isdir(target_dir):
        print(f"不是一个目录: {target_dir}")
        return

    # 遍历目录中的所有内容
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)

        try:
            # 如果是文件夹，递归删除
            if os.path.isdir(item_path):
                print(f"删除文件夹: {item_path}")
                shutil.rmtree(item_path)
            # 如果是文件，判断是否为.log_zip类型
            else:
                # 保留.log_zip文件，删除其他所有文件（包括.zip）
                if item.endswith('.log_zip'):
                    print(f"保留文件: {item_path}")
                else:
                    print(f"删除文件: {item_path}")
                    os.remove(item_path)
        except Exception as e:
            print(f"处理 {item_path} 时出错: {e}")


def do_unzip_init(directory_to_clean=r"C:\Users\xiejun4\Desktop\pro_PathFinder\debug\test9\logs"):
    # 调用函数进行清理
    delete_directory_contents(directory_to_clean)
    print("清理完成")


def do_unzip(zip_path):
    # -------------------- unzip_otplus 调试 -------------------------
    # 复制 xx.log_zip文件，然后重命名 xx.log_zip文件为 xx.zip。
    res = unzip_otplus_helper_rename_log_zip(zip_path)
    print(f'返回值：{res[0]} \n信息：{res[1]}')

    # 创建Path对象并获取父目录
    path_obj = Path(zip_path)
    directory = path_obj.parent
    print(f"目录路径: {directory}")

    # 解压 log_zip文件
    try:
        zip_path_rename = res[2]
    except IndexError:
        print(f"error: result list is not exist element of index 2. zip_path:{zip_path}")
        zip_path_rename = None

    if os.name == 'nt':  # Windows 系统
        config = {
            "zip_file_path": zip_path_rename,
            "folder_in_zip": "prod/log",
            "dest_path": f"{directory}\\extracted_logs",
            "overwrite": True
        }
    else:  # Linux 系统
        config = {
            "zip_file_path": zip_path_rename,
            "folder_in_zip": "prod/log",
            "dest_path": f"{directory}/extracted_logs",
            "overwrite": True
        }

    success, msg = unzip_otplus_helper_unzip_file(**config)
    print(f"\n{'成功' if success else '失败'}: {msg}")
    filter_results = []
    if success:
        keywords = {"_startup", "resourceHistory.xml.txt", ".txt", ".xml"}
        filter_results = unzip_otplus_helper_filter_files2(config["dest_path"], keywords)

        print("\n过滤后保留的文件:")
        for file in filter_results.filtered_files:
            print(file)

    # 0.解析文件信息：获取文件目录，文件名，文件扩展名，不带扩展名的文件名
    file_path, file_dir, file_name, file_ext, file_name_without_ext = extract_file_info(
        filter_results.filtered_files[0])

    # 返回解析后的文件信息
    return file_path, file_dir, file_name, file_ext, file_name_without_ext


def do_unzip_process(file_name='NexTestLogs_L2VISION_LAGOS25_EUROPE_L2_VISION_BE37-LVISION14_Failed_ADB_input keyevent 223_ZY32M2F9WB_2025-09-15_T13-09-57~22.log_zip'):
    # 指定要清理的目录
    directory_to_clean = r"C:\Users\xiejun4\Desktop\pro_PathFinder\debug\test9\logs"
    do_unzip_init(directory_to_clean)

    if os.name == 'posix':  # Linux
        log_zip_path = '/opt/xiejun4/pro_PathFinder/uploads/machuan_LAR02_TRACKID_fail.log_zip'
    else:  # windows
        log_zip_path = os.path.join(os.path.dirname(__file__),
                                    'logs',
                                    file_name)

    file_path, file_dir, file_name, file_ext, file_name_without_ext = do_unzip(log_zip_path)

    # 打印文件信息
    print(f"文件路径: {file_path}")
    print(f"文件目录: {file_dir}")
    print(f"文件名: {file_name}")
    print(f"文件扩展名: {file_ext}")
    print(f"不带扩展名的文件名: {file_name_without_ext}")

    return file_path, file_dir, file_name, file_ext, file_name_without_ext


if __name__ == "__main__":
    file_name = 'NexTestLogs_L2VISION_LAGOS25_EUROPE_L2_VISION_BE37-LVISION14_Failed_ADB_input keyevent 223_ZY32M2F9WB_2025-09-15_T13-09-57~22.log_zip'
    do_unzip_process(file_name)
