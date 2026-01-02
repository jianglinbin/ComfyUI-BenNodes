# GitHub 提交指南

## 📝 准备工作

你的 SSH 密钥信息：
- **类型**: ED25519
- **指纹**: SHA256:iSqWzCK89Wd3Zxk/Ymg73tmlt5rpqhWgZdoaUtNw3uU
- **添加时间**: 2025年9月11日
- **权限**: 读写
- **有效期**: 最近4个月内使用

## 🚀 提交步骤

### 步骤 1: 初始化 Git 仓库

在项目根目录（ComfyUI-BenNodes）打开终端，执行：

```bash
# 初始化 Git 仓库
git init

# 配置用户信息（如果还没配置）
git config user.name "你的GitHub用户名"
git config user.email "你的GitHub邮箱"
```

### 步骤 2: 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `ComfyUI-BenNodes`
   - **Description**: `ComfyUI 自定义节点集合，提供图像处理、文本处理、数据转换、AI 分析等功能`
   - **Public/Private**: 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（我们已经有了）
3. 点击 "Create repository"

### 步骤 3: 添加文件到 Git

```bash
# 添加所有文件
git add .

# 查看将要提交的文件
git status

# 提交到本地仓库
git commit -m "Initial commit: ComfyUI-BenNodes v1.0

- 添加 21 个自定义节点
- 支持 AI 分析、图像处理、文本处理等功能
- 完整的 README 文档
- 依赖管理和分类报告"
```

### 步骤 4: 连接到 GitHub 仓库

将 `YOUR_USERNAME` 替换为你的 GitHub 用户名：

```bash
# 添加远程仓库（使用 SSH）
git remote add origin git@github.com:YOUR_USERNAME/ComfyUI-BenNodes.git

# 验证远程仓库
git remote -v
```

### 步骤 5: 推送到 GitHub

```bash
# 推送到 GitHub（首次推送）
git push -u origin main

# 如果提示分支名称是 master，使用：
git branch -M main
git push -u origin main
```

## 🔐 SSH 密钥验证

如果推送时提示权限问题，验证 SSH 连接：

```bash
# 测试 SSH 连接
ssh -T git@github.com

# 应该看到类似输出：
# Hi YOUR_USERNAME! You've successfully authenticated, but GitHub does not provide shell access.
```

如果连接失败，检查 SSH 密钥：

```bash
# 查看 SSH 密钥
ls -la ~/.ssh

# 应该看到 id_ed25519 和 id_ed25519.pub

# 如果没有，生成新密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥到剪贴板（Windows）
clip < ~/.ssh/id_ed25519.pub

# 然后到 GitHub Settings > SSH and GPG keys > New SSH key 添加
```

## 📦 后续更新

当你修改代码后，使用以下命令更新：

```bash
# 查看修改的文件
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

## 🏷️ 创建版本标签（可选）

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签到 GitHub
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

## 📋 常用 Git 命令

```bash
# 查看提交历史
git log --oneline

# 查看当前状态
git status

# 查看修改内容
git diff

# 撤销未提交的修改
git checkout -- <file>

# 撤销已添加但未提交的文件
git reset HEAD <file>

# 修改最后一次提交
git commit --amend

# 拉取远程更新
git pull origin main

# 克隆仓库
git clone git@github.com:YOUR_USERNAME/ComfyUI-BenNodes.git
```

## 🌐 GitHub 仓库设置建议

### 1. 添加 Topics（标签）

在 GitHub 仓库页面，点击 "Add topics"，添加：
- `comfyui`
- `comfyui-nodes`
- `image-processing`
- `ai`
- `python`
- `stable-diffusion`

### 2. 设置 About（关于）

在仓库页面右侧，点击设置图标，填写：
- **Description**: `ComfyUI 自定义节点集合，提供图像处理、文本处理、数据转换、AI 分析等功能`
- **Website**: 你的网站（如果有）
- **Topics**: 如上所述

### 3. 启用 Issues

Settings > Features > Issues（勾选）

### 4. 添加 License

如果还没有，可以在 GitHub 上添加：
1. 点击 "Add file" > "Create new file"
2. 文件名输入 `LICENSE`
3. 点击 "Choose a license template"
4. 选择 MIT License
5. 填写年份和名字
6. 提交

### 5. 创建 Release

1. 点击 "Releases" > "Create a new release"
2. Tag version: `v1.0.0`
3. Release title: `ComfyUI-BenNodes v1.0.0`
4. 描述发布内容
5. 点击 "Publish release"

## 🔄 与 ComfyUI Manager 集成

如果想让用户通过 ComfyUI Manager 安装，需要：

1. 在 GitHub 仓库根目录创建 `pyproject.toml` 或确保有 `requirements.txt`
2. 提交 Pull Request 到 ComfyUI Manager 的节点列表
3. 等待审核通过

## 📞 需要帮助？

如果遇到问题：
1. 检查 SSH 密钥是否正确配置
2. 确认 GitHub 用户名和邮箱配置正确
3. 查看 Git 错误信息
4. 搜索 GitHub 文档或 Stack Overflow

## ✅ 完成检查清单

- [ ] Git 仓库已初始化
- [ ] 用户信息已配置
- [ ] GitHub 仓库已创建
- [ ] 文件已添加和提交
- [ ] 远程仓库已连接
- [ ] 代码已推送到 GitHub
- [ ] SSH 密钥工作正常
- [ ] README.md 显示正常
- [ ] Topics 已添加
- [ ] License 已添加（可选）
- [ ] Release 已创建（可选）

---

**祝你提交顺利！** 🎉
