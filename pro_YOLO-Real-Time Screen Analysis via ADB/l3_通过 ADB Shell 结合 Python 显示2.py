import os
import cv2
import numpy as np
import struct
from adbutils import adb
import time

# 初始化 ADB 设备
d = adb.device()
REMOTE_PATH = "/sdcard/screen_raw"
LOCAL_PATH = "screen_raw"

def get_screenshot():
    try:
        # 1. 在手机上生成 raw 截图
        d.shell(f"screencap {REMOTE_PATH}")
        
        # 2. 拉取到本地
        d.sync.pull(REMOTE_PATH, LOCAL_PATH)
        
        # 3. 读取本地文件
        with open(LOCAL_PATH, 'rb') as f:
            data = f.read()
        
        if len(data) < 8:
            print("❌ 数据太短，无法解析头部")
            os.remove(LOCAL_PATH)
            return None
        
        # 4. 解析头部：width, height (小端 uint32)
        width, height = struct.unpack_from('<II', data, 0)
        pixel_data = data[8:]
        
        # 5. 计算期望大小
        expected_rgba = width * height * 4
        expected_rgb565 = width * height * 2
        
        # 6. 判断格式（重点：允许 +8 字节 padding）
        if len(pixel_data) == expected_rgba:
            fmt = "RGBA"
            arr = np.frombuffer(pixel_data, dtype=np.uint8).reshape((height, width, 4))
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
        elif len(pixel_data) == expected_rgba + 8:
            # vivo 可能加了 8 字节尾部（如时间戳或校验）
            fmt = "RGBA+padding"
            arr = np.frombuffer(pixel_data[:expected_rgba], dtype=np.uint8).reshape((height, width, 4))
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
        elif len(pixel_data) == expected_rgb565:
            fmt = "RGB565"
            print(f"⚠️ 检测到 RGB565，但未实现解码")
            os.remove(LOCAL_PATH)
            return None
            
        else:
            print(f"❌ 未知格式: 实际={len(pixel_data)}, RGBA期望={expected_rgba}, RGBA+8={expected_rgba+8}")
            print(f"   分辨率: {width}x{height}")
            os.remove(LOCAL_PATH)
            return None
        
        print(f"✅ 成功解析 {fmt}: {width}x{height}")
        os.remove(LOCAL_PATH)  # 清理临时文件
        return bgr
        
    except Exception as e:
        print(f"📸 截图异常: {e}")
        # 如果本地文件存在，清理它
        if os.path.exists(LOCAL_PATH):
            os.remove(LOCAL_PATH)
        return None

# 主循环
while True:
    start = time.time()
    frame = get_screenshot()
    
    if frame is None:
        print("⚠️ 截图失败，2秒后重试...")
        time.sleep(2)
        continue

    print(f"🖼️ 成功获取帧: {frame.shape}")
    cv2.imshow("Android Screen", frame)
    if cv2.waitKey(1) == ord('q'):
        break

    # 控制帧率（例如 3 FPS）
    elapsed = time.time() - start
    time.sleep(max(0, 1/3 - elapsed))

cv2.destroyAllWindows()