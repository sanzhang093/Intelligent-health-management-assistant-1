#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能健康管理主控制器
根据用户问题自动归类并调用相应的专业Agent进行处理

功能：
1. 使用Qwen-Max模型对用户问题进行智能归类
2. 症状问诊类问题 -> 调用health_ask_quickly.py
3. 健康评估类问题 -> 调用health_management_agent_enhanced.py
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import dashscope

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model

# 导入两个专业Agent
from health_ask_quickly import HealthAskQuickly
from health_management_agent_enhanced import EnhancedHealthManagementAgent

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置 DashScope API Key
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
dashscope.api_key = DASHSCOPE_API_KEY
dashscope.timeout = 60

class HealthMainController:
    """智能健康管理主控制器"""
    
    def __init__(self):
        """初始化主控制器"""
        self.llm_config = {
            'model': 'qwen-max',
            'timeout': 60,
            'retry_count': 3,
        }
        
        # 初始化分类助手
        self.classifier = self._init_classifier()
        
        # 初始化两个专业Agent
        self.symptom_agent = None  # 症状问诊Agent
        self.health_agent = None   # 健康管理Agent
        
        # 当前用户
        self.current_user = None
        
        print("🏥 智能健康管理主控制器初始化完成")
    
    def _init_classifier(self) -> Assistant:
        """初始化问题分类助手"""
        try:
            system_prompt = self._get_classifier_prompt()
            
            classifier = Assistant(
                llm=self.llm_config,
                name='健康问题分类器',
                description='智能分析用户健康问题并归类到相应专业Agent',
                system_message=system_prompt
            )
            
            logger.info("问题分类器初始化成功")
            return classifier
            
        except Exception as e:
            logger.error(f"问题分类器初始化失败: {e}")
            raise
    
    def _get_classifier_prompt(self) -> str:
        """获取分类器系统提示词"""
        return """你是一位专业的健康问题分类专家，负责分析用户的健康相关问题并将其归类到相应的专业处理模块。

你的任务是根据用户的问题内容，判断应该使用哪个专业Agent来处理：

## 两个专业Agent的功能范围：

### 1. 症状问诊Agent (health_ask_quickly.py)
**适用场景：**
- 用户描述具体症状（如头痛、发热、咳嗽、胸痛等）
- 询问症状的可能原因
- 症状的严重程度评估
- 紧急医疗情况判断
- 用药相关问题
- 疾病诊断相关咨询
- 急性症状处理建议

**关键词示例：**
- 症状类：头痛、发热、咳嗽、胸痛、腹痛、恶心、呕吐、腹泻、皮疹、瘙痒
- 疾病类：感冒、发烧、高血压、糖尿病、心脏病、胃病
- 紧急类：胸痛、呼吸困难、意识不清、严重出血
- 用药类：药物副作用、用药方法、药物相互作用

### 2. 健康管理Agent (health_management_agent_enhanced.py)
**适用场景：**
- 健康趋势分析和评估
- 长期健康规划
- 生活方式改善建议
- 健康风险评估
- 个性化健康计划制定
- 健康数据分析和解读
- 预防保健建议
- 健康目标设定
- 慢性病管理
- 健康档案管理

**关键词示例：**
- 管理类：健康管理、健康规划、生活方式、健康评估
- 分析类：健康趋势、数据分析、风险评估、健康指标
- 计划类：健康计划、目标设定、改善建议、预防保健
- 长期类：长期规划、慢性病管理、健康维护

## 分类规则：
1. 如果问题涉及具体症状、疾病诊断、紧急医疗情况，选择"症状问诊"
2. 如果问题涉及健康管理、趋势分析、长期规划、生活方式改善，选择"健康管理"
3. 如果问题同时涉及两个方面，优先选择更紧急或更具体的方面
4. 如果不确定，选择"症状问诊"以确保用户安全

## 输出格式：
请严格按照以下JSON格式输出分类结果：
{
    "category": "症状问诊" 或 "健康管理",
    "confidence": 0.0-1.0之间的数值,
    "reason": "分类理由的简要说明"
}

请基于用户问题的具体内容进行准确分类。"""
    
    def classify_health_query(self, query: str) -> Dict[str, Any]:
        """
        使用Qwen-Max模型对健康问题进行分类
        
        Args:
            query: 用户健康问题
            
        Returns:
            分类结果字典
        """
        try:
            print(f"🤖 正在分析问题分类...")
            
            # 构建分类提示
            classification_prompt = f"""
请分析以下用户健康问题，并判断应该使用哪个专业Agent来处理：

用户问题：{query}

请根据问题内容判断：
1. 如果涉及具体症状、疾病诊断、紧急医疗情况 -> 选择"症状问诊"
2. 如果涉及健康管理、趋势分析、长期规划、生活方式改善 -> 选择"健康管理"

请严格按照JSON格式输出结果。
"""
            
            messages = [{'role': 'user', 'content': classification_prompt}]
            response = self.classifier.run(messages)
            
            # 提取分类结果
            classification_result = self._extract_classification(response)
            
            print(f"📊 分类结果: {classification_result['category']} (置信度: {classification_result['confidence']:.2f})")
            print(f"💡 分类理由: {classification_result['reason']}")
            
            return classification_result
            
        except Exception as e:
            logger.error(f"问题分类失败: {e}")
            # 默认分类为症状问诊，确保用户安全
            return {
                "category": "症状问诊",
                "confidence": 0.5,
                "reason": f"分类过程出错，默认选择症状问诊以确保用户安全: {str(e)}"
            }
    
    def _extract_classification(self, response) -> Dict[str, Any]:
        """提取分类结果"""
        try:
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
                                        # 尝试解析JSON
                                        try:
                                            # 查找JSON内容
                                            import re
                                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                            if json_match:
                                                json_str = json_match.group()
                                                result = json.loads(json_str)
                                                
                                                # 验证结果格式
                                                if 'category' in result and 'confidence' in result and 'reason' in result:
                                                    return result
                                        except json.JSONDecodeError:
                                            pass
                                        
                                        # 如果JSON解析失败，尝试文本解析
                                        return self._parse_text_classification(content)
            
            # 默认返回症状问诊
            return {
                "category": "症状问诊",
                "confidence": 0.5,
                "reason": "无法解析分类结果，默认选择症状问诊"
            }
            
        except Exception as e:
            logger.error(f"提取分类结果失败: {e}")
            return {
                "category": "症状问诊",
                "confidence": 0.5,
                "reason": f"提取分类结果失败: {str(e)}"
            }
    
    def _parse_text_classification(self, content: str) -> Dict[str, Any]:
        """从文本中解析分类结果"""
        try:
            content_lower = content.lower()
            
            # 检查关键词
            if any(keyword in content_lower for keyword in ['症状问诊', '症状', '诊断', '疾病', '症状分析']):
                category = "症状问诊"
            elif any(keyword in content_lower for keyword in ['健康管理', '健康评估', '健康规划', '健康分析']):
                category = "健康管理"
            else:
                category = "症状问诊"  # 默认
            
            return {
                "category": category,
                "confidence": 0.7,
                "reason": "基于文本关键词分析"
            }
            
        except Exception as e:
            logger.error(f"文本分类解析失败: {e}")
            return {
                "category": "症状问诊",
                "confidence": 0.5,
                "reason": f"文本解析失败: {str(e)}"
            }
    
    def _init_symptom_agent(self) -> Optional[HealthAskQuickly]:
        """初始化症状问诊Agent"""
        if self.symptom_agent is None:
            try:
                print("🔄 正在初始化症状问诊Agent...")
                self.symptom_agent = HealthAskQuickly()
                print("✅ 症状问诊Agent初始化成功")
            except Exception as e:
                logger.error(f"症状问诊Agent初始化失败: {e}")
                print(f"⚠️ 症状问诊Agent初始化失败，将使用健康管理Agent处理所有问题")
                self.symptom_agent = None
        return self.symptom_agent
    
    def _init_health_agent(self) -> EnhancedHealthManagementAgent:
        """初始化健康管理Agent"""
        if self.health_agent is None:
            try:
                print("🔄 正在初始化健康管理Agent...")
                self.health_agent = EnhancedHealthManagementAgent()
                print("✅ 健康管理Agent初始化成功")
            except Exception as e:
                logger.error(f"健康管理Agent初始化失败: {e}")
                raise
        return self.health_agent
    
    def process_health_query(self, query: str, user_id: str = None) -> Dict[str, Any]:
        """
        处理健康查询的主入口
        
        Args:
            query: 用户健康问题
            user_id: 用户ID（可选）
            
        Returns:
            处理结果字典
        """
        try:
            print(f"\n🔍 开始处理健康查询...")
            print(f"📝 用户问题: {query}")
            
            # 1. 问题分类
            classification = self.classify_health_query(query)
            
            # 2. 根据分类结果调用相应的Agent
            if classification['category'] == "症状问诊":
                print(f"🏥 调用症状问诊Agent处理...")
                agent = self._init_symptom_agent()
                
                if agent is None:
                    # 如果症状问诊Agent初始化失败，使用健康管理Agent处理
                    print(f"⚠️ 症状问诊Agent不可用，使用健康管理Agent处理...")
                    agent = self._init_health_agent()
                    
                    # 设置用户
                    if user_id:
                        agent.set_current_user(user_id)
                    elif self.current_user:
                        agent.set_current_user(self.current_user)
                    
                    # 调用健康管理Agent
                    result = agent.analyze_health_query(query)
                    
                    return {
                        'category': '症状问诊(由健康管理Agent处理)',
                        'classification_confidence': classification['confidence'],
                        'classification_reason': classification['reason'] + " (症状问诊Agent不可用，使用健康管理Agent)",
                        'agent_result': result,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # 设置用户
                    if user_id:
                        agent.set_current_user(user_id)
                    elif self.current_user:
                        agent.set_current_user(self.current_user)
                    
                    # 调用症状问诊Agent
                    result = agent.analyze_health_query(query, user_id)
                    
                    return {
                        'category': '症状问诊',
                        'classification_confidence': classification['confidence'],
                        'classification_reason': classification['reason'],
                        'agent_result': result,
                        'timestamp': datetime.now().isoformat()
                    }
                
            else:  # 健康管理
                print(f"📊 调用健康管理Agent处理...")
                agent = self._init_health_agent()
                
                # 设置用户
                if user_id:
                    agent.set_current_user(user_id)
                elif self.current_user:
                    agent.set_current_user(self.current_user)
                
                # 调用健康管理Agent
                result = agent.analyze_health_query(query)
                
                return {
                    'category': '健康管理',
                    'classification_confidence': classification['confidence'],
                    'classification_reason': classification['reason'],
                    'agent_result': result,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"处理健康查询失败: {e}")
            return {
                'category': '错误',
                'classification_confidence': 0.0,
                'classification_reason': f'处理失败: {str(e)}',
                'agent_result': {
                    'answer': f'抱歉，处理您的问题时出现错误: {str(e)}',
                    'confidence': 0.0,
                    'sources_count': 0
                },
                'timestamp': datetime.now().isoformat()
            }
    
    def set_current_user(self, user_id: str) -> bool:
        """设置当前用户"""
        self.current_user = user_id
        print(f"✅ 已设置当前用户: {user_id}")
        return True
    
    def get_available_users(self) -> List[str]:
        """获取可用用户列表"""
        try:
            # 直接从文件系统获取用户列表，不依赖Agent初始化
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
            logger.info(f"主控制器加载了 {len(users)} 个用户")
            return users
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    def display_available_users(self) -> None:
        """显示可用用户列表"""
        try:
            users = self.get_available_users()
            if not users:
                print("❌ 没有找到可用的用户数据")
                return
            
            print(f"\n📋 可用用户列表 (共 {len(users)} 个用户):")
            print("=" * 60)
            
            # 每行显示5个用户
            for i in range(0, len(users), 5):
                row_users = users[i:i+5]
                user_display = []
                for user in row_users:
                    user_display.append(f"{user:>12}")
                print(" | ".join(user_display))
            
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"显示用户列表失败: {e}")
            print(f"❌ 显示用户列表失败: {e}")

