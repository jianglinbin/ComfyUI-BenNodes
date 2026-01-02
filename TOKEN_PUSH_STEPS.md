# 🔑 使用 Token 推送到 GitHub - 详细步骤

## 当前状态

✅ 代码已提交到本地 Git 仓库  
❌ SSH 密钥权限被拒绝  
✅ 准备使用 Token 推送

---

## 📝 步骤 1: 创建 Personal Access Token

### 1.1 访问 Token 创建页面

点击这个链接：https://github.com/settings/tokens/new

或者手动访问：
1. 登录 GitHub
2. 点击右上角头像 → **Settings**
3. 左侧菜单最底部 → **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**

### 1.2 填写 Token 信息

| 字段 | 填写内容 |
|------|---------|
| **Note** | `ComfyUI-BenNodes` |
| **Expiration** | 选择 `90 days` |
| **Select scopes** | 勾选 `repo` (完整的仓库控制权限) |

**重要**: 必须勾选 `repo`，这样才有推送代码的权限！

### 1.3 生成并保存 Token

1. 滚动到页面底部，点击绿色按钮 **Generate token**
2. **立即复制 Token**（只显示一次！）
   - Token 格式：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - 长度约 40 个字符
3. 保存到安全的地方（记事本、密码管理器等）

---

## 🚀 步骤 2: 在 GitHub 创建仓库

### 2.1 访问创建仓库页面

点击这个链接：https://github.com/new

或者：
1. 登录 GitHub
2. 点击右上角 `+` 号
3. 选择 **New repository**

### 2.2 填写仓库信息

| 字段 | 填写内容 |
|------|---------|
| **Owner** | `jianglinbin` (你的用户名) |
| **Repository name** | `ComfyUI-BenNodes` |
| **Description** | `ComfyUI 自定义节点集合，提供图像处理、文本处理、数据转换、AI 分析等功能` |
| **Public/Private** | 选择 `Public` (公开) |
| **Initialize** | **不要**勾选任何选项 |

### 2.3 创建仓库

点击绿色按钮 **Create repository**

---

## 💻 步骤 3: 推送代码

### 方法 A: 使用自动化脚本（推荐）

1. 双击运行 `push_with_token.bat`
2. 按提示粘贴你的 Token
3. 等待推送完成

### 方法 B: 手动命令

打开 PowerShell 或 CMD，在项目目录执行：

```bash
# 1. 添加远程仓库（替换 YOUR_TOKEN）
git remote add origin https://YOUR_TOKEN@github.com/jianglinbin/ComfyUI-BenNodes.git

# 2. 推送代码
git push -u origin main
```

**示例**（替换实际的 Token）：
```bash
git remote add origin https://ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/jianglinbin/ComfyUI-BenNodes.git
git push -u origin main
```

---

## ✅ 步骤 4: 验证推送成功

推送成功后，你会看到类似输出：

```
Enumerating objects: 100, done.
Counting objects: 100% (100/100), done.
Delta compression using up to 8 threads
Compressing objects: 100% (80/80), done.
Writing objects: 100% (100/100), 50.00 KiB | 5.00 MiB/s, done.
Total 100 (delta 20), reused 0 (delta 0), pack-reused 0
To https://github.com/jianglinbin/ComfyUI-BenNodes.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

访问你的仓库：https://github.com/jianglinbin/ComfyUI-BenNodes

---

## 🔧 故障排除

### 问题 1: Token 无效

**错误信息**：
```
remote: Invalid username or password.
fatal: Authentication failed
```

**解决方法**：
1. 检查 Token 是否完整复制
2. 确认 Token 已勾选 `repo` 权限
3. 重新生成 Token

### 问题 2: 仓库不存在

**错误信息**：
```
remote: Repository not found.
fatal: repository 'https://github.com/jianglinbin/ComfyUI-BenNodes.git/' not found
```

**解决方法**：
1. 确认已在 GitHub 创建仓库
2. 检查仓库名称是否正确
3. 确认用户名是否正确

### 问题 3: 权限被拒绝

**错误信息**：
```
remote: Permission denied to jianglinbin/ComfyUI-BenNodes.
```

**解决方法**：
1. 确认 Token 有 `repo` 权限
2. 确认你是仓库的所有者
3. 重新生成 Token 并勾选正确权限

### 问题 4: 远程仓库已存在

**错误信息**：
```
fatal: remote origin already exists.
```

**解决方法**：
```bash
# 删除现有远程仓库
git remote remove origin

# 重新添加
git remote add origin https://YOUR_TOKEN@github.com/jianglinbin/ComfyUI-BenNodes.git
```

---

## 📋 完整命令参考

```bash
# 查看当前状态
git status

# 查看远程仓库
git remote -v

# 删除远程仓库
git remote remove origin

# 添加远程仓库（使用 Token）
git remote add origin https://TOKEN@github.com/jianglinbin/ComfyUI-BenNodes.git

# 推送到 GitHub
git push -u origin main

# 查看推送历史
git log --oneline
```

---

## 🎯 后续操作

推送成功后，你可以：

### 1. 添加 Topics（标签）

在 GitHub 仓库页面：
1. 点击右侧 "About" 旁边的设置图标
2. 添加 Topics：
   - `comfyui`
   - `comfyui-nodes`
   - `image-processing`
   - `ai`
   - `python`

### 2. 创建 Release

1. 点击 "Releases" → "Create a new release"
2. Tag version: `v1.0.0`
3. Release title: `ComfyUI-BenNodes v1.0.0`
4. 描述发布内容
5. 点击 "Publish release"

### 3. 添加 License

1. 点击 "Add file" → "Create new file"
2. 文件名：`LICENSE`
3. 点击 "Choose a license template"
4. 选择 MIT License
5. 提交

### 4. 更新 README

如果需要修改 README.md：
```bash
# 编辑 README.md
# 然后提交
git add README.md
git commit -m "Update README"
git push
```

---

## 🔐 安全提示

1. ✅ **不要将 Token 提交到代码**
2. ✅ **不要分享 Token**
3. ✅ **定期更换 Token**（建议 3-6 个月）
4. ✅ **Token 过期前会收到邮件提醒**
5. ✅ **可以随时在 GitHub 撤销 Token**

撤销 Token：https://github.com/settings/tokens

---

## 📞 需要帮助？

如果遇到其他问题：
1. 查看完整的 Token 指南：`TOKEN_GUIDE.md`
2. 查看认证方式对比：`AUTHENTICATION_COMPARISON.md`
3. GitHub 文档：https://docs.github.com/en/authentication

---

**祝你推送成功！** 🎉
