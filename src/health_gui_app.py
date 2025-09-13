#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能健康管理GUI前端应用
基于Streamlit构建的用户交互界面

功能：
1. 用户问答交互界面
2. 用户ID选择功能
3. 症状问诊和健康评估两个场景
4. 回答和报告展示
5. 历史记录查看
"""

import streamlit as st
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主控制器
from main_choice import HealthMainController

# 页面配置
st.set_page_config(
    page_title="智能健康管理系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .system-message {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

class HealthGUIApp:
    """智能健康管理GUI应用"""
    
    def __init__(self):
        """初始化应用"""
        self.controller = None
        self.available_users = []
        
        # 初始化会话状态
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'controller_initialized' not in st.session_state:
            st.session_state.controller_initialized = False
    
    def initialize_controller(self):
        """初始化主控制器"""
        if not st.session_state.controller_initialized:
            try:
                with st.spinner("🔄 正在初始化智能健康管理系统..."):
                    self.controller = HealthMainController()
                    self.available_users = self.controller.get_available_users()
                    st.session_state.controller_initialized = True
                    st.session_state.controller = self.controller
                    st.session_state.available_users = self.available_users
                
                st.success("✅ 系统初始化成功！")
                return True
                
            except Exception as e:
                st.error(f"❌ 系统初始化失败: {str(e)}")
                return False
        else:
            self.controller = st.session_state.controller
            self.available_users = st.session_state.available_users
            return True
    
    def render_header(self):
        """渲染页面头部"""
        st.markdown('<div class="main-header">🏥 智能健康管理系统</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h4>💡 系统功能</h4>
            <ul>
                <li><strong>智能问题分类</strong>：自动判断您的问题属于症状问诊还是健康管理</li>
                <li><strong>专业Agent处理</strong>：调用相应的专业Agent提供精准回答</li>
                <li><strong>个性化服务</strong>：基于用户档案提供个性化健康建议</li>
                <li><strong>实时交互</strong>：支持连续对话和历史记录查看</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.markdown("## 🔧 系统设置")
            
            # 用户选择
            st.markdown("### 👤 用户选择")
            if self.available_users:
                selected_user = st.selectbox(
                    "选择用户ID",
                    options=[""] + self.available_users,
                    index=0,
                    help="请选择一个用户ID以获取个性化服务"
                )
                
                if selected_user:
                    st.session_state.current_user = selected_user
                    st.success(f"✅ 已选择用户: {selected_user}")
                    
                    # 显示用户基本信息
                    if st.button("📋 查看用户信息"):
                        self.show_user_info(selected_user)
                else:
                    st.session_state.current_user = None
                    st.warning("⚠️ 请选择一个用户ID")
            else:
                st.error("❌ 没有可用的用户数据")
            
            st.markdown("---")
            
            # 系统信息
            st.markdown("### 📊 系统信息")
            if self.available_users:
                st.info(f"📋 可用用户: {len(self.available_users)} 个")
            
            # 清空历史记录
            if st.button("🗑️ 清空对话历史"):
                st.session_state.chat_history = []
                st.success("✅ 对话历史已清空")
            
            # 导出对话记录
            if st.session_state.chat_history:
                if st.button("📥 导出对话记录"):
                    self.export_chat_history()
    
    def show_user_info(self, user_id: str):
        """显示用户信息"""
        try:
            if self.controller:
                # 尝试从健康管理Agent获取用户信息
                health_agent = self.controller._init_health_agent()
                if health_agent:
                    user_info = health_agent.get_user_info(user_id)
                    if 'error' not in user_info:
                        st.markdown("### 👤 用户详细信息")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**用户ID**: {user_info['user_id']}")
                            st.write(f"**年龄**: {user_info['age']}岁")
                            st.write(f"**性别**: {user_info['gender']}")
                            st.write(f"**身高**: {user_info['height']}cm")
                            st.write(f"**体重**: {user_info['weight']}kg")
                            st.write(f"**BMI**: {user_info['bmi']:.2f}")
                        
                        with col2:
                            st.write(f"**职业**: {user_info['occupation']}")
                            st.write(f"**运动频率**: {user_info['exercise_frequency']}")
                            st.write(f"**睡眠质量**: {user_info['sleep_quality']}")
                            st.write(f"**压力水平**: {user_info['stress_level']}")
                            st.write(f"**BMI分类**: {user_info['bmi_category']}")
                        
                        # 健康状态
                        if user_info.get('chronic_conditions'):
                            st.write(f"**慢性疾病**: {', '.join(user_info['chronic_conditions'])}")
                        if user_info.get('allergies'):
                            st.write(f"**过敏史**: {', '.join(user_info['allergies'])}")
                    else:
                        st.error(f"❌ 获取用户信息失败: {user_info['error']}")
        except Exception as e:
            st.error(f"❌ 显示用户信息失败: {str(e)}")
    
    def render_chat_interface(self):
        """渲染聊天界面"""
        st.markdown('<div class="section-header">💬 健康问答</div>', unsafe_allow_html=True)
        
        # 聊天历史显示
        if st.session_state.chat_history:
            st.markdown("### 📜 对话历史")
            
            for i, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 您:</strong> {message['content']}
                        <br><small>时间: {message['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                elif message['role'] == 'assistant':
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 健康助手:</strong>
                        <br><strong>分类:</strong> {message.get('category', '未知')}
                        <br><strong>置信度:</strong> {message.get('confidence', 0):.2f}
                        <br><strong>回答:</strong>
                        <br>{message['content']}
                        <br><small>时间: {message['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 问题输入
        st.markdown("### ❓ 请输入您的健康问题")
        
        # 问题输入框
        user_question = st.text_area(
            "健康问题",
            placeholder="例如：我最近经常头痛，这是什么原因？",
            height=100,
            help="请详细描述您的健康问题，系统会自动判断问题类型并调用相应的专业Agent"
        )
        
        # 提交按钮
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submit_btn = st.button("🚀 提交问题", type="primary", use_container_width=True)
        
        with col2:
            if st.button("📊 生成健康报告", use_container_width=True):
                self.generate_health_report()
        
        # 处理问题提交
        if submit_btn and user_question.strip():
            if not st.session_state.current_user:
                st.error("❌ 请先在侧边栏选择一个用户ID")
            else:
                self.process_user_question(user_question.strip())
    
    def process_user_question(self, question: str):
        """处理用户问题"""
        try:
            # 添加用户消息到历史
            st.session_state.chat_history.append({
                'role': 'user',
                'content': question,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # 显示处理进度
            with st.spinner("🤖 正在分析您的问题..."):
                # 调用主控制器处理问题
                result = self.controller.process_health_query(question, st.session_state.current_user)
                
                # 添加助手回复到历史
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': result['agent_result'].get('answer', '抱歉，无法获取回答'),
                    'category': result['category'],
                    'confidence': result['classification_confidence'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # 刷新页面显示结果
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 处理问题失败: {str(e)}")
    
    def generate_health_report(self):
        """生成健康报告"""
        if not st.session_state.current_user:
            st.error("❌ 请先选择一个用户ID")
            return
        
        try:
            with st.spinner("📊 正在生成健康报告..."):
                # 调用健康管理Agent生成报告
                health_agent = self.controller._init_health_agent()
                if health_agent:
                    health_agent.set_current_user(st.session_state.current_user)
                    report_file = health_agent.generate_and_save_report()
                    
                    if report_file and not report_file.startswith("生成并保存报告失败"):
                        st.success("✅ 健康报告生成成功！")
                        
                        # 显示报告预览
                        try:
                            with open(report_file, 'r', encoding='utf-8') as f:
                                report_content = f.read()
                                
                            st.markdown("### 📄 健康报告预览")
                            st.markdown(report_content[:1000] + "..." if len(report_content) > 1000 else report_content)
                            
                            # 提供下载链接
                            st.download_button(
                                label="📥 下载完整报告",
                                data=report_content,
                                file_name=f"health_report_{st.session_state.current_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown"
                            )
                        except Exception as e:
                            st.error(f"❌ 读取报告失败: {str(e)}")
                    else:
                        st.error(f"❌ 报告生成失败: {report_file}")
        except Exception as e:
            st.error(f"❌ 生成健康报告失败: {str(e)}")
    
    def export_chat_history(self):
        """导出对话历史"""
        try:
            # 转换为DataFrame
            df = pd.DataFrame(st.session_state.chat_history)
            
            # 创建CSV内容
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            
            # 提供下载
            st.download_button(
                label="📥 下载对话记录",
                data=csv,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.success("✅ 对话记录已准备下载")
            
        except Exception as e:
            st.error(f"❌ 导出对话记录失败: {str(e)}")
    
    def render_footer(self):
        """渲染页脚"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; margin-top: 2rem;">
            <p>🏥 智能健康管理系统 | 基于Qwen-Max AI技术 | 提供专业健康咨询服务</p>
            <p><small>⚠️ 本系统仅供参考，不能替代专业医疗诊断，如有紧急情况请及时就医</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """运行应用"""
        # 渲染页面头部
        self.render_header()
        
        # 初始化控制器
        if not self.initialize_controller():
            st.stop()
        
        # 渲染侧边栏
        self.render_sidebar()
        
        # 渲染聊天界面
        self.render_chat_interface()
        
        # 渲染页脚
        self.render_footer()

def main():
    """主函数"""
    app = HealthGUIApp()
    app.run()

if __name__ == "__main__":
    main()
