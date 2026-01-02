@echo off
chcp 65001 >nul
echo ========================================
echo ComfyUI-BenNodes GitHub 提交脚本
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

REM 配置用户信息（如果需要）
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
git commit -m "Initial commit: ComfyUI-BenNodes v1.0 - 添加 21 个自定义节点 - 支持 AI 分析、图像处理、文本处理等功能 - 完整的 README 文档 - 依赖管理和分类报告"
echo.

REM 添加远程仓库
echo [步骤 6] 添加远程仓库...
set /p repo_url="请输入 GitHub 仓库 URL (例如: git@github.com:username/ComfyUI-BenNodes.git): "
git remote add origin %repo_url%
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
echo 访问你的仓库查看: https://github.com/%username%/ComfyUI-BenNodes
echo.
pause
