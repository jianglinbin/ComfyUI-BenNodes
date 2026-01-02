# 🔑 使用 Personal Access Token 提交到 GitHub

## 为什么使用 Token？

✅ **优点**：
- 不需要配置 SSH 密钥
- 设置更简单
- 可以随时撤销
- 可以设置细粒度权限

❌ **缺点**：
- Token 需要妥善保管
- 有过期时间
- 每次克隆都需要输入（除非保存）

## 📝 步骤 1: 创建 Personal Access Token

### 1.1 访问 Token 设置页面

访问：https://github.com/settings/tokens/new

或者：
1. 登录 GitHub
2. 点击右上角头像 → Settings
3. 左侧菜单 → Developer settings
4. Personal access tokens → Tokens (classic)
5. Generate new token → Generate new token (classic)

### 1.2 配置 Token

填写以下信息：

| 字段 | 值 |
|------|-----|
| **Note** | `ComfyUI-BenNodes` |
| **Expiration** | 90 days（或根据需要选择） |
| **Select scopes** | 勾选 `repo`（完整仓库访问权限） |

**必需权限**：
- ✅ `repo` - 完整的仓库控制权限
  - repo:status
  - repo_deployment
  - public_repo
  - repo:invite
  - security_events

### 1.3 生成并保存 Token

1. 点击页面底部的 "Generate token"
2. **立即复制 Token**（只显示一次！）
3. 保存到安全的地方（密码管理器或安全笔记）

Token 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 🚀 步骤 2: 使用 Token 提交代码

### 方法 1: 使用自动化脚本（推荐）

**Windows**：
```bash
# 双击运行
git_setup_token.bat
```

**Linux/Mac**：
```bash
chmod +x git_setup_token.sh
./git_setup_token.sh
```

按提示输入：
1. GitHub 用户名
2. GitHub 邮箱
3. Personal Access Token

### 方法 2: 手动命令

#### 2.1 初始化和配置

```bash
# 初始化仓库
git init

# 配置用户信息
git config user.name "你的用户名"
git config user.email "你的邮箱"
```

#### 2.2 提交代码

```bash
# 添加文件
git add .

# 提交
git commit -m "Initial commit: ComfyUI-BenNodes v1.0"
```

#### 2.3 连接 GitHub（使用 Token）

**方式 A: Token 嵌入 URL（简单但不太安全）**

```bash
# 替换 YOUR_TOKEN 和 YOUR_USERNAME
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/ComfyUI-BenNodes.git

# 推送
git branch -M main
git push -u origin main
```

**方式 B: 使用 Git Credential Manager（推荐）**

```bash
# 使用普通 HTTPS URL
git remote add origin https://github.com/YOUR_USERNAME/ComfyUI-BenNodes.git

# 推送时会提示输入凭据
git branch -M main
git push -u origin main

# 提示时输入：
# Username: 你的GitHub用户名
# Password: 你的Personal Access Token（不是GitHub密码！）
```

## 🔐 步骤 3: 保存 Token（可选）

### Windows - Git Credential Manager

Git for Windows 自带凭据管理器，会自动保存：

```bash
# 配置凭据存储
git config --global credential.helper manager

# 首次推送时输入 Token，之后会自动使用
```

### Linux/Mac - 凭据存储

**选项 1: 缓存（临时，15分钟）**
```bash
git config --global credential.helper cache
```

**选项 2: 存储（永久，明文保存）**
```bash
git config --global credential.helper store
```

**选项 3: macOS Keychain（推荐）**
```bash
git config --global credential.helper osxkeychain
```

## 📋 完整示例

```bash
# 1. 创建 Token（在 GitHub 网站上）
# 访问: https://github.com/settings/tokens/new
# 勾选 'repo' 权限
# 复制生成的 Token: ghp_xxxxxxxxxxxx

# 2. 初始化仓库
cd E:\DEV\ComfyUI-BenNodes
git init

# 3. 配置用户
git config user.name "YourUsername"
git config user.email "your.email@example.com"

# 4. 添加和提交
git add .
git commit -m "Initial commit: ComfyUI-BenNodes v1.0"

# 5. 添加远程仓库（使用 Token）
git remote add origin https://ghp_xxxxxxxxxxxx@github.com/YourUsername/ComfyUI-BenNodes.git

# 6. 推送
git branch -M main
git push -u origin main
```

## 🔄 后续更新

```bash
# 修改代码后
git add .
git commit -m "更新说明"
git push

# 如果已保存凭据，不需要再输入 Token
```

## 🛡️ 安全建议

### ✅ 推荐做法

1. **使用 Git Credential Manager**
   - Windows: 自动安装
   - Mac: 使用 Keychain
   - Linux: 使用 libsecret

2. **设置 Token 过期时间**
   - 建议 90 天
   - 过期前会收到邮件提醒

3. **最小权限原则**
   - 只勾选必需的 `repo` 权限
   - 不要勾选不需要的权限

4. **定期轮换 Token**
   - 每 3-6 个月更换一次
   - 旧 Token 立即撤销

### ❌ 避免做法

1. **不要将 Token 提交到代码**
   - 不要写在脚本中
   - 不要提交到 Git 仓库
   - 不要分享给他人

2. **不要使用明文存储**
   - 避免 `credential.helper store`（除非必要）
   - 使用系统凭据管理器

3. **不要使用永不过期的 Token**
   - 始终设置过期时间
   - 定期审查和撤销

## 🔧 故障排除

### Token 无效

```bash
# 错误: remote: Invalid username or password
# 解决: 检查 Token 是否正确，是否已过期
```

访问 https://github.com/settings/tokens 检查 Token 状态

### Token 权限不足

```bash
# 错误: remote: Permission denied
# 解决: 确保 Token 有 'repo' 权限
```

重新生成 Token 并勾选 `repo` 权限

### Token 已保存但失效

```bash
# Windows - 清除凭据
cmdkey /delete:git:https://github.com

# Mac - 清除 Keychain
git credential-osxkeychain erase
host=github.com
protocol=https
[按 Enter 两次]

# Linux - 清除存储
rm ~/.git-credentials
```

然后重新推送，输入新 Token

## 📊 Token vs SSH 对比

| 特性 | Personal Access Token | SSH Key |
|------|----------------------|---------|
| 设置难度 | ⭐⭐ 简单 | ⭐⭐⭐ 中等 |
| 安全性 | ⭐⭐⭐ 好 | ⭐⭐⭐⭐ 很好 |
| 过期时间 | 有（可设置） | 无 |
| 撤销 | 容易 | 容易 |
| 跨设备 | 需要复制 Token | 需要复制密钥 |
| 推荐场景 | 临时使用、CI/CD | 长期使用、个人开发 |

## 🎯 推荐方案

### 个人开发（长期）
- 使用 SSH Key
- 一次配置，长期使用

### 临时使用/多设备
- 使用 Personal Access Token
- 灵活方便，易于管理

### CI/CD 自动化
- 使用 Personal Access Token
- 设置为环境变量
- 定期轮换

## 📞 需要帮助？

- GitHub Token 文档: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- Git 凭据存储: https://git-scm.com/docs/git-credential-store

---

**选择最适合你的方式开始吧！** 🚀
