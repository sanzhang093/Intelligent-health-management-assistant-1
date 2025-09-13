#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能健康管理GUI应用配置文件
"""

import os
from typing import Dict, Any

class Config:
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME = "智能健康管理系统"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "基于Qwen-Max AI的智能健康管理平台"
    
    # Streamlit配置
    STREAMLIT_CONFIG = {
        "page_title": "智能健康管理系统",
        "page_icon": "🏥",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # 服务器配置
    SERVER_CONFIG = {
        "port": 8501,
        "address": "localhost",
        "max_upload_size": 200,  # MB
        "enable_cors": True
    }
    
    # API配置
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
    if not DASHSCOPE_API_KEY:
        raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
    QWEN_MODEL_CONFIG = {
        'model': 'qwen-max',
        'timeout': 60,
        'retry_count': 3,
    }
    
    # 文件路径配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
    REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
    VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "RAG", "vector_db")
    
    # 用户界面配置
    UI_CONFIG = {
        "max_chat_history": 50,  # 最大聊天历史记录数
        "max_report_preview": 1000,  # 报告预览最大字符数
        "auto_refresh_interval": 1,  # 自动刷新间隔（秒）
        "show_debug_info": False,  # 是否显示调试信息
    }
    
    # 健康管理配置
    HEALTH_CONFIG = {
        "default_analysis_days": 30,  # 默认分析天数
        "max_rag_results": 5,  # 最大RAG检索结果数
        "confidence_threshold": 0.5,  # 置信度阈值
    }
    
    # 样式配置
    STYLE_CONFIG = {
        "primary_color": "#1f77b4",
        "secondary_color": "#2c3e50",
        "success_color": "#28a745",
        "warning_color": "#ffc107",
        "error_color": "#dc3545",
        "info_color": "#17a2b8",
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取完整配置"""
        return {
            "app": {
                "name": cls.APP_NAME,
                "version": cls.APP_VERSION,
                "description": cls.APP_DESCRIPTION,
            },
            "streamlit": cls.STREAMLIT_CONFIG,
            "server": cls.SERVER_CONFIG,
            "api": {
                "dashscope_key": cls.DASHSCOPE_API_KEY,
                "qwen_model": cls.QWEN_MODEL_CONFIG,
            },
            "paths": {
                "project_root": cls.PROJECT_ROOT,
                "data_dir": cls.DATA_DIR,
                "profiles_dir": cls.PROFILES_DIR,
                "reports_dir": cls.REPORTS_DIR,
                "vector_db_dir": cls.VECTOR_DB_DIR,
            },
            "ui": cls.UI_CONFIG,
            "health": cls.HEALTH_CONFIG,
            "style": cls.STYLE_CONFIG,
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置"""
        try:
            # 检查必要的目录
            required_dirs = [cls.DATA_DIR, cls.PROFILES_DIR]
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    print(f"⚠️ 目录不存在: {dir_path}")
                    return False
            
            # 检查API密钥
            if not cls.DASHSCOPE_API_KEY:
                print("⚠️ DashScope API密钥未设置")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 配置验证失败: {e}")
            return False

# 创建全局配置实例
config = Config()
