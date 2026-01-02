# 🚀 快速开始 - GitHub 提交

## 方法 1: 使用自动化脚本（推荐）

### Windows 用户

1. 双击运行 `git_setup.bat`
2. 按提示输入信息
3. 完成！

### Linux/Mac 用户

```bash
# 添加执行权限
chmod +x git_setup.sh

# 运行脚本
./git_setup.sh
```

## 方法 2: 手动执行命令

### 1. 初始化 Git 仓库

```bash
cd E:\DEV\ComfyUI-BenNodes
git init
```

### 2. 配置用户信息

```bash
git config user.name "你的GitHub用户名"
git config user.email "你的GitHub邮箱"
```

### 3. 在 GitHub 创建仓库

访问: https://github.com/new

- Repository name: `ComfyUI-BenNodes`
- Description: `ComfyUI 自定义节点集合`
- Public
- 不要勾选 "Initialize with README"

### 4. 提交代码

```bash
# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: ComfyUI-BenNodes v1.0"

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin git@github.com:YOUR_USERNAME/ComfyUI-BenNodes.git

# 推送
git branch -M main
git push -u origin main
```

## ✅ 验证 SSH 连接

```bash
# 测试连接
ssh -T git@github.com

# 应该看到:
# Hi YOUR_USERNAME! You've successfully authenticated...
```

## 🔧 如果遇到问题

### SSH 密钥问题

```bash
# 查看现有密钥
ls -la ~/.ssh

# 如果没有 id_ed25519，生成新密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥（Windows）
clip < ~/.ssh/id_ed25519.pub

# 复制公钥（Linux/Mac）
cat ~/.ssh/id_ed25519.pub | pbcopy  # Mac
cat ~/.ssh/id_ed25519.pub | xclip   # Linux
```

然后到 GitHub Settings > SSH and GPG keys > New SSH key 添加

### 权限问题

如果推送时提示权限错误：

1. 确认 SSH 密钥已添加到 GitHub
2. 确认使用 SSH URL（git@github.com:...）而不是 HTTPS
3. 测试 SSH 连接: `ssh -T git@github.com`

### 分支名称问题

如果默认分支是 master：

```bash
git branch -M main
git push -u origin main
```

## 📝 后续更新

```bash
# 修改代码后
git add .
git commit -m "描述你的修改"
git push
```

## 🎯 下一步

1. ✅ 代码已推送到 GitHub
2. 📝 在 GitHub 添加 Topics: `comfyui`, `comfyui-nodes`, `python`
3. 📄 添加 License（如果需要）
4. 🏷️ 创建 Release v1.0.0
5. 📢 分享你的项目！

---

**需要详细说明？** 查看 `GITHUB_SETUP.md`
