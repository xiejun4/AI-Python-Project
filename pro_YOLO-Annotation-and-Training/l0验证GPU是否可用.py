import os
import torch

model_path = r"D:\ProgramData\projects\pro_python\pro_debug\YOLO\models\yolov8n.pt"

# 1. 检查文件是否存在
print("✅ 文件存在:", os.path.exists(model_path))

# 2. 检查文件大小（官方 yolov8n.pt 应为 6,379,520 字节 ≈ 6.1 MB）
size = os.path.getsize(model_path)
print("📊 文件大小:", size, "字节")
if size != 6379520:
    print("❌ 文件大小异常！官方模型应为 6,379,520 字节")

# 3. 尝试直接用 torch.load 加载（绕过 YOLO 封装）
try:
    weights = torch.load(model_path, map_location='cpu')
    print("🎉 torch.load 成功！模型结构正常")
except Exception as e:
    print("💥 torch.load 失败:", str(e))