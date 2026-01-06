import os

from functions import bt_analysis

# import bt_analysis
    
if __name__ == "__main__":
    #compress_path_zip(path)
    #decompress_path_zip(path)    
    path = r"D:\PythonProject\pro_PathFinder\uploads\NexTestLogs_Boardtst_FUJI25_JAPAN_Boardtst_Left_WHFE06B-BT15B_Failed_T83_N79_ULF4702.83M_CID10_RUT393727_CKG3_CP-QPSK_BW40_30K_RB106@0_PWR20_PwrS0_FE140_FEL15_TxPower_NF0M110216_2025-07-10_T13-38-02_0.log_zip"
    #log_info = bt_analysis.log_file_name_parse(path)
    if os.path.exists(path):
        json_str = bt_analysis.process_log_file(path)
        print(json_str)
    
    