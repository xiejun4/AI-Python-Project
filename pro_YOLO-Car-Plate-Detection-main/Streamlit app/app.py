import streamlit as st  # 导入Streamlit库，用于创建Web应用界面
from ultralytics import YOLO  # 导入YOLO模型库，用于目标检测
import cv2  # 导入OpenCV库，用于图像和视频处理
import numpy as np  # 导入NumPy库，用于数值计算
from PIL import Image  # 导入PIL库，用于图像处理
import tempfile  # 导入临时文件库，用于处理上传的文件
import os  # 导入os库，用于操作系统相关功能（如路径操作）


# 使用Streamlit的缓存功能来缓存模型加载，提高性能
# 这样可以避免每次运行时都重新加载模型，节省时间
@st.cache_resource
def load_model(model_path: str) -> YOLO:
    """
    加载YOLO模型的函数
    参数：model_path - 模型文件的路径
    返回：加载好的YOLO模型对象
    """
    model = YOLO(model_path)  # 创建YOLO模型对象
    return model


def process_image(image: Image.Image, model: YOLO, confidence_threshold: float) -> np.ndarray:
    """
    处理单张图片的函数
    参数：
        image - PIL格式的图片对象
        model - 已加载的YOLO模型
        confidence_threshold - 置信度阈值
    返回：标注了检测结果的图片（NumPy数组格式）
    """
    # 使用YOLO模型对图片进行推理，设置置信度阈值
    results = model(image, conf=confidence_threshold)

    # 在图片上绘制检测结果（画出检测框和标签）
    annotated_image = results[0].plot()

    return annotated_image


def process_video(video_path: str, model: YOLO, confidence_threshold: float, output_path: str = "output.mp4") -> str:
    """
    处理视频文件的函数
    参数：
        video_path - 输入视频文件的路径
        model - 已加载的YOLO模型
        confidence_threshold - 置信度阈值
        output_path - 输出视频文件的路径
    返回：输出视频文件的路径，如果处理失败则返回None
    """
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("错误：无法打开视频文件。")  # 如果无法打开视频文件，显示错误信息
        return None

    # 获取视频的基本信息（宽度、高度、帧率）
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取视频宽度
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 获取视频高度
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # 获取视频帧率

    # 定义视频编码器和创建视频写入对象
    # 'avc1'是H.264编码，更适合网页播放
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 添加进度条，让用户知道处理进度
    progress_bar = st.progress(0)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 获取总帧数
    frame_count = 0  # 当前处理的帧数计数器

    # 循环处理视频的每一帧
    while cap.isOpened():
        ret, frame = cap.read()  # 读取一帧
        if not ret:  # 如果读取失败（到达视频末尾），退出循环
            break

        # 使用YOLO模型对当前帧进行推理
        results = model(frame, conf=confidence_threshold)
        annotated_frame = results[0].plot()  # 在帧上绘制检测结果

        # 将标注后的帧写入输出视频
        out.write(annotated_frame)

        # 更新进度条
        frame_count += 1
        if total_frames > 0:
            progress_bar.progress(frame_count / total_frames)  # 计算并显示进度百分比

    # 释放视频捕获和写入对象
    cap.release()
    out.release()
    progress_bar.empty()  # 清空进度条
    return output_path


