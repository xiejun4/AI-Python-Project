import json
import pandas as pd
import os
import threading
import time
from queue import Queue


def process_dataframe(df):
    """处理DataFrame数据：日期转换、NaN替换、字段名翻译"""
    required_date_columns = ['日期', '截止日期']
    for col in required_date_columns:
        if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d')

    df = df.fillna('')

    field_mapping = {
        "Status": "状态",
        "Categrey": "类别"
    }

    return [{field_mapping.get(key, key): value for key, value in item.items()}
            for item in df.to_dict('records')]


def show_progress(queue):
    """显示进度提示，直到队列接收到完成信号"""
    print("正在读取Excel文件，请稍候...")
    start_time = time.time()
    while True:
        if not queue.empty():
            msg = queue.get()
            if msg == 'DONE':
                elapsed = time.time() - start_time
                print(f"读取完成，耗时: {elapsed:.2f}秒")
                break
        time.sleep(0.5)
        print(".", end="", flush=True)


def read_excel_file(excel_path, sheet_name, queue):
    """在后台线程中读取Excel文件"""
    try:
        excel_file = pd.ExcelFile(excel_path)
        df = excel_file.parse(sheet_name)
        queue.put('DONE')  # 发送完成信号
        return df
    except Exception as e:
        queue.put(f"ERROR: {str(e)}")
        raise


