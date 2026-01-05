import os
# 设置环境变量，仅当前Python进程生效
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 开始模型训练
from ultralytics import YOLO

# 加载预训练模型
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "models", "yolo11n.pt")
a1 = YOLO(model_path)

# 开始训练模型
a1.train(
    data=os.path.join(script_dir, 'data.yaml'),  # 数据集配置文件路径
    epochs=500,        # 训练轮次
    imgsz=640,         # 输入图片尺寸 官方推荐640
    batch=-1,          # 每次训练的批量
    device=0       # GPU= 0 CPU= 'cpu'
)

print('模型训练完毕')