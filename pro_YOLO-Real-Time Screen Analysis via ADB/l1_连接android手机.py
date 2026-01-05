from ppadb.client import Client as AdbClient

# 连接到本地 ADB server（默认 127.0.0.1:5037）
client = AdbClient(host="127.0.0.1", port=5037)

# 获取所有已连接的设备
devices = client.devices()

if len(devices) == 0:
    print("没有检测到设备，请检查 USB 调试是否开启，并运行 'adb devices' 确认")
else:
    device = devices[0]  # 使用第一个设备
    print(f"已连接设备: {device.serial}")

    # 示例：获取设备型号
    model = device.shell("getprop ro.product.model").strip()
    print(f"设备型号: {model}")

    # 示例：执行 shell 命令
    output = device.shell("ls /sdcard")
    print("SD卡根目录内容:")
    print(output)

    # 示例：推送文件
    # device.push("local_file.txt", "/sdcard/remote_file.txt")

    # 示例：拉取文件
    # device.pull("/sdcard/remote_file.txt", "local_copy.txt")