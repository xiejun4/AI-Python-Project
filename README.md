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
