#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境配置工具
帮助用户设置环境变量和配置API密钥
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """创建.env文件"""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("✅ .env文件已存在")
        return True
    
    if not env_example.exists():
        print("❌ env_example.txt文件不存在")
        return False
    
    # 复制示例文件
    with open(env_example, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已创建.env文件，请编辑并填入您的API密钥")
    return True

def check_api_key():
    """检查API密钥是否设置"""
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if api_key and api_key != 'your_dashscope_api_key_here':
        print("✅ DASHSCOPE_API_KEY已设置")
        return True
    else:
        print("❌ DASHSCOPE_API_KEY未设置或使用默认值")
        return False

def interactive_setup():
    """交互式设置"""
    print("🏥 智能健康管理助手 - 环境配置")
    print("=" * 50)
    
    # 检查.env文件
    if not Path(".env").exists():
        print("\n📝 创建环境配置文件...")
        if not create_env_file():
            return False
    
    # 检查API密钥
    if not check_api_key():
        print("\n🔑 请设置您的DashScope API密钥:")
        print("1. 访问: https://dashscope.console.aliyun.com/")
        print("2. 注册并获取API密钥")
        print("3. 编辑.env文件，将DASHSCOPE_API_KEY设置为您的真实密钥")
        print("\n或者运行以下命令设置环境变量:")
        print("export DASHSCOPE_API_KEY='your_actual_api_key'")
        return False
    
    print("\n🎉 环境配置完成！")
    return True

def main():
    """主函数"""
    try:
        if interactive_setup():
            print("\n✅ 可以启动应用了:")
            print("   Web界面: start_gui_app_2.bat")
            print("   桌面应用: start_desktop_app_2.bat")
            print("   命令行: python src/main_choice.py")
        else:
            print("\n❌ 环境配置未完成，请按照提示设置API密钥")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 配置过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
