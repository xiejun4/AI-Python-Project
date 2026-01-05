# -------------------------------------------------------------------------
# 2025-12-28
# 目的：使用 adbutils 库来模拟adb shell命令，跟手机交互。
# 实现：
  ### 方案三：绕过 `M2Crypto` —— 改用其他 ADB 库

  你真正需要的是 **ADB 功能**，而不是 `M2Crypto`。`adb` 
  这个包（[pypi: adb](https://pypi.org/project/adb/)）
  是一个较老的库，依赖 `M2Crypto` 做 SSL（其实 ADB 协议本身不需要它！）。

  #### 推荐替代方案：
  0. **`adbutils`**（更现代，支持 auth）  
    ```bash
    pip install adbutils
    ```
  1. **`pure-python-adb`**（纯 Python，无 C 依赖）  
    ```bash
    pip install pure-python-adb
    ```
    GitHub: https://github.com/Swind/pure-python-adb

  2. **`adb-shell`**（更现代，支持 auth）  
   ```bash
   pip install adb-shell
   ```

  > 这3个库都不依赖 `M2Crypto`，在 Windows + Python 3.13 上也能正常工作。

  ---

  ## 🔚 总结建议
  | 方案 | 可行性 | 推荐度 |
  |------|--------|--------|
  | 使用 `adbutils` 或 `pure-python-adb` 或 `adb-shell` | ⭐⭐⭐⭐⭐ | ✅✅✅ 强烈推荐 |

# -------------------------------------------------------------------------
# 2025-12-28
### platform-tools-latest-windows.zip
### 一、pure-python-adb 是什么？
`pure-python-adb`（常简称为 `ppadb`）是一个**纯 Python 实现的 Android Debug Bridge (ADB) 协议库**，无需依赖系统自带的 ADB 二进制可执行文件（如 adb.exe/adb），完全通过 Python 代码封装 ADB 协议的底层通信逻辑，让开发者可以直接在 Python 脚本中与 Android 设备/模拟器进行交互。

#### 核心特点：
1. **无外部依赖**：不依赖 Android SDK 中的 adb 工具，仅需 Python 环境即可运行；
2. **跨平台**：支持 Windows/macOS/Linux，与 Python 跨平台特性一致；
3. **轻量灵活**：以 Python 模块形式集成，可按需调用 ADB 核心功能，无需启动独立的 adb 服务进程（或可自动管理）；
4. **协议级封装**：直接实现 ADB 通信协议（TCP/UDP），而非调用 adb 命令行，效率更高、可控性更强。

> 补充：常见的替代方案是通过 `subprocess` 调用系统 adb 命令，而 `pure-python-adb` 则是更底层、更原生的实现。

### 二、pure-python-adb 的核心作用
本质是**用 Python 脚本自动化控制 Android 设备**，覆盖 ADB 原生支持的绝大部分功能，常见场景如下：

#### 1. 设备管理
- 扫描并连接已接入的 Android 设备（USB 连接）或模拟器（TCP 端口，如 5555）；
- 验证设备在线状态、获取设备基本信息（型号、系统版本、序列号等）；
- 管理设备连接（断开、重连、端口转发等）。

#### 2. 文件操作
- 从 PC 向设备推送文件/文件夹（替代 `adb push`）；
- 从设备拉取文件/文件夹到 PC（替代 `adb pull`）；
- 查看设备文件系统、创建/删除目录、修改文件权限。

#### 3. 命令执行
- 在设备端执行 shell 命令（替代 `adb shell`），如：
  - 查看进程：`ps`、`top`；
  - 控制应用：`am start`（启动应用）、`pm uninstall`（卸载应用）；
  - 系统操作：`input tap`（模拟点击）、`screencap`（截图）；
- 获取命令执行的输出和返回码，便于脚本判断执行结果。

#### 4. 应用管理
- 安装/卸载 APK 文件（替代 `adb install/uninstall`）；
- 清除应用数据、启动/停止应用进程；
- 查看已安装应用列表、获取应用包信息。

#### 5. 输入/界面模拟
- 模拟屏幕点击、滑动、按键输入（如输入文字、按返回键/主页键）；
- 截取设备屏幕并保存为图片；
- 录制设备屏幕（部分系统支持）。

#### 6. 调试与日志
- 实时读取设备的 Logcat 日志（替代 `adb logcat`），并过滤指定标签/级别；
- 监控设备状态变化（如连接/断开、应用崩溃）。

### 三、典型使用场景
1. **自动化测试**：为 Android 应用编写 Python 自动化测试脚本，替代 Appium 等重型框架（轻量场景）；
2. **设备批量管理**：同时控制多台 Android 设备，批量安装应用、推送文件、执行统一命令；
3. **移动端爬虫/数据采集**：模拟用户操作爬取 App 内容（需遵守合规性）；
4. **自定义工具开发**：开发轻量的 Android 设备管理工具（如批量截图、日志分析工具）；
5. **嵌入式/物联网场景**：在无 Android SDK 环境的设备（如树莓派）中，通过 Python 控制 Android 终端。

### 四、基础使用示例
#### 1. 安装
```bash
pip install pure-python-adb
# 或从 GitHub 安装最新版
pip install git+https://github.com/Swind/pure-python-adb.git
```

#### 2. 核心代码示例
```python
from ppadb.client import Client as AdbClient

# 1. 连接 ADB 服务（默认端口 5037）
client = AdbClient(host="127.0.0.1", port=5037)

# 2. 获取已连接的设备列表
devices = client.devices()
if not devices:
    print("无可用设备")
    exit()

# 选择第一个设备
device = devices[0]
print(f"已连接设备：{device.serial}")

# 3. 执行 shell 命令
output = device.shell("getprop ro.build.version.release")
print(f"设备 Android 版本：{output.strip()}")

# 4. 推送文件到设备
local_file = "test.txt"
remote_path = "/sdcard/test.txt"
device.push(local_file, remote_path)
print(f"文件 {local_file} 已推送到 {remote_path}")

# 5. 模拟屏幕点击（坐标 x=500, y=800）
device.shell("input tap 500 800")

# 6. 截取屏幕并保存到本地
screen_data = device.screencap()
with open("screen.png", "wb") as f:
    f.write(screen_data)
print("屏幕截图已保存为 screen.png")
```

### 五、注意事项
1. **设备需开启 USB 调试**：使用前需在 Android 设备上开启「开发者选项」→「USB 调试」，部分设备还需开启「USB 调试（安全设置）」；
2. **权限问题**：推送/拉取系统目录（如 `/system`）可能需要设备 root 权限；
3. **兼容性**：部分高版本 Android（如 Android 11+）对 ADB 权限、文件访问有更严格的限制，需适配；
4. **与原生 ADB 的区别**：`pure-python-adb` 不支持部分小众 ADB 命令（如 `adb reverse`），核心功能完全覆盖。

### 总结
`pure-python-adb` 是 Python 开发者操作 Android 设备的轻量利器，无需依赖原生 ADB 工具，通过代码直接掌控设备行为，适合自动化、批量管理、轻量测试等场景，是替代「命令行调用 adb」的更优雅方案。



# -------------------------------------------------------------------------
# 2025-12-28
### scrcpy-win64-v3.3.4.zip
### 目的：使用 scrcpy 工具来镜像 Android 设备屏幕。
### 实现：
你遇到的错误是：

ERROR: Could not find a version that satisfies the requirement scrcpy (from versions: none)
ERROR: No matching distribution found for scrcpy
❌ 原因分析

scrcpy 不是 Python 包，而是一个 独立的跨平台工具（C++ 编写），它通过 ADB 与 Android 设备通信，实现屏幕镜像、控制等功能。

所以：
✅ 它没有在 PyPI 上发布为 pip install scrcpy
❌ 不能用 pip install scrcpy 安装
🛠 必须手动下载可执行文件

✅ 正确安装方法：从官网下载二进制文件
🔗 官方地址：
👉 [https://github.com/Genymobile/scrcpy/releases](https://github.com/Genymobile/scrcpy/releases)

📦 Windows 用户操作步骤（推荐）

1. 打开浏览器，进入上面链接。
2. 找到最新版本（如 v2.0），点击 “Assets” 下拉框。
3. 下载以下文件：

scrcpy-win64.zip
或者 scrcpy-win32.zip（32位系统）

4. 解压到任意目录，比如：

D:\tools\scrcpy

5. 打开命令行（CMD 或 PowerShell），进入该目录：
bash
cd D:\tools\scrcpy

6. 运行：
bash
.\scrcpy.exe

✅ 如果一切正常，会弹出一个窗口显示你的手机屏幕！

💡 注意事项

项目 说明
------ ------
🔹 是否需要 ADB？ 是！必须先安装 ADB 并能运行 adb devices
🔹 是否支持中文？ 支持，但界面默认英文
🔹 是否可以缩放？ 可以，按 Ctrl + 鼠标滚轮 调整大小
🔹 是否支持键盘输入？ 是！可以直接打字、粘贴
🔹 是否支持鼠标点击？ 是！直接点击屏幕即可

🧪 如何验证是否成功？

1. 确保手机已连接并开启 USB 调试。
2. 在 CMD 中运行：
bash
adb devices

应看到设备序列号。

3. 进入 scrcpy 目录，运行：
bash
scrcpy.exe

✅ 若出现手机画面 → 成功！

⚠️ 常见问题排查

问题 解决方案
------ ----------
❌ 提示“无法启动” 检查是否安装了 Visual C++ Redistributable
❌ 显示黑屏 尝试 scrcpy -r 强制重新连接
❌ 报错 ADB not found 把 platform-tools 的路径加入 PATH 环境变量
❌ 不响应 确保手机开启了“USB 调试”，并点击“允许”

🔄 替代方案：使用 Python 启动 scrcpy（高级）

如果你希望用 Python 脚本自动启动 scrcpy，可以用 subprocess：

python
import subprocess
启动 scrcpy
proc = subprocess.Popen(["D:\\tools\\scrcpy\\scrcpy.exe"], shell=True)
但这只是调用外部程序，并非 Python 实现。

✅ 总结

方法 是否可行 推荐度
------ ---------- --------
pip install scrcpy ❌ 不行 ❌
从 GitHub 下载 .exe 文件 ✅ 可行 ✅✅✅ 强烈推荐
使用 adb + scrcpy 组合 ✅ 最佳体验 ✅✅✅

📌 快速操作指南（Windows）

bash
1. 下载并解压 scrcpy-win64.zip 到 D:\tools\scrcpy
2. 打开 CMD，进入目录
cd D:\tools\scrcpy
3. 运行
.\scrcpy.exe

现在你就可以在 PC 上实时查看手机界面，调试代码更方便了！

如果想让 scrcpy 支持中文、自动连接、热键控制等高级功能，我也可以帮你配置！欢迎继续提问 😊


# -------------------------------------------------------------------------
# 2025-12-28


三、场景 2：USB 直连设备（更稳定）
无需 --tcpip 参数，直接转发端口 + 启动 scrcpy：
bash
執行
# 第一步：转发 8888 端口到 scrcpy 内置视频流端口 27183
adb forward tcp:8888 localabstract:scrcpy

# 第二步：启动 scrcpy（USB连接 + 无播放窗口 + 保持唤醒）
scrcpy --no-playback --stay-awake

# 操作过程，在PC上

D:\ProgramData\projects\pro_python\pro_debug\scrcpy-win64-v3.3.4>adb forward tcp:8888 localabstract:scrcpy
8888

D:\ProgramData\projects\pro_python\pro_debug\scrcpy-win64-v3.3.4>scrcpy --no-playback --stay-awake
scrcpy 3.3.4 <https://github.com/Genymobile/scrcpy>
INFO: No video playback, no recording, no V4L2 sink: video disabled
INFO: No audio playback, no recording: audio disabled
INFO: No video mirroring, SDK mouse disabled
INFO: ADB device found:
INFO:     -->   (usb)  10AE3U0P980068M                 device  V2301A
D:\ProgramData\projects\pro_python\pro_debug\scrcpy-win64-... file pushed, 0 skipped. 75.1 MB/s (90980 bytes in 0.001s)
[server] INFO: Device: [vivo] vivo V2301A (Android 15)
INFO: Renderer: direct3d

# -------------------------------------------------------------------------
# 2025-12-28
# 场景：现在你遇到的问题是 帧率偏低、画面卡顿
# 目的：提高帧率，解决卡顿问题
# 实现：l2_通过 ADB Shell 结合 Python 显示
# 实现：l3_通过 ADB Shell 结合 Python 显示2
# 实现：l4_加入YOLOAI模型来实时分析通过ADB获取的手机屏幕截图
✅ 方案 1：降低截图分辨率（最有效！）

# 1. 降低分辨率（关键！）
adb shell wm size 720x1600

# 2. 运行你的 Python 脚本（保持当前代码即可）

# 3. 完成后恢复
adb shell wm size reset
这样你很可能获得 6~8 FPS 的流畅画面，足够用于大多数自动化任务（如 YOLO 实时检测）。

📊 性能对比（估算）
方法	分辨率	数据量	预估 FPS
原始	1260×2800	14MB	2~3 FPS
降分辨率	720×1600	~4.6MB	6~8 FPS
流式 + 降分辨率	720×1600	~4.6MB	8~10 FPS