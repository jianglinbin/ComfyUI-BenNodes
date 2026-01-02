@echo off
chcp 65001 >nul
echo ========================================
echo 同步并推送到 GitHub
echo ========================================
echo.

REM 设置默认 Token（请在此处填入你的 Token）
set token=YOUR_TOKEN_HERE

if "%token%"=="YOUR_TOKEN_HERE" (
    echo [错误] 请先在脚本中设置你的 Token！
    echo 编辑 sync_and_push.bat 文件，将 YOUR_TOKEN_HERE 替换为你的实际 Token
    echo.
    pause
    exit /b 1
)

echo [步骤 1] 检查 Git 状态...
git status
echo.

echo [步骤 2] 添加所有修改（包括删除的文件）...
git add -A
echo.

echo [步骤 3] 查看将要提交的更改...
git status
echo.

set /p confirm="确认提交这些更改吗？(y/n): "
if /i not "%confirm%"=="y" (
    echo 操作已取消
    pause
    exit /b
)
echo.

echo [步骤 4] 提交更改...
set /p commit_msg="请输入提交信息 (直接回车使用默认): "
if "%commit_msg%"=="" set commit_msg=Update: sync local changes and deletions

git commit -m "%commit_msg%"
echo.

echo [步骤 5] 推送到 GitHub...
echo 使用 Token: ghp_***...%token:~-4%
echo.

REM 检查远程仓库是否存在
git remote -v | findstr origin >nul
if %ERRORLEVEL% NEQ 0 (
    echo 添加远程仓库...
    git remote add origin https://%token%@github.com/jianglinbin/ComfyUI-BenNodes.git
)

echo 正在推送...
git push origin main
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
    echo 请检查网络连接和 Token 权限
    echo.
)

pause
