# AI-Python-Project
“A project for developing AI tools based on personal ideas, mainly focusing on video - related AI training.”



### Git 操作指令清单（含 SSH 创建 + 首次 / 后续推送）

#### 一、前置：创建 SSH 密钥（首次必做）

1. 检查本地 SSH 密钥：`ls ~/.ssh`（有 id_ed25519/id_rsa 则跳过创建）
2. 生成 SSH 密钥：`ssh-keygen -t ed25519 -C "你的GitHub邮箱"`（回车默认路径，可留空密码）
3. 复制公钥：`cat ~/.ssh/id_ed25519.pub`（全选复制，后续添加到 GitHub）
4. 验证 SSH 连接（可选）：`ssh -T git@github.com`（出现用户名提示则成功）

#### 二、首次初始化 & 上传首个项目

1. 进入项目上级目录：`cd /d/D/ProgramData/projects/pro_python`（替换实际路径）

2. 初始化 Git 仓库：`git init`

3. 配置提交身份：

   - `git config --global user.name "你的GitHub用户名"`
   - `git config --global user.email "你的GitHub邮箱"`

   

4. 关联远程仓库（SSH）：`git remote add origin git@github.com:xiejun4/AI-Python-Project.git`

5. 配置 Git LFS（处理大文件）：

   - `git lfs install`
   - `git lfs track "*.exe"` `git lfs track "*.zip"`（按需加.tar/.rar 等）
   - `git add .gitattributes`

   

6. 添加首个项目到暂存区：`git add "pro_YOLO-Real-Time Screen Analysis via ADB/"`

7. 提交变更：`git commit -m "添加首个YOLO项目"`（身份异常则加：`git commit --amend --reset-author`）

8. 拉取远程内容合并：`git pull origin main --allow-unrelated-histories`

9. 推送至 GitHub：`git push origin main`

#### 三、推送后续项目（复用环境）

1. 进入项目上级目录：`cd /d/D/ProgramData/projects/pro_python`
2. 添加新项目到暂存区：`git add "pro_YOLO-Annotation-and-Training/"`
3. 提交变更：`git commit -m "添加第二个YOLO项目"`
4. 推送至 GitHub：`git push origin main`

#### 四、常见异常修复

1. 分支名不匹配：`git branch -m master main`（本地 master 改 main）
2. 强制推送（谨慎）：`git push origin main --force`（仅确认覆盖远程时用）
3. SSH 验证失败：重新执行`cat ~/.ssh/id_ed25519.pub`，将公钥添加到 GitHub「Settings→SSH and GPG keys」
4. 网络连接失败：`ipconfig /flushdns`（刷新 DNS）或切换手机热点
5. Vim 编辑器退出：按`Esc`→输入`:wq`→按`Enter`





# 2026-1-8

## 更新远程仓库已存在的.gitignore内容，是否直接提交，然后push到远程即可。



Qwen3-Max

是的！✅ **更新 `.gitignore` 后，只需正常提交（commit）并推送（push）到远程仓库即可**，操作非常简单。

- 修改它 → `git add` → `git commit` → `git push`，流程完全一致。

------

### ✅ 正确步骤（三步走）

```
1# 1. 确保你已修改并保存了 .gitignore 文件
2
3# 2. 将更改加入暂存区
4git add .gitignore
5
6# 3. 提交更改
7git commit -m "Update .gitignore to ignore additional files"
8
9# 4. 推送到远程仓库（如 GitHub）
10git push origin main
```





# 2026-1-9

非常好！你已经有一个**远程 GitHub 仓库**（例如 `https://github.com/xiejun4/AI-Python-Project.git`），并且已经上传过一些项目。现在你想**继续往这个仓库里添加新的本地项目**（比如 `pro_OTPlus_validate_modelinfo`）。

下面是最清晰、安全、推荐的操作步骤，附带详细注释：

------

## ✅ 目标

将一个新的本地项目文件夹（如 `pro_OTPlus_validate_modelinfo/`）作为**子目录**添加到已有的 GitHub 仓库中，**不破坏已有内容**。

------

## 📌 前提条件

