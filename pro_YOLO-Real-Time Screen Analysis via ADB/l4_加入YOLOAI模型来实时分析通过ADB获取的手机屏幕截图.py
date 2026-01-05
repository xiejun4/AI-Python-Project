import os
import cv2
import numpy as np
import struct
from adbutils import adb
import time
from ultralytics import YOLO  # 确保已 pip install ultralytics

# === 初始化 ===
d = adb.device()
REMOTE_PATH = "/sdcard/screen_raw"
LOCAL_PATH = "screen_raw"

# 加载本地 YOLO 模型（支持 yolo11n.pt）
model = YOLO("pro_debug/YOLO-Real-Time Screen Analysis via ADB/models/yolo11n.pt")

def get_screenshot():
    try:
        d.shell(f"screencap {REMOTE_PATH}")
        d.sync.pull(REMOTE_PATH, LOCAL_PATH)
        
        with open(LOCAL_PATH, 'rb') as f:
            data = f.read()
        
        if len(data) < 8:
            print("❌ 数据太短，无法解析头部")
            os.remove(LOCAL_PATH)
            return None
        
        width, height = struct.unpack_from('<II', data, 0)
        pixel_data = data[8:]
        expected_rgba = width * height * 4
        
        if len(pixel_data) == expected_rgba:
            arr = np.frombuffer(pixel_data, dtype=np.uint8).reshape((height, width, 4))
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        elif len(pixel_data) == expected_rgba + 8:
            arr = np.frombuffer(pixel_data[:expected_rgba], dtype=np.uint8).reshape((height, width, 4))
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        else:
            print(f"❌ 未知格式: 实际={len(pixel_data)}, 期望={expected_rgba}")
            os.remove(LOCAL_PATH)
            return None
        
        os.remove(LOCAL_PATH)
        return bgr
        
    except Exception as e:
        print(f"📸 截图异常: {e}")
        if os.path.exists(LOCAL_PATH):
            os.remove(LOCAL_PATH)
        return None

# === 主循环 ===
while True:
    start = time.time()
    frame = get_screenshot()
    
    if frame is None:
        print("⚠️ 截图失败，2秒后重试...")
        time.sleep(2)
        continue

    # ✅ 使用 YOLO 进行推理
    results = model(frame)

    # ✅ 获取带检测框的图像（关键！）
    annotated_frame = results[0].plot()  # 返回 BGR 图像，带边界框和标签

    print(f"🖼️ 成功获取帧: {frame.shape} | 检测到 {len(results[0].boxes)} 个目标")
    
    # 显示结果
    cv2.imshow("Android Screen with YOLO", annotated_frame)
    if cv2.waitKey(1) == ord('q'):
        break

    # 控制帧率（可选）
    elapsed = time.time() - start
    time.sleep(max(0, 1/5 - elapsed))  # 提高到 5 FPS

cv2.destroyAllWindows()