@echo off
chcp 65001 >nul
echo ========================================
echo 使用 Token 推送到 GitHub
echo ========================================
echo.

echo 请访问以下链接创建 Personal Access Token:
echo https://github.com/settings/tokens/new
echo.
echo 设置说明:
echo - Note: ComfyUI-BenNodes
echo - Expiration: 90 days
echo - 勾选: repo (完整仓库权限)
echo.
echo 生成后，立即复制 Token (格式: ghp_xxxxxxxxxxxx...)
echo.

set /p token="请粘贴你的 Token: "
echo.

echo 正在添加远程仓库...
git remote add origin https://%token%@github.com/jianglinbin/ComfyUI-BenNodes.git
echo.

echo 正在推送到 GitHub...
git push -u origin main
echo.

if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo 推送成功！
    echo ========================================
    echo.
    echo 访问你的仓库: https://github.com/jianglinbin/ComfyUI-BenNodes
    echo.
) else (
    echo ========================================
    echo 推送失败！
    echo ========================================
    echo.
    echo 可能的原因:
    echo 1. Token 无效或权限不足
    echo 2. 仓库不存在（请先在 GitHub 创建）
    echo 3. 网络连接问题
    echo.
    echo 请检查后重试
    echo.
)

pause
