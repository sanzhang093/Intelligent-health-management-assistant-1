#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能医疗快速问答系统
基于用户查询、身体状况信息、RAG检索结果的综合医疗分析系统
"""

import os
import sys
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pickle

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 向量化和检索相关
import faiss
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Qwen相关
import dashscope
from qwen_agent.agents import Assistant

# 导入项目模块
from src.user_profile import HealthProfile, HealthProfileManager
from tools.health_management_tools import HealthDataExtractor
from tools.health_comparison import HealthComparison

logger = logging.getLogger(__name__)

class HealthAskQuickly:
    """智能医疗快速问答系统"""
    
    def __init__(self, 
                 vector_db_path: str = None,
                 profiles_dir: str = None):
        """
        初始化智能医疗问答系统
        
        Args:
            vector_db_path: 向量数据库路径
            profiles_dir: 用户档案目录
        """
        # 获取项目根目录（基于脚本文件位置）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # 自动检测向量数据库路径
        if vector_db_path is None:
            # 尝试多个可能的路径
            possible_paths = [
                os.path.join(project_root, "RAG", "vector_db"),  # 绝对路径
                "RAG/vector_db",  # 从项目根目录运行
                "vector_db",       # 从RAG目录运行
                "../RAG/vector_db", # 从src目录运行
            ]
            
            for path in possible_paths:
                abs_path = os.path.abspath(path)
                if os.path.exists(os.path.join(abs_path, "faiss_index.bin")):
                    self.vector_db_path = abs_path
                    break
            
            if not hasattr(self, 'vector_db_path') or self.vector_db_path is None:
                self.vector_db_path = os.path.join(project_root, "RAG", "vector_db")  # 默认绝对路径
        else:
            self.vector_db_path = vector_db_path
            
        # 设置用户档案目录
        if profiles_dir is None:
            self.profiles_dir = os.path.join(project_root, "data", "profiles")
        else:
            self.profiles_dir = profiles_dir
        
        # 初始化组件
        self.embedding_model = None
        self.vector_index = None
        self.documents = []
        self.assistant = None
        
        # 健康管理组件
        self.health_extractor = None
        self.health_comparison = None
        self.profile_manager = None
        
        # 用户管理
        self.current_user = None
        self.available_users = []
        
        # Qwen配置
        self.llm_config = {
            'model': 'qwen-max',
            'timeout': 60,
            'retry_count': 3,
        }
        
        # 初始化系统
        self._init_system()
    
    def _init_system(self):
        """初始化系统组件"""
        try:
            print("🏥 智能医疗快速问答系统初始化中...")
            print("=" * 60)
            
            # 初始化嵌入模型
            print("🔄 正在加载嵌入模型...")
            self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            print("✅ 嵌入模型加载成功")
            
            # 初始化Qwen助手
            self._init_qwen_assistant()
            
            # 加载向量数据库
            self._load_vector_db()
            
            # 初始化健康管理组件
            self._init_health_components()
            
            print("✅ 系统初始化完成！")
            print("=" * 60)
            
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            raise
    
    def _init_qwen_assistant(self):
        """初始化Qwen助手"""
        try:
            # 配置DashScope API Key
            api_key = os.getenv('DASHSCOPE_API_KEY')
            if not api_key:
                raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
            dashscope.api_key = api_key
            dashscope.timeout = 60
            
            system_prompt = self._get_medical_system_prompt()
            
            self.assistant = Assistant(
                llm=self.llm_config,
                name='智能医疗分析助手',
                description='基于多源数据的专业医疗分析助手',
                system_message=system_prompt
            )
            
            print("✅ Qwen助手初始化成功")
            
        except Exception as e:
            logger.error(f"Qwen助手初始化失败: {e}")
            raise
    
    def _get_medical_system_prompt(self) -> str:
        """获取医疗系统提示词"""
        return """你是一位专业的医疗AI分析专家，具有丰富的临床经验和医学知识。

