# ---------------


# 学习过程
## 环境说明: Python 3.10 + PaddlePaddle 3.2.2
## 注意: PaddleDetection 需兼容 Paddle 3.x
## 创建虚拟环境 (推荐使用 venv 而非 conda，因 Python 3.10 较新)
python -m venv paddle_env
## Windows 激活: paddle_env\Scripts\activate
## Linux/macOS 激活: source paddle_env/bin/activate
## 升级 pip 并安装 PaddlePaddle 3.2.2
python -m pip install --upgrade pip
## CPU 版 (根据你的初始问题):
python -m pip install paddlepaddle==3.2.2 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
## 若需 GPU 版 (需 CUDA 11.6+):
python -m pip install paddlepaddle-gpu==3.2.2 -i https://www.paddlepaddle.org.cn/packages/stable/cuda116/
## 验证安装
python -c "import paddle; print(paddle.__version__); paddle.utils.run_check()"


# ----------------------------------------------------------------------------------------------------
## 安装 pycocotools (Python 3.10 需要兼容版本)
pip install pycocotools

## 安装 PaddleDetection (需使用支持 Paddle 3.x 的版本)
git clone https://github.com/PaddlePaddle/PaddleDetection.git
cd PaddleDetection
pip install -r requirements.txt
pip install -e . # 推荐用 -e 可编辑模式安装

## 安装 PaddleDetection 依赖（推荐使用阿里云镜像）
# 1. 安装 pycocotools（Windows + Python 3.10 兼容版）
pip install pycocotools-windows -i https://mirrors.aliyun.com/pypi/simple/

# 2. 克隆 PaddleDetection 仓库
git clone https://github.com/PaddlePaddle/PaddleDetection.git
cd PaddleDetection
# ----------------------------------------------------------------------------------------------------
# 实际安装过程中遇到的问题
# ----------------------------------------------------------------------------------------------------
# 2. 克隆 PaddleDetection 仓库（GitHub）遇到的问题1
## 问题描述
## 当使用 git clone 命令克隆 PaddleDetection 仓库时，可能会遇到以下速度太慢的情况：
    (paddle32) C:\Users\xiaoxiang3>git clone https://github.com/PaddlePaddle/PaddleDetection.git
    Cloning into 'PaddleDetection'...
    remote: Enumerating objects: 258356, done.
    remote: Counting objects: 100% (526/526), done.
    remote: Compressing objects: 100% (284/284), done.
    fatal: fetch-pack: invalid index-pack output0 KiB | 8.00 KiB/s
    fetch-pack: unexpected disconnect while reading sideband packet

    (paddle32) C:\Users\xiaoxiang3>cd PaddleDetectiongit clone https://gitee.com/paddlepaddle/PaddleDetection.git
    文件名、目录名或卷标语法不正确。
## 问题解决，跟换成 Gitee 镜像，可能会快很多，但是会出现以下问题，突然中断。
    (paddle32) C:\Users\xiaoxiang3>
    (paddle32) C:\Users\xiaoxiang3>git clone https://gitee.com/paddlepaddle/PaddleDetection.git
    Cloning into 'PaddleDetection'...
    remote: Enumerating objects: 259506, done.
    remote: Counting objects: 100% (316/316), done.
    remote: Compressing objects: 100% (187/187), done.
    error: RPC failed; curl 56 OpenSSL SSL_read: SSL_ERROR_SYSCALL, errno 0
    error: 55726 bytes of body are still expected
    fetch-pack: unexpected disconnect while reading sideband packet
    fatal: early EOF
    fatal: fetch-pack: invalid index-pack output
## 问题解决，清git下的缓存，然后只下载最新版本的代码，速度快，不易突然中断。

    (paddle32) C:\Users\xiaoxiang3>git config --global --unset http.proxy

    (paddle32) C:\Users\xiaoxiang3>git config --global --unset https.proxy

    (paddle32) C:\Users\xiaoxiang3>git clone --depth=1 https://gitee.com/paddlepaddle/PaddleDetection.git
    Cloning into 'PaddleDetection'...
    remote: Enumerating objects: 2408, done.
    remote: Counting objects: 100% (2408/2408), done.
    remote: Compressing objects: 100% (1717/1717), done.
    remote: Total 2408 (delta 978), reused 1511 (delta 659), pack-reused 0 (from 0)
    Receiving objects: 100% (2408/2408), 42.35 MiB | 1.97 MiB/s, done.
    Resolving deltas: 100% (978/978), done.
    Updating files: 100% (2087/2087), done.

    (paddle32) C:\Users\xiaoxiang3>cd PaddleDetection

    (paddle32) C:\Users\xiaoxiang3\PaddleDetection>

