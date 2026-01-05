import pyautogui
import cv2
import numpy as np
from ultralytics import YOLO
import os

# 设置环境变量，仅当前Python进程生效
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 1. 加载训练好的 best.pt 模型
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "runs/detect/train4/weights", "best.pt")
# 加载模型前校验路径
if not os.path.exists(model_path):
    raise FileNotFoundError(f"模型文件不存在：{model_path}")
model = YOLO(model_path)

# 2. 指定屏幕检测范围（起始x, 起始y, 宽度, 高度）
# 示例：从屏幕(100, 100)位置开始，检测500x500的区域
detect_area = (1, 1, 500, 500)  # 格式：(x, y, w, h)


# 3. 循环检测屏幕区域
while True:

    try:
        # 截取指定区域的屏幕画面
        screen_img = pyautogui.screenshot(region=detect_area)
        
        # 转换为OpenCV格式（BGR）
        frame = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)
        
        # 4. 用YOLO模型推理
        results = model(frame)
        
        # 5. 绘制检测结果（在画面上显示框、标签）
        result_frame = results[0].plot()  # 生成带检测框的画面
        
        # 6. 显示检测窗口
        cv2.imshow("Screen Detection", result_frame)

    except Exception as e:
        print(f"检测出错：{e}")
        continue  # 出错后继续循环

    
    # 按ESC键退出循环
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 7. 释放资源
cv2.destroyAllWindows()