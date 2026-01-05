# 导入必要的库
import os                      # 用于处理文件路径、环境变量等操作系统相关操作
import torch                   # PyTorch 深度学习框架
from ultralytics import YOLO   # YOLOv8（及后续版本如YOLOv11）官方库，用于目标检测

# ⚠️ 必须放在最外层（不能写在 if __name__ == '__main__' 里面）
# 解决某些系统（尤其是 Windows + Intel CPU）上因 OpenMP 多线程冲突导致的报错
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def main():
    # 自动检测是否有可用的 GPU（CUDA）
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🚀 使用设备: {device}")  # 打印当前使用的设备（GPU 或 CPU）

    # 获取当前脚本所在的目录（避免路径错误）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建模型文件的完整路径：假设模型放在当前目录下的 models/yolo11n.pt
    model_path = os.path.join(script_dir, "models", "yolo11n.pt")
    
    # 加载预训练的 YOLO 模型（这里用的是 YOLOv11 nano 版本）
    a1 = YOLO(model_path)

    # 开始训练模型
    a1.train(
        data=os.path.join(script_dir, 'data.yaml'),     # 数据集配置文件路径（定义了训练/验证路径、类别等）
        epochs=500,                                     # 训练轮数（遍历整个数据集 500 次）
        imgsz=640,                                      # 输入图像统一缩放到 640x640 像素
        batch=-1,                                       # 自动选择最大可能的 batch size（-1 表示自动）
        device=device,                                  # 使用上面检测到的设备（GPU 或 CPU）
        workers=4,                                      # 数据加载时使用的子进程数（加快读取速度）
        cache=True,                                     # 将数据集缓存到内存中，加速训练（适合小数据集）
        amp=True,                                       # 启用自动混合精度训练（节省显存、提速，通常安全）
        project=os.path.join(script_dir, 'runs'),       # 训练结果保存的根目录
        name='yolov11n_custom_2',                       # 本次训练的文件夹名称（结果会保存在 runs/yolov11n_custom_2/）
        exist_ok=False                                  # 如果该名称已存在，是否覆盖？False 表示不允许，防止误覆盖
    )

    print('🎉 模型训练完毕！')

# ✅ 关键：必须加这行！
# 在 Windows 上使用多进程（如 DataLoader 的 workers > 0）时，必须用这个保护主程序入口
if __name__ == '__main__':
    # 引入多进程模块（Windows 特别需要）
    import multiprocessing
    # freeze_support() 用于支持将程序打包成 .exe 后正常运行（即使不打包也建议保留，无害）
    multiprocessing.freeze_support()
    
    # 调用主函数开始训练
    main()