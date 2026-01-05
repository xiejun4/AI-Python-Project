import pyautogui
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
# import winsound
import pygame  # 替换playsound，实现同步播放

# 初始化pygame音频（必须在使用前初始化）
pygame.mixer.init()

# 设置环境变量
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 加载模型
script_dir = os.path.dirname(os.path.abspath(__file__))
custom_sound_path = os.path.join(script_dir, "pics2videos", "alarm2.mp3")
model_path = os.path.join(script_dir, "runs/yolov11n_custom/weights", "best.pt")
# model_path = os.path.join(script_dir, "runs/detect/train4/weights", "best.pt")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"模型文件不存在：{model_path}")
model = YOLO(model_path)

# 检测区域
detect_area = (1, 1, 500, 500)

# 定义同步播放的提示音函数
def play_alert(custom_sound_path: str = custom_sound_path):
    # 优先播放自定义音频（同步阻塞）
    if os.path.exists(custom_sound_path):
        try:
            pygame.mixer.music.load(custom_sound_path)
            pygame.mixer.music.play()  # 开始播放
            # 等待音频播放完成（阻塞直到播放结束）
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("播放自定义提示音：发现小粉红猪小妹")
            return
        except Exception as e:
            print(f"自定义音频播放失败：{e}，切换为默认蜂鸣")
    
    # 兜底蜂鸣
    winsound.Beep(440, 500)
    print("播放默认蜂鸣提示音")

# 冷却时间
last_play_time = 0
cool_down = 3

# 循环检测
while True:
    try:
        # 截图+转换格式
        screen_img = pyautogui.screenshot(region=detect_area)
        frame = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)
        
        # YOLO推理
        results = model(frame)
        result = results[0]
        
        # 检测佩奇
        detect_peppa = False
        for box in result.boxes:
            cls_idx = int(box.cls[0])
            cls_name = result.names[cls_idx]
            if cls_name == "佩奇":
                detect_peppa = True
                break
        
        # 满足条件则播放提示音
        current_time = time.time()
        if detect_peppa and (current_time - last_play_time) > cool_down:
            play_alert()
            last_play_time = current_time
        
        # 显示检测结果
        result_frame = result.plot()
        cv2.imshow("Screen Detection", result_frame)

    except Exception as e:
        print(f"检测出错：{e}")
        continue

    # 按ESC退出
    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()