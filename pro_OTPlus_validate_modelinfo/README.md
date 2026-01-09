# 以下是 D:\PythonProject\pro_python\pro_debug\test6 目录下的文件结构：
test6/
├── ModelInfoFile_Beryl.xml        # 待验证的 XML 文件
├── README.md                      # 项目说明文件
├── README_node.md                 # Node.js 相关说明文件
├── TestModelInfo.xml              # 测试用 XML 文件
├── package-lock.json              # npm 依赖锁定文件
├── package.json                   # npm 项目配置文件
├── test_frontend.html             # 浏览器端测试页面
├── test_frontend_logic.js         # Node.js 测试脚本
├── validate_modelinfo.html        # 原始 HTML 验证工具
├── validate_modelinfo.py          # 原始 Python 验证脚本
├── validate_modelinfo_backend.py  # Python 后端验证脚本
└── validate_modelinfo_frontend.html  # HTML 前端验证工具



# 标题：ModelInfo.xml配置规则说明
# 一、例子

    BT4G
        射频基座编号   功分器端口号 + 仪表RF-IO（主/分集）
        Connector 1 -> UUT_RF_CONN1_TO_TESTSET_MAIN_RF
        Connector 2 -> UUT_RF_CONN8_TO_TESTSET_MAIN_RF
        Connector 6 -> UUT_RF_CONN6_TO_TESTSET_MAIN_RF
        Connector 7 -> UUT_RF_CONN7_TO_TESTSET_MAIN_RF
        Connector 4 -> UUT_RF_CONN2_TO_TESTSET_ALT1_RF
        Connector 5 -> UUT_RF_CONN5_TO_TESTSET_ALT1_RF
        Connector 9 -> UUT_RF_CONN9_TO_TESTSET_ALT1_RF
        Connector 8 -> UUT_RF_CONN10_TO_TESTSET_ALT1_RF

    BT5G
        Connector 1 -> UUT_RF_CONN1_TO_TESTSET_MAIN_RF
        Connector 2 -> UUT_RF_CONN8_TO_TESTSET_MAIN_RF
        Connector 6 -> UUT_RF_CONN6_TO_TESTSET_MAIN_RF
        Connector 7 -> UUT_RF_CONN7_TO_TESTSET_MAIN_RF
    WIFI
        Connector 4 -> UUT_RF_CONN2_TO_TESTSET_ALT1_RF
        Connector 5 -> UUT_RF_CONN5_TO_TESTSET_ALT1_RF
        Connector 9 -> UUT_RF_CONN9_TO_TESTSET_ALT1_RF
        Connector 8 -> UUT_RF_CONN10_TO_TESTSET_ALT1_RF

# 二、规则说明

# 1.功分器端口号 + 仪表RF-IO（主/分集）对应关系：
左边：测试仪表上的RF-IO口
右边：的功分器端口，是moto配置约定俗成的ALT1_RF = 2,5,9,10 = "RF_IO_2"
MAIN_RF = 1,3,4，6,7,8,11，12,13,14,15 = "RF_IO_1"

# 2.modelFile.xls文件内容说明：
左边：测试Band
右边：主板上的射频通路
N78 
N3500 Tx/Rx 		device_path = 0
N3500 RxDiv 		device_path = 1
N3500 Tx/RxMIMO1	device_path = 2 
N3500 RxMIMO2	    device_path = 3

# 标题：VS Code 代码折叠 / 展开快捷键
# 一、核心：VS Code（最可能的目标编辑器）代码折叠 / 展开快捷键
# VS Code 的代码折叠快捷键分 Windows/Linux 和 Mac 两套，以下是最常用的组合：
操作场景	Windows / Linux 快捷键	Mac 快捷键	说明
折叠当前代码块	Ctrl + Shift + [	Cmd + Shift + [	折叠光标所在的函数 / 类 / 区块
展开当前代码块	Ctrl + Shift + ]	Cmd + Shift + ]	展开光标所在的折叠区块
折叠所有代码块	Ctrl + K + Ctrl + 0	Cmd + K + Cmd + 0	0 是数字键，折叠全部层级
展开所有代码块	Ctrl + K + Ctrl + J	Cmd + K + Cmd + J	展开所有折叠的代码
折叠指定层级（如层级 1）	Ctrl + K + Ctrl + 1	Cmd + K + Cmd + 1	1/2/3… 对应代码嵌套层级
折叠选中的代码（手动）	Ctrl + K + Ctrl + 8	Cmd + K + Cmd + 8	先选中代码，再按此组

# 标题：xx项目结构说明
# 1. 纯python脚本
validate_modelinfo.py ： 验证ModelInfo.xml配置文件是否符合规则的纯python脚本。
# 2. html页面
validate_modelinfo.html ： 验证ModelInfo.xml配置文件是否符合规则的html页面。
# 3. 前后端交互
validate_modelinfo.html 页面通过调用 
validate_modelinfo.py 脚本实现前后端交互。