def main():
    """
    主函数 - 应用的入口点
    这里设置页面配置和创建用户界面
    """
    # 设置页面的基本配置
    st.set_page_config(
        page_title="车牌识别",  # 页面标题
        page_icon="🚗",  # 页面图标
        layout="wide",  # 页面布局（宽屏）
        initial_sidebar_state="expanded"  # 侧边栏初始状态（展开）
    )

    # 创建页面标题和介绍文字
    st.title("🚗 基于YOLO的车牌识别")
    st.markdown("""
    欢迎使用！上传图片或视频来检测车牌。
    你可以在侧边栏调整模型路径和置信度阈值。
    """)

    # 获取app.py文件所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构造默认模型路径（相对于app.py文件的位置）
    default_model_path = os.path.join(script_dir, "best.pt")

    # 创建侧边栏，用于设置参数
    with st.sidebar:
        st.header("⚙️ 设置")  # 侧边栏标题
        # 文本输入框：输入模型文件路径，默认值为best.pt的绝对路径
        model_path = st.text_input("模型路径", value=default_model_path)
        # 滑块：设置检测的置信度阈值（0.0到1.0之间，默认0.5）
        confidence_threshold = st.slider("置信度阈值", 0.0, 1.0, 0.5, 0.05)

    # 创建文件上传组件
    uploaded_file = st.file_uploader(
        "选择一张图片或视频...",  # 上传组件的提示文字
        type=["jpg", "jpeg", "png", "mp4"],  # 支持的文件类型
        help="支持格式：JPG、JPEG、PNG（图片）；MP4（视频）"  # 帮助信息
    )

    # 如果用户上传了文件
    if uploaded_file is not None:
        # 获取上传文件的扩展名（如.jpg、.mp4）
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        try:
            # 加载YOLO模型
            model = load_model(model_path)

            # 如果上传的是图片文件
            if file_extension in [".jpg", ".jpeg", ".png"]:
                # --- 图片处理逻辑 ---
                image = Image.open(uploaded_file)  # 打开上传的图片

                # 创建两列布局，用于显示原图和处理后的图
                col1, col2 = st.columns(2)
                with col1:
                    # 在第一列显示原始上传的图片
                    st.image(image, caption="上传的图片", use_column_width=True)

                # 创建检测按钮
                if st.button("检测图片中的车牌", key="image_button"):
                    with st.spinner("正在处理图片..."):  # 显示加载动画
                        # 调用图片处理函数
                        annotated_image = process_image(image, model, confidence_threshold)
                        with col2:
                            # 在第二列显示处理后的图片
                            st.image(annotated_image, caption="处理后的图片", use_column_width=True)

            # 如果上传的是视频文件
            elif file_extension == ".mp4":
                # --- 视频处理逻辑 ---
                # 创建临时文件来保存上传的视频
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
                    tfile.write(uploaded_file.read())  # 将上传的视频数据写入临时文件
                    temp_video_path = tfile.name  # 获取临时文件路径

                # 在页面上播放原始上传的视频
                st.video(temp_video_path, format="video/mp4")

                # 创建检测按钮
                if st.button("检测视频中的车牌", key="video_button"):
                    with st.spinner("正在处理视频...这可能需要一些时间。"):  # 显示加载动画
                        # 调用视频处理函数
                        output_video_path = process_video(temp_video_path, model, confidence_threshold)

                        st.success("✅ 视频处理完成！")  # 显示成功信息

                        # 检查处理后的视频文件是否存在且不为空
                        if output_video_path and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                            # 读取处理后的视频文件
                            with open(output_video_path, 'rb') as video_file:
                                video_bytes = video_file.read()
                            # 在页面上播放处理后的视频
                            st.video(video_bytes, format="video/mp4")

                            # 删除临时输出文件（清理空间）
                            os.unlink(output_video_path)
                        else:
                            # 如果处理失败，显示错误信息
                            st.error("❌ 处理后的视频文件无法创建或找不到。系统可能不支持该视频编码。")

                    # 删除临时输入文件（清理空间）
                    if os.path.exists(temp_video_path):
                        os.unlink(temp_video_path)

        # 捕获文件未找到的错误
        except FileNotFoundError:
            st.error(f"模型文件在 '{model_path}' 位置未找到。请在侧边栏检查路径。")
        # 捕获其他所有错误
        except Exception as e:
            st.error(f"发生错误：{str(e)}")
            st.info("请确保模型文件兼容并重试。")


# 当直接运行此脚本时执行main函数
if __name__ == "__main__":
    main()