#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能健康管理桌面应用
基于tkinter构建的桌面GUI应用

功能：
1. 桌面窗口界面
2. 用户问答交互
3. 症状问诊和健康评估
4. 回答和报告展示
5. 历史记录管理
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import sys
import json
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import webbrowser

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主控制器
from main_choice import HealthMainController

class HealthDesktopApp:
    """智能健康管理桌面应用"""
    
    def __init__(self):
        """初始化桌面应用"""
        self.root = tk.Tk()
        self.controller = None
        self.available_users = []
        self.chat_history = []
        self.current_user = None
        
        # 设置窗口属性
        self.setup_window()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化控制器
        self.initialize_controller()
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("🏥 智能健康管理系统")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            # 可以设置自定义图标
            pass
        except:
            pass
        
        # 设置窗口居中
        self.center_window()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 创建标题
        self.create_header(main_frame)
        
        # 创建左侧面板
        self.create_left_panel(main_frame)
        
        # 创建主面板
        self.create_main_panel(main_frame)
        
        # 创建状态栏
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """创建标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 标题
        title_label = ttk.Label(
            header_frame, 
            text="🏥 智能健康管理系统", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # 状态指示器
        self.status_label = ttk.Label(
            header_frame, 
            text="🔄 正在初始化...", 
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        left_frame = ttk.LabelFrame(parent, text="系统设置", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 用户选择
        ttk.Label(left_frame, text="👤 选择用户:").pack(anchor=tk.W, pady=(0, 5))
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(
            left_frame, 
            textvariable=self.user_var,
            state="readonly",
            width=20
        )
        self.user_combo.pack(fill=tk.X, pady=(0, 10))
        self.user_combo.bind("<<ComboboxSelected>>", self.on_user_selected)
        
        # 查看用户信息按钮
        self.user_info_btn = ttk.Button(
            left_frame,
            text="📋 查看用户信息",
            command=self.show_user_info,
            state="disabled"
        )
        self.user_info_btn.pack(fill=tk.X, pady=(0, 10))
        
        # 分隔线
        ttk.Separator(left_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # 问题类型选择
        ttk.Label(left_frame, text="🎯 问题类型:").pack(anchor=tk.W, pady=(0, 5))
        
        self.question_type_var = tk.StringVar(value="自动判断")
        question_types = ["自动判断", "症状问诊", "健康管理"]
        
        for qtype in question_types:
            ttk.Radiobutton(
                left_frame,
                text=qtype,
                variable=self.question_type_var,
                value=qtype
            ).pack(anchor=tk.W, pady=2)
        
        # 分隔线
        ttk.Separator(left_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # 操作按钮
        ttk.Label(left_frame, text="🛠️ 操作:").pack(anchor=tk.W, pady=(0, 5))
        
        self.generate_report_btn = ttk.Button(
            left_frame,
            text="📊 生成健康报告",
            command=self.generate_health_report,
            state="disabled"
        )
        self.generate_report_btn.pack(fill=tk.X, pady=2)
        
        self.clear_history_btn = ttk.Button(
            left_frame,
            text="🗑️ 清空历史",
            command=self.clear_chat_history
        )
        self.clear_history_btn.pack(fill=tk.X, pady=2)
        
        self.export_btn = ttk.Button(
            left_frame,
            text="📥 导出记录",
            command=self.export_chat_history
        )
        self.export_btn.pack(fill=tk.X, pady=2)
        
        # 分隔线
        ttk.Separator(left_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # 系统信息
        ttk.Label(left_frame, text="📊 系统信息:").pack(anchor=tk.W, pady=(0, 5))
        
        self.system_info_text = tk.Text(
            left_frame,
            height=6,
            width=25,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.system_info_text.pack(fill=tk.BOTH, expand=True)
    
    def create_main_panel(self, parent):
        """创建主面板"""
        main_panel = ttk.Frame(parent)
        main_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_panel.columnconfigure(0, weight=1)
        main_panel.rowconfigure(0, weight=1)
        
        # 创建聊天区域
        self.create_chat_area(main_panel)
        
        # 创建输入区域
        self.create_input_area(main_panel)
    
    def create_chat_area(self, parent):
        """创建聊天区域"""
        chat_frame = ttk.LabelFrame(parent, text="💬 对话历史", padding="5")
        chat_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # 创建聊天文本框
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED,
            bg="#f8f9fa"
        )
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置标签样式
        self.chat_text.tag_configure("user", foreground="#2196f3", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("assistant", foreground="#9c27b0", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("system", foreground="#4caf50", font=("Arial", 9, "italic"))
        self.chat_text.tag_configure("timestamp", foreground="#666666", font=("Arial", 8))
    
    def create_input_area(self, parent):
        """创建输入区域"""
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # 问题输入标签
        ttk.Label(input_frame, text="❓ 请输入您的健康问题:").pack(anchor=tk.W, pady=(0, 5))
        
        # 问题输入文本框
        self.question_text = tk.Text(
            input_frame,
            height=4,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        self.question_text.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X)
        
        # 提交按钮
        self.submit_btn = ttk.Button(
            button_frame,
            text="🚀 提交问题",
            command=self.submit_question,
            state="disabled"
        )
        self.submit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空输入按钮
        ttk.Button(
            button_frame,
            text="🗑️ 清空输入",
            command=self.clear_input
        ).pack(side=tk.LEFT)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 状态信息
        self.status_text = ttk.Label(
            status_frame,
            text="就绪",
            font=("Arial", 9)
        )
        self.status_text.pack(side=tk.LEFT)
        
        # 当前用户显示
        self.current_user_label = ttk.Label(
            status_frame,
            text="当前用户: 未选择",
            font=("Arial", 9)
        )
        self.current_user_label.pack(side=tk.RIGHT)
    
    def initialize_controller(self):
        """初始化控制器"""
        def init_thread():
            try:
                self.update_status("🔄 正在初始化系统...")
                self.controller = HealthMainController()
                self.available_users = self.controller.get_available_users()
                
                # 更新用户列表
                self.root.after(0, self.update_user_list)
                
                # 更新系统信息
                self.root.after(0, self.update_system_info)
                
                # 更新状态
                self.root.after(0, lambda: self.update_status("✅ 系统初始化完成"))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"❌ 初始化失败: {str(e)}"))
                messagebox.showerror("初始化错误", f"系统初始化失败:\n{str(e)}")
        
        # 在后台线程中初始化
        threading.Thread(target=init_thread, daemon=True).start()
    
    def update_user_list(self):
        """更新用户列表"""
        if self.available_users:
            self.user_combo['values'] = [""] + self.available_users
            self.user_combo.current(0)
        else:
            self.user_combo['values'] = ["没有可用用户"]
            self.user_combo.current(0)
    
    def update_system_info(self):
        """更新系统信息"""
        info_text = f"""系统状态: 正常
