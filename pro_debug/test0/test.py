import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def check_packages_installed():
    print(f"NumPy版本: {np.__version__}")
    print(f"Pandas版本: {pd.__version__}")
    print("所有包安装成功！")


import re

processed_line = """HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::Start --------------------------------------------------------------------------------------------------------------------------------------------------------------------------
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::Info Port #1 | Send timeout = 5000msec | Receive timeout = 11000msec
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::SendHeader C/R=0x00 | SeqTag=0x12 | OpCode=0x0039 | RR=0x00 | Length=2
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::Send '0012003900000000000000021202'
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::Receive '821200390006000000000006056D756D6261'
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::ResponseHeader Req/Rsp=CommandResponse | FormatVersion=0 | PassFailBit=Pass | DataIndicator=DataToFollow | RespType=solicited | SeqTag=0x12 | OpCode=0x0039 | RespCode=GenericResponse | DataLength=6
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::PropertyValues ActiveInterface=NETWORK | UsbPortNumber=1 | OpCode=0039 | OpCodeGroup=0 | TestCommandDataStringHex=056D756D6261
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::Timer Total time to execute = 2 msec
HW_VERSION_PRODUCT_NAME_2_PORTO testcommandclass::End --------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

# 修正正则：匹配 ::Start 后接任意字符（包括换行）直到 ::End 及后续内容
processed_line = re.sub(
    r'::Start .*?::End .*?(?=\n|$)',
    lambda m: f'<span style="color:red;">{m.group()}</span>',
    processed_line,
    flags=re.DOTALL
)

print(processed_line)
