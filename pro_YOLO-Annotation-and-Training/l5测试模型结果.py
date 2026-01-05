# 检测模型结果

from ultralytics import YOLO
# 模型训练完毕之后自动保存到： debug/YOLO/runs/detect/train4/weights
# best.pt 是训练过程中表现最好的模型（适用于最终应用）
# last.pt 是训练过程中最后一个模型（适用于继续训练）


import os
# 设置环境变量，仅当前Python进程生效
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


script_dir = os.path.dirname(os.path.abspath(__file__))

# 加载视频文件
video_path = os.path.join(script_dir, "pics2videos/small pig.mp4")

# 加载 best.pt 模型
model_path = os.path.join(script_dir, "runs/detect/train4/weights", "best.pt")
a1 = YOLO(model_path)

# 开始检测
results = a1(video_path, show=True, save=True)

# 打印检测结果
print(results)
