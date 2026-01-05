# 加载预训练模型
# 安装三方库：ultralytics
# 导包: from ultralytics import YOLO

from ultralytics import YOLO
import os

def main():

    # 1, 加载模型
    # 2, 检测目标


    # 加载预训练模型
    # yolo11n.pt 是官方提供的基础测试和训练模型
    # 首次运行自动下载，也可以在课程资料内获取
    # 获取app.py文件所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "models", "yolo11n.pt")
    # pics2videos_path = os.path.join(script_dir, "pics2videos", "m1.mp4")
        # "https://qcloud.dpfile.com/pc/ou1jviNlMMlUpRpnaZDooNmdmQsTkDVB2o-XMr7UMdYk0Q0599ShPbm4SJMyRbzk.jpg"
    pics2videos_path = os.path.join(script_dir, "pics2videos", "1.jpg")

    if not os.path.exists(model_path):
        print("模型文件不存在，请检查路径！")
    else:
        model = YOLO(model_path)

        # 如果是URL，先下载到临时文件
        if pics2videos_path.startswith('http'):
            pics2videos_path_url = pics2videos_path
            model(source=pics2videos_path_url, show=True, save=True)

        elif pics2videos_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')):
            pics2videos_path_pic = pics2videos_path
            model(source=pics2videos_path_pic, show=True, save=True)

        elif pics2videos_path.endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg')):
            pics2videos_path_mp4 = pics2videos_path
            model(source=pics2videos_path_mp4, show=True, save=True)

        elif not os.path.exists(pics2videos_path):
            print("图片或视频文件不存在，请检查路径！")

        else:
            # 2, 检测目标
            # show=True  显示检测结果
            # save=True  保存检测结果
            model(source=pics2videos_path, show=True, save=True)

# 当直接运行此脚本时执行main函数
if __name__ == "__main__":
    main()