可用用户: {len(self.available_users)} 个
控制器: 已初始化
时间: {datetime.now().strftime('%H:%M:%S')}"""
        
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(1.0, info_text)
    
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.config(text=message)
        self.status_text.config(text=message)
        self.root.update_idletasks()
    
    def on_user_selected(self, event=None):
        """用户选择事件"""
        selected_user = self.user_var.get()
        if selected_user and selected_user != "没有可用用户":
            self.current_user = selected_user
            self.current_user_label.config(text=f"当前用户: {selected_user}")
            self.user_info_btn.config(state="normal")
            self.submit_btn.config(state="normal")
            self.generate_report_btn.config(state="normal")
            self.update_status(f"✅ 已选择用户: {selected_user}")
        else:
            self.current_user = None
            self.current_user_label.config(text="当前用户: 未选择")
            self.user_info_btn.config(state="disabled")
            self.submit_btn.config(state="disabled")
            self.generate_report_btn.config(state="disabled")
            self.update_status("⚠️ 请选择一个用户")
    
    def show_user_info(self):
        """显示用户信息"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        
        try:
            # 获取用户信息
            health_agent = self.controller._init_health_agent()
            if health_agent:
                user_info = health_agent.get_user_info(self.current_user)
                if 'error' not in user_info:
                    # 创建用户信息窗口
                    self.create_user_info_window(user_info)
                else:
                    messagebox.showerror("错误", f"获取用户信息失败:\n{user_info['error']}")
        except Exception as e:
            messagebox.showerror("错误", f"显示用户信息失败:\n{str(e)}")
    
    def create_user_info_window(self, user_info):
        """创建用户信息窗口"""
        info_window = tk.Toplevel(self.root)
        info_window.title(f"用户信息 - {self.current_user}")
        info_window.geometry("500x400")
        info_window.resizable(False, False)
        
        # 居中显示
        info_window.transient(self.root)
        info_window.grab_set()
        
        # 创建滚动文本框
        text_widget = scrolledtext.ScrolledText(
            info_window,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 格式化用户信息
        info_text = f"""用户详细信息
{'='*50}

基本信息:
  用户ID: {user_info['user_id']}
  年龄: {user_info['age']}岁
  性别: {user_info['gender']}
  身高: {user_info['height']}cm
  体重: {user_info['weight']}kg
  BMI: {user_info['bmi']:.2f}
  BMI分类: {user_info['bmi_category']}

职业信息:
  职业: {user_info['occupation']}
  工作地点: {user_info.get('location', '未知')}

健康状态:
  运动频率: {user_info['exercise_frequency']}
  运动类型: {user_info.get('exercise_type', '未知')}
  饮食类型: {user_info['diet_type']}
  睡眠时长: {user_info['sleep_hours']}小时
  睡眠质量: {user_info['sleep_quality']}
  压力水平: {user_info['stress_level']}
  吸烟: {'是' if user_info.get('smoking') else '否'}
  饮酒: {user_info.get('alcohol_consumption', '未知')}

医疗信息:
  慢性疾病: {', '.join(user_info.get('chronic_conditions', [])) or '无'}
  过敏史: {', '.join(user_info.get('allergies', [])) or '无'}
  当前用药: {', '.join(user_info.get('current_medications', [])) or '无'}

健康目标:
  主要目标: {', '.join(user_info.get('primary_goals', [])) or '无'}
  目标体重: {user_info.get('target_weight', '未设定')}kg
"""
        
        text_widget.insert(1.0, info_text)
        text_widget.config(state=tk.DISABLED)
        
        # 关闭按钮
        ttk.Button(
            info_window,
            text="关闭",
            command=info_window.destroy
        ).pack(pady=10)
    
    def submit_question(self):
        """提交问题"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        
        question = self.question_text.get(1.0, tk.END).strip()
        if not question:
            messagebox.showwarning("警告", "请输入问题")
            return
        
        # 添加用户消息到聊天记录
        self.add_message_to_chat("user", question)
        
        # 清空输入框
        self.clear_input()
        
        # 在后台线程中处理问题
        def process_question():
            try:
                self.update_status("🤖 正在分析问题...")
                
                question_type = self.question_type_var.get()
                
                if question_type == "自动判断":
                    result = self.controller.process_health_query(question, self.current_user)
                elif question_type == "症状问诊":
                    if hasattr(self.controller, 'symptom_agent') and self.controller.symptom_agent:
                        agent = self.controller._init_symptom_agent()
                        if agent:
                            agent.set_current_user(self.current_user)
                            agent_result = agent.analyze_health_query(question, self.current_user)
                            result = {
                                'category': '症状问诊',
                                'classification_confidence': 1.0,
                                'classification_reason': '用户手动选择症状问诊',
                                'agent_result': agent_result,
                                'timestamp': datetime.now().isoformat()
                            }
                        else:
                            # 降级处理
                            health_agent = self.controller._init_health_agent()
                            health_agent.set_current_user(self.current_user)
                            agent_result = health_agent.analyze_health_query(question)
                            result = {
                                'category': '症状问诊(由健康管理Agent处理)',
                                'classification_confidence': 0.8,
                                'classification_reason': '症状问诊Agent不可用，使用健康管理Agent',
                                'agent_result': agent_result,
                                'timestamp': datetime.now().isoformat()
                            }
                    else:
                        # 降级处理
                        health_agent = self.controller._init_health_agent()
                        health_agent.set_current_user(self.current_user)
                        agent_result = health_agent.analyze_health_query(question)
                        result = {
                            'category': '症状问诊(由健康管理Agent处理)',
                            'classification_confidence': 0.8,
                            'classification_reason': '症状问诊Agent不可用，使用健康管理Agent',
                            'agent_result': agent_result,
                            'timestamp': datetime.now().isoformat()
                        }
                else:  # 健康管理
                    health_agent = self.controller._init_health_agent()
                    health_agent.set_current_user(self.current_user)
                    agent_result = health_agent.analyze_health_query(question)
                    result = {
                        'category': '健康管理',
                        'classification_confidence': 1.0,
                        'classification_reason': '用户手动选择健康管理',
                        'agent_result': agent_result,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.display_result(result))
                
            except Exception as e:
                error_msg = f"处理问题失败: {str(e)}"
                self.root.after(0, lambda: self.update_status(f"❌ {error_msg}"))
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        threading.Thread(target=process_question, daemon=True).start()
    
    def display_result(self, result):
        """显示处理结果"""
        try:
            answer = result['agent_result'].get('answer', '抱歉，无法获取回答')
            category = result['category']
            confidence = result['classification_confidence']
            
            # 格式化回答
            formatted_answer = f"""分类: {category}
置信度: {confidence:.2f}

回答:
{answer}"""
            
            # 添加到聊天记录
            self.add_message_to_chat("assistant", formatted_answer)
            
            # 保存到历史记录
            self.chat_history.append({
                'role': 'assistant',
                'content': formatted_answer,
                'category': category,
                'confidence': confidence,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            self.update_status("✅ 问题处理完成")
            
        except Exception as e:
            error_msg = f"显示结果失败: {str(e)}"
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
    
    def add_message_to_chat(self, role, content):
        """添加消息到聊天区域"""
        self.chat_text.config(state=tk.NORMAL)
        
        # 添加时间戳
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # 添加角色标识
        if role == "user":
            self.chat_text.insert(tk.END, "👤 您: ", "user")
        elif role == "assistant":
            self.chat_text.insert(tk.END, "🤖 健康助手: ", "assistant")
        else:
            self.chat_text.insert(tk.END, "💻 系统: ", "system")
        
        # 添加内容
        self.chat_text.insert(tk.END, f"{content}\n\n")
        
        # 滚动到底部
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
    
    def clear_input(self):
        """清空输入框"""
        self.question_text.delete(1.0, tk.END)
    
    def clear_chat_history(self):
        """清空聊天历史"""
        if messagebox.askyesno("确认", "确定要清空所有对话历史吗？"):
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)
            self.chat_history.clear()
            self.update_status("✅ 对话历史已清空")
    
    def export_chat_history(self):
        """导出聊天历史"""
        if not self.chat_history:
            messagebox.showinfo("提示", "没有对话历史可以导出")
            return
        
        # 选择保存文件
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存对话记录"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("智能健康管理系统 - 对话记录\n")
                    f.write("="*50 + "\n\n")
                    
                    for i, message in enumerate(self.chat_history, 1):
                        f.write(f"记录 {i}:\n")
                        f.write(f"时间: {message['timestamp']}\n")
                        f.write(f"类型: {message.get('category', '未知')}\n")
                        f.write(f"置信度: {message.get('confidence', 0):.2f}\n")
                        f.write(f"内容:\n{message['content']}\n")
                        f.write("-"*30 + "\n\n")
                
                messagebox.showinfo("成功", f"对话记录已保存到:\n{filename}")
                self.update_status("✅ 对话记录已导出")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败:\n{str(e)}")
    
    def generate_health_report(self):
        """生成健康报告"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        
        def generate_thread():
            try:
                self.update_status("📊 正在生成健康报告...")
                
                health_agent = self.controller._init_health_agent()
                if health_agent:
                    health_agent.set_current_user(self.current_user)
                    report_file = health_agent.generate_and_save_report()
                    
                    if report_file and not report_file.startswith("生成并保存报告失败"):
                        self.root.after(0, lambda: self.show_report_window(report_file))
                        self.root.after(0, lambda: self.update_status("✅ 健康报告生成完成"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("错误", f"报告生成失败:\n{report_file}"))
                        self.root.after(0, lambda: self.update_status("❌ 报告生成失败"))
                        
            except Exception as e:
                error_msg = f"生成健康报告失败: {str(e)}"
                self.root.after(0, lambda: self.update_status(f"❌ {error_msg}"))
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def show_report_window(self, report_file):
        """显示报告窗口"""
        try:
            # 读取报告内容
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # 创建报告窗口
            report_window = tk.Toplevel(self.root)
            report_window.title(f"健康报告 - {self.current_user}")
            report_window.geometry("800x600")
            
            # 创建文本框
            text_widget = scrolledtext.ScrolledText(
                report_window,
                wrap=tk.WORD,
                font=("Arial", 10)
            )
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 插入报告内容
            text_widget.insert(1.0, report_content)
            text_widget.config(state=tk.DISABLED)
            
            # 按钮框架
            button_frame = ttk.Frame(report_window)
            button_frame.pack(pady=10)
            
            # 保存按钮
            ttk.Button(
                button_frame,
                text="💾 另存为",
                command=lambda: self.save_report_as(report_content)
            ).pack(side=tk.LEFT, padx=5)
            
            # 关闭按钮
            ttk.Button(
                button_frame,
                text="关闭",
                command=report_window.destroy
            ).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示报告失败:\n{str(e)}")
    
    def save_report_as(self, content):
        """另存为报告"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存健康报告"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"报告已保存到:\n{filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{str(e)}")
    
    def on_closing(self):
        """关闭窗口事件"""
        if messagebox.askokcancel("退出", "确定要退出智能健康管理系统吗？"):
            self.root.destroy()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = HealthDesktopApp()
        app.run()
    except Exception as e:
        messagebox.showerror("启动错误", f"应用启动失败:\n{str(e)}")

if __name__ == "__main__":
    main()