- 远程仓库：`https://github.com/xiejun4/AI-Python-Project.git`
- 本地已有新项目：`D:\myprojects\pro_OTPlus_validate_modelinfo\`
- 你**不要**在新项目目录下直接 `git init` 并推送（这会导致“无关历史”冲突）

------

## 🔧 正确操作步骤（带注释）

### 第 1 步：进入你的工作区目录（可选但推荐）

```bash
# 进入你存放代码的主目录（便于管理）
cd D:\PythonProject\pro_python\pro_debug
```

> 💡 注：路径按你实际环境修改。

------

### 第 2 步：克隆远程仓库（如果还没本地副本）

```bash
# 克隆已有仓库到本地（只做一次）
git clone https://github.com/xiejun4/AI-Python-Project.git
```

> ✅ 这会创建一个名为 `AI-Python-Project` 的文件夹，里面包含你之前上传的所有内容。

> ⚠️ 如果你已经有这个仓库的本地副本，**跳过此步**，直接进入第 3 步。

------

### 第 3 步：把新项目复制进仓库目录

```bash
# 把你的新项目文件夹复制进去（保留整个文件夹）
cp -r pro_OTPlus_validate_modelinfo AI-Python-Project/
```

> - Windows 用户可用资源管理器拖拽，或用：
>
>   ```cmd
>   xcopy "pro_OTPlus_validate_modelinfo" "AI-Python-Project\pro_OTPlus_validate_modelinfo" /E /I
>   ```
>
> - 最终结构应为：
>
>   ```
>   AI-Python-Project/
>   ├── existing_project/       ← 已有项目
>   ├── README.md
>   └── pro_OTPlus_validate_modelinfo/   ← 新增项目
>       ├── main.py
>       └── ...
>   ```

------

### 第 4 步：进入仓库目录并检查状态

```bash
cd AI-Python-Project
git status
```

> ✅ 你会看到 `pro_OTPlus_validate_modelinfo/` 被列为 **Untracked files**（未跟踪的新文件）。

------

### 第 5 步：添加新项目到 Git 跟踪

```bash
# 添加整个新项目文件夹
git add pro_OTPlus_validate_modelinfo/
```

> 💡 如果你只想添加部分文件，可以指定具体路径。

> 🚫 不要运行 `git add .` 如果你不确定是否要提交所有改动（比如临时文件）。

------

### 第 6 步：（可选）配置 `.gitignore` 避免上传无用文件

在 `AI-Python-Project/` 根目录下编辑 `.gitignore`，添加：

```gitignore
# Python
__pycache__/
*.pyc
.env
venv/

# YOLO / 模型缓存
*.cache
runs/

# IDE
.vscode/
.idea/
```

然后也把它加入版本控制：

```bash
git add .gitignore
```

------

### 第 7 步：提交更改

```bash
git commit -m "Add new module: pro_OTPlus_validate_modelinfo"
```

> ✅ 提交信息要清晰，说明你加了什么。

------

### 第 8 步：推送到 GitHub

```bash
git push origin main
```

> ✅ 成功后，你的新项目就会出现在 GitHub 仓库中，作为子目录存在。

------

## ✅ 最终效果

在 GitHub 上你会看到：

```
AI-Python-Project/
├── project_A/
├── project_B/
└── pro_OTPlus_validate_modelinfo/   ← 新增
    ├── src/
    ├── config.yaml
    └── README.md
```

------

## ❌ 错误做法（避免！）

| 错误操作                                                     | 后果                          |
| ------------------------------------------------------------ | ----------------------------- |
| 在 `pro_OTPlus_validate_modelinfo` 里 `git init` 然后 `git remote add` | 导致“unrelated histories”冲突 |
| 直接 `git push -f` 覆盖远程                                  | 会删除已有项目！              |
| 不用 `git clone`，而是手动建 `.git`                          | 容易丢失历史或权限错误        |

------

## 💡 小贴士

- **每次新增项目都重复第 3~8 步即可**
- 如果你经常这样做，可以把 `AI-Python-Project` 作为你的“主工作区”
- 使用 VS Code 打开 `AI-Python-Project`，它会自动识别 Git 状态

------

如果你已经有一个本地 `AI-Python-Project` 仓库副本，也可以直接跳到第 3 步，无需重新 clone。

需要我帮你写一个一键脚本自动完成复制+提交吗？😊
