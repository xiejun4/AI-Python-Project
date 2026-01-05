import pyautogui
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
import winsound  # Windows默认蜂鸣（兜底）
from playsound import playsound  # 自定义音频

# 设置环境变量，仅当前Python进程生效
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 1. 加载训练好的 best.pt 模型
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "runs/detect/train4/weights", "best.pt")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"模型文件不存在：{model_path}")
model = YOLO(model_path)

# 2. 指定屏幕检测范围
detect_area = (1, 1, 500, 500)  # (x, y, w, h)

# 3. 定义提示音函数（优先自定义音频，兜底蜂鸣）
def play_alert():
    # 自定义音频路径（可修改为你的音频文件名）
    custom_sound = r"D:\\PythonProject\\pro_PathFinder\\debug\\YOLO\\pics2videos\\alarm.mp3" 
    #os.path.join(script_dir, "pics2videos", "alarm.mp3")
    
    # 优先播放自定义音频
    if os.path.exists(custom_sound):
        try:
            playsound(custom_sound)
            print("播放自定义提示音：发现小粉红猪小妹")
            return
        except Exception as e:
            print(f"自定义音频播放失败：{e}，切换为默认蜂鸣")
    
    # 兜底：系统默认蜂鸣（Windows）
    winsound.Beep(440, 500)  # 频率440Hz，时长500ms
    print("播放默认蜂鸣提示音")

# 4. 冷却时间（避免连续播放）
last_play_time = 0
cool_down = 3  # 3秒内仅播放一次

# 5. 循环检测
while True:
    try:
        # 截图并转换格式
        screen_img = pyautogui.screenshot(region=detect_area)
        frame = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)
        
        # YOLO推理
        results = model(frame)
        result = results[0]
        
        # 检测是否有佩奇
        detect_peppa = False
        for box in result.boxes:
            cls_idx = int(box.cls[0])
            cls_name = result.names[cls_idx]
            if cls_name == "佩奇":
                detect_peppa = True
                break
        
        # 检测到佩奇且冷却时间已过，播放提示音
        current_time = time.time()
        if detect_peppa and (current_time - last_play_time) > cool_down:
            play_alert()
            last_play_time = current_time
        
        # 绘制并显示检测结果
        result_frame = result.plot()
        cv2.imshow("Screen Detection", result_frame)

    except Exception as e:
        print(f"检测出错：{e}")
        continue

    # 按ESC退出
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 释放资源
cv2.destroyAllWindows()