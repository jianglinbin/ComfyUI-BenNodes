@echo off
chcp 65001 >nul
echo ========================================
echo ComfyUI-BenNodes GitHub 提交脚本 (Token)
echo ========================================
echo.

REM 检查是否已经是 Git 仓库
if exist .git (
    echo [信息] Git 仓库已存在
) else (
    echo [步骤 1] 初始化 Git 仓库...
    git init
    echo.
)

REM 配置用户信息
echo [步骤 2] 配置 Git 用户信息...
set /p username="请输入你的 GitHub 用户名: "
set /p email="请输入你的 GitHub 邮箱: "

git config user.name "%username%"
git config user.email "%email%"
echo 用户信息已配置
echo.

REM 添加文件
echo [步骤 3] 添加文件到 Git...
git add .
echo.

REM 显示状态
echo [步骤 4] 查看将要提交的文件...
git status
echo.

REM 提交
echo [步骤 5] 提交到本地仓库...
git commit -m "Initial commit: ComfyUI-BenNodes v1.0 - 添加 21 个自定义节点 - 支持 AI 分析、图像处理、文本处理等功能 - 完整的 README 文档"
echo.

REM 添加远程仓库（使用 HTTPS + Token）
echo [步骤 6] 添加远程仓库...
echo.
echo 请输入你的 GitHub Personal Access Token
echo (如果还没有 Token，请访问: https://github.com/settings/tokens/new)
echo.
set /p token="请输入你的 Token: "
echo.

REM 使用 Token 构建 URL
set repo_url=https://%token%@github.com/%username%/ComfyUI-BenNodes.git
git remote add origin %repo_url%
echo 远程仓库已添加
echo.

REM 重命名分支为 main
echo [步骤 7] 设置主分支为 main...
git branch -M main
echo.

REM 推送到 GitHub
echo [步骤 8] 推送到 GitHub...
echo 正在推送，请稍候...
git push -u origin main
echo.

echo ========================================
echo 提交完成！
echo ========================================
echo.
echo 你的项目已成功推送到 GitHub！
echo 访问你的仓库: https://github.com/%username%/ComfyUI-BenNodes
echo.
echo [安全提示] Token 已保存在 Git 配置中
echo 如需移除 Token，运行: git remote set-url origin https://github.com/%username%/ComfyUI-BenNodes.git
echo.
pause
