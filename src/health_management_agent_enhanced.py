#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强版智能健康管理Agent

基于Qwen-Max模型的思考型健康管理助手
支持用户选择功能，确保每次运行都能成功生成.md报告
提供健康趋势分析、疾病风险评估、个性化健康计划、长期健康规划
"""

import json
import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import dashscope

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model

# 导入工具类
from tools.health_management_tools import HealthAnalysisTool, HealthPlanTool, HealthRiskTool

# 配置 DashScope API Key
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
dashscope.api_key = DASHSCOPE_API_KEY
dashscope.timeout = 60  # 设置超时时间为 60 秒

logger = logging.getLogger(__name__)

class EnhancedHealthManagementAgent:
    """增强版智能健康管理Agent"""
    
    def __init__(self):
        self.llm_config = {
            'model': 'qwen-max',
            'timeout': 60,
            'retry_count': 3,
        }
        self.assistant = self._init_assistant()
        self.current_user = None
        self.available_users = self._load_available_users()
    
    def _init_assistant(self) -> Assistant:
        """初始化助手"""
        try:
            system_prompt = self._get_system_prompt()
            
            assistant = Assistant(
                llm=self.llm_config,
                name='智能健康管理助手',
                description='专业的健康管理顾问，提供健康趋势分析、疾病风险评估、个性化健康计划和长期健康规划',
                system_message=system_prompt
            )
            
            logger.info("健康管理助手初始化成功")
            return assistant
        except Exception as e:
            logger.error(f"健康管理助手初始化失败: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的健康管理顾问，具有丰富的医学知识和健康管理经验。

你的职责是：
1. 健康趋势分析：分析用户的健康数据变化趋势，识别潜在的健康问题
2. 疾病风险评估：基于用户的身体指标和生活方式，评估患病的风险
3. 个性化健康计划：制定符合用户实际情况的健康改善计划
4. 长期健康规划：为用户提供可持续的健康管理策略

分析原则：
- 基于客观数据进行分析，避免主观臆断
- 提供科学、实用的健康建议
- 考虑用户的年龄、性别、健康状况等个体差异
- 重点关注可改善的风险因素
- 提供具体、可执行的行动建议

回答格式：
请按照以下四个维度进行回答：
1. 健康趋势分析
2. 疾病风险评估  
3. 个性化健康计划
4. 长期健康规划

每个维度都要提供详细、专业的分析和建议。"""
    
    def _load_available_users(self) -> List[str]:
        """加载可用的用户列表"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            profiles_dir = os.path.join(project_root, "data", "profiles")
            
            if not os.path.exists(profiles_dir):
                logger.warning(f"用户数据目录不存在: {profiles_dir}")
                return []
            
            users = []
            for filename in os.listdir(profiles_dir):
                if filename.endswith('_profile.json'):
                    user_id = filename.replace('_profile.json', '')
                    users.append(user_id)
            
            users.sort()  # 按用户ID排序
            logger.info(f"加载了 {len(users)} 个用户")
            return users
            
        except Exception as e:
            logger.error(f"加载用户列表失败: {e}")
            return []
    
    def get_available_users(self) -> List[str]:
        """获取可用用户列表"""
        return self.available_users.copy()
    
    def display_available_users(self) -> None:
        """显示可用用户列表"""
        if not self.available_users:
            print("❌ 没有找到可用的用户数据")
            return
        
        print(f"\n📋 可用用户列表 (共 {len(self.available_users)} 个用户):")
        print("=" * 60)
        
        # 每行显示5个用户
        for i in range(0, len(self.available_users), 5):
            row_users = self.available_users[i:i+5]
            user_display = []
            for user in row_users:
                user_display.append(f"{user:>12}")
            print(" | ".join(user_display))
        
        print("=" * 60)
    
    def set_current_user(self, user_id: str) -> bool:
        """设置当前用户"""
        if user_id not in self.available_users:
            print(f"❌ 用户 {user_id} 不存在，请从可用用户列表中选择")
            return False
        
        self.current_user = user_id
        logger.info(f"设置当前用户: {user_id}")
        print(f"✅ 已选择用户: {user_id}")
        return True
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户基本信息"""
        try:
            from tools.health_management_tools import HealthDataExtractor
            extractor = HealthDataExtractor()
            profile = extractor.get_user_profile(user_id)
            
            if not profile:
                return {"error": f"无法获取用户 {user_id} 的信息"}
            
            # 计算BMI
            bmi = profile.demographics.calculate_bmi()
            bmi_category = profile.demographics.get_bmi_category()
            
            return {
                "user_id": profile.user_id,
                "age": profile.demographics.age,
                "gender": profile.demographics.gender,
                "height": profile.demographics.height,
                "weight": profile.demographics.weight,
                "bmi": round(bmi, 2),
                "bmi_category": bmi_category,
                "occupation": profile.demographics.occupation,
                "location": profile.demographics.location,
                "chronic_conditions": profile.health_status.chronic_conditions,
                "allergies": profile.health_status.allergies,
                "current_medications": profile.health_status.current_medications,
                "exercise_frequency": profile.lifestyle.exercise_frequency,
                "exercise_type": profile.lifestyle.exercise_type,
                "diet_type": profile.lifestyle.diet_type,
                "sleep_hours": profile.lifestyle.sleep_hours,
                "sleep_quality": profile.lifestyle.sleep_quality,
                "stress_level": profile.lifestyle.stress_level,
                "smoking": profile.lifestyle.smoking,
                "alcohol_consumption": profile.lifestyle.alcohol_consumption,
                "work_schedule": profile.lifestyle.work_schedule,
                "primary_goals": profile.health_goals.primary_goals,
                "target_weight": profile.health_goals.target_weight
            }
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return {"error": str(e)}
    
    def _get_health_analysis_data(self, user_id: str) -> Dict[str, Any]:
        """获取健康分析数据"""
        try:
            from tools.health_management_tools import HealthAnalysisEngine
            engine = HealthAnalysisEngine()
            return engine.analyze_health_trend(user_id)
        except Exception as e:
            logger.error(f"获取健康分析数据失败: {e}")
            return {"error": str(e)}
    
    def _get_health_plan_data(self, user_id: str) -> Dict[str, Any]:
        """获取健康计划数据"""
        try:
            from tools.health_management_tools import HealthPlanGenerator
            generator = HealthPlanGenerator()
            return generator.generate_personalized_plan(user_id)
        except Exception as e:
            logger.error(f"获取健康计划数据失败: {e}")
            return {"error": str(e)}
    
    def _get_health_risk_data(self, user_id: str) -> Dict[str, Any]:
        """获取健康风险数据"""
        try:
            from tools.health_management_tools import HealthRiskAssessment
            assessor = HealthRiskAssessment()
            return assessor.assess_disease_risk(user_id)
        except Exception as e:
            logger.error(f"获取健康风险数据失败: {e}")
            return {"error": str(e)}
    
    def _call_qwen_with_retry(self, messages: List[Dict], max_retries: int = 3) -> str:
        """调用Qwen模型，带重试机制"""
        for attempt in range(max_retries):
            try:
                print(f"🤖 正在询问Qwen模型... (尝试 {attempt + 1}/{max_retries})")
                response = self.assistant.run(messages)
                
                # 处理响应 - run()返回生成器，需要转换为列表
                if hasattr(response, '__iter__'):
                    response_list = list(response)
                    if len(response_list) > 0:
                        # 查找最后一个有内容的assistant消息
                        for msg_list in reversed(response_list):
                            if isinstance(msg_list, list) and len(msg_list) > 0:
                                for msg in msg_list:
                                    if isinstance(msg, dict) and msg.get('role') == 'assistant':
                                        content = msg.get('content', '')
                                        if content and content.strip():
                                            return content
                        # 如果没有找到assistant消息，返回最后一个消息的内容
                        last_msg_list = response_list[-1]
                        if isinstance(last_msg_list, list) and len(last_msg_list) > 0:
                            last_msg = last_msg_list[-1]
                            if isinstance(last_msg, dict):
                                return last_msg.get('content', '无法获取响应')
                            else:
                                return str(last_msg)
                
                return '抱歉，我无法处理您的健康查询。'
                
            except Exception as e:
                logger.warning(f"Qwen模型调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise e
                print(f"⏳ 等待2秒后重试...")
                import time
                time.sleep(2)
        
        return '抱歉，多次尝试后仍无法获取响应。'
    
    def get_comprehensive_health_report(self, user_id: Optional[str] = None) -> str:
        """获取综合健康报告"""
        try:
            target_user = user_id or self.current_user
            if not target_user:
                return "请先设置用户ID"
            
            # 获取所有分析数据
            print(f"\n🔍 生成综合报告用户: {target_user}")
            analysis_data = self._get_health_analysis_data(target_user)
            plan_data = self._get_health_plan_data(target_user)
            risk_data = self._get_health_risk_data(target_user)
            
            # 检查数据获取是否成功
            if 'error' in analysis_data:
                return f"获取健康分析数据失败: {analysis_data['error']}"
            if 'error' in plan_data:
                return f"获取健康计划数据失败: {plan_data['error']}"
            if 'error' in risk_data:
                return f"获取健康风险数据失败: {risk_data['error']}"
            
            # 显示调试信息
            print(f"📋 健康分析数据: {len(str(analysis_data))} 字符")
            print(f"📋 健康计划数据: {len(str(plan_data))} 字符") 
            print(f"📋 风险评估数据: {len(str(risk_data))} 字符")
            
            # 构建综合报告提示
            prompt = f"""
基于以下完整的用户健康数据，请提供一份综合的健康管理报告：

用户ID: {target_user}
分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 健康分析数据 ===
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

=== 健康计划数据 ===
{json.dumps(plan_data, ensure_ascii=False, indent=2)}

=== 风险评估数据 ===
{json.dumps(risk_data, ensure_ascii=False, indent=2)}

请从以下四个维度提供一份完整、专业的健康管理报告：

1. 健康趋势分析
   - 当前健康状况总结
   - 关键健康指标分析
   - 健康变化趋势识别
   - 需要关注的问题

2. 疾病风险评估
   - 总体风险等级评估
   - 具体疾病风险分析
   - 风险因素识别
   - 预防建议

3. 个性化健康计划
   - 短期目标设定
   - 具体行动计划
   - 监测指标安排
   - 时间进度规划

4. 长期健康规划
   - 长期健康目标
   - 可持续管理策略
   - 定期评估计划
   - 健康维护建议

请提供详细、专业、可执行的健康管理建议。
"""
            
            messages = [{'role': 'user', 'content': prompt}]
            return self._call_qwen_with_retry(messages)
                
        except Exception as e:
            logger.error(f"生成综合健康报告失败: {e}")
            return f'生成综合健康报告失败：{str(e)}'
    
    def save_report_to_file(self, report_content: str, user_id: str, report_type: str = "comprehensive") -> str:
        """保存报告到文件，确保成功保存"""
        try:
            import os
            from datetime import datetime
            
            # 创建报告目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            reports_dir = os.path.join(project_root, "reports")
            
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                print(f"📁 创建报告目录: {reports_dir}")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_health_report_{user_id}_{timestamp}.md"
            filepath = os.path.join(reports_dir, filename)
            
            # 确保报告内容不为空
            if not report_content or not report_content.strip():
                report_content = f"# 健康报告生成失败\n\n用户ID: {user_id}\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n报告内容生成失败，请检查用户数据和系统配置。"
            
            # 保存报告
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# 智能健康管理报告\n\n")
                f.write(f"**用户ID**: {user_id}\n")
                f.write(f"**报告类型**: {report_type}\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(report_content)
            
            # 验证文件是否成功保存
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"✅ 报告已成功保存到: {filepath}")
                print(f"📊 文件大小: {os.path.getsize(filepath)} 字节")
                return filepath
            else:
                raise Exception("文件保存失败或文件为空")
            
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            # 尝试保存错误报告
            try:
                error_filepath = os.path.join(reports_dir, f"error_report_{user_id}_{timestamp}.md")
                with open(error_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# 报告生成错误\n\n")
                    f.write(f"**用户ID**: {user_id}\n")
                    f.write(f"**错误时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"**错误信息**: {str(e)}\n\n")
                    f.write("请检查系统配置和用户数据。")
                print(f"⚠️ 错误报告已保存到: {error_filepath}")
                return error_filepath
            except:
                return f"保存报告失败：{str(e)}"
    
    def analyze_health_query(self, query: str) -> Dict[str, Any]:
        """分析健康查询问题"""
        try:
            if not self.current_user:
                return {
                    'answer': '请先选择用户',
                    'confidence': 0.0,
                    'sources_count': 0
                }
            
            # 获取用户健康数据
            health_data = self._get_health_analysis_data(self.current_user)
            health_plan = self._get_health_plan_data(self.current_user)
            health_risk = self._get_health_risk_data(self.current_user)
            
            # 构建分析提示
            analysis_prompt = f"""
用户问题：{query}

用户健康数据：
{json.dumps(health_data, ensure_ascii=False, indent=2)}

健康计划数据：
{json.dumps(health_plan, ensure_ascii=False, indent=2)}

健康风险数据：
{json.dumps(health_risk, ensure_ascii=False, indent=2)}

请基于以上数据，对用户的问题进行专业的健康分析，提供详细的建议和指导。
"""
            
            # 调用Qwen进行分析
            messages = [
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self._call_qwen_with_retry(messages)
            
            return {
                'answer': response,
                'confidence': 0.85,  # 健康评估的置信度
                'sources_count': 3   # 基于三个数据源
            }
            
        except Exception as e:
            logger.error(f"健康查询分析失败: {e}")
            return {
                'answer': f'健康分析失败: {str(e)}',
                'confidence': 0.0,
                'sources_count': 0
            }

    def generate_and_save_report(self, user_id: Optional[str] = None, report_type: str = "comprehensive") -> str:
        """生成并保存健康报告，确保成功"""
        try:
            target_user = user_id or self.current_user
            if not target_user:
                return "请先设置用户ID"
            
            print(f"\n🚀 开始为用户 {target_user} 生成健康报告...")
            
            # 生成报告内容
            report_content = self.get_comprehensive_health_report(target_user)
            
            if not report_content or report_content.strip() == "":
                report_content = f"# 健康报告生成失败\n\n用户ID: {target_user}\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n报告内容生成失败，请检查用户数据和系统配置。"
            
            # 保存报告到文件
            report_file = self.save_report_to_file(report_content, target_user, report_type)
            
            print(f"🎉 健康报告生成完成！")
            print(f"📄 报告文件: {report_file}")
            
            return report_file
            
        except Exception as e:
            logger.error(f"生成并保存报告失败: {e}")
            return f"生成并保存报告失败：{str(e)}"

def main():
    """主函数 - 交互式健康管理Agent"""
    print("🏥 增强版智能健康管理Agent")
    print("=" * 60)
    
    try:
        # 初始化Agent
        agent = EnhancedHealthManagementAgent()
        print("✅ 健康管理Agent初始化成功")
        
        # 显示可用用户
        agent.display_available_users()
        
        # 用户选择循环
        while True:
            print(f"\n📋 当前用户: {agent.current_user if agent.current_user else '未选择'}")
            print("\n请选择操作:")
            print("1. 选择用户")
            print("2. 查看用户信息")
            print("3. 生成健康报告")
            print("4. 退出")
            
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                # 选择用户
                agent.display_available_users()
                user_input = input("\n请输入用户ID (如 user_001): ").strip()
                if user_input:
                    if agent.set_current_user(user_input):
                        # 显示用户基本信息
                        user_info = agent.get_user_info(user_input)
                        if 'error' not in user_info:
                            print(f"\n👤 用户信息:")
                            print(f"   年龄: {user_info['age']}岁")
                            print(f"   性别: {user_info['gender']}")
                            print(f"   BMI: {user_info['bmi']:.2f}")
                            print(f"   身高: {user_info['height']}cm")
                            print(f"   体重: {user_info['weight']}kg")
                            print(f"   职业: {user_info['occupation']}")
                            print(f"   运动频率: {user_info['exercise_frequency']}")
                            print(f"   睡眠质量: {user_info['sleep_quality']}")
                            print(f"   压力水平: {user_info['stress_level']}")
                        else:
                            print(f"❌ 获取用户信息失败: {user_info['error']}")
            
            elif choice == "2":
                # 查看用户信息
                if not agent.current_user:
                    print("❌ 请先选择用户")
                    continue
                
                user_info = agent.get_user_info(agent.current_user)
                if 'error' not in user_info:
                    print(f"\n👤 用户 {agent.current_user} 的详细信息:")
                    print("=" * 50)
                    for key, value in user_info.items():
                        print(f"{key}: {value}")
                else:
                    print(f"❌ 获取用户信息失败: {user_info['error']}")
            
            elif choice == "3":
                # 生成健康报告
                if not agent.current_user:
                    print("❌ 请先选择用户")
                    continue
                
                print(f"\n🚀 开始为用户 {agent.current_user} 生成健康报告...")
                report_file = agent.generate_and_save_report()
                
                if report_file and not report_file.startswith("生成并保存报告失败"):
                    print(f"✅ 报告生成成功！")
                    print(f"📄 报告文件: {report_file}")
                    
                    # 询问是否查看报告预览
                    preview = input("\n是否查看报告预览？(y/n): ").strip().lower()
                    if preview == 'y':
                        try:
                            with open(report_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                print("\n📄 报告预览:")
                                print("=" * 60)
                                print(content[:500] + "..." if len(content) > 500 else content)
                                print("=" * 60)
                        except Exception as e:
                            print(f"❌ 读取报告失败: {e}")
                else:
                    print(f"❌ 报告生成失败: {report_file}")
            
            elif choice == "4":
                # 退出
                print("👋 感谢使用智能健康管理Agent！")
                break
            
            else:
                print("❌ 无效选择，请输入 1-4")
        
    except Exception as e:
        print(f"❌ 程序运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

