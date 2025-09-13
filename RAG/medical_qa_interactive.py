#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
医疗RAG系统 - 交互式问答
基于已构建的向量数据库进行实时医疗问答
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pickle
import hashlib

# 向量化和检索相关
import faiss
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Qwen相关
import dashscope
from qwen_agent.agents import Assistant

logger = logging.getLogger(__name__)

class MedicalQAInteractive:
    """医疗问答交互系统"""
    
    def __init__(self):
        """初始化医疗问答系统"""
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        # 修复路径问题：使用脚本所在目录的相对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.vector_db_path = os.path.join(script_dir, "vector_db")
        
        # 初始化组件
        self.embedding_model = None
        self.vector_index = None
        self.documents = []
        
        # Qwen配置
        self.llm_config = {
            'model': 'qwen-max',
            'timeout': 60,
            'retry_count': 3,
        }
        self.assistant = None
        
        # 初始化系统
        self._init_system()
    
    def _init_system(self):
        """初始化系统组件"""
        try:
            print("🏥 医疗问答系统初始化中...")
            print("=" * 50)
            
            # 初始化嵌入模型
            print("🔄 正在加载嵌入模型...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print(f"✅ 嵌入模型加载成功: {self.embedding_model_name}")
            
            # 初始化Qwen助手
            self._init_qwen_assistant()
            
            # 加载向量数据库
            self._load_vector_db()
            
            print("✅ 系统初始化完成！")
            print("=" * 50)
            
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            raise
    
    def _init_qwen_assistant(self):
        """初始化Qwen助手"""
        try:
            # 配置DashScope API Key
            dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', 'your_dashscope_api_key_here')
            dashscope.timeout = 60
            
            system_prompt = self._get_medical_system_prompt()
            
            self.assistant = Assistant(
                llm=self.llm_config,
                name='医疗问答助手',
                description='基于医学知识库的专业医疗问答助手',
                system_message=system_prompt
            )
            
            print("✅ Qwen助手初始化成功")
            
        except Exception as e:
            logger.error(f"Qwen助手初始化失败: {e}")
            raise
    
    def _get_medical_system_prompt(self) -> str:
        """获取医疗系统提示词"""
        return """你是一位专业的医疗AI助手，具有丰富的医学知识和临床经验。

你的职责是：
1. 症状查询：帮助用户理解症状的可能原因和应对方法
2. 药物信息：提供准确的药物使用指导和安全信息
3. 健康指标解读：解释各种健康检查指标的含义
4. 紧急情况处理：识别紧急医疗情况并提供应急指导

回答原则：
- 基于提供的医学知识库进行回答
- 提供准确、科学的医疗信息
- 对于紧急情况，明确建议立即就医
- 避免给出具体的诊断建议，建议咨询专业医生
- 引用相关的医学文献和知识来源

回答格式：
1. 直接回答用户问题
2. 提供详细的解释和背景信息
3. 给出实用的建议和注意事项
4. 在必要时建议就医
5. 列出参考来源

请始终以用户的安全和健康为首要考虑。"""
    
    def _load_vector_db(self):
        """加载向量数据库"""
        try:
            # 加载FAISS索引
            index_file = os.path.join(self.vector_db_path, "faiss_index.bin")
            if not os.path.exists(index_file):
                raise FileNotFoundError(f"向量索引文件不存在: {index_file}")
            
            self.vector_index = faiss.read_index(index_file)
            
            # 加载元数据
            metadata_file = os.path.join(self.vector_db_path, "metadata.pkl")
            if not os.path.exists(metadata_file):
                raise FileNotFoundError(f"元数据文件不存在: {metadata_file}")
            
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            self.documents = metadata['documents']
            
            print(f"✅ 向量数据库加载完成，包含 {len(self.documents)} 个文档块")
            
        except Exception as e:
            logger.error(f"加载向量数据库失败: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        搜索相关文档
        
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
            logger.error(f"搜索失败: {e}")
            return []
    
    def ask(self, question: str, max_context_length: int = 4000) -> Dict[str, Any]:
        """
        询问医疗问题
        
        Args:
            question: 用户问题
            max_context_length: 最大上下文长度
            
        Returns:
            查询结果
        """
        try:
            print(f"🔍 正在搜索相关知识...")
            
            # 搜索相关文档
            search_results = self.search(question, top_k=5)
            
            if not search_results:
                return {
                    'answer': '抱歉，我在知识库中没有找到相关信息。建议您咨询专业医生。',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # 构建上下文
            context_parts = []
            sources = []
            total_length = 0
            
            for result in search_results:
                content = result['content']
                metadata = result['metadata']
                score = result['score']
                
                if total_length + len(content) > max_context_length:
                    break
                
                context_parts.append(content)
                sources.append({
                    'source': metadata.get('source', 'unknown'),
                    'index': metadata.get('index', -1),
                    'question': metadata.get('question', ''),
                    'score': score
                })
                total_length += len(content)
            
            context = "\n\n".join(context_parts)
            
            # 构建提示词
            prompt = f"""
基于以下医学知识库信息，请回答用户的问题：

用户问题: {question}

相关医学知识:
{context}

请提供准确、专业的回答，并说明信息来源。
"""
            
            print("🤖 正在生成回答...")
            
            # 调用Qwen模型
            messages = [{'role': 'user', 'content': prompt}]
            response = self.assistant.run(messages)
            
            # 处理响应
            answer = self._extract_answer(response)
            
            # 计算置信度
            confidence = self._calculate_confidence(search_results)
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'context_length': total_length
            }
            
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return {
                'answer': f'查询过程中出现错误: {str(e)}',
                'sources': [],
                'confidence': 0.0
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
    
    def _calculate_confidence(self, search_results: List[Dict]) -> float:
        """计算回答置信度"""
        if not search_results:
            return 0.0
        
        # 基于搜索结果的相似度分数计算置信度
        scores = [result['score'] for result in search_results]
        avg_score = sum(scores) / len(scores)
        
        # 将相似度分数转换为置信度 (0-1)
        confidence = min(avg_score * 2, 1.0)  # 简单的线性映射
        
        return confidence
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'embedding_model': self.embedding_model_name,
            'total_documents': len(self.documents),
            'vector_db_path': self.vector_db_path,
            'vector_index_size': self.vector_index.ntotal if self.vector_index else 0
        }

def main():
    """主函数 - 交互式问答"""
    print("🏥 医疗RAG问答系统")
    print("=" * 60)
    
    try:
        # 初始化问答系统
        qa_system = MedicalQAInteractive()
        
        # 显示系统信息
        info = qa_system.get_system_info()
        print(f"\n📊 系统信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        print(f"\n💡 使用说明:")
        print("   - 输入医疗相关问题")
        print("   - 输入 'quit' 或 'exit' 退出")
        print("   - 输入 'info' 查看系统信息")
        print("   - 输入 'help' 查看帮助")
        print("=" * 60)
        
        # 交互式问答循环
        while True:
            try:
                # 获取用户输入
                question = input("\n❓ 请输入您的医疗问题: ").strip()
                
                # 处理特殊命令
                if question.lower() in ['quit', 'exit', '退出']:
                    print("👋 感谢使用医疗问答系统，再见！")
                    break
                elif question.lower() in ['info', '信息']:
                    info = qa_system.get_system_info()
                    print(f"\n📊 系统信息:")
                    for key, value in info.items():
                        print(f"   {key}: {value}")
                    continue
                elif question.lower() in ['help', '帮助']:
                    print(f"\n💡 帮助信息:")
                    print("   - 可以询问症状、疾病、药物、检查等相关问题")
                    print("   - 系统会基于医学知识库提供专业回答")
                    print("   - 回答仅供参考，具体诊断请咨询专业医生")
                    continue
                elif not question:
                    print("⚠️ 请输入有效的问题")
                    continue
                
                # 处理医疗问题
                print(f"\n🔍 正在处理您的问题: {question}")
                result = qa_system.ask(question)
                
                # 显示结果
                print(f"\n📝 回答:")
                print(f"{result['answer']}")
                
                print(f"\n📊 回答质量:")
                print(f"   置信度: {result['confidence']:.2f}")
                print(f"   参考来源: {len(result['sources'])} 个")
                
                if result['sources']:
                    print(f"\n📚 相关来源:")
                    for i, source in enumerate(result['sources'][:3], 1):
                        print(f"   {i}. {source['question'][:80]}... (相似度: {source['score']:.3f})")
                
                print("\n" + "=" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用医疗问答系统，再见！")
                break
            except Exception as e:
                print(f"\n❌ 处理问题时出现错误: {e}")
                continue
        
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