你的职责是：
1. 症状分析：基于用户查询、身体状况信息、医学知识进行综合症状分析
2. 风险评估：评估用户的健康风险等级和潜在风险因素
3. 个性化建议：提供针对性的健康建议和医疗咨询建议
4. 档案更新：建议用户健康档案的更新内容

分析原则：
- 基于提供的多源数据进行综合分析
- 结合用户的具体情况进行个性化分析
- 对于紧急情况，明确建议立即就医
- 避免给出具体诊断，建议咨询专业医生
- 提供可操作的具体建议
- 引用相关的医学知识来源

请始终以用户的安全和健康为首要考虑，提供专业、准确、实用的分析结果。"""
    
    def _load_vector_db(self):
        """加载向量数据库"""
        try:
            print(f"🔍 正在查找向量数据库，路径: {self.vector_db_path}")
            
            # 加载FAISS索引
            index_file = os.path.join(self.vector_db_path, "faiss_index.bin")
            abs_index_file = os.path.abspath(index_file)
            print(f"🔍 检查索引文件: {abs_index_file}")
            
            if not os.path.exists(abs_index_file):
                raise FileNotFoundError(f"向量索引文件不存在: {abs_index_file}")
            
            print(f"✅ 找到索引文件，大小: {os.path.getsize(abs_index_file) / (1024*1024):.1f} MB")
            
            # 处理中文路径问题：复制到临时位置
            import tempfile
            import shutil
            
            # 加载元数据
            metadata_file = os.path.join(self.vector_db_path, "metadata.pkl")
            abs_metadata_file = os.path.abspath(metadata_file)
            print(f"🔍 检查元数据文件: {abs_metadata_file}")
            
            if not os.path.exists(abs_metadata_file):
                raise FileNotFoundError(f"元数据文件不存在: {abs_metadata_file}")
            
            print(f"✅ 找到元数据文件，大小: {os.path.getsize(abs_metadata_file) / (1024*1024):.1f} MB")
            
            # 创建临时文件
            temp_dir = tempfile.mkdtemp()
            temp_index_file = os.path.join(temp_dir, "faiss_index.bin")
            temp_metadata_file = os.path.join(temp_dir, "metadata.pkl")
            
            print(f"🔄 复制文件到临时目录: {temp_dir}")
            shutil.copy2(abs_index_file, temp_index_file)
            shutil.copy2(abs_metadata_file, temp_metadata_file)
            
            # 从临时文件读取
            self.vector_index = faiss.read_index(temp_index_file)
            
            with open(temp_metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            self.documents = metadata['documents']
            
            print(f"✅ 向量数据库加载完成，包含 {len(self.documents)} 个文档块")
            
        except Exception as e:
            logger.error(f"加载向量数据库失败: {e}")
            raise
    
    def _init_health_components(self):
        """初始化健康管理组件"""
        try:
            # 初始化用户档案管理器
            self.profile_manager = HealthProfileManager(self.profiles_dir)
            
            # 加载现有用户档案
            if os.path.exists(self.profiles_dir):
                print(f"🔄 正在加载用户档案从: {self.profiles_dir}")
                success = self.profile_manager.load_all_profiles(self.profiles_dir)
                if success:
                    print(f"✅ 成功加载 {len(self.profile_manager.profiles)} 个用户档案")
                else:
                    print("⚠️ 用户档案加载失败，将使用默认档案")
            else:
                print(f"⚠️ 用户档案目录不存在: {self.profiles_dir}")
            
            # 初始化健康数据提取器（使用已加载的档案管理器）
            self.health_extractor = HealthDataExtractor(self.profiles_dir)
            # 使用同一个档案管理器实例
            self.health_extractor.profile_manager = self.profile_manager
            
            # 初始化健康比较工具
            self.health_comparison = HealthComparison()
            
            # 加载可用用户列表
            self.available_users = self._load_available_users()
            
            print("✅ 健康管理组件初始化成功")
            
        except Exception as e:
            logger.error(f"健康管理组件初始化失败: {e}")
            raise
    
    def _load_available_users(self) -> List[str]:
        """加载可用的用户列表"""
        try:
            users = []
            for user_id in self.profile_manager.profiles.keys():
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
            profile = self.profile_manager.get_profile(user_id)
            
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
    
    def search_medical_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        搜索医学知识
        
        Args:
            query: 查询文本
            top_k: 返回的文档数量
            
        Returns:
            相关文档列表
        """
        try:
            # 生成查询向量
            query_embedding = self.embedding_model.encode([query])
            query_embedding = query_embedding.astype('float32')
            faiss.normalize_L2(query_embedding)
            
            # 搜索相似向量
            scores, indices = self.vector_index.search(query_embedding, top_k)
            
            # 构建结果
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': float(score)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"搜索医学知识失败: {e}")
            return []
    
    def get_user_health_data(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取用户健康数据
        
        Args:
            user_id: 用户ID
            days: 获取最近几天的数据
            
        Returns:
            用户健康数据
        """
        try:
            # 获取用户基本信息
            user_profile = self.profile_manager.get_profile(user_id)
            if not user_profile:
                # 如果用户档案不存在，创建默认档案
                print(f"⚠️ 用户 {user_id} 的档案不存在，创建默认档案...")
                user_profile = self.profile_manager.create_default_profile(user_id)
            
            # 从用户档案中提取健康数据
            health_data = {
                'user_id': user_id,
                'basic_info': {
                    'age': user_profile.demographics.age if user_profile.demographics else 'unknown',
                    'gender': user_profile.demographics.gender if user_profile.demographics else 'unknown',
                    'height': user_profile.demographics.height if user_profile.demographics else 'unknown',
                    'weight': user_profile.demographics.weight if user_profile.demographics else 'unknown'
                },
                'recent_vital_signs': {},
                'recent_symptoms': user_profile.health_status.recent_symptoms if user_profile.health_status else [],
                'current_medications': user_profile.health_status.current_medications if user_profile.health_status else [],
                'lifestyle_factors': {
                    'exercise_frequency': user_profile.lifestyle.exercise_frequency if user_profile.lifestyle else 'unknown',
                    'diet_type': user_profile.lifestyle.diet_type if user_profile.lifestyle else 'unknown',
                    'sleep_hours': user_profile.lifestyle.sleep_hours if user_profile.lifestyle else 'unknown',
                    'stress_level': user_profile.lifestyle.stress_level if user_profile.lifestyle else 'unknown',
                    'smoking': user_profile.lifestyle.smoking if user_profile.lifestyle else False,
                    'alcohol_consumption': user_profile.lifestyle.alcohol_consumption if user_profile.lifestyle else 'unknown'
                },
                'medical_history': user_profile.health_status.medical_history if user_profile.health_status else [],
                'chronic_conditions': user_profile.health_status.chronic_conditions if user_profile.health_status else [],
                'allergies': user_profile.health_status.allergies if user_profile.health_status else [],
                'time_period': f"最近{days}天"
            }
            
            return health_data
            
        except Exception as e:
            logger.error(f"获取用户健康数据失败: {e}")
            # 返回默认健康数据
            return {
                'user_id': user_id,
                'basic_info': {
                    'age': 'unknown',
                    'gender': 'unknown',
                    'height': 'unknown',
                    'weight': 'unknown'
                },
                'recent_vital_signs': {},
                'recent_symptoms': [],
                'current_medications': [],
                'lifestyle_factors': {},
                'medical_history': [],
                'chronic_conditions': [],
                'allergies': [],
                'time_period': f"最近{days}天"
            }
    
    def build_analysis_prompt(self, 
                             user_query: str, 
                             health_data: Dict[str, Any], 
                             rag_results: List[Dict]) -> str:
        """
        构建分析提示词
        
        Args:
            user_query: 用户查询
            health_data: 用户健康数据
            rag_results: RAG检索结果
            
        Returns:
            分析提示词
        """
        # 构建RAG知识内容
        rag_knowledge = ""
        if rag_results:
            rag_knowledge = "\n".join([
                f"知识片段 {i+1} (相似度: {result['score']:.3f}):\n{result['content']}\n"
                for i, result in enumerate(rag_results)
            ])
        
        # 构建分析提示词
        prompt = f"""
你是一位专业的医疗AI分析专家，具有丰富的临床经验和医学知识。请基于以下信息进行综合分析和建议：

## 用户基本信息
- 用户ID: {health_data.get('user_id', 'unknown')}
- 年龄: {health_data.get('basic_info', {}).get('age', 'unknown')}
- 性别: {health_data.get('basic_info', {}).get('gender', 'unknown')}
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 用户当前查询
用户问题: {user_query}

## 用户近期身体状况信息
### 生命体征 (最近30天)
{json.dumps(health_data.get('recent_vital_signs', {}), ensure_ascii=False, indent=2)}

### 症状记录
{json.dumps(health_data.get('recent_symptoms', []), ensure_ascii=False, indent=2)}

### 用药情况
{json.dumps(health_data.get('current_medications', []), ensure_ascii=False, indent=2)}

### 生活方式
{json.dumps(health_data.get('lifestyle_factors', {}), ensure_ascii=False, indent=2)}

### 病史记录
{json.dumps(health_data.get('medical_history', []), ensure_ascii=False, indent=2)}

## 相关医学知识 (基于RAG检索)
{rag_knowledge}

## 分析任务
请基于以上信息进行以下分析：

### 1. 症状分析
- 识别主要症状模式
- 分析症状的可能原因
- 评估症状的严重程度
- 识别潜在的风险因素

### 2. 健康风险评估
- 评估即时健康风险
- 识别长期健康风险
- 确定风险等级 (低/中/高/紧急)
- 分析风险因素

### 3. 个性化建议
- 提供即时行动建议
- 给出生活方式调整建议
- 建议医疗咨询需求
- 制定监测计划

### 4. 用户档案更新建议
- 需要记录的新症状
- 需要关注的健康指标
- 建议的随访计划
- 生活方式改进点
1
## 回答要求
1. 基于提供的医学知识库进行专业分析，知识库检索内容应当作为主要参考依据
2. 结合用户的具体情况进行个性化建议
3. 对于紧急情况，明确建议立即就医
4. 避免给出具体诊断，建议咨询专业医生
5. 提供可操作的具体建议
6. 引用相关的医学知识来源

请以结构化的方式提供分析结果，包含症状分析、风险评估、个性化建议和档案更新建议。
"""
        
        return prompt
    
    def analyze_health_query(self, 
                           user_query: str, 
                           user_id: str = None, 
                           max_context_length: int = 4000) -> Dict[str, Any]:
        """
        分析健康查询
        
        Args:
            user_query: 用户查询
            user_id: 用户ID（可选，如果不提供则使用当前用户）
            max_context_length: 最大上下文长度
            
        Returns:
            分析结果
        """
        try:
            # 确定目标用户
            target_user = user_id or self.current_user
            if not target_user:
                return {
                    'answer': '请先选择用户或提供用户ID',
                    'sources': [],
                    'confidence': 0.0,
                    'analysis_result': None
                }
            
            print(f"🔍 开始分析用户 {target_user} 的健康查询...")
            
            # 1. 获取用户健康数据
            print("📊 正在获取用户健康数据...")
            health_data = self.get_user_health_data(target_user)
            
            # 2. 搜索相关医学知识
            print("🔍 正在搜索相关医学知识...")
            rag_results = self.search_medical_knowledge(user_query, top_k=5)
            
            if not rag_results:
                return {
                    'answer': '抱歉，我在知识库中没有找到相关信息。建议您咨询专业医生。',
                    'sources': [],
                    'confidence': 0.0,
                    'analysis_result': None
                }
            
            # 打印获取到的医学知识
            print(f"\n📚 获取到的医学知识 (共 {len(rag_results)} 条):")
            print("=" * 80)
            for i, result in enumerate(rag_results, 1):
                print(f"\n【知识片段 {i}】")
                print(f"相似度分数: {result['score']:.4f}")
                print(f"来源: {result['metadata'].get('source', 'unknown')}")
                print(f"问题: {result['metadata'].get('question', 'unknown')}")
                print(f"内容: {result['content'][:500]}{'...' if len(result['content']) > 500 else ''}")
                print("-" * 80)
            
            # 3. 构建分析提示词
            print("🤖 正在构建分析提示词...")
            analysis_prompt = self.build_analysis_prompt(user_query, health_data, rag_results)
            
            # 4. 调用Qwen模型进行分析
            print("🧠 正在调用Qwen模型进行智能分析...")
            try:
                messages = [{'role': 'user', 'content': analysis_prompt}]
                response = self.assistant.run(messages)
                
                # 5. 处理响应
                answer = self._extract_answer(response)
            except Exception as e:
                logger.error(f"Qwen模型调用失败: {e}")
                answer = f"抱歉，AI分析服务暂时不可用。基于检索到的医学知识，建议您咨询专业医生获取更详细的诊断和建议。"
            
            # 6. 计算置信度
            confidence = self._calculate_confidence(rag_results)
            
            # 7. 构建分析结果
            analysis_result = {
                'user_id': target_user,
                'user_query': user_query,
                'timestamp': datetime.now().isoformat(),
                'health_data': health_data,
                'rag_results': rag_results,
                'analysis_answer': answer,
                'confidence': confidence,
                'sources': [
                    {
                        'source': result['metadata'].get('source', 'unknown'),
                        'index': result['metadata'].get('index', -1),
                        'question': result['metadata'].get('question', ''),
                        'score': result['score']
                    }
                    for result in rag_results
                ]
            }
            
            print("✅ 健康查询分析完成")
            
            return {
                'answer': answer,
                'sources': analysis_result['sources'],
                'confidence': confidence,
                'analysis_result': analysis_result
            }
            
        except Exception as e:
            logger.error(f"分析健康查询失败: {e}")
            return {
                'answer': f'分析过程中出现错误: {str(e)}',
                'sources': [],
                'confidence': 0.0,
                'analysis_result': None
            }
    
    def _extract_answer(self, response) -> str:
        """提取模型回答"""
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
                                        return content
                    # 如果没有找到assistant消息，返回最后一个消息的内容
                    last_msg_list = response_list[-1]
                    if isinstance(last_msg_list, list) and len(last_msg_list) > 0:
                        last_msg = last_msg_list[-1]
                        if isinstance(last_msg, dict):
                            return last_msg.get('content', '无法获取回答')
                        else:
                            return str(last_msg)
            
            return '抱歉，我无法处理您的问题。'
            
        except Exception as e:
            logger.error(f"提取回答失败: {e}")
            return '抱歉，我无法处理您的问题。'
    
    def _calculate_confidence(self, rag_results: List[Dict]) -> float:
        """计算回答置信度"""
        if not rag_results:
            return 0.0
        
        # 基于搜索结果的相似度分数计算置信度
        scores = [result['score'] for result in rag_results]
        avg_score = sum(scores) / len(scores)
        
        # 将相似度分数转换为置信度 (0-1)
        confidence = min(avg_score * 2, 1.0)  # 简单的线性映射
        
        return confidence
    
    def update_user_profile(self, user_id: str, analysis_result: Dict[str, Any]) -> bool:
        """
        更新用户档案
        
        Args:
            user_id: 用户ID
            analysis_result: 分析结果
            
        Returns:
            更新是否成功
        """
        try:
            if not analysis_result:
                return False
            
            # 获取用户档案
            user_profile = self.profile_manager.get_profile(user_id)
            if not user_profile:
                print(f"⚠️ 用户 {user_id} 的档案不存在")
                return False
            
            # 更新档案信息
            current_time = datetime.now()
            
            # 添加新的分析记录
            if 'analysis_history' not in user_profile.__dict__:
                user_profile.analysis_history = []
            
            user_profile.analysis_history.append({
                'timestamp': current_time.isoformat(),
                'query': analysis_result.get('user_query', ''),
                'analysis': analysis_result.get('analysis_answer', ''),
                'confidence': analysis_result.get('confidence', 0.0)
            })
            
            # 更新最后分析时间
            user_profile.last_analysis = current_time
            
            # 保存档案
            self.profile_manager.save_profile(user_profile)
            
            print(f"✅ 用户 {user_id} 的档案已更新")
            return True
            
        except Exception as e:
            logger.error(f"更新用户档案失败: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'total_documents': len(self.documents),
            'vector_db_path': self.vector_db_path,
            'vector_index_size': self.vector_index.ntotal if self.vector_index else 0,
            'profiles_dir': self.profiles_dir
        }

def main():
    """主函数 - 交互式智能医疗问答系统"""
    print("🏥 智能医疗快速问答系统")
    print("=" * 60)
    
    try:
        # 初始化系统
        health_system = HealthAskQuickly()
        
        # 显示系统信息
        info = health_system.get_system_info()
        print(f"\n📊 系统信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # 显示可用用户
        health_system.display_available_users()
        
        # 用户选择循环
        while True:
            print(f"\n📋 当前用户: {health_system.current_user if health_system.current_user else '未选择'}")
            print("\n请选择操作:")
            print("1. 选择用户")
            print("2. 查看用户信息")
            print("3. 健康问答")
            print("4. 退出")
            
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                # 选择用户
                health_system.display_available_users()
                user_input = input("\n请输入用户ID (如 user_001): ").strip()
                if user_input:
                    if health_system.set_current_user(user_input):
                        # 显示用户基本信息
                        user_info = health_system.get_user_info(user_input)
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
                if not health_system.current_user:
                    print("❌ 请先选择用户")
                    continue
                
                user_info = health_system.get_user_info(health_system.current_user)
                if 'error' not in user_info:
                    print(f"\n👤 用户 {health_system.current_user} 的详细信息:")
                    print("=" * 50)
                    for key, value in user_info.items():
                        print(f"{key}: {value}")
                else:
                    print(f"❌ 获取用户信息失败: {user_info['error']}")
            
            elif choice == "3":
                # 健康问答
                if not health_system.current_user:
                    print("❌ 请先选择用户")
                    continue
                
                print(f"\n💬 健康问答 (用户: {health_system.current_user})")
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
                    
                    print(f"\n🔍 正在分析您的问题...")
                    result = health_system.analyze_health_query(query)
                    
                    print(f"\n📝 分析结果:")
                    print(f"{result['answer']}")
                    print(f"\n📊 回答质量:")
                    print(f"   置信度: {result['confidence']:.2f}")
                    print(f"   参考来源: {len(result['sources'])} 个")
                    
                    if result['sources']:
                        print(f"\n📚 相关来源:")
                        for i, source in enumerate(result['sources'][:3], 1):
                            print(f"   {i}. {source['question'][:80]}... (相似度: {source['score']:.3f})")
                    
                    print("\n" + "=" * 50)
            
            elif choice == "4":
                # 退出
                print("👋 感谢使用智能医疗问答系统！")
                break
            
            else:
                print("❌ 无效选择，请输入 1-4")
        
    except Exception as e:
        print(f"❌ 程序运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
