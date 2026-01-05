# ✅ 方法一：【推荐】强制让手机返回 PNG 格式截图

import os
from ppadb.client import Client as AdbClient
import cv2
import numpy as np
import time

client = AdbClient(host="127.0.0.1", port=5037)
devices = client.devices()

if not devices:
    print("未检测到设备")
else:
    device = devices[0]
    print(f"已连接: {device.serial}")

    while True:
        try:
            # 1. 在手机上执行 screencap 保存为 PNG
            device.shell("screencap -p /sdcard/screen.png")

            # 2. 拉取到本地临时文件
            local_path = "temp_screen.png"
            device.pull("/sdcard/screen.png", local_path)

            # 3. 用 OpenCV 读取
            img = cv2.imread(local_path)
            if img is None:
                print("拉取的图片无法读取")
                continue

            cv2.imshow("Android Screen (via PNG)", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # 可选：删除临时文件
            # os.remove(local_path)

            time.sleep(0.5)  # 控制刷新频率

        except Exception as e:
            print(f"异常: {e}")
            time.sleep(1)

    cv2.destroyAllWindows()