# 3. 升级 pip（确保支持新特性）
python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/

# 4. 安装依赖（使用阿里云镜像，超时时间设长些防中断）
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --timeout 1000

# 5. 可编辑模式安装 PaddleDetection
pip install -e . -i https://mirrors.aliyun.com/pypi/simple/
# ----------------------------------------------------------------------------------------------------

## 测试安装
python ppdet/modeling/tests/test_architectures.py

# ----------------------------------------------------------------------------------------------------
# 实际安装过程中遇到的问题
# ----------------------------------------------------------------------------------------------------
## 测试过程中遇到的问题，提示numba没有安装，请按照以下步骤安装。
## 安装 numba（针对 Python 3.10），numba 是一个用于 PP-Tracking（视频目标跟踪），建议安装 numba 以获得更好性能。
✅ 推荐做法（针对 Python 3.10）
✔ 方案一：安装 兼容 Python 3.10 的最新稳定版 numba
    pip install numba==0.58.1
    ✅ numba >= 0.57 开始正式支持 Python 3.10。
    ✅ 0.58.x 是目前（截至 2025 年）广泛使用的稳定版本，与 PaddleDetection 兼容性良好。
# ----------------------------------------------------------------------------------------------------


## 推理测试 (修正文件路径)
python tools/infer.py -c configs/ppyolo/ppyolo_r50vd_dcn_365e_coco.yml -o weights=https://paddledet.bj.bcebos.com/models/ppyolo_r50vd_dcn_365e_coco.pdparams --infer_img=demo.jpg


## 训练 PP-YOLOv2 (关键修改点)
## 1. 数据集准备: COCO 格式
## 2. 修改配置文件:
configs/ppyolo/ppyolo_r50vd_dcn_365e_coco.yml: snapshot_epoch
configs/datasets/coco_detection.yml: num_classes (你的类别数)
configs/ppyolo/_base_/optimizer_365e.yml: 学习率 = 0.01 / 8 * GPU数量
configs/ppyolo/_base_/ppyolo_reader.yml: batch_size, worker_num
## 3. 生成 anchors (PP-YOLOv2 通常不需要，但若需):
python tools/anchor_cluster.py -c configs/ppyolo/ppyolo_r50vd_dcn_365e_coco.yml -n 9 -s 640 -m v2 -i 1000
## 4. 启动训练:
python tools/train.py -c configs/ppyolo/ppyolo_r50vd_dcn_365e_coco.yml
## 推理验证
python tools/infer.py -c configs/ppyolo/ppyolo_r50vd_dcn_365e_coco.yml -o weights=output/ppyolo_r50vd_dcn_365e_coco/model_final.pdparams --infer_img=your_image.jpg

🔑 关键优化点说明：
原内容 优化后 原因
-------- -------- ------
conda create -n paddle21 python=3.8 改用 venv + Python 3.10 你使用 Python 3.10，且 conda 对新版 Python 支持可能滞后
paddlepaddle-gpu (CUDA 10.2) 明确区分 CPU/GPU 安装命令 Paddle 3.2.2 不再支持 CUDA 10.2，最低需 CUDA 11.2
手动编译 pycocotools 直接 pip install pycocotools Python 3.10 有预编译 wheel
ppyolo2_r50vd... 改为 ppyolo_r50vd... PaddleDetection 2.7+ 中 PP-YOLOv2 配置文件名已简化
权重路径 output/ppyolo/ 补全为 model_final.pdparams 明确最终模型文件名
💡 重要提示：PaddleDetection 的最新版本（如 2.8+）已适配 PaddlePaddle 3.x。请确保克隆的是 [最新 release](https://github.com/PaddlePaddle/PaddleDetection/releases)。

📌 下一步建议：
如果你实际有截图，请上传图片，我会精准提取并优化。
如果使用 GPU，请确认 CUDA 版本（nvidia-smi），Paddle 3.2.2 要求 CUDA ≥ 11.2。
如需 自定义数据集训练模板，可告知类别数和数据格式。

期待你的进一步指示！