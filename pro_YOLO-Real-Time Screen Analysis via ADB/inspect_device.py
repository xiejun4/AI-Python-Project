from ppadb.client import Client as AdbClient

# 连接到本地 ADB server
client = AdbClient(host="127.0.0.1", port=5037)

# 获取所有已连接的设备
devices = client.devices()

if len(devices) == 0:
    print("没有检测到设备")
else:
    device = devices[0]
    print(f"已连接设备: {device.serial}")
    
    # 查看 Device 对象的所有属性和方法
    print("\nDevice 对象的所有属性和方法:")
    for attr in dir(device):
        if not attr.startswith('_'):
            print(attr)
    
    # 尝试通过 shell 命令获取设备属性（替代方法）
    print("\n通过 shell 命令获取设备型号:")
    model = device.shell("getprop ro.product.model")
    print(f"设备型号: {model.strip()}")