def convert_excel_to_json(excel_path, sheet_name='FE NTF', json_filename_template="{base_name}_{sheet_name}.json"):
    """主函数：读取Excel并转换为JSON"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"未找到Excel文件: {excel_path}")

        # 从文件路径中提取基本文件名（不包含扩展名）
        base_name = os.path.splitext(os.path.basename(excel_path))[0]
        # 替换基本文件名中的空格为下划线
        base_name = base_name.replace(' ', '_')

        # 创建队列用于线程间通信
        progress_queue = Queue()

        # 启动进度提示线程
        progress_thread = threading.Thread(target=show_progress, args=(progress_queue,))
        progress_thread.daemon = True
        progress_thread.start()

        # 启动Excel读取线程
        read_thread = threading.Thread(target=read_excel_file,
                                       args=(excel_path, sheet_name, progress_queue))
        read_thread.start()
        read_thread.join()  # 等待读取完成

        # 获取读取结果
        if not progress_queue.empty():
            msg = progress_queue.get()
            if msg.startswith("ERROR:"):
                raise Exception(msg[7:])  # 提取错误信息

        # 从全局变量获取DataFrame
        df = read_excel_file(excel_path, sheet_name, progress_queue)

        # 数据处理和保存逻辑保持不变
        print(f"工作表 '{sheet_name}' 的基本信息：")
        df.info()

        rows, columns = df.shape
        if rows < 100 and columns < 20:
            print('数据全部内容信息：')
            print(df.to_csv(sep='\t', na_rep='nan'))
        else:
            print('数据前几行内容信息：')
            print(df.head().to_csv(sep='\t', na_rep='nan'))

        processed_data = process_dataframe(df)

        # 替换 sheet_name 中的空格为下划线
        sheet_name = sheet_name.replace(' ', '_')
        # 使用模板生成 json_filename，包含从Excel文件名提取的基本名称
        json_filename = json_filename_template.format(base_name=base_name, sheet_name=sheet_name)
        json_path = os.path.abspath(os.path.join(script_dir, '..', '..', 'docs', json_filename))

        json_dir = os.path.dirname(json_path)
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)

        print(f"数据已成功写入JSON文件: {json_path}")

    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
    except KeyError as e:
        print(f"键错误: 数据中缺少 {e} 列")
    except Exception as e:
        print(f"发生未知错误: {e}")


def batch_convert_excel_to_json(sheet_name='FE NTF', json_filename_template="{base_name}_{sheet_name}.json"):
    """批量处理目录下的所有Excel文件并转换为JSON"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        docs_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'docs'))

        # 检查文档目录是否存在
        if not os.path.exists(docs_dir):
            raise FileNotFoundError(f"文档目录不存在: {docs_dir}")

        # 获取目录下所有Excel文件
        excel_files = [f for f in os.listdir(docs_dir) if f.endswith('.xlsx')]

        if not excel_files:
            raise FileNotFoundError(f"在 {docs_dir} 中未找到Excel文件")

        print(f"找到 {len(excel_files)} 个Excel文件，开始批量处理...")

        success_count = 0
        fail_count = 0

        # 遍历并处理每个Excel文件
        for filename in excel_files:
            file_path = os.path.join(docs_dir, filename)
            print(f"\n正在处理: {filename}")

            try:
                # 修改全局变量中的excel_path
                global excel_path
                excel_path = file_path

                # 调用原有的转换函数
                convert_excel_to_json(excel_path, sheet_name, json_filename_template)
                success_count += 1

            except FileNotFoundError as e:
                print(f"文件不存在错误: {e}")
                fail_count += 1
            except KeyError as e:
                print(f"键错误: 数据中缺少 {e} 列")
                fail_count += 1
            except pd.errors.ParserError as e:
                print(f"Excel解析错误: {e}")
                fail_count += 1
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                fail_count += 1

        # 输出处理摘要
        print(f"\n批量处理完成！")
        print(f"成功: {success_count} 个，失败: {fail_count} 个")

    except FileNotFoundError as e:
        print(f"错误: {e}")
    except PermissionError as e:
        print(f"权限错误: 无法访问目录 {docs_dir}, {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


def generate_config_json(json_paths):
    """生成 config.json 文件"""
    config_data = {
        "jsonFiles": []
    }
    for json_path in json_paths:
        # 假设文件名中包含日期信息，例如 "TITANS项目_SOVP2_Report__0615_FE_NTF.json"
        base_name = os.path.basename(json_path)
        date_str = base_name.split('__')[1].split('_')[0]
        report_name = f"{date_str} 日报表"
        relative_path = os.path.relpath(json_path, os.path.dirname(os.path.abspath(__file__)))
        config_data["jsonFiles"].append({
            "path": relative_path,
            "name": report_name
        })

    # 保存 config.json 文件
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.abspath(os.path.join(config_dir, '..', '..', 'docs'))
    config_path = os.path.join(config_dir, 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

    print(f"config.json 文件已生成: {config_path}")

def load_json_files(docs_dir=None, exclude_config=True, verbose=True):
    """
    加载指定目录下的所有JSON文件（默认排除config.json）

    参数:
        docs_dir (str, optional): JSON文件所在目录路径，默认为脚本上级目录的docs目录
        exclude_config (bool, optional): 是否排除config.json，默认为True
        verbose (bool, optional): 是否打印详细信息，默认为True

    返回:
        list: JSON文件的完整路径列表

    异常:
        FileNotFoundError: 当指定目录不存在时抛出
        PermissionError: 当没有权限访问指定目录时抛出
        NotADirectoryError: 当指定的路径不是目录时抛出
    """
    try:
        # 如果未指定目录，使用默认路径
        if docs_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            docs_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'docs'))

        # 验证目录是否存在
        if not os.path.exists(docs_dir):
            raise FileNotFoundError(f"指定的目录不存在: {docs_dir}")

        # 验证是否为目录
        if not os.path.isdir(docs_dir):
            raise NotADirectoryError(f"指定的路径不是目录: {docs_dir}")

        # 获取所有JSON文件
        if exclude_config:
            json_files = [f for f in os.listdir(docs_dir)
                          if f.endswith('.json') and f.lower() != 'config.json']
        else:
            json_files = [f for f in os.listdir(docs_dir) if f.endswith('.json')]

        # 构建完整路径
        json_paths = [os.path.join(docs_dir, f) for f in json_files]

        if verbose:
            print(f"找到 {len(json_paths)} 个 JSON 文件:")
            for path in json_paths:
                print(f"- {path}")

        return json_paths

    except FileNotFoundError as e:
        print(f"错误: 文件或目录不存在 - {e}")
        raise
    except PermissionError as e:
        print(f"错误: 权限不足，无法访问目录 - {e}")
        raise
    except NotADirectoryError as e:
        print(f"错误: 指定的路径不是有效目录 - {e}")
        raise
    except Exception as e:
        print(f"未知错误: {e}")
        raise


if __name__ == "__main__":
    # convert_excel_to_json()

    # 批量处理所有Excel文件
    # batch_convert_excel_to_json()

    # # 获取 docs 目录下的所有 JSON 文件
    # jsons_dir = os.path.dirname(os.path.abspath(__file__))
    # docs_dir = os.path.abspath(os.path.join(jsons_dir, '..', '..', 'docs'))
    # json_files = [f for f in os.listdir(docs_dir) if f.endswith('.json') and f != 'config.json']
    #
    # # 构建完整的文件路径列表
    # json_paths = [os.path.join(docs_dir, f) for f in json_files]
    #
    # # 打印找到的文件
    # print(f"找到 {len(json_paths)} 个 JSON 文件:")
    # for path in json_paths:
    #     print(f"- {path}")

    # 调用生成配置文件的函数
    json_paths = load_json_files(docs_dir=None, exclude_config=True, verbose=False)
    generate_config_json(json_paths)