def main():
    """主函数 - 智能健康管理主控制器"""
    print("🏥 智能健康管理主控制器")
    print("=" * 60)
    print("💡 本系统会自动分析您的健康问题并调用相应的专业Agent进行处理")
    print("   - 症状问诊类问题 -> 症状问诊Agent")
    print("   - 健康管理类问题 -> 健康管理Agent")
    print("=" * 60)
    
    try:
        # 初始化主控制器
        controller = HealthMainController()
        
        # 显示可用用户
        controller.display_available_users()
        
        # 用户选择循环
        while True:
            print(f"\n📋 当前用户: {controller.current_user if controller.current_user else '未选择'}")
            print("\n请选择操作:")
            print("1. 选择用户")
            print("2. 健康问答")
            print("3. 退出")
            
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                # 选择用户
                controller.display_available_users()
                user_input = input("\n请输入用户ID (如 user_001): ").strip()
                if user_input:
                    controller.set_current_user(user_input)
            
            elif choice == "2":
                # 健康问答
                if not controller.current_user:
                    print("❌ 请先选择用户")
                    continue
                
                print(f"\n💬 智能健康问答 (用户: {controller.current_user})")
                print("💡 输入 'quit' 或 'exit' 退出问答模式")
                print("=" * 50)
                
                while True:
                    query = input(f"\n❓ 请输入您的健康问题: ").strip()
                    
                    if query.lower() in ['quit', 'exit', '退出']:
                        print("👋 退出问答模式")
                        break
                    
                    if not query:
                        print("⚠️ 请输入有效的问题")
                        continue
                    
                    # 处理健康查询
                    result = controller.process_health_query(query, controller.current_user)
                    
                    print(f"\n📊 处理结果:")
                    print(f"🎯 问题分类: {result['category']}")
                    print(f"📈 分类置信度: {result['classification_confidence']:.2f}")
                    print(f"💡 分类理由: {result['classification_reason']}")
                    
                    print(f"\n📝 专业回答:")
                    agent_result = result['agent_result']
                    print(f"{agent_result.get('answer', '无回答')}")
                    
                    if 'confidence' in agent_result:
                        print(f"\n📊 回答质量:")
                        print(f"   置信度: {agent_result['confidence']:.2f}")
                    
                    if 'sources' in agent_result and agent_result['sources']:
                        print(f"   参考来源: {len(agent_result['sources'])} 个")
                        print(f"\n📚 相关来源:")
                        for i, source in enumerate(agent_result['sources'][:3], 1):
                            if isinstance(source, dict):
                                question = source.get('question', '未知来源')
                                score = source.get('score', 0)
                                print(f"   {i}. {question[:80]}... (相似度: {score:.3f})")
                    
                    print("\n" + "=" * 50)
            
            elif choice == "3":
                # 退出
                print("👋 感谢使用智能健康管理系统！")
                break
            
            else:
                print("❌ 无效选择，请输入 1-3")
        
    except Exception as e:
        print(f"❌ 程序运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
