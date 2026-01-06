import os
import zipfile
import shutil
import re
import json

class Analysis_basic(object):
    def __init__(self, language, id, info_list):
        self.language = language
        self.id = id
        self.info_list = info_list
        self.mean = ''
        self.indicate = ''
        self.suggest = '' 

    @staticmethod
    def identify(info_list):        
        return True
     
    def analysis_in(self, mean, indicate, suggest):
        self.mean = mean
        self.indicate = indicate
        self.suggest = suggest

    def analysis_out(self):        
        return {'mean':self.mean, 'indicate':self.indicate, 'suggest':self.suggest}
    
    def analysis_process(self):        
        self.mean = ''
        self.indicate = ''
        self.suggest = ''
        
        
class Analysis_baseband(Analysis_basic):
    def __init__(self, language, id, info_list):
        super.__init__(language, id, info_list) 
        # 中文信息输出
        if self.language == 'zh':
            self.mean = ''
            self.indicate = ''
            self.solution = ''
        # 英文信息输出
        else:
            self.mean = ''
            self.indicate = ''
            self.solution = ''

    @staticmethod
    def identify(info_list):   
        _fail_msg = info_list.get('failMsg','Unknow')
        return True
        
# input parameter, test item/test_value...
# return json format analysis string
def generate_json_analysis_report(infor_dict):
    json_template = {
    "Report_Theme": "Interpretation of ZY22LC4HHC MTK_WLAN_5G_C0_TX_POWER_MCH100_ANT_CW Report",
    "Global_Overview": {
        "Status_Indicators": {
            "WiFi_2_4G_TX": "",
            "WiFi_2_4G_RX": "",
            "WiFi_5G_TX": "",
            "WiFi_5G_RX": "",
            "Bluetooth_TX": "",
            "GPS_RX": "",
            "LTE_TX": "",
            "LTE_RX": ""
        },
        "Key_Conclusion_Summary": {
            "WCN_Status": "The RX RSSI",
            "LTE_status": "The RX RS"
        }
    },
    "Modular_Test_Results_Display": {
        "Test_Analysis": {
            "Test_Project_Results": [
                {
                    "Test_Project": "",
                    "Meaning": "",
                    "Indicator": "",
                    "Test_Value": "",
                    "Range": "",
                    "Test_Result": "",
                    "Trend_Analysis": "",
                    "Implied_Problem_Possibility": "",
                    "Chart_Name": "",
                    "Chart_Content": ""
                }
            ],
            "Analysis_Logic_Chain": "RSSI below the lower limit: Insufficient antenna gain or non - compliant transmission power."
        }
    },
    "Optimization_Suggestions_or_Solutions": {
        "Emergency_Plan": "Use a golden unit to determine whether the whole device is defective or mis - tested. Recalibrate the line loss, compensate for the line loss offset, and then retest.",
        "Radical_Solution": "Disassemble the device to determine whether the materials are defective or the soldering is poor. Optimize the incoming materials to ensure good products, or optimize the assembly process (see Appendix A - Hardware Modification Guide)."
    }
}
    display = 'Modular_Test_Results_Display'
    analysis = 'Test_Analysis'
    result = 'Test_Project_Results' 
    json_template[display][analysis][result][0]['Test_Project'] = infor_dict['test_name']
    json_template[display][analysis][result][0]['Meaning'] = infor_dict['meaning']
    json_template[display][analysis][result][0]['Indicator'] = infor_dict['indicator']
    json_template[display][analysis][result][0]['Test_Value'] = infor_dict['value']
    json_template[display][analysis][result][0]['Range'] = infor_dict['range']
    json_template[display][analysis][result][0]['Test_Result'] = infor_dict['status']
    json_template[display][analysis][result][0]['Trend_Analysis'] = "None"
    json_template[display][analysis][result][0]['Implied_Problem_Possibility'] = infor_dict['solution']
    json_template[display][analysis][result][0]['Chart_Name'] = "None"
    json_template[display][analysis][result][0]['Chart_Content'] = "None"

    return json.dumps(json_template)    
        
# input parameter, nextest_log file path
# return dictionary, include product/process/trackID/status/failMsg/date_time information 
def log_file_name_parse(log_file):
    status = failMsg = ""
    #if type(log_file) == str:
    file_name =os.path.basename(log_file)
    list_split = re.split(r"[!_]", file_name)
    process = list_split[1]
    product = list_split[2]    
    
    #time_reg =r"(\d{4}-\d{2}-\d{2}_T\d{2}-\d{2}-\d{2})"    
    match_time = re.search(r"_\d{4}-\d{2}-\d{2}_T", file_name)
    time_str = match_time.group()    
    sub_str = file_name[:file_name.rfind(time_str)]
    list_split = sub_str.split('_')
    TrackID = list_split[len(list_split)-1]
    if file_name.find("Failed") != -1:        
        status = "Fail"
        _begin = file_name.find("Failed")+len("Failed")
        _end = file_name.rfind(TrackID)
        failMsg = file_name[_begin:_end].strip('_')
    elif file_name.find("Passed") != -1:
        status = "Pass"
        failMsg = ""
    
    return {'product':f'{product}','process':f'{process}','trackID':f'{TrackID}','status':f'{status}','failMsg':f'{failMsg}'}

def analysis_evalAndLogResult_info(log_title_info):
    key_word = 'EvalAndLogResults'    
    _test_name = log_title_info.get('failMsg')
    nextest_log = log_title_info.get('nextest_log')

    if re.search(r'(READ|WRITE)_FIB_QC_MODELFILE',_test_name) != None:
         _test_name = 'FIB'
    
    log_lines_list = read_universal_file(nextest_log)

    search_line = [x for x in log_lines_list if x.rfind(_test_name) != -1 and x.rfind(key_word) != -1]
    list_length = len(search_line)
    if list_length > 0:        
        fail_evaluate_gather =''
        i =0
        while i < list_length:
            _cur_line = search_line[i] 
            _pos = _cur_line.find(key_word) + len(key_word) + 1
            _cur_line = _cur_line[_pos:]

            if _cur_line.find("\t* FAILED *") != -1:
                if len(fail_evaluate_gather) == 0:                
                    fail_evaluate_gather = search_line[i]
                elif len(fail_evaluate_gather) != 0:
                    break
            elif _cur_line.find("\tPASSED\t") != -1 and len(fail_evaluate_gather) !=0:
                break
            elif len(fail_evaluate_gather) != 0:
                fail_evaluate_gather += _cur_line                
            i += 1 

        if len(fail_evaluate_gather) != 0:        
            split_str = re.split(r'[\t]', fail_evaluate_gather)
            if len(split_str) >= 5:
                test_name = split_str[5].strip()
                log_title_info.update({'test_name' : test_name})
            if len(split_str) >= 9:            
                test_desc = split_str[9].strip()
                log_title_info.update({'test_description' : test_desc})
            if len(split_str) >= 10:            
                limit_low = split_str[10].strip()
                log_title_info.update({'limit_low' : limit_low}) 
            if len(split_str) >= 11:           
                limit_high = split_str[11].strip()
                log_title_info.update({'limit_high' : limit_high})
            if len(split_str) >= 12:             
                test_value = split_str[12].strip()
                log_title_info.update({'test_value' : test_value})
            if len(split_str) >= 16:                              
                test_status = split_str[16].strip() 
            if len(split_str) >= 17:                              
                error_message = split_str[17].strip()
                log_title_info.update({'error_msg' : error_message})
                
                _index = error_message.rfind('Details:')
                if _index != -1:
                    _err = error_message[_index + len('Details:'):]
                    log_title_info.update({'error_detail' : _err.strip()})

                _index = error_message.find('Error code:')
                if _index != -1:
                    _p0 = error_message.find('\n', _index)
                    _err = error_message[_index + len('Error code:'):_p0]
                    log_title_info.update({'error_code' : _err.strip()})

                _index = error_message.find('Error code name:')
                if _index != -1:
                    _p0 = error_message.find('\n', _index)
                    _err = error_message[_index + len('Error code name:'):_p0]
                    log_title_info.update({'error_code_name' : _err.strip()})               
                    
            if len(split_str) >= 22:           
                meascode = split_str[22].strip().rstrip('\n')
                log_title_info.update({'meas_code' : meascode})

            split_str = re.split(r'[\n]', fail_evaluate_gather)            
            log_title_info.update({'fail_EvalAndLogResults_line' : split_str[0]})
            try:
                _index = log_lines_list.index(f'{split_str[0]}\n')
                log_title_info.update({'fail_EvalAndLogResults_line_number' : _index})
            except Exception as e:
                print(f"未找到EvalAndLogResults失败行：{e}")



def analysis_nextest_log(log_title_info, language='zh'):  
    fail_description = log_title_info.get('failMsg')
    # retrieve evalAndLogResult information  
    analysis_evalAndLogResult_info(log_title_info)

    # main analysis process
    final_analysis = analysis_main_procedure(log_title_info, language)

    use_info = {}
    #use_info['test_name'] = test_name
    use_info['test_name'] = log_title_info.get('test_description', fail_description)
    use_info['meaning'] = final_analysis[0]
    use_info['indicator'] = final_analysis[1]
    use_info['value'] = log_title_info.get('test_value', '1')
    low = log_title_info.get('limit_low', '0')
    high =log_title_info.get('limit_high', '0')
    use_info['range'] = f'{low}, {high}'
    use_info['status'] = 'FAILED'
    use_info['solution'] = final_analysis[2]

    return use_info

# main analysis process
def process_log_file(log_file, language='zh'):
# def log_sub_file_list(log_file):
    platform = startup_log = nextest_log = detail_log = ""
    temp_dir = "../uploads/temp/"
    log_title_info = log_file_name_parse(log_file)

    if check_station(log_title_info) == "other":
        return ""
    else:
        #unzip nextest_log file
        if os.path.exists(temp_dir):
             shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        zip_file = zipfile.ZipFile(log_file, 'r')
        zip_file.extractall(temp_dir)
        #zip_extract.close()

        if os.path.exists(os.path.join(temp_dir, 'MTK')):
           platform = 'MTK'
        if os.path.exists(os.path.join(temp_dir, 'Qualcomm')):
           platform = 'Qualcomm'
        
        log_title_info.update({'platform':f'{platform}'})

        prod_log_dir =os.path.join(temp_dir, "prod", "log")
        if os.path.exists(prod_log_dir):
           prod_log_list = os.listdir(prod_log_dir)
           for prod_log in prod_log_list:
               if prod_log.endswith("_startup.log"):
                   startup_log =os.path.join(prod_log_dir, prod_log)
                   log_title_info.update({'startup_log':f'{startup_log}'})
               elif prod_log.endswith(".log"):
                   nextest_log =os.path.join(prod_log_dir, prod_log)
                   log_title_info.update({'nextest_log':f'{nextest_log}'})        
        
        fail_infos = analysis_nextest_log(log_title_info, language)

        if(fail_infos != None):
            json_analysis_str = generate_json_analysis_report(fail_infos)

            if os.name == 'posix':  # Linux
                json_file = '/opt/xiejun4/pro_PathFinder/uploads/bt_json.json'
            else:  # windows
                json_file = r'D:\PythonProject\pro_PathFinder\uploads\bt_json.json'

            save_json_string(json_analysis_str, json_file)
            json_content = read_json_file(json_file)

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


            return json_content
    return ''

