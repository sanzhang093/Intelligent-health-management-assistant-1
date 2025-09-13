#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试综合健康报告功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.health_management_agent import HealthManagementAgent

def test_comprehensive_report():
    """测试综合健康报告"""
    print("📋 综合健康报告测试")
    print("=" * 60)
    
    try:
        # 初始化Agent
        agent = HealthManagementAgent()
        print("✅ Agent初始化成功")
        
        # 设置测试用户
        agent.set_current_user("user_001")
        print("✅ 设置用户成功")
        
        # 测试综合健康报告
        print("\n📊 生成综合健康报告...")
        report = agent.get_comprehensive_health_report()
        
        print("\n📋 综合健康报告:")
        print("=" * 60)
        print(report)
        print("=" * 60)
        
        # 检查报告质量
        if report and len(report) > 100:
            print("\n✅ 综合健康报告生成成功")
            print(f"📊 报告长度: {len(report)} 字符")
        else:
            print("\n❌ 综合健康报告生成失败或内容过短")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_comprehensive_report()
