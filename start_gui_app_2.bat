@echo off
chcp 65001 >nul
echo 🏥 启动智能健康管理GUI应用 (简化版)
echo ========================================
echo.
echo 💡 基于Streamlit的Web界面 (兼容症状问诊Agent不可用的情况)
echo    - 用户问答交互
echo    - 症状问诊和健康评估
echo    - 个性化健康报告
echo    - 自动降级处理
echo.
echo 🔄 正在启动Web应用...
echo.

cd /d "%~dp0"

echo 📦 检查依赖包...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚠️ 正在安装Streamlit...
    pip install streamlit pandas
)

echo 🚀 启动Web服务器...
echo.
echo 🌐 应用将在浏览器中自动打开
echo 📱 如果没有自动打开，请访问: http://localhost:8502
echo.
echo 💡 按 Ctrl+C 停止服务器
echo.

streamlit run src\health_gui_app_2.py --server.port 8502 --server.address localhost

echo.
echo 👋 应用已停止
pause
