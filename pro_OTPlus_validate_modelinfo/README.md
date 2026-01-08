<<<<<<< HEAD
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
=======
# AI-Python-Project
“A project for developing AI tools based on personal ideas, mainly focusing on video - related AI training.”



### Git 操作指令清单（含 SSH 创建 + 首次 / 后续推送）

#### 一、前置：创建 SSH 密钥（首次必做）

1. 检查本地 SSH 密钥：`ls ~/.ssh`（有 id_ed25519/id_rsa 则跳过创建）
2. 生成 SSH 密钥：`ssh-keygen -t ed25519 -C "你的GitHub邮箱"`（回车默认路径，可留空密码）
3. 复制公钥：`cat ~/.ssh/id_ed25519.pub`（全选复制，后续添加到 GitHub）
4. 验证 SSH 连接（可选）：`ssh -T git@github.com`（出现用户名提示则成功）

#### 二、首次初始化 & 上传首个项目

1. 进入项目上级目录：`cd /d/D/ProgramData/projects/pro_python`（替换实际路径）

2. 初始化 Git 仓库：`git init`

3. 配置提交身份：

   - `git config --global user.name "你的GitHub用户名"`
   - `git config --global user.email "你的GitHub邮箱"`

   

4. 关联远程仓库（SSH）：`git remote add origin git@github.com:xiejun4/AI-Python-Project.git`

5. 配置 Git LFS（处理大文件）：

   - `git lfs install`
   - `git lfs track "*.exe"` `git lfs track "*.zip"`（按需加.tar/.rar 等）
   - `git add .gitattributes`

   

6. 添加首个项目到暂存区：`git add "pro_YOLO-Real-Time Screen Analysis via ADB/"`

7. 提交变更：`git commit -m "添加首个YOLO项目"`（身份异常则加：`git commit --amend --reset-author`）

8. 拉取远程内容合并：`git pull origin main --allow-unrelated-histories`

9. 推送至 GitHub：`git push origin main`

#### 三、推送后续项目（复用环境）

1. 进入项目上级目录：`cd /d/D/ProgramData/projects/pro_python`
2. 添加新项目到暂存区：`git add "pro_YOLO-Annotation-and-Training/"`
3. 提交变更：`git commit -m "添加第二个YOLO项目"`
4. 推送至 GitHub：`git push origin main`

#### 四、常见异常修复

1. 分支名不匹配：`git branch -m master main`（本地 master 改 main）
2. 强制推送（谨慎）：`git push origin main --force`（仅确认覆盖远程时用）
3. SSH 验证失败：重新执行`cat ~/.ssh/id_ed25519.pub`，将公钥添加到 GitHub「Settings→SSH and GPG keys」
4. 网络连接失败：`ipconfig /flushdns`（刷新 DNS）或切换手机热点
5. Vim 编辑器退出：按`Esc`→输入`:wq`→按`Enter`





## 更新远程仓库已存在的.gitignore内容，是否直接提交，然后push到远程即可。



Qwen3-Max

是的！✅ **更新 `.gitignore` 后，只需正常提交（commit）并推送（push）到远程仓库即可**，操作非常简单。

- 修改它 → `git add` → `git commit` → `git push`，流程完全一致。

------

### ✅ 正确步骤（三步走）

```
1# 1. 确保你已修改并保存了 .gitignore 文件
2
3# 2. 将更改加入暂存区
4git add .gitignore
5
6# 3. 提交更改
7git commit -m "Update .gitignore to ignore additional files"
8
9# 4. 推送到远程仓库（如 GitHub）
10git push origin main
```
>>>>>>> 613e4e4740fff78c0e67a167ada1641c8d64a8f9
