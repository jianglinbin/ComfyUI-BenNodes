# 🔐 GitHub 认证方式对比

## 快速选择

| 你的情况 | 推荐方式 |
|---------|---------|
| 🆕 第一次使用 Git | Personal Access Token |
| 💻 长期个人开发 | SSH Key |
| 🔄 多台电脑切换 | Personal Access Token |
| 🤖 CI/CD 自动化 | Personal Access Token |
| 🔒 最高安全性 | SSH Key |
| ⚡ 快速开始 | Personal Access Token |

## 详细对比

### Personal Access Token (PAT)

#### ✅ 优点

1. **设置简单**
   - 只需在网页上生成
   - 不需要命令行配置
   - 5分钟内完成

2. **易于管理**
   - 可以随时撤销
   - 可以设置过期时间
   - 可以查看使用记录

3. **细粒度权限**
   - 可以只授予特定权限
   - 可以限制访问范围
   - 更安全的权限控制

4. **跨平台一致**
   - Windows/Mac/Linux 使用方式相同
   - 不需要特殊配置

#### ❌ 缺点

1. **需要保管 Token**
   - Token 泄露风险
   - 需要安全存储

2. **有过期时间**
   - 需要定期更新
   - 过期后需要重新生成

3. **每次克隆需要输入**
   - 除非使用凭据管理器
   - 稍微不便

#### 📋 使用步骤

```bash
# 1. 生成 Token（在 GitHub 网站）
# 访问: https://github.com/settings/tokens/new

# 2. 使用 Token
git remote add origin https://TOKEN@github.com/USER/REPO.git
git push -u origin main
```

#### 🎯 适用场景

- ✅ 新手入门
- ✅ 临时项目
- ✅ 多设备使用
- ✅ CI/CD 流水线
- ✅ 需要细粒度权限控制

---

### SSH Key

#### ✅ 优点

1. **一次配置，长期使用**
   - 配置后无需再输入密码
   - 自动认证
   - 使用便捷

2. **更安全**
   - 使用公钥加密
   - 私钥不会传输
   - 难以被窃取

3. **无过期时间**
   - 不需要定期更新
   - 长期有效

4. **性能更好**
   - 连接速度快
   - 加密效率高

#### ❌ 缺点

1. **初始配置复杂**
   - 需要生成密钥对
   - 需要添加到 GitHub
   - 需要配置 SSH agent

2. **跨设备需要重新配置**
   - 每台电脑需要单独配置
   - 或者需要复制私钥（不推荐）

3. **故障排除较难**
   - SSH 连接问题较难诊断
   - 需要了解 SSH 知识

#### 📋 使用步骤

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 添加到 SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. 复制公钥到 GitHub
cat ~/.ssh/id_ed25519.pub

# 4. 使用 SSH
git remote add origin git@github.com:USER/REPO.git
git push -u origin main
```

#### 🎯 适用场景

- ✅ 长期个人开发
- ✅ 固定工作电脑
- ✅ 需要最高安全性
- ✅ 频繁 Git 操作
- ✅ 熟悉命令行

---

## 性能对比

| 指标 | Token (HTTPS) | SSH |
|------|--------------|-----|
| 初始设置时间 | 5 分钟 | 10-15 分钟 |
| 推送速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 克隆速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 安全性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 维护成本 | 中（需定期更新） | 低（一次配置） |

## 安全性对比

### Token 安全建议

1. ✅ 使用最小权限（只勾选 `repo`）
2. ✅ 设置过期时间（建议 90 天）
3. ✅ 使用凭据管理器存储
4. ✅ 定期轮换 Token
5. ❌ 不要将 Token 提交到代码
6. ❌ 不要分享 Token

### SSH 安全建议

1. ✅ 使用 ED25519 算法（更安全）
2. ✅ 设置密钥密码（passphrase）
3. ✅ 私钥权限设为 600
4. ✅ 定期审查授权密钥
5. ❌ 不要复制私钥到不安全的地方
6. ❌ 不要使用弱密码保护私钥

## 切换认证方式

### 从 Token 切换到 SSH

```bash
# 1. 配置 SSH（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"
# 添加公钥到 GitHub

# 2. 更改远程 URL
git remote set-url origin git@github.com:USER/REPO.git

# 3. 测试
git push
```

### 从 SSH 切换到 Token

```bash
# 1. 生成 Token（在 GitHub 网站）

# 2. 更改远程 URL
git remote set-url origin https://TOKEN@github.com/USER/REPO.git

# 3. 测试
git push
```

## 混合使用

你可以为不同的仓库使用不同的认证方式：

```bash
# 仓库 A 使用 SSH
cd repo-a
git remote add origin git@github.com:USER/repo-a.git

# 仓库 B 使用 Token
cd repo-b
git remote add origin https://TOKEN@github.com/USER/repo-b.git
```

## 推荐配置

### 新手推荐

```
1. 使用 Personal Access Token
2. 安装 Git Credential Manager
3. 设置 90 天过期
4. 使用自动化脚本: git_setup_token.bat
```

### 专业开发者推荐

```
1. 使用 SSH Key
2. 配置 SSH agent
3. 设置密钥密码
4. 使用自动化脚本: git_setup.sh
```

### 企业/团队推荐

```
1. 使用 SSH Key（个人开发）
2. 使用 Token（CI/CD）
3. 启用 2FA（双因素认证）
4. 定期审查权限
```

## 常见问题

### Q: 我应该选择哪个？

**A**: 
- 如果你是新手或临时使用 → Token
- 如果你是长期开发者 → SSH
- 如果你不确定 → Token（更简单）

### Q: Token 过期了怎么办？

**A**: 
1. 生成新 Token
2. 更新远程 URL: `git remote set-url origin https://NEW_TOKEN@github.com/USER/REPO.git`
3. 或者使用凭据管理器，下次推送时输入新 Token

### Q: SSH 连接失败怎么办？

**A**:
1. 测试连接: `ssh -T git@github.com`
2. 检查密钥: `ls -la ~/.ssh`
3. 检查 SSH agent: `ssh-add -l`
4. 查看详细日志: `ssh -vT git@github.com`

### Q: 可以同时使用两种方式吗？

**A**: 可以！不同仓库可以使用不同的认证方式。

### Q: 哪个更安全？

**A**: SSH Key 理论上更安全，但正确使用的 Token 也很安全。关键是：
- Token: 设置过期时间、最小权限、安全存储
- SSH: 使用强密码、保护私钥、定期审查

## 总结

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 🆕 新手 | Token | 简单易用 |
| 💼 专业开发 | SSH | 高效安全 |
| 🔄 多设备 | Token | 灵活方便 |
| 🏢 企业 | 两者结合 | 各取所长 |
| 🤖 自动化 | Token | 易于管理 |

**最终建议**: 
- 从 Token 开始（快速上手）
- 熟悉后切换到 SSH（长期使用）
- 根据实际需求灵活选择

---

**需要帮助？**
- Token 指南: `TOKEN_GUIDE.md`
- SSH 指南: `GITHUB_SETUP.md`
- 快速开始: `QUICK_START.md`
