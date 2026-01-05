import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import math
import json


class AnnotationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("图片标注工具")
        self.root.geometry("1200x800")

        # 初始化变量
        self.image_path = ""
        self.image = None
        self.photo = None
        self.canvas = None
        self.rect = None
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.drawing = False
        self.annotations = []
        self.class_window = None  # 用于跟踪当前打开的标签设置窗口
        
        # 从配置文件加载默认类型
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(current_dir, "config.json")        
        self.config_file = config_file
        self.class_types = self.load_default_classes()
        self.current_class = self.class_types[0] if self.class_types else "马叔"
        self.image_width = 0
        self.image_height = 0

        # 创建界面
        self.create_widgets()

    def load_default_classes(self):
        """
        从配置文件加载默认类别类型
        :return: 默认类别列表
        """
        default_classes = ["马叔", "桂英"]
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "default_classes" in config and isinstance(config["default_classes"], list):
                        default_classes = config["default_classes"]
                        if not default_classes:
                            default_classes = ["马叔", "桂英"]
        except json.JSONDecodeError:
            print(f"配置文件 {self.config_file} 格式错误，使用默认类别")
        except Exception as e:
            print(f"读取配置文件时出错: {e}，使用默认类别")
        return default_classes
    
    def create_widgets(self):
        # 菜单栏
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="导入图片", command=self.import_image)
        filemenu.add_command(label="保存标注", command=self.save_annotation)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=filemenu)
        self.root.config(menu=menubar)

        # 工具栏
        toolbar = tk.Frame(self.root, bg="#f0f0f0")
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        import_btn = tk.Button(toolbar, text="导入图片", command=self.import_image, width=10)
        import_btn.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(toolbar, text="保存标注", command=self.save_annotation, width=10)
        save_btn.pack(side=tk.LEFT, padx=5)

        # 图片显示区域
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 标注信息区域
        info_frame = tk.Frame(self.root, bg="#f0f0f0", height=50)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        info_frame.pack_propagate(False)

        # 设置信息标签样式：蓝色、加粗、较大字号
        self.info_label = tk.Label(
            info_frame,
            text="未导入图片",
            bg="#f0f0f0",
            fg="blue",
            font=("Arial", 12, "bold")
        )
        self.info_label.pack(pady=15)

    def import_image(self):
        # 打开文件对话框选择图片
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            # 清空之前的标注
            self.annotations = []
            # 加载并显示图片
            self.load_image()
            self.info_label.config(text=f"已导入图片: {os.path.basename(file_path)}")

    def load_image(self):
        # 加载图片
        self.image = Image.open(self.image_path)
        self.image_width, self.image_height = self.image.size

        # 计算缩放比例，适应窗口
        max_width = self.canvas_frame.winfo_width() if self.canvas_frame.winfo_width() > 0 else 1000
        max_height = self.canvas_frame.winfo_height() if self.canvas_frame.winfo_height() > 0 else 600

        scale = min(max_width / self.image_width, max_height / self.image_height)
        new_width = int(self.image_width * scale)
        new_height = int(self.image_height * scale)

        # 缩放图片
        resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        # 创建或更新画布
        if self.canvas:
            self.canvas.destroy()

        self.canvas = tk.Canvas(self.canvas_frame, width=new_width, height=new_height, bg="gray")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # 保存缩放比例
        self.scale = scale

    def on_mouse_down(self, event):
        # 开始绘制矩形
        self.start_x = event.x
        self.start_y = event.y
        self.drawing = True

        # 创建矩形
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_mouse_drag(self, event):
        # 拖动鼠标调整矩形大小
        if self.drawing:
            self.current_x = event.x
            self.current_y = event.y
            self.canvas.coords(self.rect, self.start_x, self.start_y, self.current_x, self.current_y)

    def on_mouse_up(self, event):
        # 结束绘制矩形
        if self.drawing:
            self.drawing = False
            # 显示类别选择窗口
            self.show_class_window()

    def show_class_window(self):
        # 先关闭已存在的标签设置窗口
        if self.class_window and self.class_window.winfo_exists():
            self.class_window.destroy()

        # 创建类别选择窗口
        self.class_window = tk.Toplevel(self.root)
        self.class_window.title("目标标签设置")
        self.class_window.geometry("300x210")
        self.class_window.resizable(False, False)

        # 类别选择下拉菜单
        tk.Label(self.class_window, text="选择类型:").pack(pady=5)
        # 默认选择最后一个类型
        class_var = tk.StringVar(value=self.class_types[-1])
        class_option = tk.OptionMenu(self.class_window, class_var, *self.class_types)
        class_option.pack(pady=5, fill=tk.X, padx=20)

        # 添加新类型
        tk.Label(self.class_window, text="或添加新类型:").pack(pady=5)
        new_class_var = tk.StringVar()
        new_class_entry = tk.Entry(self.class_window, textvariable=new_class_var)
        new_class_entry.pack(pady=5, fill=tk.X, padx=20)

        def add_new_class():
            new_class = new_class_var.get().strip()
            if new_class and new_class not in self.class_types:
                self.class_types.append(new_class)
                # 更新下拉菜单
                menu = class_option["menu"]
                menu.delete(0, "end")
                for c in self.class_types:
                    menu.add_command(label=c, command=lambda value=c: class_var.set(value))
                class_var.set(new_class)
                self.show_message("info", f"已添加新类型: {new_class}")

        # 按钮框架
        btn_frame = tk.Frame(self.class_window)
        btn_frame.pack(pady=5)

        # 增大按钮大小，设置合适的宽度
        confirm_btn = tk.Button(btn_frame, text="确定类型", command=lambda: confirm_class(), width=10)
        confirm_btn.pack(side=tk.LEFT, padx=10)

        add_btn = tk.Button(btn_frame, text="添加类型", command=add_new_class, width=10)
        add_btn.pack(side=tk.LEFT, padx=10)

        # 提示文字
        tk.Label(self.class_window, text="无类型时，先添加类型，再选择", fg="red", font=("Arial", 9)).pack(pady=5)

        def confirm_class():
            selected_class = class_var.get()
            if selected_class:
                # 保存标注
                self.save_annotation_data(selected_class)
                if self.class_window and self.class_window.winfo_exists():
                    self.class_window.destroy()
                    self.class_window = None
            else:
                self.show_message("warning", "请选择一个类型")

        # 处理窗口关闭事件
        def on_window_close():
            if self.class_window and self.class_window.winfo_exists():
                self.class_window.destroy()
                self.class_window = None

        # 添加窗口关闭协议处理
        self.class_window.protocol("WM_DELETE_WINDOW", on_window_close)

    def save_annotation_data(self, class_name):
        # 计算矩形在原始图片中的坐标
        x1, y1, x2, y2 = self.canvas.coords(self.rect)

        # 转换为原始图片坐标
        original_x1 = int(min(x1, x2) / self.scale)
        original_y1 = int(min(y1, y2) / self.scale)
        original_x2 = int(max(x1, x2) / self.scale)
        original_y2 = int(max(y1, y2) / self.scale)

        # 计算中心点和宽高
        center_x = (original_x1 + original_x2) / (2 * self.image_width)
        center_y = (original_y1 + original_y2) / (2 * self.image_height)
        width = (original_x2 - original_x1) / self.image_width
        height = (original_y2 - original_y1) / self.image_height

        # 获取类型下标
        class_index = self.class_types.index(class_name)

        # 保存标注
        annotation = {
            "class_name": class_name,
            "class_index": class_index,
            "center_x": center_x,
            "center_y": center_y,
            "width": width,
            "height": height
        }
        self.annotations.append(annotation)

        # 在画布上显示标注
        self.canvas.create_text(
            min(x1, x2), max(y1, y2) + 15,
            text=class_name,
            fill="red",
            font=("Arial", 12, "bold"),
            anchor=tk.NW
        )

        # 更新信息
        self.info_label.config(
            text=f"已标注: {len(self.annotations)} 个对象，当前图片: {os.path.basename(self.image_path)}"
        )

    def show_message(self, message_type, message):
        """
        在主界面底部显示提示信息
        :param message_type: 消息类型，可选值："info", "warning", "error", "success"
        :param message: 消息内容
        """
        # 根据消息类型设置字体颜色
        if message_type == "info" or message_type == "success":
            color = "blue"
        elif message_type == "warning":
            color = "yellow"
        elif message_type == "error":
            color = "red"
        else:
            color = "blue"  # 默认蓝色

        # 更新信息标签
        self.info_label.config(
            text=message,
            fg=color
        )

    def save_annotation(self):
        if not self.image_path:
            self.show_message("warning", "警告: 请先导入图片")
            return

        if not self.annotations:
            self.show_message("warning", "警告: 没有标注内容")
            return

        # 生成标注文件名
        image_name = os.path.splitext(os.path.basename(self.image_path))[0]
        annotation_file = os.path.join(os.path.dirname(self.image_path), f"{image_name}.txt")

        # 保存标注内容
        try:
            with open(annotation_file, "w", encoding="utf-8") as f:
                for annotation in self.annotations:
                    f.write(f"{annotation['class_index']} {annotation['center_x']} {annotation['center_y']} {annotation['width']} {annotation['height']}\n")
            self.show_message("info", f"成功: 标注已保存到: {annotation_file}")
        except Exception as e:
            self.show_message("error", f"错误: 保存标注失败: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnnotationTool(root)
    root.mainloop()