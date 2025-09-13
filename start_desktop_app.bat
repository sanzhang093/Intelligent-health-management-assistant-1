@echo off
chcp 65001 >nul
echo 🏥 启动智能健康管理桌面应用
echo ========================================
echo.
echo 💡 基于tkinter的桌面GUI应用
echo    - 桌面窗口界面
echo    - 用户问答交互
echo    - 症状问诊和健康评估
echo    - 个性化健康报告
echo.
echo 🔄 正在启动桌面应用...
echo.

cd /d "%~dp0"

echo 📦 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo 🚀 启动桌面应用...
echo.
echo 💡 桌面窗口将自动弹出
echo.

python src\health_desktop_app.py

echo.
echo 👋 桌面应用已关闭
pause