def read_json_file(file_path='/opt/xiejun4/pro_PathFinder/uploads/bt_json.json'):
    """Read the contents of a JSON file and return the parsed dictionary or list"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_content = json.load(file)
            return json_content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' is not a valid JSON format")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred while reading the file: {e}")
        return None

def save_json_string(json_analysis_str, file_path='/opt/xiejun4/pro_PathFinder/uploads/bt_json.json'):
    """
    Save a JSON string to a JSON file

    Parameters:
    json_analysis_str (str): The JSON string to be saved
    file_path (str): The path to save the file

    Returns:
    bool: True if saved successfully, False otherwise
    """
    try:
        # Parse the JSON string
        data = json.loads(json_analysis_str)

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"JSON file saved successfully to: {file_path}")
        return True

    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON - {e}")
        return False
    except FileNotFoundError:
        print(f"Error: The specified path does not exist - {file_path}")
        return False
    except PermissionError:
        print(f"Error: Permission denied to write file - {file_path}")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred while saving the file - {e}")
        return False

def delete_temp_files(directory='/opt/xiejun4/pro_PathFinder/uploads'):
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
            if filename == "tb_json.json" and os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1

            # 处理.log_zip文件
            if filename.endswith(".log_zip") and os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1

    except Exception as e:
        errors.append(f"处理过程中发生错误: {str(e)}")

    return (deleted_count, errors)

def check_station(log_title_info):
    """
    Process log title information and determine if the process belongs to BT station

    Args:
    log_title_info (dict): Dictionary containing log information, must include "process" key

    Returns:
    dict: Processed log information dictionary
    """
    # Define keywords for BT station (case-insensitive)
    bt_keywords = {"boardtst", "brdtest", "5gfr1bdtst"}

    # Get process value and convert to lowercase for comparison
    process_value = log_title_info.get("process", "").lower()

    # Check if process contains any BT station keywords
    is_bt_station = any(keyword in process_value for keyword in bt_keywords)

    if is_bt_station:
        return "BT"
    else:
        return "other"

def read_universal_file(input_file):
    try:
    # 使用utf-8编码并忽略解码错误
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f_in:
            return f_in.readlines()
    except FileNotFoundError:
        print(f"error\：文件未找到。请检查输入文件 '{input_file}' 是否存在。")
    except UnicodeDecodeError:
        print(f"error\：在读取文件 '{input_file}' 时出现编码问题。")
        # 尝试使用其他编码
        try:
            with open(input_file, 'r', encoding='gb18030', errors='ignore') as f_in:
                return f_in.readlines()
        except Exception as e:
            print(f"无法使用其他编码处理文件：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")
    return None

def analysis_main_procedure(log_title_info, language='zh'):
    suggestion = 'Please retest,if still fail, maybe it\'s PCBA defect (SMT defect/IC defect) and need repair.'
    fail_item = log_title_info.get('failMsg','Unknow')
    meas_code = log_title_info.get('meas_code','')
    platform = log_title_info.get('platform','Unknow')
    tets_name = log_title_info.get('test_name','Unknow')

    if (out_Msg := general_communication_interrupt_failure_analysis(log_title_info, language)) != None:
        return out_Msg
    
    if meas_code.startswith('QIAM') or meas_code.startswith('QIAR'):
        if platform=='MTK':
            return plat_mtk_library_callback_analysis(log_title_info,language)
        elif platform =='Qualcomm':
            if meas_code.startswith('QIAM'):
                qc_log_dir = os.path.join("../uploads/temp/Qualcomm/Logs/", tets_name)
                if os.path.exists(qc_log_dir):
                    qc_log_list = os.listdir(qc_log_dir)
                    for qc_log_single in qc_log_list:
                        if qc_log_single.endswith("_F.xml"): # find fail xml file.
                            qc_log = os.path.join(qc_log_dir, qc_log_single)
                            log_title_info.update({'qc_fail_xml':f'{qc_log}'})                
                return plat_Qualcomm_radio_performance_failure_analysis(log_title_info, language)
                #return [fail_item,fail_item,'Qualcomm RF test fail item analysis in development']
            elif meas_code.startswith('QIAR'):                 
                return plat_Qualcomm_radio_coarse_failure_analysis(log_title_info, language)
    else:
        return boardtest_basic_analysis(log_title_info, language)
       
    return [fail_item, fail_item, suggestion]

def boardtest_basic_analysis(log_title_info, language='zh'):
    """
    分析基础板级测试（meascode长度为8）的失败原因，支持中英文输出
    :param log_title_info: 包含失败信息的字典
    :param language: 输出语言，'zh'为中文，'en'为英文，默认中文
    :return: 包含含义、指示信息、建议的列表，根据语言参数返回对应语言内容
    """
    # 初始化中英文结果字典
    result = {
        'zh': {'mean': '', 'indicate': '', 'suggest': ''},
        'en': {'mean': '', 'indicate': '', 'suggest': ''}
    }

    fail_item = log_title_info.get('failMsg', 'Unknown')
    test_name = log_title_info.get('test_name', 'Unknown')
    test_descrip = log_title_info.get('test_description', '')
    error_msg = log_title_info.get('error_msg', '')
    error_detail = log_title_info.get('error_detail', '')

    # 通用异常信息（中英文）
    moto_tcmd_exception = {
        'en': 'Mototola TCMD executed fail. Maybe the communication interface disconnect during the test.',
        'zh': '摩托罗拉TCMD执行失败。可能是测试过程中通信接口断开连接。'
    }
    advice = {
        'en': 'retest,if still fail, maybe it\'s PCBA defect (SMT defect/IC defect) and need repair.',
        'zh': '请重新测试，若仍失败，可能是PCBA缺陷（SMT缺陷/IC缺陷），需要维修。'
    }

    if (_res := general_motorola_tcmd_failure_analysis(log_title_info, language)) != None:
        return _res 

    if (_res := measure_process_failure_analysis(log_title_info, language)) != None:
        return _res

    # 1. 测试应用启动模式
    # Entry_Handler
    if re.search(r'^ENTRY_HANDLER', fail_item) != None:
        if test_descrip.find('TEST_APPLICATION_LAUNCH_MODE') != -1:
            result['en'] = {'mean': 'OT+ system can be startup in different mode.',
                'indicate': 'OT+ system startup is incorrect mode.',
                'suggest': 'Generally use Launcher tool to startup OT+ system, Confirm the startup is in correct mode.'}
            result['zh'] = {'mean': 'OT+系统可以在不同模式下启动。',
                'indicate': 'OT+系统启动模式不正确。',
                'suggest': '通常使用Launcher工具启动OT+系统，确认启动模式正确。'}

    # 2. Q盘远程可用性
    elif re.search(r'CHECK_Q_REMOTE_IS_AVAILABLE_\d+', fail_item) != None:
        result['en'] = {'mean': 'Q: disk is remote shared space which used to store test record for MQS.',
            'indicate': 'Q: disk access fail, test record upload will fail.',
            'suggest': 'Need technician to run the mount.bat and check the Q: disk can be access.'}
        result['zh'] = {'mean': 'Q盘是远程共享空间，用于存储MQS的测试记录。',
            'indicate': 'Q盘访问失败，测试记录上传将失败。',
            'suggest': '需要技术人员运行mount.bat并检查Q盘是否可访问。'}

    # 3. eBT测试盒状态检查
    elif re.search(r'eBT_BOX_STATUS_CHECK_CLOSE', fail_item) != None:
        result['en'] = {'mean': 'Confirm the eBT test BOX is close before test.',
                        'indicate': 'Detect the eBT test BOX is not close in time.',
                        'suggest': 'Need operator close the eBT test BOX in time.'}
        result['zh'] = {'mean': '测试前确认eBT测试盒已关闭。',
                        'indicate': '检测到eBT测试盒未及时关闭。',
                        'suggest': '需要操作员及时关闭eBT测试盒。'}

    # 4. RF参数管理器初始化
    elif re.search(r"DEFINED_RF_PARAM_MANAGER_\S*", fail_item, re.IGNORECASE) != None:
        result['en'] = {'mean': 'Default file is a zip format file include RF calibration parameter files and NSFT configurate files.',
            'indicate': 'Download default file from remote disk fail.',
            'suggest': 'Make sure the default file is existed in the remote disk or the V: disk can be access.'}
        result['zh'] = {'mean': '默认文件是包含RF校准参数文件和NSFT配置文件的zip格式文件。',
            'indicate': '从远程磁盘下载默认文件失败。',
            'suggest': '确保默认文件存在于远程磁盘或V盘可访问。'}

    # 5. 加载频段数据和附件损耗
    elif re.search(r"LOAD_BAND_DATA_AND_ACCESSORY_LOSSES", fail_item) != None:
        result['en'] = {
            'mean': 'Procuction bands information maintained in the OT+ system and will be used for test.',
            'indicate': 'Query the band information in the OT+ system fail for the current production.',
            'suggest': 'Contact engineer and confirm the band information has maintained in the OT+ system.'
        }
        result['zh'] = {
            'mean': '生产频段信息保存在OT+系统中，将用于测试。',
            'indicate': '查询当前产品在OT+系统中的频段信息失败。',
            'suggest': '联系工程师确认频段信息已在OT+系统中维护。'
        }

    # 6. 配件上电电流测量
    elif re.search(r"MEAS_ACC_ON_CURRENT_BOARD\S*", fail_item) != None:
        if re.search(r"^ACCESSORY_ON_CURRENT_BOARD\S*", test_descrip) != None:
            result['en'] = {
                'mean': 'Measure the VBUS current when the PCBA unit in power on procedure.',
                'indicate': 'Measure the VBUS current value is out of the SPEC.',
                'suggest': f'Confirm the test probe is touched with test point in the PCBA, or {advice["en"]}'
            }
            result['zh'] = {
                'mean': '测量PCBA单元上电过程中的VBUS电流。',
                'indicate': '测量的VBUS电流值超出规格范围。',
                'suggest': f'确认测试探针与PCBA上的测试点接触良好，或{advice["zh"]}'
            }

        # 7. 配件上电状态检查
        elif re.search(r"^ACCESSORY_TURN_ON_STATUS_BOARD\S*", test_descrip) != None:
            result['en'] = {
                'mean': 'Indicate the status of the process of VBUS current measurement.',
                'indicate': 'Exception occured during the VBUS current measurement.',
                'suggest': 'Confirm the power meter is online for measurement.'
            }
            result['zh'] = {
                'mean': '指示VBUS电流测量过程的状态。',
                'indicate': 'VBUS电流测量过程中发生异常。',
                'suggest': '确认功率计在线以进行测量。'
            }    
    # 8. 等待BLAN网络设备出现
    elif re.search(r"^WAIT_FOR_BLAN_NETWORK_DEVICE_ARRIVAL\S*", fail_item) != None:
        result['en'] = {
            'mean': 'BLAN NETWORK DEVICE is \'Mototola USB Networking Driver\', you can check it in PC device manager, below network adapter.',
            'indicate': '\'Mototola USB Networking Driver\' isn\'t enumerated in OS for test.',
            'suggest': '''Confirm \'Motorola USB Networking Driver\' has binded correct, 
                        or check the VBAT/VBUS current are normal in the startup procedure.'''
        }
        result['zh'] = {
            'mean': 'BLAN网络设备是"摩托罗拉USB网络驱动程序"，可在PC设备管理器的网络适配器下查看。',
            'indicate': '测试用的"摩托罗拉USB网络驱动程序"未在操作系统中枚举。',
            'suggest': '''确认"摩托罗拉USB网络驱动程序"已正确绑定，
                        或检查启动过程中的VBAT/VBUS电流是否正常。'''
        }

    # 9. 连接BLAN网络设备
    elif re.search(r"^CONNECT_TO_BLAN_NETWORK_DEVICE\S*", fail_item) != None:
        result['en'] = {'mean': 'Socket connect with \'Mototola USB Networking Driver\' in port 11000 for test.',
            'indicate': 'Socket connect with \'Mototola USB Networking Driver\' fail.',
            'suggest': f'Confirm \'Motorola USB Networking Driver\' has binded correct, or {advice["en"]}'}
        result['zh'] = {'mean': '通过端口11000与"摩托罗拉USB网络驱动程序"建立socket连接以进行测试。',
            'indicate': '与"摩托罗拉USB网络驱动程序"的socket连接失败。',
            'suggest': f'确认"摩托罗拉USB网络驱动程序"已正确绑定，或{advice["zh"]}'}

    # 10. 验证手机DHCP已禁用
    elif re.search(r"^VERIFY_PHONE_DHCP_DISABLED\S*", fail_item) != None:
        result['en'] = {
            'mean': '\'Mototola USB Networking Driver\' is TCPIP device, and need diasble for test.',
            'indicate': '\'Mototola USB Networking Driver\' DHCP disable verify fail.',
            'suggest': 'You can use \'StaticIPConfiguration v2.exe\' in \'C:/prod/bin\' to disable the DHCP for the Motorola device.'
        }
        result['zh'] = {
            'mean': '"摩托罗拉USB网络驱动程序"是TCPIP设备，测试时需要禁用。',
            'indicate': '"摩托罗拉USB网络驱动程序"的DHCP禁用验证失败。',
            'suggest': '可以使用"C:/prod/bin"中的"StaticIPConfiguration v2.exe"禁用摩托罗拉设备的DHCP。'
        }

    # 11. 配件供电下电池电流检查
    elif re.search(r"^MEAS_BATT_CURRENT_ACC_POWERED\S*", fail_item) != None:
        result['en'] = {
            'mean': 'Measure the VBAT current while the VBUS provide the voltage.',
            'indicate': 'Measure the VBAT current value is out of the SPEC.',
            'suggest': f'{advice["en"]}'
        }
        result['zh'] = {
            'mean': '在VBUS提供电压时测量VBAT电流。',
            'indicate': '测量的VBAT电流值超出规格范围。',
            'suggest': f'{advice["zh"]}'
        }

    # 12. 上电检查点查询
    elif re.search(r"^POWER_UP_CHECKPOINT_QUERY\S*", fail_item) != None:
        result['en'] = {
            'mean': 'Query the status of DUT whether it is power up completely.',
            'indicate': 'DUT don\'t power up completely in time, or communication disconnected in the query.',
            'suggest': 'Make the query time longer or add delay before the query.'
        }
        result['zh'] = {
            'mean': '查询DUT是否已完全开机。',
            'indicate': 'DUT未完全开机，或查询过程中通信断开。',
            'suggest': '延长查询时间或在查询前增加延迟。'
        }

    # 13. 等待ADB设备出现
    elif re.search(r"^WAIT_FOR_ADB_DEVICE_ARRIVAL\S*", fail_item) != None:
        result['en'] = {
            'mean': 'Wait ADB device enumeration for test, you can check it in PC device manager',
            'indicate': 'ADB device enumeration fail.',
            'suggest': 'Make sure ADB interface is enabled before wait.'
        }
        result['zh'] = {
            'mean': '等待ADB设备枚举以进行测试，可在PC设备管理器中查看。',
            'indicate': 'ADB设备枚举失败。',
            'suggest': '等待前确保ADB接口已启用。'
        }

    # 14. 连接ADB设备
    elif re.search(r"^CONNECT_TO_ADB_DEVICE", fail_item) != None:
        result['en'] = {
            'mean': 'Check the arrived ADB device cooperated the test DUT.',
            'indicate': 'ADB device list exclude the test DUT.',
            'suggest': 'Make sure ADB connection configuration override the PNP serial number.'
        }
        result['zh'] = {
            'mean': '检查已出现的ADB设备是否与测试DUT匹配。',
            'indicate': 'ADB设备列表中不包含测试DUT。',
            'suggest': '确保ADB连接配置覆盖PNP序列号。'
        }

    # 15. 等待MTK内核端口出现
    elif re.search(r"^WAIT_FOR_MTK_KERNEL_PORT_ARRIVAL", fail_item) != None:
        result['en'] = {
            'mean': 'Check the DUT MTK kernel port arrive for test.',
            'indicate': 'wait for MTK kernel port arrive fail.',
            'suggest': 'Make sure DUT has power up completely and in the correct mode.'
        }
        result['zh'] = {
            'mean': '检查DUT的MTK内核端口是否出现以进行测试。',
            'indicate': '等待MTK内核端口出现失败。',
            'suggest': '确保DUT已完全上电并处于正确模式。'
        }

    # 16. RTCC设置系统时间为当前时间状态
    elif re.search(r"^RTCC_SET_SYTEM_TIME_TO_NOW", fail_item) != None:
        result['en'] = {'mean': 'Synchronize the DUT real time with PC time.',
            'indicate': moto_tcmd_exception['en'], 'suggest': f'{advice["en"]}'}
        result['zh'] = {'mean': '将DUT的实时时间与PC时间同步。',
            'indicate': moto_tcmd_exception['zh'], 'suggest': f'{advice["zh"]}'}

    # 17. 从UTAG验证追踪ID
    elif re.search(r"VERIFY_TRACK_ID_FROM_UTAG\S*", fail_item) != None:
        if test_descrip == "VERIFY_TRACK_ID_FROM_UTAG":
            result['en'] = {
                'mean': 'Read trackID from DUT UTAG and verify whether it is same as the input trackID.',
                'indicate': 'The trackID read from UTAG is not match the label or the input trackID is not match the label.',
                'suggest': 'Make sure the trackID read from UTAG and input match the label.'
            }
            result['zh'] = {
                'mean': '从DUT的UTAG中读取trackID，并验证是否与输入的trackID一致。',
                'indicate': '从UTAG读取的trackID与标签不符，或输入的trackID与标签不符。',
                'suggest': '确保从UTAG读取的trackID和输入的trackID与标签一致。'
            }
        # 18. 从UTAG验证追踪ID状态
        elif test_descrip == "VERIFY_TRACK_ID_FROM_UTAG_STATUS":
            result['en'] = {
                'mean': 'Indicate the status of the \'VERIFY_TRACK_ID_FROM_UTAG\' process.',
                'indicate': moto_tcmd_exception['en'],
                'suggest': f'{advice["en"]}'
            }
            result['zh'] = {
                'mean': '指示"VERIFY_TRACK_ID_FROM_UTAG"过程的状态。',
                'indicate': moto_tcmd_exception['zh'],
                'suggest': f'{advice["zh"]}'
            }

    # 19. FIB追踪ID覆盖状态
    elif re.search("^FIB_TrackID_OVERWRITE", fail_item) != None:
        result['en'] = {
            'mean': 'Write the input trackID into DUT FIB (Factory Information Byte) .',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}'
        }
        result['zh'] = {
            'mean': '将输入的trackID写入DUT FIB（工厂信息字节）。',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}'
        }

    # 20. 读取/写入工厂信息字节状态
    elif re.search(r"^(READ|WRITE)_FIB_QC_MODELFILE", fail_item) != None:
        if re.search(r"^READ_FIB_QC_MODELFILE", fail_item) != None:
            result['en'] = {
                'mean': 'Read FIB (Factory Information Byte), and check the previous process is completed pass.',
                'indicate': 'The previous process test flag isn\'t pass.',
                'suggest': 'Confirm all of the previous process tested pass completely.'
            }
            result['zh'] = {
                'mean': '读取FIB（工厂信息字节），并检查之前的流程是否已通过。',
                'indicate': '之前流程的测试标志未通过。',
                'suggest': '确认所有之前的流程都已完全通过测试。'
            }
        elif re.search(r"^WRITE_FIB_QC_MODELFILE", fail_item) != None:
            result['en'] = {
                'mean': 'Update FIB (Factory Information Byte) in the end of the test.',
                'indicate': 'Update FIB failed.',
                'suggest': 'Confirm all of the items tested pass completely.'
            }
            result['zh'] = {
                'mean': '在测试结束时更新FIB（工厂信息字节）。',
                'indicate': '更新FIB失败。',
                'suggest': '确认所有测试项目都已完全通过。'
            }

    # 21. 读取Android系统错误日志
    elif re.search(r"READ_LOG_PANIC_ANDROID\S+", test_name) != None:
        result['en'] = {
            'mean': 'Checks for panic codes stored in the phone. Panics are usually caused by software bugs or process issues.',
            'indicate': 'Detect panic stored in the phone.',
            'suggest': 'Need software team to take log and fix it.'
        }
        result['zh'] = {
            'mean': '检查手机中存储的系统错误代码。错误通常由软件漏洞或流程问题引起。',
            'indicate': '检测到手机中存储的系统错误。',
            'suggest': '需要软件团队获取日志并修复。'
        }

    elif re.search(r"^SWITCH_TO_(BATTERY|ACCESSORY)\S*", fail_item) != None:
        match = re.search(r"SWITCH_TO_(BATTERY|ACCESSORY)\S*", fail_item)
        psu_type = match.groups()[0].lower()
        result['en'] = {
            'mean': f'Internal power supply change, switch to {psu_type}.',
            'indicate': f'Internal power supply switch to {psu_type} fail, generally exception occured during the TCMD communication.',
            'suggest': f'{advice["en"]}'
        }
        result['zh'] = {
            'mean': f'内部供电切换，切换至{"电池" if psu_type == "battery" else "USB"}供电模式。',
            'indicate': f'内部供电切换至{"电池" if psu_type == "battery" else "USB"}供电模式失败，通常是TCMD通信过程中发生异常。',
            'suggest': f'{advice["zh"]}'
        }

    elif re.search(r"^MEAS_BATT_ON_CURRENT_BOARD", fail_item) != None:
        if re.search(r"MEAS_BATTERY_ON_CURRENT_BOARD_STATUS\S*", test_descrip) != None:
            result['en'] = {
                'mean': 'Indicate the status of the process of VBAT current measurement.',
                'indicate': 'The VBAT current is unstable or visa exception occured during the measurement.',
                'suggest': f'Confirm the power meter in online or {advice["en"]}'
            }
            result['zh'] = {
                'mean': '指示VBAT电流测量过程的状态。',
                'indicate': 'VBAT电流不稳定或测量过程中发生visa异常。',
                'suggest': f'确认功率计在线，或{advice["zh"]}'
            }

        elif re.search(r"^BATTERY_ON_CURRENT_BOARD_\d+", test_descrip) != None:
            result['en'] = {
                'mean': 'Measure the VBAT current when the internal power supply switch to battery.',
                'indicate': 'Measure the VBAT current value is out of the SPEC.',
                'suggest': f'Confirm the test current is correct, or {advice["en"]}'
            }
            result['zh'] = {
                'mean': '当内部电源切换至电池模式时，测量VBAT电流。',
                'indicate': '测量的VBAT电流值超出规格范围。',
                'suggest': f'确认测试电流正确，或{advice["zh"]}'
            }

    elif re.search(r"^NFC_FIRMWARE_VERIFY_DOWNLOAD_COMPLETE", fail_item) != None:
        result['en'] = {
            'mean': 'Upgrade the NFC firmware internal, the firmware download when the PCBA software flash.',
            'indicate': 'No NFC component on the PCBA or the NFC component can not work.',
            'suggest': f'Confirm NFC component is on PCBA, or {advice["en"]}'
        }
        result['zh'] = {
            'mean': '内部升级NFC固件，固件在PCBA软件烧录时下载。',
            'indicate': 'PCBA上没有NFC组件或NFC组件无法工作。',
            'suggest': f'确认PCBA上有NFC组件，或{advice["zh"]}'
        }

    elif re.search(r"SUSPEND_\d+", fail_item) != None:
        result['en'] = {
            'mean': 'Enable DUT entering suspend mode, few APP will work in suspend mode.',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}'
        }
        result['zh'] = {
            'mean': '使DUT进入休眠模式，极少数应用程序会在休眠模式下运行。',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}'
        }

    elif re.search(r"^HW_VERSION_CHECK", fail_item) != None:
        result['en'] = {
            'mean': 'Read the hardware version from DUT and compare it from modelfile maintained.',
            'indicate': 'Hardware version is not match it from modelfile.',
            'suggest': 'Need engineer confirm the hardware version is correct.'
        }
        result['zh'] = {
            'mean': '从DUT读取硬件版本，并与维护在modelfile.txt内信息比较。',
            'indicate': '硬件版本与modelfile.txt内版本不匹配。',
            'suggest': '需要工程师确认硬件版本正确。'
        }

    elif re.search("UTAG_VERIFY_RADIO_MODELFILE", fail_item) != None:
        result['en'] = {
            'mean': 'Read the radio UTAG from DUT and compare it from modelfile maintained.',
            'indicate': 'Radio UTAG is not match it from modelfile.',
            'suggest': 'Need engineer confirm the radio UTAG is correct.'
        }
        result['zh'] = {
            'mean': '从DUT读取射频UTAG，并与维护在modelfile.txt内信息进行比较。',
            'indicate': '射频UTAG与modelfile.txt内信息不匹配。',
            'suggest': '需要工程师确认射频UTAG正确。'
        }

    elif re.search(r"^UTAG_VERIFY_RADIO_\S+", fail_item) != None:
        result['en'] = {
            'mean': 'Read the radio UTAG from DUT and compare it from recipe. Actually this test is pre-test for JUMP depend different SKU.',
            'indicate': 'Probably TCMD exception occured during the test.',
            'suggest': f'{advice["en"]}'
        }
        result['zh'] = {
            'mean': '从DUT读取射频UTAG并与配方进行比较。实际上，该测试是针对不同SKU的JUMP的预测试。',
            'indicate': '测试过程中可能发生了TCMD异常。',
            'suggest': f'{advice["zh"]}'
        }

    elif re.search(r"^HW_VERSION_PRODUCT_NAME", fail_item) != None:
        if test_descrip == "production_name_length":
            result['en'] = {
                'mean': 'Read the production name from DUT and compare it from recipe.',
                'indicate': 'The production name is not match it from recipe.',
                'suggest': 'Need engineer confirm the production name is correct.'
            }
            result['zh'] = {
                'mean': '从DUT读取产品名称，并与脚本配置产品名进行比较。',
                'indicate': '产品名称与脚本配置产品名不匹配。',
                'suggest': '需要工程师确认产品名称正确。'
            }

        elif test_descrip == "production_name_status":
            result['en'] = {
                'mean': 'Indicate the status of \'production_name_length\'.',
                'indicate': 'Probably TCMD executed fail, communication interface disconnect during the test.',
                'suggest': f'{advice["en"]}'
            }
            result['zh'] = {
                'mean': '指示"production_name_length"的状态。',
                'indicate': '可能TCMD执行失败，测试过程中通信接口断开。',
                'suggest': f'{advice["zh"]}'
            }

    elif re.search(r"^SOFTWARE_VERSION_TYPE_FFFF", fail_item) != None:
        result['en'] = {
            'mean': 'Read software version from DUT and compare it from modelfile.',
            'indicate': 'The software version is not match it from modelfile.',
            'suggest': 'Need engineer confirm the software version is correct.'
        }
        result['zh'] = {
            'mean': '从DUT读取软件版本，并与modelfile.txt内信息进行比较。',
            'indicate': '软件版本与modelfile.txt内的版本不匹配。',
            'suggest': '需要工程师确认软件版本正确。'
        }

    elif re.search(r'^SOFTWARE_VERSION_BP_BOOTLOADER', fail_item) != None:
        result['en'] = {
            'mean': 'Read bootloader version from DUT and compare it from modelfile.',
            'indicate': 'The bootloader version is not match it from modelfile.',
            'suggest': 'Need engineer confirm the bootloader version is correct.'
        }
        result['zh'] = {
            'mean': '从DUT读取引导程序版本，并与modelfile.txt内信息进行比较。',
            'indicate': '引导程序版本与modelfile.txt内的版本不匹配。',
            'suggest': '需要工程师确认引导程序版本正确。'
        }

    elif re.search(r"^VERIFY_UFS_VENDOR_AND_FIRMWARE_VERSION", fail_item) != None:
        result['en'] = {
            'mean': 'Read UFS vendor and firmware version from DUT and check it\'s include modelfile.',
            'indicate': 'The UFS information is not match it from modelfile.',
            'suggest': 'Need engineer confirm the UFS information is correct.'
        }
        result['zh'] = {
            'mean': '从DUT读取UFS供应商和固件版本，并检查是否包含在modelfile.txt内。',
            'indicate': 'UFS信息与modelfile.txt内的不匹配。',
            'suggest': '需要工程师确认UFS信息正确。'
        }

    elif re.search(r"READ_PROCESSOR_ID", fail_item) != None:
        result['en'] = {
            'mean': 'Read processor ID and compare the returned value with expected value.',
            'indicate': 'The processor ID is different with expected value.',
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '读取处理器ID，并将返回值与预期值进行比较。',
            'indicate': '处理器ID与预期值不同。',
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"THERMISTOR_TEMP_(\S+)_THERM\S*", fail_item) != None:
        match = re.search(r"THERMISTOR_TEMP_(\S+)_THERM\S*", fail_item)
        thermistor = match.groups()[0]
        if test_descrip.endswith('_READINGS'):
            indicate_en = f'The temperature of {thermistor} is out of the limits.'
            indicate_zh = f'{thermistor}的温度超出限制范围。'
            
            result['en'] = {
                'mean': f'Read temperature of the {thermistor} thermistor on PCBA and check it\'s in the range of the specification.',
                'indicate': indicate_en,
                'suggest': f'{advice["en"]}.'
            }
            result['zh'] = {
                'mean': f'读取PCBA上{thermistor}热敏电阻的温度，并检查是否在规格范围内。',
                'indicate': indicate_zh,
                'suggest': f'{advice["zh"]}.'
            }
        elif test_descrip.find('_STATUS') != -1:
            indicate_en = f'The temperature of {thermistor} is unstable.'
            indicate_zh = f'{thermistor}的温度读值不稳定。'
            
            result['en'] = {
                'mean': f'Read temperature of the {thermistor} thermistor on PCBA and confirm the readings are stable.',
                'indicate': indicate_en,
                'suggest': f'{advice["en"]}.'
            }
            result['zh'] = {
                'mean': f'读取PCBA上{thermistor}热敏电阻的温度，判断温度读值是否稳定。',
                'indicate': indicate_zh,
                'suggest': f'{advice["zh"]}.'
            } 

    elif re.search(r"^UFS_CARD_PRESENT_AND_SIZE", fail_item) != None:
        if test_descrip == 'UFS_PRESENT':
            indicate_en = f'The UFS present status is invalid.'
            indicate_zh = f'UFS存在状态无效。'
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'
        elif test_descrip == 'UFS_SIZE':
            indicate_en = f'the UFS size is match it from modelfile.'
            indicate_zh = f'UFS大小与modelfile.txt内的不匹配。'
            suggest_en = f'Need engineer confirm the UFS information is correct.'
            suggest_zh = f'需要工程师确认UFS信息正确。'
        elif test_descrip == 'UFS_PRESENT_AND_SIZE_STATUS':
            indicate_en = moto_tcmd_exception['en']
            indicate_zh = moto_tcmd_exception['zh']
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'

        result['en'] = {
            'mean': 'Read UFS information and check the volumn size is match it from modelfile.',
            'indicate': indicate_en,
            'suggest': suggest_en
        }
        result['zh'] = {
            'mean': '读取UFS信息，并检查容量大小与modelfile.txt内的匹配。',
            'indicate': indicate_zh,
            'suggest': suggest_zh
        }

    elif re.search(r"^RAM_TEST_LPDDR_INFO_SIZE", fail_item) != None:
        if test_descrip == 'RAM_LPDDR_SIZE':
            indicate_en = f'the RAM size is match it from modelfile.'
            indicate_zh = f'RAM大小与modelfile.txt内的不匹配。'
            suggest_en = f'Need engineer confirm the RAM information is correct.'
            suggest_zh = f'需要工程师确认RAM信息正确。'
        elif test_descrip == 'RAM_TEST_STATUS':
            indicate_en = moto_tcmd_exception['en']
            indicate_zh = moto_tcmd_exception['zh']
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'

        result['en'] = {
            'mean': 'Read RAM information and check the volumn size is match it from modelfile.',
            'indicate': indicate_en,
            'suggest': suggest_en
        }
        result['zh'] = {
            'mean': '读取RAM信息，并检查容量大小与modelfile.txt内的匹配。',
            'indicate': indicate_zh,
            'suggest': suggest_zh
        }

    elif re.search(r'^ACCELEROMETER_SELF_TEST', fail_item) != None:
        result['en'] = {
            'mean': '''Send TCMD to run Accelerometer sensor self test 
                    and verify that the physical hardware lines being used on the accelerometer are connected and functioning properly.
                    ''',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '''发送TCMD运行加速度传感器自检，
                    验证加速度计上使用的物理硬件线路是否连接并正常工作。
                    ''',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'GYROSCOPE_SELF_TEST', fail_item) != None:
        result['en'] = {
            'mean': '''Send TCMD to run Gyroscope sensor self test 
                    and verify connectivity and functionality of the Gyroscope part.
                    ''',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '''发送TCMD运行陀螺仪传感器自检，
                    验证陀螺仪部件的连接性和功能。
                    ''',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}.'
        }
    elif re.search(r'ESE_SELF_TEST', fail_item) != None:
        result['en'] = {
            'mean': '''Send TCMD to run eSE (Embedded Secure Element) self test 
                    and verify connectivity and functionality of the eSE part.
                    ''',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '''发送TCMD运行eSE (Embedded Secure Element)自检，
                    验证eSE连接性和功能。
                    ''',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'MAGNETOMETER_TEST_MAG_SENSE_READINGS', fail_item) != None:
        if re.search(r'MAGNETOMETER_(X|Y|Z)_AXIS_ABSOLUTE_MAG_FIELD', test_descrip) != None:
            match = re.search(r'MAGNETOMETER_(X|Y|Z)_AXIS_ABSOLUTE_MAG_FIELD', test_descrip)
            indicate_en = f"The absolute magnetic field data of the {match.groups()[0]} axes in non-self test mode is out of specification."
            indicate_zh = f'非自检模式下{match.groups()[0]}轴的绝对磁场数据超出规格。'
        elif re.search(r'Absolute_Self_Test_Magnetic_Field_(X|Y|Z)_Axis', test_descrip) != None:
            match = re.search(r'Absolute_Self_Test_Magnetic_Field_(X|Y|Z)_Axis', test_descrip)
            indicate_en = f"The absolute magnetic field data of the {match.groups()[0]} axes in self test mode states is out of specification."
            indicate_zh = f'自检模式下{match.groups()[0]}轴的绝对磁场数据超出规格。'
        elif fail_item == 'MAGNETOMETER_PRESENSE_STATUS':
            indicate_en = moto_tcmd_exception['en']
            indicate_zh = moto_tcmd_exception['zh']

        result['en'] = {
            'mean': '''Verifies that all the lines used on the Magnetometer part are functional by reading out 
                           the absolute magnetic field data of the X, Y, and Z axes 
                           in both non-self test mode and self test mode states.''',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '''通过读取X、Y和Z轴的绝对磁场数据（在非自检模式和自检模式下），
                           验证磁力计部件上使用的所有线路是否正常工作。''',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'MAGNETOMETER_BOARD_RESULTS_SUM', fail_item) != None:
        result['en'] = {
            'mean': '''Verifies the sum of the absolute magnetic field data of the X, Y, and Z axes in specification.''',
            'indicate': 'The sum of absolute magnetic field data of X,Y,and Z axes is out of specification.',
            'suggest': 'Confirm magnetic field data of the X,Y,and Z isn\'t all no-zero .'
        }
        result['zh'] = {
            'mean': '''验证X、Y和Z轴的绝对磁场数据之和是否在规格范围内。''',
            'indicate': 'X、Y和Z轴的绝对磁场数据之和超出规格。',
            'suggest': '确认X、Y和Z轴的磁场数据并非全为零。'
        }

    elif re.search(r'PROX_SENSOR_COVERED_BOARD', fail_item) != None:
        if test_descrip == 'PROX_SENSOR_COVERED_BOARD':
            indicate_en = 'The readings of Proximity sensor is out of specification.'
            indicate_zh = '接近传感器的读数超出规格。'
        elif test_descrip == 'PROX_SENSOR_COVERED_BOARD_STATUS':
            indicate_en = 'The readings of Proximity sensor is unstable.'
            indicate_zh = '接近传感器的读数不稳定。'

        result['en'] = {
            'mean': 'Verify the Proximity sensor is functioning by reading out the covered response value.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '通过读取覆盖响应值来验证接近传感器是否正常工作。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }
    elif re.search(r'PROX_INTERRUPT_TEST', fail_item) != None:        
        indicate_en = 'The Proximity interrupt test.'
        indicate_zh = '接近传感器中断测试。'       

        result['en'] = {
            'mean': 'Verify the Proximity sensor interrupt test status.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '接近传感器中断测试检测。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }
    elif re.search(r'CAP_SENSOR_VENDOR_INTEGER', fail_item) != None:
        if test_descrip == 'CAP_SENSOR_VENDOR_ID_INTEGER':
            indicate_en = 'The vendor ID value is out of specification.'
            indicate_zh = '供应商ID值超出规格。'
            suggest_en = 'Confirm the specification is open limit for vendor ID list.'
            suggest_zh = '确认规格对供应商ID列表是开放限制。'
        elif test_descrip == 'CAP_SENSOR_VENDOR_ID_READ_STATUS':
            indicate_en = moto_tcmd_exception['en']
            indicate_zh = moto_tcmd_exception['zh']
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'

        result['en'] = {
            'mean': 'Send TCMD to read Antenna Capacitive Sensor vendor ID.',
            'indicate': indicate_en,
            'suggest': suggest_en
        }
        result['zh'] = {
            'mean': '发送TCMD读取天线电容传感器的供应商ID。',
            'indicate': indicate_zh,
            'suggest': suggest_zh
        }
    elif re.search(r'^ANT_CAP_SENSOR_BRD_READ_STORE_', fail_item) != None:
        if test_descrip == 'CAP_SENSOR_DETECT_STATUS':
            mean_en = 'Verify the Antenna Capacitive Sensor is present and ready.'
            mean_zh = '验证天线电容传感器是否存在且就绪。'
            indicate_en = 'The Antenna Capacitive Sensor is not present.'
            indicate_zh = '天线电容传感器不存在。'
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'
        elif re.search(r'CAP(\d)_COMP_BRD_VALUE_CS(\d+)', test_descrip) != None:
            match = re.search(r'CAP(\d)_COMP_BRD_VALUE_CS(\d+)', test_descrip)
            mean_en = 'Read Board level Capacitor Compensation Value(CS0/1/2/3/4/5/6/7), and ensure that it is within the limits specified.'
            mean_zh = '读取板级电容补偿值（CS0/1/2/3/4/5/6/7），并确保在规定的限制范围内。'
            indicate_en = f"The Board level Capacitor Compensation Value(CS{match.groups()[1]}) is out of the limits."
            indicate_zh = f'板级电容补偿值（CS{match.groups()[1]}）超出限制范围。'
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'
        elif re.search(r'CAP(\d)_COMP_DIFF_IDAC_BRD_VALUE_CS(\d+)', test_descrip) != None:
            match = re.search(r'CAP(\d)_COMP_DIFF_IDAC_BRD_VALUE_CS(\d+)', test_descrip)
            mean_en = 'Read the Capacitor Diff value CS0/1/2/3/4/5/6/7 and verify the Diff current value are within the limits specified.'
            mean_zh = '读取电容差值CS0/1/2/3/4/5/6/7，并验证差值电流值在规定的限制范围内。'
            indicate_en = f"the Capacitor Diff value(CS{match.groups()[1]}) is out of the limits."
            indicate_zh = f'电容差值（CS{match.groups()[1]}）超出限制范围。'
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'
        elif test_descrip == 'CAP_SENSOR_INTERRUPT_DETECT_STATUS':
            mean_en = 'Reads Capacitor Interrupts status and Verify the Interrupt test passed.'
            mean_zh = '读取电容中断状态并验证中断测试通过。'
            indicate_en = 'The Capacitor Interrupt test failed.'
            indicate_zh = '电容中断测试失败。'
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'
        elif re.search(r'^ANT_CAP_SENSOR_BRD_RESULT_STATUS\S*', test_descrip) != None:
            mean_en = f'Final test status of {test_name}.'
            mean_zh = f'{test_name}的最终测试状态。'
            indicate_en = moto_tcmd_exception['en']
            indicate_zh = moto_tcmd_exception['zh']
            suggest_en = f'{advice["en"]}.'
            suggest_zh = f'{advice["zh"]}.'

        result['en'] = {
            'mean': mean_en,
            'indicate': indicate_en,
            'suggest': suggest_en
        }
        result['zh'] = {
            'mean': mean_zh,
            'indicate': indicate_zh,
            'suggest': suggest_zh
        }

    elif re.search(r'^SUSPEND_CURRENT_BOARD', fail_item) != None:
        if test_descrip == 'SUSPEND CURRENT WITHOUT DISPLAY':
            indicate_en = 'The suspend current is out of the limits specified.'
            indicate_zh = '休眠电流超出规定的限制范围。'
        elif re.search(r'^SUSPEND_CURRENT_STATUS', test_descrip) != None:
            indicate_en = 'The suspend current is unstable.'
            indicate_zh = '休眠电流不稳定。'

        result['en'] = {
            'mean': 'Measure the VBAT current when the DUT in suspend mode and verify the current value is within the limits specified.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '测量DUT在休眠模式下的VBAT电流，并验证电流值在规定的限制范围内。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'RDWR_IO_(ENABLE|DISABLE)_SW_FACTORY_KILL', fail_item) != None:
        match = re.search(r'RDWR_IO_(ENABLE|DISABLE)_SW_FACTORY_KILL', fail_item)
        result['en'] = {
            'mean': f'{match.groups()[0]} the software factory kill.',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': f'{"启用" if match.groups()[0].lower() == "enable" else "禁用"}软件工厂模式终止功能。',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'OTG_VBUS(\S*)_VOLTAGE', fail_item) != None:
        if re.search(r'VBUS_OTG_(ON|OFF)_VOLTAGE', test_descrip) != None:
            match = re.search(r'VBUS_OTG_(ON|OFF)_VOLTAGE', test_descrip)
            indicate_en = f'The OTG {match.groups()[0]} voltage is out of the limits specified.'
            indicate_zh = f'测量的OTG {match.groups()[0]}电压超出规定的限制范围。'
        elif re.search(r'OTG_VBUS_(ON|OFF)_VOLTAGE_STATUS', test_descrip) != None:
            match = re.search(r'OTG_VBUS_(ON|OFF)_VOLTAGE_STATUS', test_descrip)
            indicate_en = f'The OTG {match.groups()[0]} voltage is unstable.'
            indicate_zh = f'测量的OTG {match.groups()[0]}电压不稳定。'
        elif re.search(r'VBUS_OTG_STATUS', test_descrip) != None:
            indicate_en = 'Exception occured during the OTG voltage measurement.'
            indicate_zh = 'OTG电压测试出现异常。'

        result['en'] = {
            'mean': 'Measure the VBUS OTG mode voltage and verify the voltage is within the limits specified.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '测量VBUS的OTG模式电压，并验证电压在规定的限制范围内。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'^TURBO_CHARGER_TEST_ADDRESS_', fail_item) != None:
        if test_descrip == 'TURBO_CHARGE_NOT_CONNECTED':
            indicate_en = 'Charger is detected as connected.'
            indicate_zh = '充电器被检测为已连接。'
        elif test_descrip == 'TURBO_CHARGE_CONNECTED':
            indicate_en = 'Charger is detected as not connected.'
            indicate_zh = '充电器被检测为未连接。'
        elif test_descrip == 'TURBO_CHARGE_OVERALL_STATUS':
            indicate_en = 'The test status of USB lines at the PMIC is failed.'
            indicate_zh = 'PMIC处USB线路的测试状态失败。'

        result['en'] = {
            'mean': 'Verify connectivity and functionality of the USB lines at the PMIC.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '验证PMIC处USB线路的连接性和功能。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'GET_USB_C_ORIENTATION\S*', fail_item) != None:
        if re.search(r'USB_C_ORIENTATION_\d', test_descrip) != None:
            indicate_en = 'The USB-C Orientation value is not within the limits specified.'
            indicate_zh = 'USB-C的方向值不在规定的限制范围内。'
        elif re.search(r'GET_USB_C_ORIENTATION_\d_STATUS', test_descrip) != None:
            indicate_en = moto_tcmd_exception['en']
            indicate_zh = moto_tcmd_exception['zh']

        result['en'] = {
            'mean': 'Send TCMD to Get USB-C Orientation value.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '发送TCMD获取USB-C的方向值。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'BATTERY_CHARGER_PMIC8996_\S*', fail_item) != None:
        if test_descrip == 'VBUS_VOLTAGE':
            indicate_en = 'Send TCMD to read the VBUS Voltage, but the voltage is out of limits specified.'
            indicate_zh = '发送TCMD读取VBUS电压，但电压超出规定的限制范围。'
        elif test_descrip == 'B_PLUS_VOLTAGE':
            indicate_en = 'Send TCMD to read the B+ Voltage, but the voltage is out of limits specified.'
            indicate_zh = '发送TCMD读取B+电压，但电压超出规定的限制范围。'
        elif test_descrip == 'VBAT_VOLTAGE':
            indicate_en = 'Send TCMD to read the VBAT Voltage, but the voltage is out of limits specified.'
            indicate_zh = '发送TCMD读取VBAT电压，但电压超出规定的限制范围。'
        elif test_descrip == 'MAIN_PATH_CHARGER_CURRENT':
            indicate_en = 'Measure the charger current from the battery power supply, but the current is out of limits specified.'
            indicate_zh = '测量来自电池电源的充电电流，但电流超出规定的限制范围。'
        elif test_descrip == 'BATT_CHARGER_THERMISTOR_VERIFY_STAT':
            indicate_en = f'Final status of {test_name} is failed.'
            indicate_zh = f'{test_name}的最终状态失败。'

        result['en'] = {
            'mean': 'Charge test to verify connectivity and functionality of the battery, charger circuitry.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '充电测试，以验证电池、充电器电路的连接性和功能。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r'^BATT_READ_BATT_VOLTAGE_CAPSWITCH', fail_item) != None:
        if test_descrip == 'BATTERY_VOLTAGE_CAPSWITCH':
            indicate_en = 'The VBAT Voltage is out of the limits specified.'
            indicate_zh = 'VBAT电压超出规定的限制范围。'
        elif test_descrip == 'BATTERY_VOLTAGE_CAPSWITCH_STATUS':
            indicate_en = moto_tcmd_exception['en']
            indicate_zh = moto_tcmd_exception['zh']

        result['en'] = {
            'mean': 'Send TCMD to read the VBAT Voltage through charge IC, and verify the Voltage value is within the limits specified.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '通过充电IC发送TCMD读取VBAT电压，并验证电压值在规定的限制范围内。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"BATT_(ENABLE|DISABLE)_FET_PATH", fail_item) != None:
        match = re.search(r"BATT_(ENABLE|DISABLE)_FET_PATH", fail_item)
        result['en'] = {
            'mean': f'Send TCMD to {match.groups()[0]} Path FET to Battery.',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': f'发送TCMD以{"开启" if match.groups()[0].lower() == "enable" else "关闭"}至电池的FET。',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"BATT_(ENABLE|DISABLE)_CAPSWITCH_CHARGER_PATH", test_descrip) != None:
        match = re.search(r"BATT_(ENABLE|DISABLE)_CAPSWITCH_CHARGER_PATH", test_descrip)
        result['en'] = {
            'mean': f'Send TCMD to set CAP-SWITCH charger {match.groups()[0].lower()}.',
            'indicate': moto_tcmd_exception['en'],
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': f'发送TCMD设置CAP-SWITCH充电器状态{"开启" if match.groups()[0] == "ENABLE" else "关闭"}。',
            'indicate': moto_tcmd_exception['zh'],
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"^ACCESSORY_CURRENT_CAPSWITCH", test_descrip, re.IGNORECASE) != None:                
        if re.search(r"^ACCESSORY_CURRENT_CAPSWITCH_\S*_STATUS$", test_descrip, re.IGNORECASE) != None:
            indicate_en = 'The turbo charge VBUS current is unstable.'
            indicate_zh = 'turbo 充电 VBUS 电流不稳定。'
        elif re.search(r"ACCESSORY_CURRENT_CAPSWITCH", test_descrip, re.IGNORECASE) != None:
            indicate_en = 'The turbo charge VBUS current is out of limits specified.'
            indicate_zh = 'turbo 充电 VBUS 电流超出规定的限制范围。'
        result['en'] = {
            'mean': 'Measure the turbo charge VBUS current from the battery power supply, and verify the current is within the limits specified.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '测量来自电池电源的 turbo 充电 VBUS 电流，并验证电流在规定的限制范围内。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"BATTERY_ON_CURRENT_CAPSWITCH_CHARGER_\d{1}$", test_descrip) != None or \
            re.search(r"MEAS_BATTERY_ON_CURRENT_CAPSWT_CHARGER_STATUS_\d{1}$", test_descrip) != None:

        if re.search(r"BATTERY_ON_CURRENT_CAPSWITCH_CHARGER_\d{1}$", test_descrip) != None:
            indicate_en = 'The turbo charge VBAT current is out of limits specified.'
            indicate_zh = 'turbo 充电 VBAT 电流超出规定的限制范围。'
        elif re.search(r"MEAS_BATTERY_ON_CURRENT_CAPSWT_CHARGER_STATUS_\d{1}$", test_descrip) != None:
            indicate_en = 'The turbo charge VBAT current is unstable.'
            indicate_zh = 'turbo 充电 VBAT 电流不稳定。'

        result['en'] = {
            'mean': 'Measure the turbo charge VBAT current from the battery power supply, and verify the current is within the limits specified.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '测量来自电池电源的 turbo 充电 VBAT 电流，并验证电流在规定的限制范围内。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"^AUD(?:IO)*_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_(AMPL|FREQ|STATUS)", test_descrip) != None:
        match = re.search(r"^AUD(?:IO)*_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_(AMPL|FREQ|STATUS)", test_descrip)

        if re.search(r"^AUD_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_AMPL", test_descrip) != None:
            indicate_en = 'The peak amplitude is out of the limits specified.'
            indicate_zh = '峰值幅度超出规定的限制范围。'
        elif re.search(r"^AUD_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_FREQ", test_descrip) != None:
            indicate_en = 'The frequency of peak amplitude is out of the limits specified.'
            indicate_zh = '峰值幅度的频率超出规定的限制范围。'
        elif re.search(r"^AUDIO_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_STATUS", test_descrip) != None:
            indicate_en = f'Status for MIC test on board, {moto_tcmd_exception["en"]}'
            indicate_zh = f'板级麦克风测试状态，{moto_tcmd_exception["zh"]}'

        result['en'] = {
            'mean': 'Calculate the peak amplitude between the frequency-specified window, Verify the Microphones is available on board level.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '计算特定频率窗口之间的峰值幅度，验证麦克风在板级是否可用。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"MTK_RF_CONNECTOR_DETECTE", test_descrip) != None:
        result['en'] = {
            'mean': 'Verify the RF Connector detection circuitry in the radio is connected and functioning properly.',
            'indicate': 'The RF connector on board don\'t attach to the prob in fixture.',
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '验证主板射频连接器检测电路是否连接并正常工作。',
            'indicate': '主板上的射频连接器未与夹具中的探针连接。',
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"TEST_SET_10MHz_REFERENCE_STATUS", test_descrip) != None or \
            re.search(r"10MHz_REFERENCE_VERIFY_OVERALL_STATUS", test_descrip) != None:
        result['en'] = {
            'mean': 'Verify the external 10M reference clock is available.',
            'indicate': 'The external 10M signal is disconnect.',
            'suggest': 'Check 10M signal cable is well connected.'
        }
        result['zh'] = {
            'mean': '验证外部10M参考时钟是否可用。',
            'indicate': '外部10M信号断开。',
            'suggest': '检查10M信号电缆连接良好。'
        }

    elif re.search(r"MTK_META_DUT_CONNECT", test_descrip) != None:
        result['en'] = {
            'mean': 'MTK META mode connect is pre-condition for test. Must execute before calibration and nonsignalling.',
            'indicate': 'MTK META mode connect fail for test.',
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': 'MTK META模式连接是测试的前提条件。必须在校准和无信令测试前执行。',
            'indicate': 'MTK META模式连接测试失败。',
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"MTK_META_AP_TO_MODEM_MODE", test_descrip) != None:
        result['en'] = {
            'mean': 'MTK META AP mode switch to modem mode, RF calibration and nonsignalling test must run in modem mode.',
            'indicate': 'MTK META AP mode switch to modem mode fail for test.',
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': 'MTK META AP模式切换至modem模式，射频校准和无信令测试必须在调制解调器模式下运行。',
            'indicate': 'MTK META AP模式切换至modem模式测试失败。',
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"MTK_META_MODEM_TO_AP_MODE", test_descrip) != None:
        result['en'] = {
            'mean': 'MTK META modem mode switch to AP mode, WIFI/GPS/FM test must run in AP mode.',
            'indicate': 'MTK META modem mode switch to AP mode fail.',
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': 'MTK META modem模式切换至AP模式，WIFI/GPS/FM测试必须在AP模式下运行。',
            'indicate': 'MTK META modem模式切换至AP模式失败。',
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"MTK_META_DUT_DISCONNECT", test_descrip) != None:
        result['en'] = {
            'mean': 'MTK META mode disconnect.',
            'indicate': 'MTK META mode disconnect fail.',
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': 'MTK META模式断开连接。',
            'indicate': 'MTK META模式断开连接失败。',
            'suggest': f'{advice["zh"]}.'
        }

    elif re.search(r"P2K_SAVE_TO_HOB", test_descrip) != None:
        result['en'] = {
            'mean': 'Send TCMD to copy certain NV items into the HOB (Hand Over Block) area for non-volatile backup.',
            'indicate': 'Calibration isn\'t passed completed case Certain NV item is blank.',
            'suggest': 'Confirm the calibration process is completed pass.'
        }
        result['zh'] = {
            'mean': '发送TCMD将某些NV项目复制到HOB（Hand Over Block）区域以进行非易失性备份。',
            'indicate': '校准未完全通过，某些NV项目为空。',
            'suggest': '确认校准过程已完全通过。'
        }

    elif re.search(r"P2K_VERIFY_HOB", test_descrip) != None:
        result['en'] = {
            'mean': 'Vefify the HOB (Hand Over Block) after SAVE TO HOB.',
            'indicate': 'Calibration isn\'t passed completed case Certain NV item is blank.',
            'suggest': 'Confirm the calibration process is completed pass.'
        }
        result['zh'] = {
            'mean': '在保存到HOB后验证HOB（Hand Over Block）。',
            'indicate': '校准未完全通过，某些NV项目为空。',
            'suggest': '确认校准过程已完全通过。'
        }

    elif re.search(r"BATTERY_OFF_CURRENT_BOARD(_\d+)*", test_descrip) != None:

        if re.search(r"^BATTERY_OFF_CURRENT_BOARD(_\d+)*", test_descrip) != None:
            indicate_en = 'Measure leakage current is out of limits specified.'
            indicate_zh = '测量的泄漏电流超出规定的限制范围。'
        elif re.search(r"BATTERY_OFF_CURRENT_BOARD\S+Status", test_descrip) != None:
            indicate_en = 'Measure leakage current is unstable.'
            indicate_zh = '测量的泄漏电流不稳定。'

        result['en'] = {
            'mean': 'Measure PABA unit leakage current after power off.',
            'indicate': indicate_en,
            'suggest': f'{advice["en"]}.'
        }
        result['zh'] = {
            'mean': '断电后测量PABA单元的泄漏电流。',
            'indicate': indicate_zh,
            'suggest': f'{advice["zh"]}.'
        }

    # 默认返回（未匹配到任何模式）
    else:
        result['en'] = {
            'mean': fail_item,
            'indicate': fail_item,
            'suggest': advice['en']
        }
        result['zh'] = {
            'mean': fail_item,
            'indicate': fail_item,
            'suggest': advice['zh']
        }

    if len(error_detail) != 0:
        result['en']['indicate'] = error_detail + ',' + result['en']['indicate']
        result['zh']['indicate'] = error_detail + ',' + result['zh']['indicate']
    elif len(error_msg) != 0:
        result['en']['indicate'] = error_msg + ',' + result['en']['indicate']
        result['zh']['indicate'] = error_msg + ',' + result['zh']['indicate']

    # 根据语言参数返回对应结果
    lang = language.lower()
    if lang == 'en':
        return [result['en']['mean'], result['en']['indicate'], result['en']['suggest']]
    else:
        return [result['zh']['mean'], result['zh']['indicate'], result['zh']['suggest']]

def plat_mtk_library_callback_analysis(log_title_info,language='zh'):
    fail_item = log_title_info.get('failMsg','Unknow')

    match = re.search(r'^TEST_TASK_(\S+)_(\d+)$', fail_item)
    if match is not None:
        log_title_info.update({'task':match.groups()[0]})
        log_title_info.update({'task_id':match.groups()[1]})
        final_analysis = plat_MTK_task_failure_analysis(log_title_info,language)
    elif fail_item.endswith('_RFCal_DONE') or re.search(r"NSFT\S+_DONE$", fail_item)!=None:
        return plat_MTK_task_failure_analysis(log_title_info,language)
    elif re.search(r"(MMAFC|GSM|GMSK|EPSK|WCDMA|LTE|NR)\S+_Measure", fail_item, re.IGNORECASE) != None:
        return plat_MTK_measure_failure_analysis(log_title_info,language)
    elif re.search(r"\S+_(Dut_FHC_StartCmd|SendDutFhcCmd|INIT_DUT_TEST)\S*", fail_item, re.IGNORECASE) != None:
        return plat_MTK_META_failure_analysis(log_title_info,language)
    else:
        return plat_MTK_radio_failure_analysis(log_title_info,language)
    
    suggestion = 'Please retest,if still fail, maybe it\'s PCBA defect (SMT defect/IC defect) and need repair.'
    return [fail_item, fail_item, suggestion]

def plat_MTK_task_failure_analysis(log_title_info, language='zh'):
    # 初始化中英文结果字典
    result = {
        'en': {'mean': '', 'indicate': '', 'suggest': ''},
        'zh': {'mean': '', 'indicate': '', 'suggest': ''}
    }

    probable_cause = '''
            1. measurement failure\n
            2. META API failure\n
            '''
    regular_suggestion_en = "if still fail after retest, maybe it's PCBA defect (SMT defect/IC defect) and need repair."
    regular_suggestion_zh = "如果重新测试后仍然失败，可能是PCBA缺陷（SMT缺陷/IC缺陷），需要维修。"

    fail_item = log_title_info.get('failMsg', 'Unknow')
    fail_task = log_title_info.get('task', 'UNKNOW')
    task_id = log_title_info.get('task_id', -1)

    # pre self/post self cal
    if 'SELF_CALIBRATION' in fail_task or 'SELF_CALIBRATION' in fail_item:
        result['en'] = {
            'mean': 'MTK platform RF internal self calibration.',
            'indicate': 'Self calibration do\'t depend on test equipment, probably META API failure occured.',
            'suggest': f'Retest DUT first, {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'MTK平台射频内部自校准。',
            'indicate': '自校准不依赖测试设备，可能发生了META API故障。',
            'suggest': f'首先重新测试DUT，{regular_suggestion_zh}'
        }
    # DPD Cal
    elif 'DPD_CALIBRATION' in fail_task or 'DPD_RFCal' in fail_item:
        result['en'] = {
            'mean': 'DPD (Digital Pre-Distortion) transform input signal, improve the linearity and boost TX output power.',
            'indicate': 'DPD calibration base on TX PA calibration result and isn\'t related with test equipment, probably META API failure occured when calibrated fail.',
            'suggest': f'Retest DUT first, {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DPD（数字预失真）转换输入信号，提高线性度并提升发射输出功率。',
            'indicate': 'DPD校准基于TX PA校准结果，与测试设备无关，校准失败可能是META API故障导致。',
            'suggest': f'首先重新测试DUT，{regular_suggestion_zh}'
        }
    # ET Cal
    elif 'ET_CALIBRATION' in fail_task or 'ET_RFCal' in fail_item:
        result['en'] = {
            'mean': 'ET (Envelope Tracking) change power supply of the power amplifier (PA) in order to optimize the PA performance.',
            'indicate': 'ET calibration do\'t depend on test equipment, probably META API failure occured.',
            'suggest': f'Retest DUT first, {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'ET（包络跟踪）改变功率放大器(PA)的电源供应，以优化PA性能。',
            'indicate': 'ET校准不依赖测试设备，可能发生了META API故障。',
            'suggest': f'首先重新测试DUT，{regular_suggestion_zh}'
        }
    # temperature calibration
    elif 'TADC_CALIBRATION' in fail_task or 'TEMPERATURE_SENSOR_CALIBRATION' in fail_item:
        result['en'] = {
            'mean': 'Adjust the eight temperature (-10,5,20,35,55,70,85,90) ADC values.',
            'indicate': 'Adjust temperature ADC values is out of the specification.',
            'suggest': f'Retest DUT first, {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': '调整八个温度点（-10,5,20,35,55,70,85,90）的ADC值。',
            'indicate': '调整后的温度ADC值超出规格范围。',
            'suggest': f'首先重新测试DUT，{regular_suggestion_zh}'
        }
    # AFC calibration
    elif 'AFC_CALIBRATION' in fail_task or 'AFC_CALIBRATION' in fail_item:
        result['en'] = {
            'mean': 'Crystal calibration for reducing the frequency error.',
            'indicate': 'Exception occured during calibration, maybe the frequency error measurement fail or META API failure occured.',
            'suggest': f'Confirm the RF signal path is perfect, {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': '晶体校准，用于减少频率误差。',
            'indicate': '校准过程中发生异常，可能是频率误差测量失败或META API故障。',
            'suggest': f'确认射频信号路径完好，{regular_suggestion_zh}'
        }
    # CO-TMS Cal
    elif 'CO-TMS_CALIBRATION' in fail_task or 'TMS_CALIBRATION' in fail_item:
        result['en'] = {
            'mean': 'Calibrate the relationship between temperature and frequency error of a crystal.',
            'indicate': 'The temperature or frequency error is out of the range required.',
            'suggest': f'Wait the PCBA cool down and retest. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': '校准晶体的温度与频率误差之间的关系。',
            'indicate': '温度或频率误差超出要求范围。',
            'suggest': f'等待PCBA冷却后重新测试。{regular_suggestion_zh}'
        }
    # GSM Calibration
    elif 'GGE_CALIBRATION' in fail_task:
        result['en'] = {
            'mean': 'MTK GSM calibration include GSM/EDGE RX path loss calibration, TX power calibration.',
            'indicate': 'Exception occured during calibration, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API failure during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'MTK GSM校准包括GSM/EDGE接收路径损耗校准、发射功率校准。',
            'indicate': '校准过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API故障。{regular_suggestion_zh}'
        }
    elif fail_item == 'GSM_FHC_DTS_AGC_RFCal_DONE':
        result['en'] = {
            'mean': 'DUT RX AGC path loss calibration.',
            'indicate': 'Exception occured during calibration, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DUT接收AGC路径损耗校准。',
            'indicate': '校准过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }
    elif fail_item == 'GSM_FHC_UTS_RFCal_DONE':
        result['en'] = {
            'mean': 'DUT GSM TX power calibration.',
            'indicate': 'Exception occured during calibration, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DUT GSM发射功率校准。',
            'indicate': '校准过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }
    elif fail_item == 'GSM_PATH_TEST_RFCal_DONE':
        result['en'] = {
            'mean': 'DUT GSM RX path loss verification',
            'indicate': 'Verify GSM RX path loss.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DUT GSM接收路径损耗验证',
            'indicate': '验证GSM接收路径损耗。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }
    # WCDMA Calibration
    elif 'WCDMA_CALIBRATION' in fail_task or fail_item == 'WCDMA_FHC_V7_RFCal_DONE':
        result['en'] = {
            'mean': 'DUT WCDMA calibration, include TX power and RX path loss calibration.',
            'indicate': 'Exception occured during calibration, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DUT WCDMA校准，包括发射功率和接收路径损耗校准。',
            'indicate': '校准过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }
    # LTE Calibration
    elif 'LTE_CALIBRATION' in fail_task or fail_item == 'LTE_FHC_TRX_RFCal_DONE':
        result['en'] = {
            'mean': 'DUT LTE calibration, include TX power and RX path loss calibration.',
            'indicate': 'Exception occured during calibration, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DUT LTE校准，包括发射功率和接收路径损耗校准。',
            'indicate': '校准过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }
    # NR Calibration
    elif 'NR_CALIBRATION' in fail_task or fail_item == 'NR_FHC_TRX_RFCal_DONE':
        result['en'] = {
            'mean': 'DUT NR5G calibration, include TX power and RX path loss calibration.',
            'indicate': 'Exception occured during calibration, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DUT NR5G校准，包括发射功率和接收路径损耗校准。',
            'indicate': '校准过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }
    # NSFT
    elif '_NSFT' in fail_task or re.search(r"NSFT\S+_DONE", fail_item) != None:
        result['en'] = {
            'mean': 'DUT non-signalling test, radio performance verification.',
            'indicate': 'Exception occured during test, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': 'DUT非信令测试，无线电性能验证。',
            'indicate': '测试过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }
    # Task CDDC_TEST
    elif 'CAL_DATA_DOWNLOAD_CHECK_TEST' in fail_task:
        result['en'] = {
            'mean': 'Calibration NV list check, avoid NV omitted.',
            'indicate': 'Probably META API failure occured.',
            'suggest': f'META API failure during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': '校准NV列表检查，避免NV遗漏。',
            'indicate': '可能发生了META API故障。',
            'suggest': f'过程中发生META API故障。{regular_suggestion_zh}'
        }
    # Task TRANSCEIVER_POWER_TEST
    elif 'TRANSCEIVER_POWER_TEST' in fail_task:
        result['en'] = {
            'mean': 'Transceiver power test.',
            'indicate': 'Exception occured during test, maybe FHC measurement failure or META API failure occured.',
            'suggest': f'FHC list measurement time synchronize fail or META API exception during the procedure. {regular_suggestion_en}'
        }
        result['zh'] = {
            'mean': '收发器功率测试。',
            'indicate': '测试过程中发生异常，可能是FHC测量失败或META API故障。',
            'suggest': f'FHC列表测量时间同步失败或过程中发生META API异常。{regular_suggestion_zh}'
        }

    # 根据语言参数返回对应结果
    lang = language.lower()
    if lang in result:
        return [result[lang]['mean'], result[lang]['indicate'], result[lang]['suggest']]
    # 默认返回中文
    return [result['zh']['mean'], result['zh']['indicate'], result['zh']['suggest']]

def plat_MTK_measure_failure_analysis(log_title_info, language='zh'):
    # 初始化中英文结果字典
    result = {
        'en': {'mean': '', 'indicate': '', 'suggest': ''},
        'zh': {'mean': '', 'indicate': '', 'suggest': ''}
    }

    probable_cause = '''
            1. measurement failure\n            
            '''
    regular_suggestion_en = "if still fail after retest, maybe it's PCBA defect (SMT defect/IC defect) and need repair."
    regular_suggestion_zh = "如果重新测试后仍然失败，可能是PCBA缺陷（SMT缺陷/IC缺陷），需要维修。"

    fail_item = log_title_info.get('failMsg', 'Unknow')

    if re.search(r"MMAFC_LTE_B(\d+)_CARKIT(\d+)_CAPID_CAL_UPLINK_SIGNAL_MEASURE", fail_item) != None:
        match = re.search(r"MMAFC_LTE_B(\d+)_CARKIT(\d+)_CAPID_CAL_UPLINK_SIGNAL_MEASURE", fail_item)
        # 英文内容
        result['en'] = {
            'mean': 'Frequency error measure fail during AFC calibration.',
            'indicate': 'AFC is first calibrated which depend on test equipment, probably RF prob and connector on board don\'t engaged well.',
            'suggest': f'Confirm RF prob and connector{match.groups()[1]} engaged perfect, you can retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': 'AFC校准期间频率误差测量失败。',
            'indicate': 'AFC是首次校准，依赖测试设备，可能是RF探针与板上连接器接触不良。',
            'suggest': f'确认RF探针和连接器{match.groups()[1]}接触良好，可重新测试PCBA，{regular_suggestion_zh}'
        }

    elif re.search(r"LTE_AFC_B(\d+)_Carkit(\d+)_TX_FREQERR_MEASURE", fail_item) != None:
        match = re.search(r"LTE_AFC_B(\d+)_Carkit(\d+)_TX_FREQERR_MEASURE", fail_item)
        # 英文内容
        result['en'] = {
            'mean': 'Frequency error measure fail during CO-TMS calibration.',
            'indicate': 'Probably RF prob and connector on board don\'t engaged well.',
            'suggest': f'Confirm RF prob and connector{match.groups()[1]} engaged perfect, you can retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': 'CO-TMS校准期间频率误差测量失败。',
            'indicate': '可能是RF探针与板上连接器接触不良。',
            'suggest': f'确认RF探针和连接器{match.groups()[1]}接触良好，可重新测试PCBA，{regular_suggestion_zh}'
        }

    elif (re.search(r"GSM_(GMSK|EPSK)_FHC_UTS_Ex_APC_TX_Measure", fail_item) != None or
          re.search(r"(GMSK|EPSK)_GSM850_FHC_UTS_Ex_512p_Measure", fail_item) != None):
        # 英文内容
        result['en'] = {
            'mean': 'GSM uplink signal measure fail during TX power calibration.',
            'indicate': 'GSM QUAD-BAND and multi frequences/PCL measured together in FHC list mode, probably time synchronize fail cause the measure failure.',
            'suggest': f'Retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': 'GSM发射功率校准期间上行信号测量失败。',
            'indicate': 'GSM四频段和多频率/PCL在FHC列表模式下一起测量，可能是时间同步失败导致测量失败。',
            'suggest': f'重新测试PCBA，{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_Band(\d+)_FHC_TX_Measure", fail_item) != None:
        match = re.search(r"WCDMA_Band(\d+)_FHC_TX_Measure", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'WCDMA BAND{match.groups()[0]} uplink signal measure fail during the calibration.',
            'indicate': f'WCDMA BAND{match.groups()[0]} TX/RX and multi frequences measured together in FHC list mode, probably time synchronize fail cause the measure failure.',
            'suggest': f'Retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'WCDMA频段{match.groups()[0]}校准期间上行信号测量失败。',
            'indicate': f'WCDMA频段{match.groups()[0]}发射/接收和多频率在FHC列表模式下一起测量，可能是时间同步失败导致测量失败。',
            'suggest': f'重新测试PCBA，{regular_suggestion_zh}'
        }

    elif re.search(r"LTE_Band(\d+)_TxCarkit(\d+)_\S+_Measure", fail_item) != None:
        match = re.search(r"LTE_Band(\d+)_TxCarkit(\d+)_\S+_Measure", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'LTE BAND{match.groups()[0]} uplink signal measure fail during the calibration.',
            'indicate': f'LTE BAND{match.groups()[0]} TX/RX and multi frequences measured together in FHC list mode, probably time synchronize fail cause the measure failure.',
            'suggest': f'Retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'LTE频段{match.groups()[0]}校准期间上行信号测量失败。',
            'indicate': f'LTE频段{match.groups()[0]}发射/接收和多频率在FHC列表模式下一起测量，可能是时间同步失败导致测量失败。',
            'suggest': f'重新测试PCBA，{regular_suggestion_zh}'
        }

    elif re.search(r"NR_Band(\d+)_TxCarkit(\d+)_\S+_Measure", fail_item) != None:
        match = re.search(r"NR_Band(\d+)_TxCarkit(\d+)_\S+_Measure", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'NR5G BAND{match.groups()[0]} uplink signal measure fail during the calibration.',
            'indicate': f'NR5G BAND{match.groups()[0]} TX/RX and multi frequences measured together in FHC list mode, probably time synchronize fail cause the measure failure.',
            'suggest': f'Retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'NR5G频段{match.groups()[0]}校准期间上行信号测量失败。',
            'indicate': f'NR5G频段{match.groups()[0]}发射/接收和多频率在FHC列表模式下一起测量，可能是时间同步失败导致测量失败。',
            'suggest': f'重新测试PCBA，{regular_suggestion_zh}'
        }

    elif re.search(r"(GSM|WCDMA)_NSFT_LIST_MODE_Measure_\d+", fail_item) != None:
        match = re.search(r"(GSM|WCDMA)_NSFT_LIST_MODE_Measure_\d+", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'{match.groups()[0]} uplink signal measure fail during non-signalling test.',
            'indicate': f'{match.groups()[0]} TX/RX multi BANDs and multi frequences measured together in list mode, probably time synchronize fail cause the measure failure.',
            'suggest': f'Retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{match.groups()[0]}非信令测试期间上行信号测量失败。',
            'indicate': f'{match.groups()[0]}发射/接收多频段和多频率在列表模式下一起测量，可能是时间同步失败导致测量失败。',
            'suggest': f'重新测试PCBA，{regular_suggestion_zh}'
        }

    elif re.search(r"(LTE|NRFR1)_SFFT_LIST_MODE_Measure_\d+", fail_item) != None:
        match = re.search(r"(LTE|NRFR1)_SFFT_LIST_MODE_Measure_\d+", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'{match.groups()[0]} uplink signal measure fail during non-signalling test.',
            'indicate': f'{match.groups()[0]} TX/RX multi BANDs and multi frequences measured together in list mode, probably time synchronize fail cause the measure failure.',
            'suggest': f'Retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{match.groups()[0]}非信令测试期间上行信号测量失败。',
            'indicate': f'{match.groups()[0]}发射/接收多频段和多频率在列表模式下一起测量，可能是时间同步失败导致测量失败。',
            'suggest': f'重新测试PCBA，{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_B(\d+)_CH(\d+)_AntPath(\d+)_LNA(\d+)_RxCalSeq(\d+)_RSSI_MEASURE", fail_item) != None:
        # 英文内容
        result['en'] = {
            'mean': f'{fail_item} DUT downlink RSSI measure fail during non-signalling test.',
            'indicate': 'probably MTK META API fail cause the measure failure.',
            'suggest': f'Retest the PCBA, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{fail_item} DUT非信令测试期间下行RSSI测量失败。',
            'indicate': '可能是MTK META API故障导致测量失败。',
            'suggest': f'重新测试PCBA，{regular_suggestion_zh}'
        }

    # 根据语言参数返回对应结果
    lang = language.lower()
    if lang in result:
        return [result[lang]['mean'], result[lang]['indicate'], result[lang]['suggest']]
    # 默认返回中文
    return [result['zh']['mean'], result['zh']['indicate'], result['zh']['suggest']]

def plat_MTK_META_failure_analysis(log_title_info, language='zh'):
    # 初始化中英文结果字典
    result = {
        'en': {'mean': '', 'indicate': '', 'suggest': ''},
        'zh': {'mean': '', 'indicate': '', 'suggest': ''}
    }

    probable_cause = '''
            1. measurement failure\n            
            '''
    regular_suggestion_en = "if still fail after retest, maybe it's PCBA defect (SMT defect/IC defect) and need repair."
    regular_suggestion_zh = "如果重新测试后仍然失败，可能是PCBA缺陷（SMT缺陷/IC缺陷），需要维修。"

    fail_item = log_title_info.get('failMsg', 'Unknow')

    if re.search(r"\S+_(Dut_FHC_StartCmd|SendDutFhcCmd|INIT_DUT_TEST)\S*", fail_item, re.IGNORECASE) != None:
        if fail_item.endswith('SendDutFhcCmd'):
            match = re.search(r'(LTE|NR)_Band(\d+)_TxCarkit(\d+)\S*_CalExecutor_SendDutFhcCmd', fail_item)
            # 英文内容
            result['en'] = {
                'mean': f'META API invoked to make DUT switch to correct status before {match.groups()[0]} FHC calibration',
                'indicate': 'META API fail or communication exception occured during the calibration.',
                'suggest': f'Retest, {regular_suggestion_en}'
            }
            # 中文内容
            result['zh'] = {
                'mean': f'调用META API使DUT在{match.groups()[0]} FHC校准前切换到正确状态',
                'indicate': '校准过程中发生META API故障或通信异常。',
                'suggest': f'重新测试，{regular_suggestion_zh}'
            }
        elif fail_item.endswith('Dut_FHC_StartCmd'):
            match = re.search(r'WCDMA_Band(\d+)_Dut_FHC_StartCmd', fail_item)
            # 英文内容
            result['en'] = {
                'mean': f'META API invoked to make DUT switch to correct status before WCDMA FHC calibration',
                'indicate': 'META API fail or communication exception occured during the calibration.',
                'suggest': f'Retest, {regular_suggestion_en}'
            }
            # 中文内容
            result['zh'] = {
                'mean': f'调用META API使DUT在WCDMA FHC校准前切换到正确状态',
                'indicate': '校准过程中发生META API故障或通信异常。',
                'suggest': f'重新测试，{regular_suggestion_zh}'
            }
        elif fail_item.endswith('WCDMA_NSFT_LIST_MODE_INIT_DUT_TEST_'):
            # 英文内容
            result['en'] = {
                'mean': f'META API invoked to make DUT switch to correct status before WCDMA NSFT List mode measurement.',
                'indicate': 'META API fail or communication exception occured during the test.',
                'suggest': f'Retest, {regular_suggestion_en}'
            }
            # 中文内容
            result['zh'] = {
                'mean': f'调用META API使DUT在WCDMA NSFT列表模式测量前切换到正确状态。',
                'indicate': '测试过程中发生META API故障或通信异常。',
                'suggest': f'重新测试，{regular_suggestion_zh}'
            }

    # 根据语言参数返回对应结果
    lang = language.lower()
    if lang in result:
        return [result[lang]['mean'], result[lang]['indicate'], result[lang]['suggest']]
    # 默认返回中文
    return [result['zh']['mean'], result['zh']['indicate'], result['zh']['suggest']]

def plat_MTK_radio_failure_analysis(log_title_info, language='zh', rx_type=None):
    # 初始化中英文结果字典
    result = {
        'en': {'mean': '', 'indicate': '', 'suggest': ''},
        'zh': {'mean': '', 'indicate': '', 'suggest': ''}
    }

    probable_cause = '''
            1. measurement failure\n            
            '''
    regular_suggestion_en = """For RF test value is out of the limits.
    1. Retest first to determine whether it is true failure or NTF.
    2. Judge whether the test value is critical; if the test value is critical, collect the test value data and count the distribution. 
    If the overall distribution deviates from the threshold, it is necessary to re-formulate the new test limit with the R&D engineer.
    3. If the test FAIL only occurs at individual sites, it is necessary to troubleshoot site differences, such as recalibrating line loss, replacing test fixtures, cleaning or replacing test RF heads, etc.
    4. If it is determined to be a real defect after re-testing, it may be a defective SMT patch or chip defect, and it needs to be sent to FAE for analysis and repair."""
    regular_suggestion_zh = """对于射频指标测试不符合门限的情况。
                            1、先复测，确定是真实不良还是误测。
                            2、判断测试值是否临界，如果测试值临界，收集测试值数据并统计分布，如整体分布偏离门限，需要和研发工程师一起重新制定新测试门限。
                            3、如果测试FAIL只发生在个别站点，需要排查站点差异，比如重新校准线损，更换测试夹具，清洁或更换测试射频头等。
                            4、如果复测后确定为真实不良，可能SMT贴片不良或芯片缺陷，需要送FAE分析维修。"""

    fail_item = log_title_info.get('failMsg', 'Unknow')

    if re.search(r"TADC_RFIC0-TEMP\d+", fail_item) != None:
        # 英文内容
        result['en'] = {
            'mean': f'Temperature sensor ADC calibration.',
            'indicate': 'TADC value is out of limits specified.',
            'suggest': f'Retest, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'温度传感器ADC校准。',
            'indicate': 'TADC值超出规定范围。',
            'suggest': f'重新测试，{regular_suggestion_zh}'
        }

    elif re.search(r"CAP_ID_VALUE", fail_item) != None:
        # 英文内容
        result['en'] = {
            'mean': f'AFC CAPID calibration.',
            'indicate': 'AFC CAPID value is out of limits specified.',
            'suggest': f'Retest, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'AFC CAPID校准。',
            'indicate': 'AFC CAPID值超出规定范围。',
            'suggest': f'重新测试，{regular_suggestion_zh}'
        }

    elif re.search(r"TMS_Temperature_\d+", fail_item) != None:
        # 英文内容
        result['en'] = {
            'mean': f'TMS Temperature calibration.',
            'indicate': 'TMS Temperature value is out of limits specified.',
            'suggest': f'Retest, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'TMS温度校准。',
            'indicate': 'TMS温度值超出规定范围。',
            'suggest': f'重新测试，{regular_suggestion_zh}'
        }

    elif re.search(r"_CoTMS.C(\d+)", fail_item) != None:
        match = re.search(r"_CoTMS.C(\d+)", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'TMS Temperature calibration result check.',
            'indicate': f'TMS calibration result C{match.groups()[0]} value is out of limits specified.',
            'suggest': f'Retest, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'TMS温度校准结果检查。',
            'indicate': f'TMS校准结果C{match.groups()[0]}值超出规定范围。',
            'suggest': f'重新测试，{regular_suggestion_zh}'
        }

    elif re.search(r"GSM_FHC_DTS_Ex_Pathloss_AntIndex(\d+)_Result_OK_Check", fail_item) != None:
        match = re.search(r"GSM_FHC_DTS_Ex_Pathloss_AntIndex(\d+)_Result_OK_Check", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'GSM Quad band AGC calibration.',
            'indicate': f'Check DUT antenna{match.groups()[0]} RSSI result is not within limits.',
            'suggest': f'Confirm the RF connector and probo attached well, {regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'GSM四频段AGC校准。',
            'indicate': f'检查发现DUT天线{match.groups()[0]}的RSSI结果超出范围。',
            'suggest': f'确认RF连接器和探针连接良好，{regular_suggestion_zh}'
        }

    elif re.search(r"GSM_DLCH(\d+)_(GSM850|GSM900|DCS1800|PCS1900)_DLP(\S+)_LNA-(UtraHigh|High|Middle|Low)-(PRx|DRx)Loss",
            fail_item) != None:
        match = re.search(r"GSM_DLCH(\d+)_(GSM850|GSM900|DCS1800|PCS1900)_DLP(\S+)_LNA-(UtraHigh|High|Middle|Low)-(PRx|DRx)Loss",
            fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'GSM AGC calibration {match.groups()[1]} Path Loss result check.',
            'indicate': f'{match.groups()[1]} TCH{match.groups()[0]} LNA:{match.groups()[3]} downlink power:{match.groups()[2]}dBm {match.groups()[4]} Path Loss is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'GSM AGC校准{match.groups()[1]}路径损耗结果检查。',
            'indicate': f'{match.groups()[1]} TCH{match.groups()[0]} LNA:{match.groups()[3]}下行功率:{match.groups()[2]}dBm {match.groups()[4]}路径损耗超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"GSM_B(850|900|1800|1900)_ULCH(\d+)_GMSK_SubBand_TxPCL(\d+)-FreqComp(DAC|Weighting)",
                   fail_item) != None:
        match = re.search(r"GSM_B(850|900|1800|1900)_ULCH(\d+)_GMSK_SubBand_TxPCL(\d+)-FreqComp(DAC|Weighting)",
                          fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'GSM APC calibration GSM{match.groups()[0]} subband TCH{match.groups()[1]} frequency compensation value Evaluate.',
            'indicate': f'GSM{match.groups()[0]} subband TCH{match.groups()[1]} PCL{match.groups()[2]} frequency compensation {match.groups()[3]} value is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'GSM APC校准GSM{match.groups()[0]}子带TCH{match.groups()[1]}频率补偿值评估。',
            'indicate': f'GSM{match.groups()[0]}子带TCH{match.groups()[1]} PCL{match.groups()[2]}频率补偿{match.groups()[3]}值超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"EDGE_ULCH(\d+)_EPSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-PCL(\d+)-FreqCompWeighting",
                   fail_item) != None:
        match = re.search(r"EDGE_ULCH(\d+)_EPSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-PCL(\d+)-FreqCompWeighting",
                          fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'EDGE APC calibration GSM{match.groups()[1]} subband TCH{match.groups()[0]} frequency compensation value Evaluate.',
            'indicate': f'EDGE GSM{match.groups()[1]} subband TCH{match.groups()[0]} PCL{match.groups()[2]} frequency compensation value is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'EDGE APC校准GSM{match.groups()[1]}子带TCH{match.groups()[0]}频率补偿值评估。',
            'indicate': f'EDGE GSM{match.groups()[1]}子带TCH{match.groups()[0]} PCL{match.groups()[2]}频率补偿值超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"GSM_ULCH(\d+)_GMSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-APC-PCL(\d+)_Power", fail_item) != None:
        match = re.search(r"GSM_ULCH(\d+)_GMSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-APC-PCL(\d+)_Power", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'GSM APC calibration {match.groups()[1]} TCH{match.groups()[0]} result check.',
            'indicate': f'{match.groups()[1]} TCH{match.groups()[0]} PCL{match.groups()[2]} APC calibration result is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'GSM APC校准{match.groups()[1]} TCH{match.groups()[0]}结果检查。',
            'indicate': f'{match.groups()[1]} TCH{match.groups()[0]} PCL{match.groups()[2]} APC校准结果超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"EDGE_(GSM850|GSM900|DCS1800|PCS1900)_PCL(\d+)_APC_PA_GAIN_DAC", fail_item) != None:
        match = re.search(r"EDGE_(GSM850|GSM900|DCS1800|PCS1900)_PCL(\d+)_APC_PA_GAIN_DAC", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'EDGE APC calibration {match.groups()[0]} Midband PCL{match.groups()[1]} PA gain DAC check.',
            'indicate': f'EDGE {match.groups()[0]} Midband PCL{match.groups()[1]} APC calibration gain DAC is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'EDGE APC校准{match.groups()[0]}中频段PCL{match.groups()[1]} PA增益DAC检查。',
            'indicate': f'EDGE {match.groups()[0]}中频段PCL{match.groups()[1]} APC校准增益DAC超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"EDGE_ULCH(\d+)_EPSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-APC-PCL(\d+)_Power", fail_item) != None:
        match = re.search(r"EDGE_ULCH(\d+)_EPSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-APC-PCL(\d+)_Power", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'EDGE APC {match.groups()[1]} TCH{match.groups()[0]} PCL{match.groups()[2]} power check.',
            'indicate': f'EDGE APC {match.groups()[1]} TCH{match.groups()[0]} PCL{match.groups()[2]} power is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'EDGE APC {match.groups()[1]} TCH{match.groups()[0]} PCL{match.groups()[2]}功率检查。',
            'indicate': f'EDGE APC {match.groups()[1]} TCH{match.groups()[0]} PCL{match.groups()[2]}功率超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_B(\d+)_MidChan(\d+)_TX_PA_Mode(\d+)_Sect(\d+)_TxPower-Prf(\d+)", fail_item) != None:
        match = re.search(r"WCDMA_B(\d+)_MidChan(\d+)_TX_PA_Mode(\d+)_Sect(\d+)_TxPower-Prf(\d+)", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'WCDMA Band{match.groups()[0]} Midband Channel APC PA calibration Power - Prf value evaluate.',
            'indicate': f'WCDMA Band{match.groups()[0]} Channel{match.groups()[1]} PA calibration Power - Prf{match.groups()[4]} value is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'WCDMA Band{match.groups()[0]}中频段信道APC PA校准功率与参考功率差值评估。',
            'indicate': f'WCDMA Band{match.groups()[0]}信道{match.groups()[1]} PA校准功率与参考功率{match.groups()[4]}差值超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_B(\d+)_DLCH(\d+)_AGC-Rx-(Main|Div)Path-LNA\(\d+\)-(HPM|LPM|TKM)-Loss", fail_item) != None:
        match = re.search(r"WCDMA_B(\d+)_DLCH(\d+)_AGC-Rx-(Main|Div)Path-LNA\(\d+\)-(HPM|LPM|TKM)-Loss", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'WCDMA Band{match.groups()[0]} AGC Path loss value check.',
            'indicate': f'WCDMA Band{match.groups()[0]} Channel{match.groups()[1]} AGC RX {match.groups()[2]} Path loss value is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'WCDMA Band{match.groups()[0]} AGC路径损耗值检查。',
            'indicate': f'WCDMA Band{match.groups()[0]}信道{match.groups()[1]} AGC接收{match.groups()[2]}路径损耗值超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_B(\d+)_ULCH(\d+)_PWR(\d+)_PwrS(\d+)_Tx-PA(\d+)-GainDAC", fail_item) != None:
        match = re.search(r"WCDMA_B(\d+)_ULCH(\d+)_PWR(\d+)_PwrS(\d+)_Tx-PA(\d+)-GainDAC", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'WCDMA Band{match.groups()[0]} Midband channel APC PA gain DAC value check.',
            'indicate': f'WCDMA Band{match.groups()[0]} channel{match.groups()[1]} target power {match.groups()[2]}dBm, APC PA gain DAC value is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'WCDMA Band{match.groups()[0]}中频段信道APC PA增益DAC值检查。',
            'indicate': f'WCDMA Band{match.groups()[0]}信道{match.groups()[1]}目标功率{match.groups()[2]}dBm，APC PA增益DAC值超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-CouplerLossDAC", fail_item) != None:
        match = re.search(r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-CouplerLossDAC", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'WCDMA Band{match.groups()[0]} Midband channel APC PD gain DAC result check.',
            'indicate': f'WCDMA Band{match.groups()[0]} channel{match.groups()[1]} PA_Mode{match.groups()[2]}, APC PD gain value is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'WCDMA Band{match.groups()[0]}中频段信道APC PD增益DAC结果检查。',
            'indicate': f'WCDMA Band{match.groups()[0]}信道{match.groups()[1]} PA模式{match.groups()[2]}，APC PD增益值超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-GainCompensationDAC", fail_item) != None:
        match = re.search(r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-GainCompensationDAC", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'WCDMA Band{match.groups()[0]} Subband channel APC PA gain Compensation DAC result check.',
            'indicate': f'WCDMA Band{match.groups()[0]} channel{match.groups()[1]} PA_mode{match.groups()[2]} APC PA gain Compensation DAC result is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'WCDMA Band{match.groups()[0]}子频段信道APC PA增益补偿DAC结果检查。',
            'indicate': f'WCDMA Band{match.groups()[0]}信道{match.groups()[1]} PA模式{match.groups()[2]}，APC PA增益补偿DAC结果超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-CouplerLossCompensationDAC", fail_item) != None:
        match = re.search(r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-CouplerLossCompensationDAC", fail_item)
        # 英文内容
        result['en'] = {
            'mean': f'WCDMA Band{match.groups()[0]} Subband channel APC PD gain Compensation DAC result check.',
            'indicate': f'WCDMA Band{match.groups()[0]} channel{match.groups()[1]} PA_mode{match.groups()[2]} APC PD gain Compensation DAC result is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'WCDMA Band{match.groups()[0]}子频段信道APC PD增益补偿DAC结果检查。',
            'indicate': f'WCDMA Band{match.groups()[0]}信道{match.groups()[1]} PA模式{match.groups()[2]}，APC PD增益补偿DAC结果超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(r"(LTE|NR)_B(\d+)_F(\d+)_CalIdx(\d+)_SxIdx(\d+)_FeIdx(\d+)_BwIdx(\d+)_Carkit(\d+)_TxPower-Prf(\d+)",
                   fail_item) != None:
        match = re.search(
            r"(LTE|NR)_B(\d+)_F(\d+)_CalIdx(\d+)_SxIdx(\d+)_FeIdx(\d+)_BwIdx(\d+)_Carkit(\d+)_TxPower-Prf(\d+)",
            fail_item)
        _tempStr = match.groups()[0]
        _rat = 'LTE_Band' if _tempStr.startswith('LTE') else 'NR_n'
        _number = match.groups()[1]
        _frequency = match.groups()[2]
        _carkit = match.groups()[7]
        _Prf = match.groups()[8]
        # 英文内容
        result['en'] = {
            'mean': f'{_rat}{_number} Middle Channel APC PA Power - Prf value evaluate.',
            'indicate': f'{_rat}{_number} Middle Channel Frequency{_frequency} PA Power - Prf{_Prf} value is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{_rat}{_number}中频段信道APC PA功率与参考功率差值评估。',
            'indicate': f'{_rat}{_number}中频段信道频率{_frequency} PA功率与参考功率{_Prf}差值超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_PwrS(\d+)_FE(\d+)_SX(\d+)_MidCH-PAGain",
            fail_item) != None:
        match = re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_PwrS(\d+)_FE(\d+)_SX(\d+)_MidCH-PAGain",
            fail_item)
        _tempStr = match.groups()[0]
        _rat = _tempStr if _tempStr.startswith('LTE') else 'NR_n'
        _number = match.groups()[1]
        _frequency = match.groups()[2]
        _carkit = match.groups()[3]
        # 英文内容
        result['en'] = {
            'mean': f'{_rat}{_number} APC Middle Channel PA Gain result check.',
            'indicate': f'{_rat}{_number} Middle Channel Frequency{_frequency} Carkit{_carkit} PA Gain result is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{_rat}{_number} APC中频段信道PA增益结果检查。',
            'indicate': f'{_rat}{_number}中频段信道频率{_frequency} Carkit{_carkit} PA增益结果超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_MidCH-Coupler-Loss",
            fail_item) != None:
        match = re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_MidCH-Coupler-Loss",
            fail_item)
        _tempStr = match.groups()[0]
        _rat = _tempStr if _tempStr.startswith('LTE') else 'NR_n'
        _number = match.groups()[1]
        _frequency = match.groups()[2]
        _carkit = match.groups()[3]
        # 英文内容
        result['en'] = {
            'mean': f'{_rat}{_number} APC Middle Channel PD Coupler Loss check.',
            'indicate': f'{_rat}{_number} APC Middle Channel Frequency{_frequency}MHz Carkit{_carkit} PD Coupler Loss is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{_rat}{_number} APC中频段信道PD耦合器损耗检查。',
            'indicate': f'{_rat}{_number} APC中频段信道频率{_frequency}MHz Carkit{_carkit} PD耦合器损耗超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_Subband-PAGain",
            fail_item) != None:
        match = re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_Subband-PAGain",
            fail_item)
        _tempStr = match.groups()[0]
        _rat = _tempStr if _tempStr.startswith('LTE') else 'NR_n'
        _number = match.groups()[1]
        _frequency = match.groups()[2]
        _carkit = match.groups()[3]
        # 英文内容
        result['en'] = {
            'mean': f'{_rat}{_number} APC Subband Channel PA Compensation result check.',
            'indicate': f'{_rat}{_number} APC Subband Channel Frequency{_frequency}MHz Carkit{_carkit} PA Compensation result is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{_rat}{_number} APC子频段信道PA补偿结果检查。',
            'indicate': f'{_rat}{_number} APC子频段信道频率{_frequency}MHz Carkit{_carkit} PA补偿结果超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\S+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_Subband-PDCouplerLoss",
            fail_item) != None:
        match = re.search(
            r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\S+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_Subband-PDCouplerLoss",
            fail_item)
        _tempStr = match.groups()[0]
        _rat = _tempStr if _tempStr.startswith('LTE') else 'NR_n'
        _number = match.groups()[1]
        _frequency = match.groups()[2]
        _carkit = match.groups()[3]
        # 英文内容
        result['en'] = {
            'mean': f'{_rat}{_number} APC Subband Channel PD Compensation result check.',
            'indicate': f'{_rat}{_number} APC Subband Channel Frequency{_frequency}MHz Carkit{_carkit} PD Compensation result is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{_rat}{_number} APC子频段信道PD补偿结果检查。',
            'indicate': f'{_rat}{_number} APC子频段信道频率{_frequency}MHz Carkit{_carkit} PD补偿结果超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }

    elif re.search(
            r"Rx_SC_Cal_(LTE_B|N)(\d+)_DLF(\S+)M_Rout(\d+)_RUT(\d+)_CKG(\S+)_CalIdx(\d+)_PwrS(\d+)_FE(\d+)_FEL(\d+)_Ant(\d+)_(HPM|LPM)_PathLoss",\
            fail_item) != None:
        match = re.search(
            r"Rx_SC_Cal_(LTE_B|N)(\d+)_DLF(\S+)M_Rout(\d+)_RUT(\d+)_CKG(\S+)_CalIdx(\d+)_PwrS(\d+)_FE(\d+)_FEL(\d+)_Ant(\d+)_(HPM|LPM)_PathLoss",\
            fail_item)
        _tempStr = match.groups()[0]
        _rat = _tempStr if _tempStr.startswith('LTE') else 'NR_n'
        _number = match.groups()[1]
        _frequency = match.groups()[2]
        _carkit = match.groups()[5]
        # 英文内容
        result['en'] = {
            'mean': f'{_rat}{_number} AGC Path Loss result check.',
            'indicate': f'{_rat}{_number} Frequency{_frequency} Carkit_group{_carkit} AGC Path Loss result is not within limits.',
            'suggest': f'{regular_suggestion_en}'
        }
        # 中文内容
        result['zh'] = {
            'mean': f'{_rat}{_number} AGC路径损耗结果检查。',
            'indicate': f'{_rat}{_number}频率{_frequency} Carkit组{_carkit} AGC路径损耗结果超出范围。',
            'suggest': f'{regular_suggestion_zh}'
        }
    #
    # Non-signalling test
    # GSM non-signalling test
    elif re.search(r"^T\d+_(GSM|EDGE)_B(850|900|1800|1900)_ULCH(\d+)(\S*)_(GMSK|EPSK)_PWR(\-*\d+\.*\d*)(_PCL\d+)*_(\S+)",\
            fail_item) != None:
        match = re.search(r"^T\d+_(GSM|EDGE)_B(850|900|1800|1900)_ULCH(\d+)(\S*)_(GMSK|EPSK)_PWR(\-*\d+\.*\d*)(_PCL\d+)*_(\S+)",\
            fail_item)
                
        tx_quality = ('TxPower','PVT','AvgFreqErr','MaxPhaseErr','AvgPhaseErr','EVM-95P','EVM-PK','EVM-RMS',\
                      'MagErr-PK','MagErr-RMS','PhaseErr-PK','PhaseErr-RMS','OrigOffset')
        rx_quality = ('BER','PRxLevel','DRxLevel');        modulation = ('SwitchSpec','ModSpec')

        _rat = match.groups()[0]
        _band = match.groups()[1]
        _channel = match.groups()[2]
        _carkit = match.groups()[3]
        _type = match.groups()[4]
        _power = match.groups()[5]
        _pcl = match.groups()[6]
        _item = match.groups()[7]

        mean_en = f'GSM{_band} {_type} non-signalling test'
        mean_zh = f'GSM{_band} {_type}非信令测试'
        indicatate_en = f'GSM{_band} {_type} Channel{_channel}' 
        indicatate_zh = f'GSM{_band} {_type} 信道{_channel}'
        
        if _pcl != None and _pcl.startswith('_PCL'):
            _match = re.search(r"_PCL(\d+)", _pcl)
            indicatate_en += f' TX PCL{_match.groups()[0]}' 
            indicatate_zh += f' TX功率级{_match.groups()[0]}'

        if _item in tx_quality:
            if _item == 'TxPower':
                indicatate_en += f'TX power strength' 
                indicatate_zh += f'发射功率强度' 
            elif _item == 'PVT':
                indicatate_en += f'PVT (Power vs Time)' 
                indicatate_zh += f'功率时间模板'
            elif _item == 'AvgFreqErr':
                indicatate_en += f'average of frequency error' 
                indicatate_zh += f'均值频率误差'
            elif _item == 'MaxPhaseErr':
                indicatate_en += f'peak of phase error' 
                indicatate_zh += f'峰值相位误差'
            elif _item == 'AvgPhaseErr':
                indicatate_en += f'average of phase error' 
                indicatate_zh += f'均值相位误差'
            elif _item == 'EVM-95P':
                indicatate_en += f'EVM (Error Vector Magnitude) 95%' 
                indicatate_zh += f'95%矢量幅度误差'
            elif _item == 'EVM-PK':
                indicatate_en += f'peak EVM (Error Vector Magnitude)' 
                indicatate_zh += f'峰值矢量幅度误差'
            elif _item == 'EVM-RMS':
                indicatate_en += f'peak EVM (Error Vector Magnitude)' 
                indicatate_zh += f'峰值矢量幅度误差'
            elif _item == 'MagErr-PK':
                indicatate_en += f'peak Magnitude error' 
                indicatate_zh += f'峰值幅度误差'
            elif _item == 'MagErr-RMS':
                indicatate_en += f'RMS Magnitude error' 
                indicatate_zh += f'均方根幅度误差'
            elif _item == 'PhaseErr-PK':
                indicatate_en += f'peak phase error' 
                indicatate_zh += f'峰值相位误差'
            elif _item == 'PhaseErr-RMS':
                indicatate_en += f'RMS phase error' 
                indicatate_zh += f'均方根相位误差'
            elif _item == 'OrigOffset':
                indicatate_en += f'Origin Offset' 
                indicatate_zh += f'原点偏移'
        elif _item in rx_quality: 
            indicatate_en += f'downlink power {_power}dBm,'
            indicatate_zh += f'下行功率{_power}dBm，'            
            if _item =='BER': 
                indicatate_en += f'RX BER (Bit Error Rate)'
                indicatate_zh += f'接收质量误码率'
            elif _item =='PRxLevel':
                indicatate_en += f'primary RX level' 
                indicatate_zh += f'主集接收电平'
            elif _item =='DRxLevel':
                indicatate_en += f'diversity RX level' 
                indicatate_zh += f'分集接收电平'
        elif re.search(r"(Mod|Switch)Spec\[(\-*\d+)k\]", _item) != None:
            _match = re.search(r"(Mod|Switch)Spec\[(\-*\d+)k\]", _item)
            _freq = _match.groups()[1]
            if _item.startswith('ModSpec'):
                indicatate_en += f'Modulation Spectrum {_freq}kHz' 
                indicatate_zh += f'发射调制谱{_freq}kHz'
            elif _item.startswith('SwitchSpec'): 
                indicatate_en += f'Switching Spectrum {_freq}kHz' 
                indicatate_zh += f'发射开关谱{_freq}kH'

        indicatate_en += f' test over range.' 
        indicatate_zh += f'测试超标。'
        
        result['en'] = {'mean': mean_en, 'indicate': indicatate_en, 'suggest': regular_suggestion_en}        
        result['zh'] = {'mean': mean_zh, 'indicate': indicatate_zh, 'suggest':regular_suggestion_zh}
    # WCDMA non-signalling    
    elif re.search(r"^T\d+_WCDMA_B(\d+)_(ULF|DLF)(\d+)_(\S+)", fail_item) != None:
        match = re.search(r"^T\d+_WCDMA_B(\d+)_(ULF|DLF)(\d+)_(\S+)", fail_item)
                
        _band = match.groups()[0]
        _direction = match.groups()[1]
        _channel = match.groups()[2]        
        _item = match.groups()[3]

        mean_en = f'WCDMA Band{_band} non-signalling test'
        mean_zh = f'WCDMA Band{_band} 非信令测试'
        indicatate_en = f'WCDMA Band{_band}' 
        indicatate_zh = f'WCDMA Band{_band}'
        
        if _direction == 'ULF':
            indicatate_en += f' uplink Channel{_channel}' 
            indicatate_zh += f'上行信道{_channel}'

            if _item == 'MaxPower':
                indicatate_en += f'Maximum output power' 
                indicatate_zh += f'最大功率输出' 
            elif _item == 'EVM-RMS':
                indicatate_en += f'RMS EVM (Error Vector Magnitude)' 
                indicatate_zh += f'均方根矢量幅度误差'
            elif _item == 'FrequencyError':
                indicatate_en += f'frequency error' 
                indicatate_zh += f'频率误差'
            elif _item == 'OriginOffset':
                indicatate_en += f'Origin Offset' 
                indicatate_zh += f'原点偏移'
            elif _item == 'PCDE':
                indicatate_en += f'PCDE (Peak Code Domain Error)' 
                indicatate_zh += f'峰值码域误差'
            elif _item == 'OBW':
                indicatate_en += f'OBW (Occupied Bandwidth)' 
                indicatate_zh += f'占用带宽'
            elif _item == 'MinPower':
                indicatate_en += f'Minimum output power' 
                indicatate_zh += f'最小功率输出'
            elif re.search(r"ACLR(\-*\d+)M", _item) != None:
                _match = re.search(r"ACLR(\-*\d+)M", _item)
                indicatate_en += f'ACLR (Adjacent Channel Leakage Ratio) {_match.groups()[0]}M' 
                indicatate_zh += f'临道泄露比{_match.groups()[0]}M'
            elif re.search(r"SEM(\d+)", _item) != None:
                _match = re.search(r"SEM(\d+)", _item)
                indicatate_en += f'SEM (Spectrum Emission Mask) offset{_match.groups()[0]}' 
                indicatate_zh += f'频谱发射模板偏移{_match.groups()[0]}'
            elif _item.startswith('ILPC'):                
                indicatate_en += f'ILPC (Inner Loop Power Control)' 
                indicatate_zh += f'内环功率控制'            
        elif _direction == 'DLF':
            indicatate_en += f' downlink Channel{_channel},' 
            indicatate_zh += f'下行信道{_channel},'
                     
            if re.search(r"BER\[(\-*\d+)\]", _item) != None:
                _match = re.search(r"BER\[(\-*\d+)\]", _item)                
                indicatate_en += f' downlink Power{_match.groups()[0]}dBm, RX BER (Bit Error Rate)'
                indicatate_zh += f'下行功率{_match.groups()[0]}dBm, 接收误码率'
            elif re.search(r"(PRx|DRx)RSSI\d+_(\-\d+)", _item) != None:
                _match = re.search(r"(PRx|DRx)RSSI\d+_(\-\d+)", _item)
                rx_type = _match.groups()[0]
                cell_power = _match.groups()[1]                
                if rx_type =='PRx':
                    indicatate_en += f' downlink Power{cell_power}dBm, primary RSSI (Received Signal Strength Indicator)' 
                    indicatate_zh += f'下行功率{cell_power}dBm, 主集RSSI(接收信号强度指示)'
                elif rx_type == 'DRx':
                    indicatate_en += f' downlink Power{cell_power}dBm, diversity RSSI (Received Signal Strength Indicator)' 
                    indicatate_zh += f'下行功率{cell_power}dBm, 分集RSSI(接收信号强度指示)'            
        
        indicatate_en += f' test over range.' 
        indicatate_zh += f'测试超标。'
        
        result['en'] = {'mean': mean_en, 'indicate': indicatate_en, 'suggest': regular_suggestion_en}        
        result['zh'] = {'mean': mean_zh, 'indicate': indicatate_zh, 'suggest':regular_suggestion_zh}
    #
    # LTE/NR RX test
    #
    elif re.search(r"^T\d+_(LTE_B|N)(\d+)_DLF(\d+\.*\d*)M_(\S+)_(PRx|DRx)(Sensitivity|RSSI)$", fail_item) != None:
        match = re.search(r"^T\d+_(LTE_B|N)(\d+)_DLF(\d+\.*\d*)M_(\S+)_(PRx|DRx)(Sensitivity|RSSI)$", fail_item)
        
        _rat = 'LTE Band' if match.groups()[0] == 'LTE_B' else 'NR n'                     
        _band = match.groups()[1]        
        _frequency = match.groups()[2]        
        _condition = match.groups()[3]
        _rx_type = match.groups()[4]
        _item = match.groups()[5]

        mean_en = f'{_rat}{_band} non-signalling RX test'
        mean_zh = f'{_rat}{_band} 非信令RX测试'
        indicatate_en = f'{_rat}{_band} downlink Frequency {_frequency}MHz,' 
        indicatate_zh = f'{_rat}{_band}下行频率{_frequency}MHz,'

        # CID
        if re.search(r'CID(\d+)', _condition) != None: 
            _match = re.search(r'CID(\d+)', _condition)
            indicatate_en += f' calibration ID{_match.groups()[0]},' 
            indicatate_zh += f'CID{_match.groups()[0]},'
        # RF route
        if re.search(r'_RUT(\d+)', _condition) != None: 
            _match = re.search(r'_RUT(\d+)', _condition)
            indicatate_en += f' RF route{_match.groups()[0]},' 
            indicatate_zh += f'射频route{_match.groups()[0]},'
        # Carkit group
        if re.search(r'_CKG(\S+)', _condition) != None: 
            _match = re.search(r'_CKG(\S+)', _condition)
            _sub_detail = f'{_match.groups()[0]}'
            _index = _sub_detail.find('_')
            _carkit_group = _sub_detail[:_index]
            indicatate_en += f' carkit{_carkit_group},' 
            indicatate_zh += f'carkit{_carkit_group},'
        # Band width
        if re.search(r'_BW(\d+)', _condition) != None: 
            _match = re.search(r'_BW(\d+)', _condition)
            indicatate_en += f' band width{_match.groups()[0]}M,' 
            indicatate_zh += f'测试带宽{_match.groups()[0]}M,'
        # downlink power
        if re.search(r'_PWR(\-*\d+\.*\d*)', _condition) != None: 
            _match = re.search(r'_PWR(\-*\d+\.*\d*)', _condition)
            indicatate_en += f' downlink power{_match.groups()[0]}dBm,' 
            indicatate_zh += f'下行功率{_match.groups()[0]}dBm,'

        if _item == 'Sensitivity':
            if rx_type =='PRx':
                indicatate_en += f' primary RX Sensitivity' 
                indicatate_zh += f'主集接收灵敏度'
            elif rx_type == 'DRx':
                indicatate_en += f' diversity RX Sensitivity' 
                indicatate_zh += f'分集接收灵敏度'
        elif _item == 'RSSI':                          
            if rx_type =='PRx':
                indicatate_en += f' primary RSSI (Received Signal Strength Indicator)' 
                indicatate_zh += f'主集RSSI(接收信号强度指示)'
            elif rx_type == 'DRx':
                indicatate_en += f' diversity RSSI (Received Signal Strength Indicator)' 
                indicatate_zh += f'分集RSSI(接收信号强度指示)'            
        
        indicatate_en += f' test over range.' 
        indicatate_zh += f'测试超标。'
        
        result['en'] = {'mean': mean_en, 'indicate': indicatate_en, 'suggest': regular_suggestion_en}        
        result['zh'] = {'mean': mean_zh, 'indicate': indicatate_zh, 'suggest':regular_suggestion_zh}
    elif re.search(r"^T\d+_(LTE_B|N)(\d+)_ULF(\d+\.*\d*)M_(\S+)$", fail_item) != None:
        match = re.search(r"^T\d+_(LTE_B|N)(\d+)_ULF(\d+\.*\d*)M_(\S+)$", fail_item)
        
        _rat = 'LTE Band' if match.groups()[0] == 'LTE_B' else 'NR n'                     
        _band = match.groups()[1]        
        _frequency = match.groups()[2]        
        _detail = match.groups()[3]
        _index = _detail.rfind('_')
        _condition =_detail[:_index] 
        _item =_detail[_index+1:]
        
        mean_en = f'{_rat}{_band} non-signalling TX test'
        mean_zh = f'{_rat}{_band} 非信令TX测试'
        indicatate_en = f'{_rat}{_band} uplink Frequency {_frequency}MHz,' 
        indicatate_zh = f'{_rat}{_band}上行频率{_frequency}MHz,'

        # CID
        if re.search(r'CID(\d+)', _condition) != None: 
            _match = re.search(r'CID(\d+)', _condition)
            indicatate_en += f' calibration ID{_match.groups()[0]},' 
            indicatate_zh += f'CID{_match.groups()[0]},'
        # RF route
        if re.search(r'_RUT(\d+)', _condition) != None: 
            _match = re.search(r'_RUT(\d+)', _condition)
            indicatate_en += f' RF route{_match.groups()[0]},' 
            indicatate_zh += f'射频route{_match.groups()[0]},'
        # Carkit group
        if re.search(r'_CKG(\S+)', _condition) != None: 
            _match = re.search(r'_CKG(\S+)', _condition)
            _sub_detail = f'{_match.groups()[0]}'
            _index = _sub_detail.find('_')
            _carkit_group = _sub_detail[:_index]
            indicatate_en += f' carkit{_carkit_group},' 
            indicatate_zh += f'carkit{_carkit_group},'
        # modulation
        if re.search(r'_(\S*)(QPSK|QAM)', _condition) != None: 
            _match = re.search(r'_(\S*)(QPSK|QAM)', _condition)
            _sub_detail = f'{_match.groups()[0]}{_match.groups()[1]}'
            _last = _sub_detail.rfind('_')
            _mod =_sub_detail[_last+1:]
            indicatate_en += f' modulation {_mod},' 
            indicatate_zh += f'调制方式{_mod},'
        # Band width
        if re.search(r'_BW(\d+)', _condition) != None: 
            _match = re.search(r'_BW(\d+)', _condition)
            indicatate_en += f' band width{_match.groups()[0]}M,' 
            indicatate_zh += f'测试带宽{_match.groups()[0]}M,'
        # RB Config
        if re.search(r'_RB(\d+)\@(\d+)', _condition) != None: 
            _match = re.search(r'_RB(\d+)\@(\d+)', _condition)
            indicatate_en += f' RB config {_match.groups()[0]}@{_match.groups()[1]},' 
            indicatate_zh += f'RB配置{_match.groups()[0]}@{_match.groups()[1]},'
        # downlink power
        if re.search(r'_PWR(\-*\d+\.*\d*)', _condition) != None: 
            _match = re.search(r'_PWR(\-*\d+\.*\d*)', _condition)
            indicatate_en += f' target power{_match.groups()[0]}dBm,' 
            indicatate_zh += f'目标功率{_match.groups()[0]}dBm,'

        if _item == 'TxPower':            
            indicatate_en += f' TX power' 
            indicatate_zh += f'发射功率'            
        elif _item == 'EVM-RMS':                          
            indicatate_en += f'RMS EVM (Error Vector Magnitude)' 
            indicatate_zh += f'均方根矢量幅度误差'            
        elif _item == 'IQOffset':                          
            indicatate_en += f'IQOffset (IQ signal Offset)' 
            indicatate_zh += f'IQ信号偏移'
        elif re.search(r'Freq(uency)*Error', _item) != None:                          
            indicatate_en += f'Frequency Error' 
            indicatate_zh += f'频率误差'
        elif re.search(r'Mag(nitude)*Error', _item) != None:                          
            indicatate_en += f'Magnitude Error' 
            indicatate_zh += f'幅度误差'
        elif _item == 'PhaseError':                          
            indicatate_en += f'Phase Error' 
            indicatate_zh += f'相位误差'
        elif re.search(r'CarrierLeak(age)*', _item) != None:                          
            indicatate_en += f'Carrier Leakage' 
            indicatate_zh += f'载波泄露'
        elif re.search(r'Flat(ness)*RP(\d+)', _item) != None:
            __match = re.search(r'Flat(ness)*RP(\d+)', _item)                          
            indicatate_en += f'Flatness Ripple {__match.groups()[0]}' 
            indicatate_zh += f'平坦度纹波{__match.groups()[0]}'
        elif re.search(r'ACLR(\S+)', _item) != None: 
            __match = re.search(r'ACLR(\S+)', _item)                         
            indicatate_en += f'ACLR (Adjacent Channel Leakage Ratio)' 
            indicatate_zh += f'临道泄露比'
        elif re.search(r"SEM(\S+)", _item) != None:
                _match = re.search(r"SEM(\S+)", _item)
                indicatate_en += f'SEM (Spectrum Emission Mask) area {_match.groups()[0]}' 
                indicatate_zh += f'频谱发射模板偏移区域{_match.groups()[0]}'

        indicatate_en += f' test over range.' 
        indicatate_zh += f'测试超标。'
        
        result['en'] = {'mean': mean_en, 'indicate': indicatate_en, 'suggest': regular_suggestion_en}        
        result['zh'] = {'mean': mean_zh, 'indicate': indicatate_zh, 'suggest':regular_suggestion_zh}

    # 根据语言参数返回对应结果
    lang = language.lower()
    if lang in result:
        return [result[lang]['mean'], result[lang]['indicate'], result[lang]['suggest']]
    # 默认返回中文
    return [result['zh']['mean'], result['zh']['indicate'], result['zh']['suggest']]

def plat_Qualcomm_radio_performance_failure_analysis(log_title_info, language='zh'):
    mean_en = '';   indicate_en = ''
    mean_zh = '';   indicate_zh = ''  
    
    suggest_en = """1. Retest first to determine whether it is true failure or NTF.
    2. Judge whether the test value is critical; if the test value is critical, collect the test value data and count the distribution. 
    If the overall distribution deviates from the threshold, it is necessary to re-formulate the new test limit with the R&D engineer.
    3. If the test FAIL only occurs at individual sites, it is necessary to troubleshoot site differences, such as recalibrating line loss, replacing test fixtures, cleaning or replacing test RF heads, etc.
    4. If it is determined to be a real defect after re-testing, it may be a defective SMT patch or chip defect, and it needs to be sent to FAE for analysis and repair."""
    suggest_zh = """1、先复测，确定是真实不良还是误测。
    2、判断测试值是否临界，如果测试值临界，收集测试值数据并统计分布，如整体分布偏离门限，需要和研发工程师一起重新制定新测试门限。
    3、如果测试FAIL只发生在个别站点，需要排查站点差异，比如重新校准线损，更换测试夹具，清洁或更换测试射频头等。
    4、如果复测后确定为真实不良，可能SMT贴片不良或芯片缺陷，需要送FAE分析维修。"""

    fail_item = log_title_info.get('failMsg','Unknow')
    mean_en = f'{fail_item}'
    mean_zh = f'{fail_item}'

    # Connected_V2,MEASUREMENTS: FBRx Gain
    if (_match := re.search(r"^QSC_(WCDMA|LTE|NR5G|NR5G_SUB6)_FBRX_(?:B|n)(\d+)_(\S+)_(PTH_GAIN|PATH_GAIN|MEAS_PWR|MeasTxPwr|LSE)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band_number = _match.group(2)
        _condition = _match.group(3)
        _item = _match.group(4)

        _band_head = 'n' if _rat.startswith('NR5G') else 'B' 
        
        mean_en = f'{_rat} {_band_head}{_band_number} connected FBRx gain calibration fail.'
        mean_zh = f'{_rat} {_band_head}{_band_number} connected FBRx gain 校准fail.'
        indicate_en = f'{_rat} {_band_head}{_band_number} connected FBRx gain calibration,'
        indicate_zh = f'{_rat} {_band_head}{_band_number} connected FBRx gain 校准，' 

        _match = re.search(r"_F(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'frequency{_match.group(1)}KHz,'
            indicate_zh += f'频率点{_match.group(1)}KHz，'

        _match = re.search(r"_(?:SP|Sig)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_(?:ANT|AntN)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'
        
        _match = re.search(r"_GS(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'FBRx Gain State{_match.group(1)},'
            indicate_zh += f'FBRx增益状态{_match.group(1)}，'
                
        indicate_en += f'{_item},'
        indicate_zh += f'{_item}，'

        if _item.lower() == "path_gain" or _item.lower() == "pth_gain": 
             indicate_en += f'FBRx Path Gain is the path gain value derived from measurements made by the internal FBRx circuit under different receiving gain conditions.'
             indicate_zh += f'FBRx Path Gain是在不同接收增益状态下，内部FBRx电路测量计算所得的路径增益值。'  
    # Connected_V2,MEASUREMENTS: Rx Gain Calibration Results 
    elif (_match := re.search(r"^QSC_(WCDMA|LTE|NR5G|NR5G_SUB6)_RXGAIN_(?:B|n)(\d+)_(\S+)_AGC_OFFSET$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band_number = _match.group(2)
        _condition = _match.group(3)
        
        _band_head = 'n' if _rat.startswith('NR5G') else 'B'
        
        mean_en = f'{_rat} {_band_head}{_band_number} connected Rx gain calibration fail.'
        mean_zh = f'{_rat} {_band_head}{_band_number} connected Rx gain 校准fail.'
        indicate_en = f'{_rat} {_band_head}{_band_number} connected Rx gain calibration,'
        indicate_zh = f'{_rat} {_band_head}{_band_number} connected Rx gain 校准，' 

        _match = re.search(r"_F(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'frequency{_match.group(1)}KHz,'
            indicate_zh += f'频率点{_match.group(1)}KHz，'

        _match = re.search(r"_(?:SP|Sig)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_(?:ANT|AntN|ANT_NUM_)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'
        
        _match = re.search(r"_LNA(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'Rx LNA{_match.group(1)},'
            indicate_zh += f'接收增益{_match.group(1)}，'

        _match = re.search(r"_(-*\d+\.*\d*)dBm", _condition, re.I) 
        if _match is not None:
            indicate_en += f'downlink power{_match.group(1)}dBm,'
            indicate_zh += f'下行功率{_match.group(1)}dBm，'

        indicate_en += f'AGC Offset is the offset between default AGC under different downlink power and different LNA conditions.'
        indicate_zh += f'AGC Offset是在不同的下行功率和不同LNA条件下，AGC偏移量。'             
    # UnConnected, MEASUREMENTS: FULL Bias Tx Linearizer  
    elif (_match := re.search(r"^QSC_(WCDMA|LTE|NR5G|NR5G_SUB6|SUB6)_FULL_BIAS_TX(_LIN)*_(?:B|n)(\d+)_(\S+)_(RgiDeltaPwr|Pwr|MAX_TxPwr|MIN_TxPwr|MxPwr|MnPwr)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band_number = _match.group(2)
        _condition = _match.group(3)
        
        _band_head = 'B'
        if _rat.startswith('NR5G') or _rat == 'SUB6':
            _rat = 'NR5G'
            _band_head = 'n'

        mean_en = f'{_rat} {_band_head}{_band_number} unconnected FULL Bias Tx Linearizer calibration fail.'
        mean_zh = f'{_rat} {_band_head}{_band_number} unconnected FULL Bias Tx Linearizer 校准fail.'
        indicate_en = f'{_rat} {_band_head}{_band_number} unconnected FULL Bias Tx Linearizer calibration,'
        indicate_zh = f'{_rat} {_band_head}{_band_number} unconnected FULL Bias Tx Linearizer校准，' 

        _match = re.search(r"_F(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'frequency{_match.group(1)}KHz,'
            indicate_zh += f'频率点{_match.group(1)}KHz，'

        _match = re.search(r"_BW(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'

        _match = re.search(r"_PA(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'PA{_match.group(1)},'
            indicate_zh += f'功率放大等级{_match.group(1)}，'
        
        _match = re.search(r"_(?:SP|Sig)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_(?:ANT|AntN)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'
                        
        indicate_en += f"""TX Full Bias Linear calibration is generally performed under a series of TxAGCs under 2 power amplification levels, VCC and ICQ remain unchanged, 
        and the scan power is performed to check whether the scan power meets the requirements."""
        indicate_zh += f"""TX Full Bias Linear 校准一般是在2个功率放大级别下，VCC及ICQ不变，在一系列TxAGC下进行功率扫描，检测扫描功率是否符合要求。""" 
    # MEASUREMENTS: APT Tx Linearizer 
    elif (_match := re.search(r"^QSC_(WCDMA|LTE|NR5G|NR5G_SUB6|SUB6)_APT_TX(_LIN)*_(?:B|n)(\d+)_(\S+)_(RgiDeltaPwr|Pwr|MAX_TxPwr|MIN_TxPwr|MxPwr|MnPwr)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band_number = _match.group(2)
        _condition = _match.group(3)
        
        _band_head = 'B'
        if _rat.startswith('NR5G') or _rat == 'SUB6':
            _rat = 'NR5G'
            _band_head = 'n'
        
        mean_en = f'{_rat} {_band_head}{_band_number} unconnected APT Tx Linearizer calibration fail.'
        mean_zh = f'{_rat} {_band_head}{_band_number} unconnected APT Tx Linearizer 校准fail.'
        indicate_en = f'{_rat} {_band_head}{_band_number} unconnected APT Tx Linearizer calibration,'
        indicate_zh = f'{_rat} {_band_head}{_band_number} unconnected APT Tx Linearizer校准，' 

        _match = re.search(r"_F(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'frequency{_match.group(1)}KHz,'
            indicate_zh += f'频率点{_match.group(1)}KHz，'

        _match = re.search(r"_BW(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'

        _match = re.search(r"_PA(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'PA{_match.group(1)},'
            indicate_zh += f'功率放大等级{_match.group(1)}，'
        
        _match = re.search(r"_(?:SP|Sig)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_(?:ANT|AntN)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'
                        
        indicate_en += f"""TX APT Linear calibration is generally performed at 2 power amplification levels, with multiple VCC and ICQ values, and TxAGC decreasing to check whether the scan power meets the requirements."""
        indicate_zh += f"""TX APT Linear 校准一般是在2个功率放大级别下，在多个设定VCC及ICQ值，TxAGC递减下进行功率扫描，检测扫描功率是否符合要求。"""  
    # RFCal_QSC_XO_Coarse_DC_Cal
    elif (_match := re.search(r"(\S+)_(XOTempInit|XOTempFinal)$", fail_item, re.I)) != None:
        _condition = _match.group(1)
        _item = _match.group(2)        
        
        mean_en = f'QSC XO (Crystal Oscillator) Coarse DC calibration temperature fail.'
        mean_zh = f'高通射频晶体振荡器粗调校准温度检测失败。'
        if _item == 'XOTempInit':
            indicate_en = f'Qualcomm XO calibration initial temperature verification,'
            indicate_zh = f'高通XO校准初始温度测试，' 
        elif _item == 'XOTempFinal':
            indicate_en = f'Qualcomm XO calibration final temperature verification,'
            indicate_zh = f'高通XO校准最终温度测试，' 

        _match = re.search(r"_F(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'frequency{_match.group(1)}KHz,'
            indicate_zh += f'频率点{_match.group(1)}KHz，'
                
        _match = re.search(r"_(?:SP|Sig)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_(?:ANT|AntN)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'
                        
        suggest_en = f'XO calibration temperature is too high, PCBA need cooling for test.'
        suggest_zh = f'XO 校准温度太高，主板需要先冷却再测试。'
    # GSM/EDGE FBRx Cal
    elif (_match := re.search(r"^(?:GSM_FBRx_Cal_)*(EGSM|GSM850|DCS|PCS)_(\S+)_(PMEAS|FBRxGain|LSE|Path_Gain)$", fail_item, re.I)) != None:
        _band = _match.group(1)
        _condition = _match.group(2)
        _item = _match.group(3)        
        
        mean_en = f'GSM {_band} FBRx Calibration fail.'
        mean_zh = f'GSM {_band} FBRx校准失败。'
        indicate_en = f'GSM {_band} FBRx Calibration,'
        indicate_zh = f'GSM {_band} FBRx校准，'
        
        _match = re.search(r"_CH(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'channel{_match.group(1)},'
            indicate_zh += f'信道{_match.group(1)}，'
                
        _match = re.search(r"_(?:SigPt|Sig)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_(?:AntPt|AntP)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        _match = re.search(r"_(?:FBRxGainS|GS)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'FBRx Gain State{_match.group(1)},'
            indicate_zh += f'FBRx增益状态{_match.group(1)}，'
                        
        if _item.lower() == "path_gain" or _item.lower() == "fbrxgain": 
             indicate_en += f'FBRx Path Gain is the path gain value derived from measurements made by the internal FBRx circuit under different receiving gain conditions.'
             indicate_zh += f'FBRx Path Gain是在不同接收增益状态下，内部FBRx电路测量计算所得的路径增益值。'
    # GSM FBRx Rx Cal FreqComp
    elif (_match := re.search(r"^(?:GSM_Rx_Cal_FreqComp_)*(EGSM|GSM850|DCS|PCS)_(\S+)_(RSSI|Rx_*GainOffset|Gain_*Offset)$", fail_item, re.I)) != None:
        _band = _match.group(1)
        _condition = _match.group(2)
        _item = _match.group(3)        
        
        mean_en = f'GSM {_band} Rx Calibration Frequency compensation Gain Offset check fail.'
        mean_zh = f'GSM {_band} Rx校准频率补偿偏移检查失败。'
        
        indicate_en = f'GSM {_band} Rx Calibration Frequency compensation Gain Offset check,'
        indicate_zh = f'GSM {_band} Rx校准频率补偿偏移检查，'

        _match = re.search(r"_CH(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'channel{_match.group(1)},'
            indicate_zh += f'信道{_match.group(1)}，'
                
        _match = re.search(r"_(?:SigPath|Sig)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_(?:AntPath|AntP)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        _match = re.search(r"_RxGain(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'Rx Gain Range {_match.group(1)},'
            indicate_zh += f'Rx增益范围{_match.group(1)}，'
                        
        if _item.lower().endswith("gainoffset"): 
             indicate_en += f'Rx Gain Offset is the receive compensation value of each channel calculated by the internal circuit measurement under different downlink power and receive gain states.'
             indicate_zh += f'Rx Gain Offset是在不同下行功率及接收增益状态下，内部电路测量计算所得的各个信道接收补偿值。'
    # GSM Rx Cal FreqComp
    elif (_match := re.search(r"^GSM_(EGSM|GSM850|DCS|PCS)_RX_GAIN_OFFSET_CH_(\d+)_RX_LEVEL_(-*\d+\.*\d*)_SIGPATH_(\d+)_RX_GAIN_RANGE_(\d+)$", fail_item, re.I)) != None:
        _band = _match.group(1)
        _channel = _match.group(2)
        _RxLevel = _match.group(3)        
        _Sig_path = _match.group(4)
        _Rx_Gain_Range = _match.group(5)

        mean_en = f'GSM {_band} Rx Calibration Frequency compensation Gain Offset check fail.'
        mean_zh = f'GSM {_band} Rx校准频率补偿偏移检查失败。'
        
        indicate_en = f'GSM {_band} Rx Calibration Frequency compensation Gain Offset check,'
        indicate_zh = f'GSM {_band} Rx校准频率补偿偏移检查，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'
               
        indicate_en += f'signal path{_Sig_path},'
        indicate_zh += f'signal path{_Sig_path}，'      
                
        indicate_en += f'Rx Gain Range {_Rx_Gain_Range},'
        indicate_zh += f'Rx增益范围{_Rx_Gain_Range}，'

        indicate_en += f'Downlink power {_RxLevel}dBm,'
        indicate_zh += f'下行功率{_RxLevel}dBm，'
        
        indicate_en += f'Rx Gain Offset is the receive compensation value of each channel calculated by the internal circuit measurement under different downlink power and receive gain states.'
        indicate_zh += f'Rx Gain Offset是在不同下行功率及接收增益状态下，内部电路测量计算所得的各个信道接收补偿值。'
    # GSM/EDGE Tx DA Cal Sweep,GSM/EDGE Tx DA Cal Min/Max
    elif (_match := re.search(r"^GSM(_GSM850|_EGSM|_DCS|_PCS)*_TX_DA_CAL(_GSM850|_EGSM|_DCS|_PCS)*_(\S+)_(gsm_min_pmeas|gsm_max_pmeas|edge_min_pmeas|edge_max_pmeas|trigger_level)$", fail_item, re.I)) != None:
        #_match = re.search(r"^GSM(_GSM850|_EGSM|_DCS|_PCS)*_TX_DA_CAL(_GSM850|_EGSM|_DCS|_PCS)*_(\S+)_(gsm_min_pmeas|gsm_max_pmeas|edge_min_pmeas|edge_max_pmeas|trigger_level)$", fail_item, re.I) 
        _band = _match.group(1)
        _band2 = _match.group(2)
        _condition = _match.group(3)
        _item = _match.group(4) 

        _item = _item.replace('_',' ')

        if len(_band) == 0:
            _band = _band2.strip('_')

        _rat = 'GSM'
        if _item.startswith('EDGE'):
            _rat = 'EDGE'

        mean_en = f'GSM {_band} Tx DA Cal sweep {_item} fail.'
        mean_zh = f'GSM {_band} Tx DA 校准功率扫描{_item}失败。'
        indicate_en = f'GSM {_band} Tx DA Cal sweep {_item},'
        indicate_zh = f'GSM {_band} Tx DA 校准功率扫描{_item}，'

        _match = re.search(r"(?:_CH_|_CH)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'channel{_match.group(1)},'
            indicate_zh += f'信道{_match.group(1)}，'
                
        _match = re.search(r"_Sig(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        _match = re.search(r"_AntP(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        _match = re.search(r"_(?:PA_|PA)(\d+)", _condition, re.I) 
        if _match is not None:
            indicate_en += f'PA{_match.group(1)},'
            indicate_zh += f'功率放大状态{_match.group(1)}，'
                        
        if _item.endswith('_PMEAS'):
             indicate_en += f'TX power calibration measures the power value of the power amplifier under different RGI values in different power amplification states, and detects whether the maximum/minimum power meets the requirements.'
             indicate_zh += f'TX功率校准，测量功率放大器在不同功率放大状态下不同RGI值下的功率值，检测最大/最小功率是否符合要求。'
    # RFVFS ALLPath verification
    elif (_match := re.search(r"^(LTE|NR5G)_RFVFS_(?:B|n)(\d+)_(?:CH)*(\d+)_(\S+)_(TX_*ERR(OR)*|AVG_*TXPWR|AVG-*PWR|TX_*PWR)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5)                
        
        _band = f'n{_band}' if _rat=='NR5G' else f'B{_band}'        
                     
        mean_en = f'{_rat} {_band} Tx Power Verification fail.'
        mean_zh = f'{_rat} {_band} Tx发射功率测试失败。'
        indicate_en = f'{_rat} {_band} Tx Power Verification,'
        indicate_zh = f'{_rat} {_band} Tx发射功率测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'

        if (_match := re.search(r"_(?:UBW|BW)(\d+)", _condition, re.I)) != None:        
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'

        if (_match := re.search(r"_(?:Sig|SP|TXSP)(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_(?:ANT|AntN)(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_(\d+\.*\d*)dBm", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'
        elif (_match := re.search(r"_(?:TRP|TTP)[\@]*(\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，' 
                        
        if _item in ('TX_ERROR','TxError','TX_ERR','TxErr'):
             indicate_en += f'{_item} is the difference between the actual measured power value and the expected target power.'
             indicate_zh += f'{_item}是实际测量功率值与期望目标功率的差值。'
    # RFVFS Tx Quality
    elif (_match := re.search(r"^(LTE|NR5G)_RFVFS_(?:B|n)(\d+)(?:_B\d+)*_(\d+)_(\S+)_(AVG-FREQ-ERR|AVG-EVM-DMRS|AVG-EVM|SPEC_FLAT_R\d+|AvgFreqErr|AvgEVM-DMRS|AvgEVM|SPEC_FlatR\d+|TX_FREQ-ERR|EXTREME_FREQ-ERR|TX_*DATA_EVM|TX_*DMRS_EVM|RIP\d+|TxFreqError|FreqError_Extr|FlatRip\d+|AVG-*ORIGIN_*OFFSET|IBE_WORST_*MARGIN|TX_IQ_OFFSET)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5) 
        _item2 =''
                
        _band = f'n{_band}' if _rat=='NR5G' else f'B{_band}'
        
        if _item in ('AVG-FREQ-ERR','AvgFreqErr','TX_FREQ-ERR','TxFreqError'):
            _item2_en = 'Frequency Error'
            _item2_zh = '频率误差'
        elif _item in ('EXTREME_FREQ-ERR','FreqError_Extr'):
            _item2_en = 'Extreme Frequency Error'
            _item2_zh = '极限频率误差'
        elif _item in ('AVG-EVM','AvgEVM','TX_DATA_EVM','TxData_EVM'):  
            _item2_en = 'Average EVM (Error Vector Magnitude)'
            _item2_zh = '均值EVM(向量幅值误差)'
        elif _item in ('AVG-EVM-DMRS','AvgEVM-DMRS','TX_DMRS_EVM','TxDMRS_EVM'):  
            _item2_en = 'EVM of DMRS (Demodulation Reference Signal)'
            _item2_zh = 'DMRS（解调参考信号）的EVM值'
        elif (_match := re.search(r"(?:SPEC_FLATR|RIP|FlatRip)(\d+)", _item, re.I)) != None:
            _item2_en = f'Flatness Ripple{_match.group(1)}'
            _item2_zh = f'发射信号平坦度'
        elif re.search(r"AVG-*ORIGIN_*OFFSET$", _item, re.I) != None or re.search(r"TX_IQ_OFFSET$", _item, re.I) != None:  
            _item2_en = f'Origin Offset'
            _item2_zh = f'原点偏移'
        elif re.search(r"IBE_WORST(_)*MARGIN$", _item, re.I) != None:
            _item2_en = f'Inband Emissions'
            _item2_zh = f'带内杂散'

        mean_en = f'{_rat} {_band} Tx Quality Verification fail.'
        mean_zh = f'{_rat} {_band} Tx发射质量测试失败。'
        indicate_en = f'{_rat} {_band} Tx Signal {_item2_en} Verification,'
        indicate_zh = f'{_rat} {_band} 发射信号{_item2} 测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'

        if (_match := re.search(r"_(\d+)MHz", _condition, re.I)) != None:        
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'

        if (_match := re.search(r"_(?:Sig|SP|TXSP)(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_(?:ANT|AntP)(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_(\d+\.*\d*)dBm", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'                             
    # RFVFS Tx OBW
    elif (_match := re.search(r"^(LTE|NR5G)(?:_RFVFS)*_(?:B|n)(\d+)_(\d+)_(\S+)_OBW$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _condition = _match.group(4)

        _band = f'n{_band}' if _rat=='NR5G' else f'B{_band}'
               
        mean_en = f'{_rat} {_band} Tx OBW Verification fail.'
        mean_zh = f'{_rat} {_band} Tx占用带宽测试失败。'
        indicate_en = f'{_rat} {_band} Tx Signal OBW Verification,'
        indicate_zh = f'{_rat} {_band} 发射信号占用带宽测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'

        if (_match := re.search(r"_(\d+)MHz", _condition, re.I)) != None:        
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'

        if (_match := re.search(r"_(?:Sig|SP|TXSP)(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_(\d+\.*\d*)dBm", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'                             
        elif (_match := re.search(r"_(?:TRP|TTP)[\@]*(\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'
    # RFVFS Tx SEM
    elif (_match := re.search(r"^(LTE|NR5G)(?:_RFVFS)*_(?:B|n)(\d+)_(\d+)_(\S+)_(AREA-*\d_SEM|AREA-*\d_OOB_Pwr|W-AREA-*\d_W-SEM|W-SEM-Area|W-SEM)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5) 
        
        _band = f'n{_band}' if _rat=='NR5G' else f'B{_band}'

        if (_match := re.search(r"AREA(-*\d)_(SEM|OOB_Pwr)", _item, re.I)) != None:
            _item2_en = f'Out-of-Band Emission Power in Area({_match.group(1)})'
            _item2_zh = f'带外发射功率区间（{_match.group(1)}）'
        elif (_match := re.search(r"W-AREA(-*\d)_W-SEM$", _item, re.I)) != None:  
            _item2_en = f'Worst SEM in Area ({_match.group(1)})'
            _item2_zh = f'SEM最差值在区间（{_match.group(1)}）'
        elif _item == 'W-SEM-Area':
            _item2_en = f'Worst SEM in Area ({_match.group(1)})'
            _item2_zh = f'SEM最差值区间（{_match.group(1)}）'
        elif _item == 'W-SEM':
            _item2_en = f'Worst SEM'
            _item2_zh = f'SEM最差值'

        mean_en = f'{_rat} {_band} Tx SEM (Spectrum Emission Mask) Verification fail.'
        mean_zh = f'{_rat} {_band} Tx SEM（频谱发射模板）测试失败。'
        indicate_en = f'{_rat} {_band} Tx Signal {_item2_en} Verification,'
        indicate_zh = f'{_rat} {_band} 发射信号{_item2_zh} 测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'

        if (_match := re.search(r"_BW(\d+)", _condition, re.I)) != None:        
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'
        elif (_match := re.search(r"_(\d+)MHz", _condition, re.I)) != None:        
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'

        if (_match := re.search(r"_(?:Sig|TxSP)(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_(?:ANT|AntP|txANT)(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_(\d+\.*\d*)dBm", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'                             
    # RFVFS Tx ACLR
    elif (_match := re.search(r"^(LTE|NR5G)_RFVFS_(?:B|n)(\d+)_(?:CH)*(\d+)_(\S+)_(W-ACLR-OFS|E_UTRA_ACLR|UTRA_ACLR_EXTREME|UTRA_ACLR_Extr|W-ACLR|UTRA_ACLR|ACLR)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5)        

        _band = f'n{_band}' if _rat=='NR5G' else f'B{_band}'

        mean_en = f'{_rat} {_band} Tx ACLR (Adjacent Channel Leakage Ratio) Verification fail.'
        mean_zh = f'{_rat} {_band} Tx ACLR(邻道泄漏功率比)测试失败。'
        indicate_en = f'{_rat} {_band} Tx ACLR (Adjacent Channel Leakage Ratio) Verification,'
        indicate_zh = f'{_rat} {_band} Tx ACLR(邻道泄漏功率比)测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'

        if (_match := re.search(r"_BW(\d+)", _condition, re.I)) != None:        
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'
        elif (_match := re.search(r"_(\d+)MHz", _condition, re.I)) != None:        
            indicate_en += f'band width{_match.group(1)}MHz,'
            indicate_zh += f'带宽{_match.group(1)}MHz，'

        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_(\d+\.*\d*)dBm", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'
        elif (_match := re.search(r"_TxPWR_(\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'

        if (_match := re.search(r"_(?:W-OFS|OFFSET|OFS)(-*\d+)", _condition, re.I)) != None: 
            indicate_en += f'ACLR Offset{_match.group(1)},'
            indicate_zh += f'ACLR区间{_match.group(1)}，'                           
    # RFVFS Rx RFCalVerification
    elif (_match := re.search(r"^(LTE|NR5G)_RFVFS_(?:B|n)(\d+)_(?:CH|ARFCN)*(\d+)_(\S+)_(RX_ERROR\d|RxAGC\d|RxError\d|RX_ERROR_\d|RxErr\d)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5)

        _band = f'n{_band}' if _rat=='NR5G' else f'B{_band}'

        _item2 = _item        
        if (_match := re.search(r'rx_*err\S*(\d)', _item, re.I)) != None:
            _item2 =f'Rx Error{_match.group(1)}'
        elif (_match := re.search(r'rx_*agc(\d)', _item, re.I)) != None:
            _item2 =f'Rx AGC{_match.group(1)}'

        mean_en = f'{_rat} {_band} RFCalVerification fail.'
        mean_zh = f'{_rat} {_band} RFCalVerification测试失败。'
        indicate_en = f'{_rat} {_band} {_item2} Verification,'
        indicate_zh = f'{_rat} {_band} {_item2}测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'
        
        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_(?:AntN|ANT)(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_IOR(-*\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Downlink Power{_match.group(1)}dBm,'
            indicate_zh += f'下行功率{_match.group(1)}dBm，'

        if _item2=='Rx Error':
            indicate_en += f'RX Error is a measurement of the difference between the Rx AGC and the downlink power.'
            indicate_zh += f'RX Error是测量Rx AGC与下行功率的差值。' 
    # RFVFS All Path Verification Rx Measurement
    elif (_match := re.search(r"^(LTE|NR5G)_RFVFS_(?:B|n)(\d+)_(?:CH)*(\d+)_(\S+)_(RX_LEVEL_Rx\d|CTON_Rx\d|CTON_DELTA_Rx\d|SENSITIVITY_Rx\d|RxLev_\d|CtoN_\d|CtoN_Delta_\d|Sensitivity_\d|RX\d_Level|EstSensitivityRX\d|Rx\dLevel|Rx\dEstSensitivity)$", fail_item, re.I)) != None:
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5)

        _band = f'n{_band}' if _rat=='NR5G' else f'B{_band}'

        _item2 = _item        
        if (_match := re.search(r'rx_*lev\S*(\d)', _item, re.I)) != None:
            _item2 =f'Rx Level{_match.group(1)}'        
        elif (_match := re.search(r'cton_(?:rx)(\d)', _item, re.I)) != None:
            _item2 =f'CTON RX{_match.group(1)}'
        elif (_match := re.search(r'cton_delta_(?:rx)(\d)', _item, re.I)) != None:
            _item2 =f'CTON DELTA RX{_match.group(1)}'
        elif (_match := re.search(r'sensitivity_(?:rx)(\d)', _item, re.I)) != None:
            _item2 =f'CTON DELTA RX{_match.group(1)}'
        elif (_match := re.search(r'rx(\d)_*level', _item, re.I)) != None:
            _item2 =f'Rx Level{_match.group(1)}'
        elif (_match := re.search(r'EstSensitivityRX(\d)', _item, re.I)) != None:
            _item2 =f'Est Sensitivity RX{_match.group(1)}'
        elif (_match := re.search(r'Rx(\d)EstSensitivity', _item, re.I)) != None:
            _item2 =f'Est Sensitivity RX{_match.group(1)}'

        mean_en = f'{_rat} {_band} RX Measurement Verification fail.'
        mean_zh = f'{_rat} {_band} RX Measurement Verification测试失败。'
        indicate_en = f'{_rat} {_band} {_item2} Verification,'
        indicate_zh = f'{_rat} {_band} {_item2}测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'
        
        if (_match := re.search(r"_(?:Sig|SigPath|Rx\dSP)(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_(?:AntN|ANT)(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_IOR(-*\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Downlink Power{_match.group(1)}dBm,'
            indicate_zh += f'下行功率{_match.group(1)}dBm，'              
    # RFVFS WCDMA MaxOutputPower
    elif (_match := re.search(r"^WCDMA_RFVFS_B(\d+)_CH(\d+)(_*\S*)_(FTM_Tx_*Pwr|MAX_TX_PWR|MIN_TX_PWR|TX_PWR|MaxOutput_MxTxPwr|MaxOutput_MnTxPwr|MaxOutput_TxPwr|EVM|FREQ_ERROR|FreqErr|MinOutputPower|MinOutput_TxPwr|ACLR)$", fail_item, re.I)) != None:
        _band = _match.group(1)
        _channel = _match.group(2)
        _condition = _match.group(3)
        _item = _match.group(4)
        
        _item2 = _item        
        if _item == 'MAX_TX_PWR' or _item == 'MaxOutput_MxTxPwr':
            _item2 =f'Maximum of Max Output Power'
            _item = "Tx Power"        
        elif _item == 'MIN_TX_PWR' or _item == 'MaxOutput_MnTxPwr':
            _item2 =f'Minimum of Max Output Power'
            _item = "Tx Power"
        elif _item == 'MaxOutput_TxPwr':
            _item2 =f'Average value of Max Output Power'
            _item = "Tx Power"
        elif _item == 'TX_PWR':
            _item2 =f'Tx Output Power'
            _item = "Tx Power"
        elif re.search(r'FTM_Tx_*Pwr', _item, re.I) != None:
            _item2 =f'FTM Tx Power'
            _item = "FTM Tx Power"
        elif _item == 'MinOutputPower' or _item == 'MinOutput_TxPwr':
            _item2 =f'Tx Minimum Output Power'
            _item = "Tx Minimum Output Power"
        elif _item == 'FREQ_ERROR' or _item == 'FreqErr':
            _item2 =f'Frequency Error'
            _item = "Tx Frequency Error" 
        elif _item == 'EVM':
            _item2 =f'Tx EVM'
            _item = "Tx EVM (Error Vector Magnitude)"       
        elif _item == 'ACLR':
            _item2 =f'Tx ACLR'
            _item = "Tx ACLR (Adjacent Channel Leakage Ratio)"

        mean_en = f'WCDMA B{_band} {_item} Verification fail.'
        mean_zh = f'WCDMA B{_band} {_item} Verification测试失败。'
        indicate_en = f'WCDMA B{_band} {_item2} Verification,'
        indicate_zh = f'WCDMA B{_band} {_item2}测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'
        
        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'
        
        if (_match := re.search(r"_(-*\d+\.*\d*)dBm", _condition, re.I)) != None or \
            (_match := re.search(r"_TARGET_TX_PWR(-*\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Target Power{_match.group(1)}dBm,'
            indicate_zh += f'目标功率{_match.group(1)}dBm，'

        if (_match := re.search(r"_OFFSET(?:\(MHz\))*_*(-*\d)", _condition, re.I)) != None: 
            indicate_en += f'ACLR Offset {_match.group(1)},'
            indicate_zh += f'ACLR 偏移{_match.group(1)}，'
    # RFVFS WCDMA RX
    elif (_match := re.search(r"^WCDMA_RFVFS_B(\d+)_CH(\d+)(_*\S*)_(RX_LEVEL|RX_ERROR|RX_AGC_Rx\d|CTON_Rx\d|CTON_DELTA_Rx\d|SENSITIVITY_Rx\d|RxLevel_\d|RxError_\d|RxAGC_\d|CtoN\d|CtoN_Delta\d|Sensitivity\d)$", fail_item, re.I)) != None:
        _band = _match.group(1)
        _channel = _match.group(2)
        _condition = _match.group(3)
        _item = _match.group(4)
        
        _item2 = _item        
        if re.search(r'Rx_*Level(_\d)*', _item, re.I) != None:
            _item2 =f'Rx Level'
            _item = "Rx Level"
        elif re.search(r'Rx_*Error(_\d)*', _item, re.I) != None:
            _item2 =f'Rx Error'
            _item = "Rx Error"
        elif re.search(r'Rx_*AGC_(?:RX)*\d', _item, re.I) != None:
            _item2 =f'Rx AGC'
            _item = "Rx AGC" 
        elif re.search(r'CTON(?:_RX)*\d', _item, re.I) != None:
            _item2 =f'Rx CtoN'
            _item = "Rx CtoN"
        elif re.search(r'CTON_DELTA(?:_RX)*\d', _item, re.I) != None:
            _item2 =f'Rx CtoN Delta'
            _item = "Rx CtoN Delta" 
        elif re.search(r'Sensitivity(?:_RX)*\d', _item, re.I) != None:
            _item2 =f'Rx Sensitivity'
            _item = "Rx Sensitivity"        

        mean_en = f'WCDMA B{_band} {_item} Verification fail.'
        mean_zh = f'WCDMA B{_band} {_item} Verification测试失败。'
        indicate_en = f'WCDMA B{_band} {_item2} Verification,'
        indicate_zh = f'WCDMA B{_band} {_item2}测试，'
        
        indicate_en += f'channel{_channel},'
        indicate_zh += f'信道{_channel}，'
        
        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'
        
        if (_match := re.search(r"_(PRI|SEC)", _condition, re.I)) != None:
            if _match.group(1) == 'PRI':         
                indicate_en += f'Primary Antenna,'
                indicate_zh += f'主集天线，'
            elif _match.group(1) == 'SEC': 
                indicate_en += f'Diversity Antenna,'
                indicate_zh += f'分集天线，'

        if (_match := re.search(r"_(-*\d+\.*\d*)dBm", _condition, re.I)) != None or \
            (_match := re.search(r"_BST_PWR(-*\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Downlink Power{_match.group(1)}dBm,'
            indicate_zh += f'下行功率{_match.group(1)}dBm，' 
    # RFVFS WCDMA ILPC
    elif (_match := re.search(r"^WCDMA_RFVFS_POWER_SWEEP(\S+)_DELTA$", fail_item, re.I)) != None:        
        _condition = _match.group(1)
        _item = 'ILPC (Inner Loop Power Control)'

        mean_en = f'WCDMA {_item} Verification fail.'
        mean_zh = f'WCDMA {_item} Verification测试失败。'
        indicate_en = f'WCDMA {_item} Verification,'
        indicate_zh = f'WCDMA {_item}测试，'
        
        if (_match := re.search(r"_B(\d+)", _condition, re.I) ) != None:
            indicate_en += f'Band{_match.group(1)},'
            indicate_zh += f'频段号{_match.group(1)}，'
        
        if (_match := re.search(r"_CH(\d+)", _condition, re.I) ) != None:
            indicate_en += f'Channel{_match.group(1)},'
            indicate_zh += f'信道{_match.group(1)}，'
        
        if (_match := re.search(r"_SEGMENT_*(E|F)", _condition, re.I) ) != None:
            indicate_en += f'Segment {_match.group(1)},'
            indicate_zh += 'E段下降' if _match.group(1)=='E' else 'F段上升'

        if (_match := re.search(r"_Slot(\d+)", _condition, re.I) ) != None:
            indicate_en += f'Slot {_match.group(1)},'
            indicate_zh += f'时隙{_match.group(1)},'

        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'                
    # RFVFS GSM Phase And Freq Err
    elif (_match := re.search(r"^GSM_RFVFS_(GSM850|EGSM|DCS|PCS)_CH(\d+)_(?:TX_LEVEL|PCL)(\d+)(\S*)_(AVG_TX_PWR|RMS_ERROR|FREQ_ERROR|TIME_MASK|AvgTxPwr|AvgRMSPhErr|MaxPeakPhErr|FreqErr|PVT)$", fail_item, re.I)) != None:        
        _band = _match.group(1)
        _channel = _match.group(2)
        _plc = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5)

        if re.search(r'AVG_*TX_*PWR', _item, re.I) != None:
            _item ='Tx Average Power'
        elif _item =='RMS_ERROR' or _item =='AvgRMSPhErr': 
            _item ='Tx Average RMS Phase Error' 
        elif _item =='MaxPeakPhErr': 
            _item ='Tx Maximum of Peak Phase Error'
        elif _item =='FREQ_ERROR' or _item =='FreqErr': 
            _item ='Tx Frequency Error'
        elif _item =='TIME_MASK' or _item =='PVT': 
            _item ='PVT (Power VS Time)'

        mean_en = f'GSM {_band} {_channel} {_item} Verification fail.'
        mean_zh = f'GSM {_band} {_channel} {_item} 测试失败。'
        indicate_en = f'GSM {_band} channel{_channel} PCL{_plc} {_item} Verification,'
        indicate_zh = f'GSM {_band}信道{_channel} 功率等级{_plc} {_item}测试，'
        
        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'                
    # RFVFS EDGE Phase And Freq Err
    elif (_match := re.search(r"^EDGE_RFVFS_(GSM850|EGSM|DCS|PCS)_CH(\d+)_(?:TX_LEVEL|PCL)(\d+)(\S*)_(AVG_TX_PWR|EVM|OrigOffset|FREQ_ERROR|MAG_ERROR|TIME_MASK|AvgTxPwr|FreqErr|MagError|PVT)$", fail_item, re.I)) != None:        
        _band = _match.group(1)
        _channel = _match.group(2)
        _plc = _match.group(3)
        _condition = _match.group(4)
        _item = _match.group(5)

        if re.search(r'AVG_*TX_*PWR', _item, re.I) != None:
            _item ='Tx Average Power'
        elif _item =='EVM': 
            _item ='Tx Average EVM (Error Vector Magnitude)' 
        elif _item =='OrigOffset': 
            _item ='Tx I/Q Original Offset'
        elif _item =='FREQ_ERROR' or _item =='FreqErr': 
            _item ='Tx Frequency Error'
        elif _item =='MAG_ERROR' or _item =='MagError': 
            _item ='Tx Magnitude Error'
        elif _item =='TIME_MASK' or _item =='PVT': 
            _item ='PVT (Power VS Time)'

        mean_en = f'EDGE {_band} {_channel} {_item} Verification fail.'
        mean_zh = f'EDGE {_band} {_channel} {_item} 测试失败。'
        indicate_en = f'EDGE {_band} channel{_channel} PCL{_plc} {_item} Verification,'
        indicate_zh = f'EDGE {_band}信道{_channel} 功率等级{_plc} {_item}测试，'
        
        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，' 
    # RFVFS Modulation/switch spectrum
    elif (_match := re.search(r"^(GSM|EDGE)_RFVFS_(GSM850|EGSM|DCS|PCS)_CH(\d+)_(?:TX_LEVEL_|PCL)(\d+)(\S*)_OFFSET(-*\d+\.*\d*)_(ORFS_MOD|ORFS_SW)$", fail_item, re.I)) != None:        
        _rat = _match.group(1)
        _band = _match.group(2)
        _channel = _match.group(3)
        _plc = _match.group(4)
        _condition = _match.group(5)
        _offset = _match.group(6)
        _item = _match.group(7)

        if _item =='ORFS_MOD': 
            _item ='Tx Modulation Spectrum'         
        elif _item =='ORFS_SW': 
            _item ='Tx Switching Spectrum'

        mean_en = f'{_rat} {_band} {_channel} {_item} Verification fail.'
        mean_zh = f'{_rat} {_band} {_channel} {_item} 测试失败。'
        indicate_en = f'{_rat} {_band} channel{_channel} PCL{_plc} {_item} Verification,'
        indicate_zh = f'{_rat} {_band}信道{_channel} 功率等级{_plc} {_item}测试，'
        
        indicate_en += f'Frequency Offset {_offset}KHz,'
        indicate_zh += f'频率偏移{_offset}KHz，'
        
        if (_match := re.search(r"_Sig(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，' 
    # RFVFS EDGE EDGE_EstimatedSensitivity
    elif (_match := re.search(r"^EDGE_EstSens(?:_GSM)*_(GSM850|EGSM|DCS|PCS)_CH(\d+)(\S+)_(CTON_MAX_*TO_*MIN_DELTA|CTON_MAX|CTON_MIN|CTON_STD_DEV|CTON|SENSITIVITY_MAX_*TO_*MIN_DELTA|SENSITIVITY_MAX|SENSITIVITY_MIN|SENSITIVITY)$", fail_item, re.I)) != None:        
        _band = _match.group(1)
        _channel = _match.group(2)        
        _condition = _match.group(3)        
        _item = _match.group(4)
        
        mean_en = f'EDGE Estimated Sensitivity Verification fail.'
        mean_zh = f'EDGE Estimated Sensitivity测试失败。'

        if re.search(r'CTON_MAX_*TO_*MIN_DELTA', _item, re.I) != None:
            _item ='CtoN Max to Min Delta'
        elif re.search(r'CTON_STD_DEV', _item, re.I) != None:
            _item ='CtoN Std Dev'
        elif re.search(r'CTON_MAX', _item, re.I) != None:
            _item ='CtoN Max'
        elif re.search(r'CTON_MIN', _item, re.I) != None:
            _item ='CtoN Min'
        elif re.search(r'CTON', _item, re.I) != None:
            _item ='CtoN'
        elif re.search(r'SENSITIVITY_MAX_*TO_*MIN_DELTA', _item, re.I) != None:
            _item ='Sensitivity Max to Min Delta'
        elif re.search(r'SENSITIVITY_MIN', _item, re.I) != None:
            _item ='Sensitivity Min'
        elif re.search(r'SENSITIVITY_MAX', _item, re.I) != None:
            _item ='Sensitivity Max'
        elif re.search(r'SENSITIVITY', _item, re.I) != None:
            _item ='Sensitivity'

        indicate_en = f'EDGE Estimated {_item} Verification,'
        indicate_zh = f'EDGE Estimated {_item}测试，'
        
        indicate_en += f'{_band} Channel{_channel},'
        indicate_zh += f'{_band} 信道{_channel}，'

        if (_match := re.search(r"_(PRI|SEC)", _condition, re.I)) != None:
            if _match.group(1) == 'PRI':         
                indicate_en += f'Primary Antenna,'
                indicate_zh += f'主集天线，'
            elif _match.group(1) == 'SEC': 
                indicate_en += f'Diversity Antenna,'
                indicate_zh += f'分集天线，'
                
        if (_match := re.search(r"_(?:Sig|SP)(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_(?:AntN|ANT)(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_(-*\d+\.*\d*)dBm", _condition, re.I)) != None: 
            indicate_en += f'Downlink Power{_match.group(1)}dBm,'
            indicate_zh += f'下行功率{_match.group(1)}dBm，'
    # RFVFS RxCalVerification
    elif (_match := re.search(r"^EDGE_RFVFS_(GSM850|EGSM|DCS|PCS)_CH(\d+)(\S+)_(RX_LEVEL_RX\d|RX_ERROR_RX\d|RxLevel\d|RxError\d)$", fail_item, re.I)) != None:        
        _band = _match.group(1)
        _channel = _match.group(2)        
        _condition = _match.group(3)        
        _item = _match.group(4)
        
        mean_en = f'EDGE Rx Cal Verification fail.'
        mean_zh = f'EDGE Rx Cal Verification失败。'

        if re.search(r'RX_*LEVEL(?:_RX)*(\d)', _item, re.I) != None:
            _item = f'Rx{_item.group(1)} Rx Level'
        elif re.search(r'RX_*ERROR(?:_RX)*(\d)', _item, re.I) != None:
            _item = f'Rx{_item.group(1)} Rx Error'
        
        indicate_en = f'EDGE {_item} Verification,'
        indicate_zh = f'EDGE {_item}测试，'
        
        indicate_en += f'{_band} Channel{_channel},'
        indicate_zh += f'{_band} 信道{_channel}，'
                        
        if (_match := re.search(r"_(?:Sig|SIGPATH)(\d+)", _condition, re.I) ) != None:        
            indicate_en += f'signal path{_match.group(1)},'
            indicate_zh += f'signal path{_match.group(1)}，'
        
        if (_match := re.search(r"_AntN(\d+)", _condition, re.I)) != None:         
            indicate_en += f'antenna number{_match.group(1)},'
            indicate_zh += f'天线编号{_match.group(1)}，'

        if (_match := re.search(r"_(-*\d+\.*\d*)dBm", _condition, re.I)) != None or \
            (_match := re.search(r"_FWD_LINK_PWR(-*\d+\.*\d*)", _condition, re.I)) != None: 
            indicate_en += f'Downlink Power{_match.group(1)}dBm,'
            indicate_zh += f'下行功率{_match.group(1)}dBm，'

        if _item.endswith('Rx Error'):
            indicate_en += f'RX Error is a measurement of the difference between the Rx AGC and the downlink power.'
            indicate_zh += f'RX Error是测量Rx AGC与下行功率的差值。'
    # QSPR_GENERAL_EXCEPTION
    elif (_match := re.search(r"QSPR_GENERAL_EXCEPTION_IN_(.*)_IN_NODE_(.*)", fail_item, re.I)) != None:  
        _node = _match.group(2)
        nextest_log = log_title_info.get('nextest_log') 
        test_name = log_title_info.get('test_name')
        key_evaluate_line = log_title_info.get('fail_EvalAndLogResults_line','')
        fail_line_number = log_title_info.get('fail_EvalAndLogResults_line_number', -1)

        split_list = re.split(r'[\t]', key_evaluate_line)
        if len(split_list) >=17 and len(split_list[17]) >0:
            mean_en = f'{_node} fail.'
            mean_zh = f'{_node}失败。'
            indicate_en = f'QSPR General Exception, {split_list[17]},'
            indicate_zh = f'QSPR异常，{split_list[17]}，'
            suggest_en = """1. Retest first to determine whether it is true failure or NTF.
                            2. If it is determined to be a real defect after re-testing, it may be a defective SMT patch or chip defect, and it needs to be sent to FAE for analysis and repair."""
            suggest_zh = """1、先复测，确定是真实不良还是误测。
                            2、如果复测后确定为真实不良，可能SMT贴片不良或芯片缺陷，需要送FAE分析维修。"""
        else:
            _keys_pattern = rf"\t{test_name}\tEvalAndLogResults\t\d+\t\d+\t{_node}\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t\* FAILED \*\t"
                    
            log_lines_list = read_universal_file(nextest_log)

            search_line = [x for x in log_lines_list if re.search(_keys_pattern, x, re.I) != None]

            if len(search_line) >0:
                i = fail_line_number
                while i >= 0:
                    i -= 1
                    _cur_line = log_lines_list[i]
                    if _cur_line in search_line:
                        log_title_info.update({'fail_EvalAndLogResults_line' : _cur_line})
                        log_title_info.update({'fail_EvalAndLogResults_line_number' : i})
                        break       
            
            return plat_Qualcomm_radio_coarse_failure_analysis(log_title_info, language)

    # 根据语言参数返回对应结果
    if language.lower() =='en':
        return [mean_en, indicate_en, suggest_en]

    return [mean_zh, indicate_zh, suggest_zh]

def plat_Qualcomm_radio_coarse_failure_analysis(log_title_info, language='zh'):

    mean_en = indicate_en = ''
    mean_zh = indicate_zh = ''  
    
    suggest_en = """1. Retest to determine whether it is NTF or true failure.
    2. If it is NTF, statistically analyse the occurrence probability; high NTF issue require capturing software logs for the development engineer to analyse.
    3. If it is true failure, it may be an SMT placement defect or chip defect, requiring sending for FAE analysis and repair."""
    suggest_zh = """1、先复测，确定是真实不良还是误测。
    2、如果是误测，统计发生概率，高概率误测需要抓软件log,请研发工程师分析。
    3、如果复测后确定为真实不良，可能SMT贴片不良或芯片缺陷，需要送FAE分析维修。"""

    fail_item = log_title_info.get('failMsg','Unknow')
    test_name = log_title_info.get('test_name','Unknow')
    nextest_log = log_title_info.get('nextest_log','')
    key_evaluate_line = log_title_info.get('fail_EvalAndLogResults_line','')
    fail_line_number = log_title_info.get('fail_EvalAndLogResults_line_number', -1)
    track_id = log_title_info.get('trackID', '')

    mean_en = f'{fail_item}'
    mean_zh = f'{fail_item}'

    indicate_en = f"{fail_item}"
    indicate_zh = f"{fail_item}"

    log_lines_list = read_universal_file(nextest_log)    
    # _index = log_lines_list.index(f'{key_evaluate_line}\n')

    _header = f'\t{test_name}\tHeader\tTest = {test_name}  |  '
    _footer = f'\t{test_name}\Footer\tTest = {test_name}  |  '
    _end_test = f'<END_OF_TEST><><>'

    error_array =[]
    test_node = ''
    i = fail_line_number
    while i >= 0:
        i -= 1
        _cur_line = log_lines_list[i]
        if _cur_line.find(_header) != -1:
            break
        elif _cur_line.find(_end_test) != -1:
            break
        elif (_match := re.search('<QIA Test Start><Test started:\s(.+)\sat:', _cur_line)) != None:
            test_node = _match.group(1) 
            break
        elif (index := _cur_line.find('<QIA_DEBUG - Error>')) != -1: 
            _error_content = _cur_line[index + len('<QIA_DEBUG - Error><'):] 
            _error_content = _error_content.rstrip(">\n")                        
            error_array.append(_error_content.rstrip()) 

    if len(test_node) != 0:
        if (_match := re.search(r'(WCDMA|LTE|Sub6).*(?:Band|B|n)(\d+).*(Unconnect|connect)',test_node,re.I)) != None:
            _cal_keyword = _match.group(3).lower()
            if _cal_keyword =='Unconnect':
                indicate_en += f",is FBRx and Rx Gain calibration,Testset is requested."
                indicate_zh += f",是接收FBRx和Rx Gain校准项,需要仪表参与。"
            elif _cal_keyword =='connect':
                indicate_en += f",is Tx power calibration, Testset is not requested."
                indicate_zh += f",是Tx功率校准项,不需要仪表参与。"
        elif (_match := re.search(r'RFCal.*QSC.*XO', test_node, re.I)) != None:
            indicate_en += f",Calibration of the XO crystal temperature and frequency, with temperatures being too high and the instrument's RF signal transmission being interrupted, can lead to calibration failure."
            indicate_zh += f",XO校准晶体温度及频率的校准，温度过高及仪表射频信号传输不通都会导致校准失败。"
        elif (_match := re.search(r'internal.*device.*cal', test_node, re.I)) != None:
            indicate_en += f",Self-calibration, check if the internal circuitry is functioning correctly."
            indicate_zh += f",自校准，检查内部电路是否正常工作。"
        elif (_match := re.search(r'RFCal.*AddActivePhone', test_node, re.I)) != None:
            indicate_en += f",check phone connection and communication status."
            indicate_zh += f",检查手机连接通信是否正常。"
        elif (_match := re.search(r'Check.*Phone.*Communication', test_node, re.I)) != None:
            indicate_en += f",check phone connection and communication status."
            indicate_zh += f",检查手机连接通信是否正常。"
        elif (_match := re.search(r'Write.*Unified.*NV.*To.*Phone', test_node, re.I)) != None:
            indicate_en += f",check and backup NV to phone."
            indicate_zh += f",检查并备份校准NV。"

    error_array.reverse()
    error_array2 =[]

    _start_flag = 1
    _regex_start = f'{test_node}.*start'
    _search_start = [x for x in error_array if re.search(_regex_start, x) != None]
    if len(_search_start) > 0:
        _start_flag =0

    for _error in error_array:
        if (_match := re.search(_regex_start, _error)) !=None:
            _start_flag = 1
            print(f"{test_node} start")
        elif (_match := re.search(f'{test_node}.*complete', _error)) !=None:            
            break                
        elif _start_flag == 1:
            if re.search('^={10,}', _error) == None: 
                error_array2.append(_error)

    _error_total = '\n'.join(error_array2)        
    indicate_en += f",'{_error_total}'"
    indicate_zh += f",'{_error_total}'"

    if (_match := re.search(r"QLIB_FTM_(\S+) API failed", _error_total, re.I)) != None:
        _api = _match.group(1)
        if _api.find('CFG_AND_EXEC_QSC_SWEEP') != -1:
            indicate_en += f",Segment config and power sweep execute fail."
            indicate_zh += f",FTM 配置segment及功率扫描执行失败."
        elif _api.find('RFCAL_PROTOBUFFER') != -1:
            indicate_en += f",Proto buffer format data transmission with no return."
            indicate_zh += f"，proto buffer格式数据传输无返回。"

    # 根据语言参数返回对应结果
    return [mean_en, indicate_en, suggest_en] if language.lower() =='en' else [mean_zh, indicate_zh, suggest_zh]

def general_communication_interrupt_failure_analysis(log_title_info, language='zh'):
    mean_en = indicate_en = suggest_en = ''
    mean_zh = indicate_zh = suggest_zh = ''

    fail_item = log_title_info.get('failMsg','Unknow')
    # test_name = log_title_info.get('test_name','Unknow')
    nextest_log = log_title_info.get('nextest_log','')
    #key_evaluate_line = log_title_info.get('fail_EvalAndLogResults_line','')
    fail_line_number = log_title_info.get('fail_EvalAndLogResults_line_number', -1)
    #track_id = log_title_info.get('trackID', '')

    mean_en = f'{fail_item}'
    mean_zh = f'{fail_item}'

    log_lines_list = read_universal_file(nextest_log)    
    
    dbcc_history_list =[]
    dbcc_name = ''
    i = fail_line_number
    connect_pass_number = -1
    while i >= 0:
        i -= 1
        _cur_line = log_lines_list[i]        
        if (_match := re.search(r"\tSocket connection '\d+\.\d+\.\d+\.\d+\:\d+' PASSED for dbcc name '(.+)'", _cur_line)) != None: 
            dbcc_name = _match.group(1)
            connect_pass_number = i 
            break

    if connect_pass_number == -1:
        return None
    
    i = connect_pass_number
    while i < fail_line_number:
        i += 1
        _cur_line = log_lines_list[i]        
        if _cur_line.find(f"{dbcc_name}") != -1:
            dbcc_history_list.append(_cur_line)
    
    if len(dbcc_history_list) == 0:
        return None
    
    _device_remove = []
    for line in dbcc_history_list:
        if line.endswith('RemoveListStatus <True>\n'):
            _device_remove.append('remove')
        elif line.find('Adding Interface') != -1:
            _device_remove.append('add')
    
    if len(set(_device_remove)) <= 1:
        if _device_remove[0] == 'remove':
            indicate_en = "Motorola Network device remove during the test,the communication interrupt cause the Fail."
            indicate_zh = "从后台设备监控进程信息看，Network设备掉线了，通信中断导致测试Fail."
            suggest_en = 'Recommended to retest first, if it passes, it can be confirmed as NTF. Track the occurrence probability of such issues and catch software logs for development analysis and processing.'
            suggest_zh = '建议先复测，如果PASS，可确定为误测，统计此类问题发生概率，抓软件log给研发分析处理。'
    else:
        indicate_en = "Motorola Network device remove and arrive again during the test,the communication interrupt cause the Fail."
        indicate_zh = "从后台设备监控进程信息看，Network设备消失后又重新枚举，通信中断导致测试Fail."
        suggest_en = 'Recommended to retest first, if it passes, it can be confirmed as NTF. Track the occurrence probability of such issues and catch software logs for development analysis and processing.'
        suggest_zh = '建议先复测，如果PASS，可确定为误测，统计此类问题发生概率，抓软件log给研发分析处理。'

    # 根据语言参数返回对应结果
    return [mean_en, indicate_en, suggest_en] if language.lower() =='en' else [mean_zh, indicate_zh, suggest_zh]

def general_motorola_tcmd_failure_analysis(log_title_info, language='zh'):
    mean_en = indicate_en = suggest_en = ''
    mean_zh = indicate_zh = suggest_zh = ''

    fail_item = log_title_info.get('failMsg','Unknow')
    test_name = log_title_info.get('test_name','Unknow')
    nextest_log = log_title_info.get('nextest_log','')
    #key_evaluate_line = log_title_info.get('fail_EvalAndLogResults_line','')
    fail_line_number = log_title_info.get('fail_EvalAndLogResults_line_number', -1)
    track_id = log_title_info.get('trackID', '')
    error_msg = log_title_info.get('error_msg', '')
    error_detail = log_title_info.get('error_detail', '')

    mean_en = f'{fail_item}'
    mean_zh = f'{fail_item}'

    indicate_en = f"{fail_item},"
    indicate_zh = f"{fail_item},"

    log_lines_list = read_universal_file(nextest_log)    
    # _index = log_lines_list.index(f'{key_evaluate_line}\n')

    _header = f'\t{test_name}\tHeader\tTest = {test_name}  |  '
    _footer = f'\t{test_name}\Footer\tTest = {test_name}  |  '
    
    regex_pattern = r"\t ERROR\t TestCommand\t\d{2}:\d{2}:\d{2}\.\d{7}\t(\S+)\t(\S+)::Error\tCommand error:"
    partial_log_list =[]
    i = fail_line_number
    while i >= 0:
        i -= 1
        _cur_line = log_lines_list[i]
        if _cur_line.find(_header) != -1:
            break
        elif re.search(regex_pattern, _cur_line, re.I) != None:
            partial_log_list.append(_cur_line)

    if len(partial_log_list) == 0:
        return None
    
    partial_log_list.reverse()
    _count = cmd_err_match_index = -1    
    for tcmd_error in partial_log_list:
        sub_index = tcmd_error.find('Command error:') + len('Command error:')
        _cmd_err = re.sub(r"[\s:]",'',tcmd_error[sub_index:])
        _err_msg = re.sub(r"[\s:]",'',error_msg)
        _count += 1
        if _err_msg.find(_cmd_err) != -1:
            cmd_err_match_index = _count
            break

    if cmd_err_match_index == -1:
        print('最终的Error信息和检索log内test command error不匹配！！！')    
    
    cmd_error_pattern = r"Test command failure:\n{1,}Details:\n{1,}Test command: (.*)\n{1,}Op code group: (.+)\n{1,}Op code: 0x(.+)\n{1,}Error code: (.+)\n{1,}Response code name: (.+)\n{1,}Response code: (.+)"
    if (_Match := re.search(cmd_error_pattern, error_msg, re.I)) !=None:
        command = _Match.group(1) 
        resp_code_name = _Match.group(5)
        if (_match := re.search(r"\nResponse ASCII error: (.+)", error_msg)) != None:
            _content = _match.group(1) 
            indicate_en = f"{_content},"
            indicate_zh = f"{_content}，"                   
            # suggest_en += f" DUT response '{_content}',"
            # suggest_zh += f"手机返回'{_content}'，"

        if error_msg.find("Message: Response fail bit is set.") != -1:                                                       
            suggest_en += f"'PassFailBit=Fail' indicate that maybe software do not support this TCMD, capture software logs and sent to the software engineer for analysis."
            suggest_zh += f"'PassFailBit=Fail'表示软件可能不支持此指令，需要抓软件log，发给软件工程师分析。" 
        elif resp_code_name == 'ReceiveDataFailed':
            if re.search(r"No (\S+) interface found on port #\d to (read data from|send data to).", error_msg) != None:
                suggest_en += f"TCMD executed failure, the device's USB port was disconnected during the testing process, please retest."
                suggest_zh += f"TCMD指令执行失败，找不到设备通信接口，测试过程中设备USB端口掉口，需要复测。"
            elif re.search(r"ReceiveData error = (.+)  \|  PNP error name = (.+); PNP error code = (\d+)", error_msg) != None:
                suggest_en += f"TCMD executed failure, the device's USB port was disconnected during the testing process, please retest."
                suggest_zh += f"TCMD指令执行失败，找不到设备通信接口，测试过程中设备USB端口掉口，需要复测。"
            elif (_match := re.search(r"ReceiveData error = (.+)  \|  PNP error code = (\d+)", error_msg)) != None:
                _error_msg = _match.group(1).rstrip('.')
                _error_code = _match.group(2)
                error_desc = socketError_detail_description(int(_error_code))
                indicate_en = f"{error_desc},"
                indicate_zh = f"{error_desc}，"    

                #### if error_desc != None and error_desc.find(_error_msg) != -1:  
                suggest_en += f"TCMD executed failure, TCPIP socket communication exception occured, please retest."
                suggest_zh += f"TCMD指令执行失败，TCPIP Socket通信异常，请复测。"

    # 根据语言参数返回对应结果
    return [mean_en, indicate_en, suggest_en] if language.lower() =='en' else [mean_zh, indicate_zh, suggest_zh]

def socketError_detail_description(err_code):
    match err_code:
        case 6:   ### WSA_INVALID_HANDLE
            return "Specified event object handle is invalid.An application attempts to use an event object, but the specified handle is not valid.";
        case 8:   ### WSA_NOT_ENOUGH_MEMORY
            return "Insufficient memory available.An application used a Windows Sockets function that directly maps to a Windows function. The Windows function is indicating a lack of required memory resources."
        case 87:   ### WSA_INVALID_PARAMETER
            return "One or more parameters are invalid.An application used a Windows Sockets function which directly maps to a Windows function. The Windows function is indicating a problem with one or more parameters."
        case 995:   ### WSA_OPERATION_ABORTED
            return "Overlapped operation aborted.An overlapped operation was canceled due to the closure of the socket, or the execution of the SIO_FLUSH command in WSAIoctl."
        case 996:   ### WSA_IO_INCOMPLETE
            return "Overlapped I/O event object not in signaled state.The application has tried to determine the status of an overlapped operation which is not yet completed.Applications that use WSAGetOverlappedResult(with the fWait flag set to FALSE) in a polling mode to determine when an overlapped operation has completed, get this error code until the operation is complete."
        case 997:   ### WSA_IO_PENDING
            return "Overlapped operations will complete later.The application has initiated an overlapped operation that cannot be completed immediately. A completion indication will be given later when the operation has been completed."
        case 10004:   ### WSAEINTR
            return "Interrupted function call.A blocking operation was interrupted by a call to WSACancelBlockingCall."            
        case 10009:   ### WSAEBADF
            return "File handle is not valid.The file handle supplied is not valid."
        case 10013:   ### WSAEACCES
            return "Permission denied.An attempt was made to access a socket in a way forbidden by its access permissions.An example is using a broadcast address for sendto without broadcast permission being set using setsockopt(SO_BROADCAST).Another possible reason for the WSAEACCES error is that when the bind function is called (on Windows NT 4.0 with SP4 and later), another application, service, or kernel mode driver is bound to the same address with exclusive access. Such exclusive access is a new feature of Windows NT 4.0 with SP4 and later, and is implemented by using the SO_EXCLUSIVEADDRUSE option."
        case 10014:   ### WSAEFAULT
            return "Bad address.The system detected an invalid pointer address in attempting to use a pointer argument of a call.This error occurs if an application passes an invalid pointer value, or if the length of the buffer is too small. For instance, if the length of an argument, which is a sockaddr structure, is smaller than the sizeof(sockaddr)."
        case 10022:   ### WSAEINVAL
            return "Invalid argument.Some invalid argument was supplied(for example, specifying an invalid level to the setsockopt function).In some instances, it also refers to the current state of the socket—for instance, calling accept on a socket that is not listening."
        case 10024:   ### WSAEMFILE
            return "Too many open files.Too many open sockets. Each implementation may have a maximum number of socket handles available, either globally, per process, or per thread."
        case 10035:   ### WSAEWOULDBLOCK
            return "Resource temporarily unavailable.This error is returned from operations on nonblocking sockets that cannot be completed immediately, for example recv when no data is queued to be read from the socket.It is a nonfatal error, and the operation should be retried later.It is normal for WSAEWOULDBLOCK to be reported as the result from calling connect on a nonblocking SOCK_STREAM socket, since some time must elapse for the connection to be established."
        case 10036:   ### WSAEINPROGRESS
            return "Operation now in progress.A blocking operation is currently executing. Windows Sockets only allows a single blocking operation—per - task or thread—to be outstanding, and if any other function call is made (whether or not it references that or any other socket) the function fails with the WSAEINPROGRESS error."
        case 10037:   ### WSAEALREADY
            return "Operation already in progress.An operation was attempted on a nonblocking socket with an operation already in progress—that is, calling connect a second time on a nonblocking socket that is already connecting, or canceling an asynchronous request(WSAAsyncGetXbyY) that has already been canceled or completed."
        case 10038:   ### WSAENOTSOCK
            return "Socket operation on nonsocket.An operation was attempted on something that is not a socket.Either the socket handle parameter did not reference a valid socket, or for select, a member of an fd_set was not valid."
        case 10039:   ### WSAEDESTADDRREQ
            return "Destination address required.A required address was omitted from an operation on a socket.For example, this error is returned if sendto is called with the remote address of ADDR_ANY."
        case 10040:   ### WSAEMSGSIZE
            return "Message too long.A message sent on a datagram socket was larger than the internal message buffer or some other network limit, or the buffer used to receive a datagram was smaller than the datagram itself."
        case 10041:   ### WSAEPROTOTYPE
            return "Protocol wrong type for socket.A protocol was specified in the socket function call that does not support the semantics of the socket type requested.For example, the ARPA Internet UDP protocol cannot be specified with a socket type of SOCK_STREAM."
        case 10042:   ### WSAENOPROTOOPT
            return "Bad protocol option.An unknown, invalid or unsupported option or level was specified in a getsockopt or setsockopt call."
        case 10043:   ### WSAEPROTONOSUPPORT
            return "Protocol not supported.The requested protocol has not been configured into the system, or no implementation for it exists. For example, a socket call requests a SOCK_DGRAM socket, but specifies a stream protocol."
        case 10044:   ### WSAESOCKTNOSUPPORT
            return "Socket type not supported.The support for the specified socket type does not exist in this address family.For example, the optional type SOCK_RAW might be selected in a socket call, and the implementation does not support SOCK_RAW sockets at all."
        case 10045:   ### WSAEOPNOTSUPP
            return "Operation not supported.The attempted operation is not supported for the type of object referenced.Usually this occurs when a socket descriptor to a socket that cannot support this operation is trying to accept a connection on a datagram socket."
        case 10046:   ### WSAEPFNOSUPPORT
            return "Protocol family not supported.The protocol family has not been configured into the system or no implementation for it exists. This message has a slightly different meaning from WSAEAFNOSUPPORT.However, it is interchangeable in most cases, and all Windows Sockets functions that return one of these messages also specify WSAEAFNOSUPPORT."
        case 10047:   ### WSAEAFNOSUPPORT
            return "Address family not supported by protocol family.An address incompatible with the requested protocol was used.All sockets are created with an associated address family(that is, AF_INET for Internet Protocols) and a generic protocol type(that is, SOCK_STREAM).This error is returned if an incorrect protocol is explicitly requested in the socket call, or if an address of the wrong family is used for a socket, for example, in sendto."
        case 10048:   ### WSAEADDRINUSE
            return "Address already in use.Typically, only one usage of each socket address(protocol / IP address / port) is permitted.This error occurs if an application attempts to bind a socket to an IP address/ port that has already been used for an existing socket, or a socket that was not closed properly, or one that is still in the process of closing.For server applications that need to bind multiple sockets to the same port number, consider using setsockopt(SO_REUSEADDR).Client applications usually need not call bind at all—connect chooses an unused port automatically. When bind is called with a wildcard address(involving ADDR_ANY), a WSAEADDRINUSE error could be delayed until the specific address is committed.This could happen with a call to another function later, including connect, listen, WSAConnect, or WSAJoinLeaf."
        case 10049:   ### WSAEADDRNOTAVAIL
            return "Cannot assign requested address.The requested address is not valid in its context. This normally results from an attempt to bind to an address that is not valid for the local computer.This can also result from connect, sendto, WSAConnect, WSAJoinLeaf, or WSASendTo when the remote address or port is not valid for a remote computer(for example, address or port 0)."
        case 10050:   ### WSAENETDOWN
            return "Network is down.A socket operation encountered a dead network.This could indicate a serious failure of the network system(that is, the protocol stack that the Windows Sockets DLL runs over), the network interface, or the local network itself."
        case 10051:   ### WSAENETUNREACH
            return "Network is unreachable.A socket operation was attempted to an unreachable network.This usually means the local software knows no route to reach the remote host."
        case 10052:   ### WSAENETRESET
            return "Network dropped connection on reset.The connection has been broken due to keep-alive activity detecting a failure while the operation was in progress.It can also be returned by setsockopt if an attempt is made to set SO_KEEPALIVE on a connection that has already failed."
        case 10053:   ### WSAECONNABORTED
            return "Software caused connection abort.An established connection was aborted by the software in your host computer, possibly due to a data transmission time -out or protocol error."
        case 10054:   ### WSAECONNRESET
            return "Connection reset by peer.An existing connection was forcibly closed by the remote host. This normally results if the peer application on the remote host is suddenly stopped, the host is rebooted, the host or remote network interface is disabled, or the remote host uses a hard close(see setsockopt for more information on the SO_LINGER option on the remote socket). This error may also result if a connection was broken due to keep-alive activity detecting a failure while one or more operations are in progress.Operations that were in progress fail with WSAENETRESET.Subsequent operations fail with WSAECONNRESET."
        case 10055:   ### WSAENOBUFS
            return "No buffer space available.An operation on a socket could not be performed because the system lacked sufficient buffer space or because a queue was full."
        case 10056:   ### WSAEISCONN
            return "Socket is already connected.A connect request was made on an already-connected socket.Some implementations also return this error if sendto is called on a connected SOCK_DGRAM socket(for SOCK_STREAM sockets, the to parameter in sendto is ignored) although other implementations treat this as a legal occurrence."
        case 10057:   ### WSAENOTCONN
            return "Socket is not connected.A request to send or receive data was disallowed because the socket is not connected and(when sending on a datagram socket using sendto) no address was supplied. Any other type of operation might also return this error—for example, setsockopt setting SO_KEEPALIVE if the connection has been reset."
        case 10058:   ### WSAESHUTDOWN
            return "Cannot send after socket shutdown.A request to send or receive data was disallowed because the socket had already been shut down in that direction with a previous shutdown call.By calling shutdown a partial close of a socket is requested, which is a signal that sending or receiving, or both have been discontinued."
        case 10059:   ### WSAETOOMANYREFS
            return "Too many references.Too many references to some kernel object."            
        case 10060:   ### WSAETIMEDOUT
            return "Connection timed out.A connection attempt failed because the connected party did not properly respond after a period of time, or the established connection failed because the connected host has failed to respond."
        case 10061:   ### WSAECONNREFUSED
            return "Connection refused.No connection could be made because the target computer actively refused it. This usually results from trying to connect to a service that is inactive on the foreign host—that is, one with no server application running."
        case 10062:   ### WSAELOOP
            return "Cannot translate name.Cannot translate a name."            
        case 10063:   ### WSAENAMETOOLONG
            return "Name too long.A name component or a name was too long."            
        case 10064:   ### WSAEHOSTDOWN
            return "Host is down.A socket operation failed because the destination host is down.A socket operation encountered a dead host.Networking activity on the local host has not been initiated. These conditions are more likely to be indicated by the error WSAETIMEDOUT."
        case 10065:   ### WSAEHOSTUNREACH
            return "No route to host.A socket operation was attempted to an unreachable host.See WSAENETUNREACH."            
        case 10066:   ### WSAENOTEMPTY
            return "Directory not empty.Cannot remove a directory that is not empty."            
        case 10067:   ### WSAEPROCLIM
            return "Too many processes.A Windows Sockets implementation may have a limit on the number of applications that can use it simultaneously. WSAStartup may fail with this error if the limit has been reached."
        case 10068:   ### WSAEUSERS
            return "User quota exceeded.Ran out of user quota."            
        case 10069:   ### WSAEDQUOT
            return "Disk quota exceeded.Ran out of disk quota."            
        case 10070:   ### WSAESTALE
            return "Stale file handle reference.The file handle reference is no longer available."            
        case 10071:   ### WSAEREMOTE
            return "Item is remote.The item is not available locally."            
        case 10091:   ### WSASYSNOTREADY
            return """Network subsystem is unavailable.
                        This error is returned by WSAStartup if the Windows Sockets implementation cannot function at this time because the underlying system it uses to provide network services is currently unavailable. Users should check:
                        That the appropriate Windows Sockets DLL file is in the current path.
                        That they are not trying to use more than one Windows Sockets implementation simultaneously. If there is more than one Winsock DLL on your system, be sure the first one in the path is appropriate for the network subsystem currently loaded.
                        The Windows Sockets implementation documentation to be sure all necessary components are currently installed and configured correctly."
            """
        case 10092:   ### WSAVERNOTSUPPORTED
            return """Winsock.dll version out of range.
                            The current Windows Sockets implementation does not support the Windows Sockets specification version requested by the application. Check that no old Windows Sockets DLL files are being accessed."""
        case 10093:   ### WSANOTINITIALISED
            return """Successful WSAStartup not yet performed.
                            Either the application has not called WSAStartup or WSAStartup failed. The application may be accessing a socket that the current active task does not own (that is, trying to share a socket between tasks), or WSACleanup has been called too many times."""
        case 10101:   ### WSAEDISCON
            return """Graceful shutdown in progress.
                        Returned by WSARecv and WSARecvFrom to indicate that the remote party has initiated a graceful shutdown sequence."""
        case 10102:   ### WSAENOMORE
            return "No more results.No more results can be returned by the WSALookupServiceNext function."
        case 10103:   ### WSAECANCELLED
            return """Call has been canceled.
                            A call to the WSALookupServiceEnd function was made while this call was still processing. The call has been canceled."""
        case 10104:   ### WSAEINVALIDPROCTABLE
            return """Procedure call table is invalid.
                            The service provider procedure call table is invalid. A service provider returned a bogus procedure table to Ws2_32.dll. This is usually caused by one or more of the function pointers being NULL."""
        case 10105:   ### WSAEINVALIDPROVIDER
            return """Service provider is invalid.
                            The requested service provider is invalid. This error is returned by the WSCGetProviderInfo and WSCGetProviderInfo32 functions if the protocol entry specified could not be found. This error is also returned if the service provider returned a version number other than 2.0."""
        case 10106:   ### WSAEPROVIDERFAILEDINIT
            return """Service provider failed to initialize.
                            The requested service provider could not be loaded or initialized. This error is returned if either a service provider's DLL could not be loaded (LoadLibrary failed) or the provider's WSPStartup or NSPStartup function failed."""
        case 10107:   ### WSASYSCALLFAILURE
            return """System call failure.
                            A system call that should never fail has failed. This is a generic error code, returned under various conditions.
                            Returned when a system call that should never fail does fail. For example, if a call to WaitForMultipleEvents fails or one of the registry functions fails trying to manipulate the protocol/namespace catalogs.
                            Returned when a provider does not return SUCCESS and does not provide an extended error code. Can indicate a service provider implementation error."""
        case 10108:   ### WSASERVICE_NOT_FOUND
            return """Service not found.
                            No such service is known. The service cannot be found in the specified name space."""            
        case 10109:   ### WSATYPE_NOT_FOUND
            return "Class type not found. The specified class was not found."           
        case 10110:   ### WSA_E_NO_MORE
            return "No more results.No more results can be returned by the WSALookupServiceNext function."           
        case 10111:   ### WSA_E_CANCELLED
            return """Call was canceled.
                            A call to the WSALookupServiceEnd function was made while this call was still processing. The call has been canceled."""
        case 10112:   ### WSAEREFUSED
            return "Database query was refused.A database query failed because it was actively refused."          
        case 11001:   ### WSAHOST_NOT_FOUND
            return """Host not found.
                            No such host is known. The name is not an official host name or alias, or it cannot be found in the database(s) being queried. This error may also be returned for protocol and service queries, and means that the specified name could not be found in the relevant database."""
        case 11002:   ### WSATRY_AGAIN
            return """Nonauthoritative host not found.
                            This is usually a temporary error during host name resolution and means that the local server did not receive a response from an authoritative server. A retry at some time later may be successful."""
        case 11003:   ### WSANO_RECOVERY
            return """This is a nonrecoverable error.
                            This indicates that some sort of nonrecoverable error occurred during a database lookup. This may be because the database files (for example, BSD-compatible HOSTS, SERVICES, or PROTOCOLS files) could not be found, or a DNS request was returned by the server with a severe error."""
        case 11004:   ### WSANO_DATA
            return """Valid name, no data record of requested type.
                            The requested name is valid and was found in the database, but it does not have the correct associated data being resolved for. The usual example for this is a host name-to-address translation attempt (using gethostbyname or WSAAsyncGetHostByName) which uses the DNS (Domain Name Server). An MX record is returned but no A record—indicating the host itself exists, but is not directly reachable."""
        case 11005:   ### WSA_QOS_RECEIVERS
            return """QoS receivers.At least one QoS reserve has arrived."""            
        case 11006:   ### WSA_QOS_SENDERS
            return """QoS senders.At least one QoS send path has arrived."""            
        case 11007:   ### WSA_QOS_NO_SENDERS
            return "No QoS senders.There are no QoS senders."            
        case 11008:   ### WSA_QOS_NO_RECEIVERS
            return "QoS no receivers.There are no QoS receivers."            
        case 11009:   ### WSA_QOS_REQUEST_CONFIRMED
            return "QoS request confirmed.The QoS reserve request has been confirmed."            
        case 11010:   ### WSA_QOS_ADMISSION_FAILURE
            return "QoS admission error.A QoS error occurred due to lack of resources."            
        case 11011:   ### WSA_QOS_POLICY_FAILURE
            return "QoS policy failure.The QoS request was rejected because the policy system couldn't allocate the requested resource within the existing policy."
        case 11012:   ### WSA_QOS_BAD_STYLE
            return "QoS bad style.An unknown or conflicting QoS style was encountered."            
        case 11013:   ### WSA_QOS_BAD_OBJECT
            return "QoS bad object.A problem was encountered with some part of the filterspec or the provider-specific buffer in general."
        case 11014:   ### WSA_QOS_TRAFFIC_CTRL_ERROR
            return """QoS traffic control error.
                            An error with the underlying traffic control (TC) API as the generic QoS request was converted for local enforcement by the TC API. This could be due to an out of memory error or to an internal QoS provider error."""
        case 11015:   ### WSA_QOS_GENERIC_ERROR
            return "QoS generic error.A general QoS error."            
        case 11016:   ### WSA_QOS_ESERVICETYPE
            return "QoS service type error.An invalid or unrecognized service type was found in the QoS flowspec."            
        case 11017:   ### WSA_QOS_EFLOWSPEC
            return "QoS flowspec error.An invalid or inconsistent flowspec was found in the QOS structure."            
        case 11018:   ### WSA_QOS_EPROVSPECBUF
            return "Invalid QoS provider buffer.An invalid QoS provider-specific buffer."            
        case 11019:   ### WSA_QOS_EFILTERSTYLE
            return "Invalid QoS filter style.An invalid QoS filter style was used."            
        case 11020:   ### WSA_QOS_EFILTERTYPE
            return "Invalid QoS filter type.An invalid QoS filter type was used."            
        case 11021:   ### WSA_QOS_EFILTERCOUNT
            return "Incorrect QoS filter count.An incorrect number of QoS FILTERSPECs were specified in the FLOWDESCRIPTOR."            
        case 11022:   ### WSA_QOS_EOBJLENGTH
            return "Invalid QoS object length.An object with an invalid ObjectLength field was specified in the QoS provider-specific buffer."            
        case 11023:   ### WSA_QOS_EFLOWCOUNT
            return "Incorrect QoS flow count.An incorrect number of flow descriptors was specified in the QoS structure."            
        case 11024:   ### WSA_QOS_EUNKOWNPSOBJ
            return "Unrecognized QoS object.An unrecognized object was found in the QoS provider-specific buffer."            
        case 11025:   ### WSA_QOS_EPOLICYOBJ
            return "Invalid QoS policy object.An invalid policy object was found in the QoS provider-specific buffer."            
        case 11026:   ### WSA_QOS_EFLOWDESC
            return "Invalid QoS flow descriptor.An invalid QoS flow descriptor was found in the flow descriptor list."            
        case 11027:   ### WSA_QOS_EPSFLOWSPEC
            return "Invalid QoS provider-specific flowspec.An invalid or inconsistent flowspec was found in the QoS provider-specific buffer."            
        case 11028:   ### WSA_QOS_EPSFILTERSPEC
            return "Invalid QoS provider-specific filterspec.An invalid FILTERSPEC was found in the QoS provider-specific buffer."            
        case 11029:   ### WSA_QOS_ESDMODEOBJ
            return "Invalid QoS shape discard mode object.An invalid shape discard mode object was found in the QoS provider-specific buffer."            
        case 11030:   ### WSA_QOS_ESHAPERATEOBJ
            return "Invalid QoS shaping rate object.An invalid shaping rate object was found in the QoS provider-specific buffer."            
        case 11031:   ### WSA_QOS_RESERVED_PETYPE
            return "Reserved policy QoS element type.A reserved policy element was found in the QoS provider-specific buffer."        
    return None

def measure_process_failure_analysis(log_title_info, language='zh'):
    mean_en = indicate_en = suggest_en = ''
    mean_zh = indicate_zh = suggest_zh = ''

    fail_item = log_title_info.get('failMsg','Unknow')
    test_name = log_title_info.get('test_name','Unknow')
    nextest_log = log_title_info.get('nextest_log','')
    #key_evaluate_line = log_title_info.get('fail_EvalAndLogResults_line','')
    fail_line_number = log_title_info.get('fail_EvalAndLogResults_line_number', -1)
    track_id = log_title_info.get('trackID', '')
    error_msg = log_title_info.get('error_msg', '')
    error_detail = log_title_info.get('error_detail', '')

    mean_en = f'{fail_item}'
    mean_zh = f'{fail_item}'

    indicate_en = f"{fail_item},"
    indicate_zh = f"{fail_item},"

    log_lines_list = read_universal_file(nextest_log)    
    # _index = log_lines_list.index(f'{key_evaluate_line}\n')

    _header = f'\t{test_name}\tHeader\tTest = {test_name}  |  '
    _footer = f'\t{test_name}\Footer\tTest = {test_name}  |  '
    
    #regex_pattern = r"\tMeasure Process\t(\S+) measure process is complete because measurement criteria has been satisifed."
    regex_pattern1 = r"\tMeasure Process\t(\S+) measure process criteria has NOT been satisfied because readings are unstable."
    regex_pattern2 = r"\tMeasure Process\t(\S+) measure process criteria has NOT been satisfied because readings are out of spec."
    regex_pattern3 = r"\tMeasure Process\t(\S+) measure process criteria has NOT been satisfied because readings are unstable because they are monotonic (ramping)."
    
    # keys = []
    # inventory = {key: [] for key in keys}
    _readings_list = []
    _measure_process =''
    i = fail_line_number
    while i >= 0:
        i -= 1
        _cur_line = log_lines_list[i]
        if _cur_line.find(_header) != -1:
            break
        elif (_match := re.search(regex_pattern1, _cur_line, re.I)) != None:
            _measure_process = _match.group(1)
            indicate_en = f"{_match.group(1)} measurement readings are unstable,The measurement result is invalid."
            indicate_zh = f"{_match.group(1)}测试读值不稳定,测量结果无效。"
            suggest_en += f"Recheck first; if the tests frequently reappear, you need to confirm with the development engineer whether the test solution is reasonable."
            suggest_zh += f"先复测，如果测试频繁浮现，需和研发工程师确认测试方案是否合理。"           
        elif (_match := re.search(regex_pattern2, _cur_line, re.I)) != None:
            _measure_process = _match.group(1)
            indicate_en = f"{_match.group(1)} measurement result are out of spec."
            indicate_zh = f"{_match.group(1)}测试结果超过了门限。" 
            suggest_en += f"Retest to determine if the results from multiple tests are stable. If the test results are stable, check with the development engineer whether the set thresholds are reasonable."
            suggest_zh += f"先复测，确定多次测试结果是否稳定，如果测试结果稳定，需和研发工程师检查设置的门限是否合理。"           
        elif (_match := re.search(regex_pattern3, _cur_line, re.I)) != None:
            _measure_process = _match.group(1)
            indicate_en = f"{_match.group(1)} test reading continuously rises or falls, not meeting the monotonicity requirements, resulting in an invalid test outcome."
            indicate_zh = f"{_match.group(1)}测试读值持续上升或下降，不符合单调性要求，测试结果无效。" 
            suggest_en += f"Recheck first; if the tests frequently reappear, you need to confirm with the development engineer whether the test solution is reasonable."
            suggest_zh += f"先复测，如果测试频繁浮现，需和研发工程师确认测试方案是否合理。"
        elif (_match := re.search("\tMeasure Process\t(.+) Reading \d+: (-*\d+\.*\d*)", _cur_line)) != None:
            if _measure_process == _match.group(1):
                _reading = _match.group(2)
                try:
                    _readings_list.append(int(_reading))
                except ValueError:
                    try:
                        _readings_list.append(float(_reading))
                    except ValueError:
                        print('convert Value Error')

    _readings_list.reverse() 

    if len(suggest_en) == 0:
        return None
    
    # 根据语言参数返回对应结果
    return [mean_en, indicate_en, suggest_en] if language.lower() =='en' else [mean_zh, indicate_zh, suggest_zh]