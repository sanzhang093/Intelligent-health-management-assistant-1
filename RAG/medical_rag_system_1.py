#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
医疗RAG系统 - 版本1
基于Qwen-Max和医学推理数据集的智能医疗问答系统
修复了路径问题，确保能正确找到医学数据文件
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

class MedicalRAGSystem:
    """医疗RAG系统"""
    
    def __init__(self, 
                 embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 vector_db_path: str = "vector_db",
                 medical_data_path: str = "../data/medical_dataset"):
        """
        初始化医疗RAG系统
        
        Args:
            embedding_model_name: 嵌入模型名称
            chunk_size: 文本分块大小
            chunk_overlap: 分块重叠大小
            vector_db_path: 向量数据库路径
            medical_data_path: 医学数据路径
        """
        self.embedding_model_name = embedding_model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_db_path = vector_db_path
        self.medical_data_path = medical_data_path
        
        # 初始化组件
        self.embedding_model = None
        self.text_splitter = None
        self.vector_index = None
        self.documents = []
        self.metadata = []
        
        # Qwen配置
        self.llm_config = {
            'model': 'qwen-max',
            'timeout': 60,
            'retry_count': 3,
        }
        self.assistant = None
        
        # 创建必要目录
        self._create_directories()
        
        # 初始化组件
        self._init_components()
    
    def _create_directories(self):
        """创建必要的目录"""
        os.makedirs(self.vector_db_path, exist_ok=True)
        os.makedirs("cache", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def _init_components(self):
        """初始化各个组件"""
        try:
            # 初始化嵌入模型
            print("🔄 正在加载嵌入模型...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print(f"✅ 嵌入模型加载成功: {self.embedding_model_name}")
            
            # 初始化文本分割器
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
            )
            
            # 初始化Qwen助手
            self._init_qwen_assistant()
            
            # 检查是否已有向量数据库
            if self._vector_db_exists():
                print("📁 发现已存在的向量数据库，正在加载...")
                self._load_vector_db()
            else:
                print("🔄 构建新的向量数据库...")
                self._build_vector_db()
                
        except Exception as e:
            logger.error(f"初始化组件失败: {e}")
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
                name='医疗RAG助手',
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
    
    def _vector_db_exists(self) -> bool:
        """检查向量数据库是否存在"""
        index_file = os.path.join(self.vector_db_path, "faiss_index.bin")
        metadata_file = os.path.join(self.vector_db_path, "metadata.pkl")
        return os.path.exists(index_file) and os.path.exists(metadata_file)
    
    def _build_vector_db(self):
        """构建向量数据库"""
        try:
            print("📚 正在加载医学数据集...")
            
            # 加载医学数据
            medical_data = self._load_medical_data()
            
            if not medical_data:
                raise ValueError("未找到医学数据")
            
            print(f"📊 加载了 {len(medical_data)} 条医学数据")
            
            # 处理文档
            print("🔄 正在处理文档...")
            documents = self._process_documents(medical_data)
            
            print(f"📄 生成了 {len(documents)} 个文档块")
            
            # 生成嵌入向量
            print("🔄 正在生成嵌入向量...")
            embeddings = self._generate_embeddings(documents)
            
            # 构建FAISS索引
            print("🔄 正在构建向量索引...")
            self._build_faiss_index(embeddings)
            
            # 保存元数据
            self.documents = documents
            self._save_metadata()
            
            print("✅ 向量数据库构建完成")
            
        except Exception as e:
            logger.error(f"构建向量数据库失败: {e}")
            raise
    
    def _load_medical_data(self) -> List[Dict]:
        """加载医学数据"""
        try:
            # 获取当前脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            current_dir = os.getcwd()
            
            print(f"🔍 脚本目录: {script_dir}")
            print(f"📁 当前工作目录: {current_dir}")
            
            # 尝试多个可能的路径
            possible_paths = [
                # 相对于脚本目录的路径
                os.path.join(script_dir, "../data/medical_dataset/train.json"),
                os.path.join(script_dir, "data/medical_dataset/train.json"),
                # 相对于当前工作目录的路径
                os.path.join(current_dir, "12-Agent智能体系统的设计与应用/CASE-智能健康管理助手/data/medical_dataset/train.json"),
                os.path.join(current_dir, "data/medical_dataset/train.json"),
                # 其他可能的路径
                "data/medical_dataset/train.json",
                "../data/medical_dataset/train.json",
                "../../data/medical_dataset/train.json"
            ]
            
            data_file = None
            for path in possible_paths:
                abs_path = os.path.abspath(path)
                print(f"🔍 尝试路径: {abs_path}")
                if os.path.exists(abs_path):
                    data_file = abs_path
                    print(f"✅ 找到医学数据文件: {data_file}")
                    break
            
            if not data_file:
                raise FileNotFoundError(f"医学数据文件不存在，已尝试的路径: {possible_paths}")
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ 成功加载医学数据，共 {len(data)} 条记录")
            return data
            
        except Exception as e:
            logger.error(f"加载医学数据失败: {e}")
            return []
    
    def _process_documents(self, medical_data: List[Dict]) -> List[Document]:
        """处理文档，生成文档块"""
        documents = []
        total_items = len(medical_data)
        
        print(f"📄 开始处理 {total_items} 条医学数据...")
        
        for i, item in enumerate(medical_data):
            # 显示进度
            if (i + 1) % 1000 == 0 or i == 0:
                print(f"🔄 处理进度: {i+1}/{total_items} ({((i+1)/total_items)*100:.1f}%)")
            
            # 创建文档内容
            content = f"""
问题: {item.get('Question', '')}

推理过程: {item.get('Complex_CoT', '')}

答案: {item.get('Response', '')}
"""
            
            # 创建元数据
            metadata = {
                'source': 'medical_dataset',
                'index': i,
                'question': item.get('Question', '')[:100] + '...' if len(item.get('Question', '')) > 100 else item.get('Question', ''),
                'original_data': item
            }
            
            # 创建Document对象
            doc = Document(page_content=content, metadata=metadata)
            
            # 分割文档
            chunks = self.text_splitter.split_documents([doc])
            
            # 为每个块添加唯一ID
            for j, chunk in enumerate(chunks):
                chunk.metadata['chunk_id'] = f"{i}_{j}"
                chunk.metadata['chunk_index'] = j
                documents.append(chunk)
        
        print(f"✅ 文档处理完成，共生成 {len(documents)} 个文档块")
        return documents
    
    def _generate_embeddings(self, documents: List[Document]) -> np.ndarray:
        """生成文档嵌入向量"""
        texts = [doc.page_content for doc in documents]
        total_texts = len(texts)
        
        print(f"🔄 开始生成嵌入向量，共 {total_texts} 个文档...")
        print("⏰ 预计需要 1-2 小时，请耐心等待...")
        
        # 批量生成嵌入向量，使用批处理提高效率
        embeddings = self.embedding_model.encode(
            texts, 
            show_progress_bar=True,
            batch_size=32,  # 控制批处理大小
            convert_to_numpy=True
        )
        
        print(f"✅ 嵌入向量生成完成，维度: {embeddings.shape}")
        return embeddings.astype('float32')
    
    def _build_faiss_index(self, embeddings: np.ndarray):
        """构建FAISS索引"""
        dimension = embeddings.shape[1]
        
        print(f"🔄 开始构建FAISS索引，维度: {dimension}, 向量数: {embeddings.shape[0]}")
        
        # 创建FAISS索引
        self.vector_index = faiss.IndexFlatIP(dimension)  # 使用内积相似度
        
        # 归一化向量（用于余弦相似度）
        print("🔄 正在归一化向量...")
        faiss.normalize_L2(embeddings)
        
        # 添加向量到索引
        print("🔄 正在添加向量到索引...")
        self.vector_index.add(embeddings)
        
        # 保存索引到当前RAG文件夹
        index_file = os.path.join(self.vector_db_path, "faiss_index.bin")
        print(f"💾 正在保存索引文件: {os.path.abspath(index_file)}")
        faiss.write_index(self.vector_index, index_file)
        
        # 验证文件是否保存成功
        if os.path.exists(index_file):
            file_size = os.path.getsize(index_file) / (1024 * 1024)  # MB
            print(f"✅ FAISS索引构建完成，维度: {dimension}, 向量数: {embeddings.shape[0]}")
            print(f"📁 索引文件已保存: {os.path.abspath(index_file)} ({file_size:.2f} MB)")
        else:
            raise RuntimeError(f"索引文件保存失败: {index_file}")
    
    def _save_metadata(self):
        """保存元数据"""
        metadata_file = os.path.join(self.vector_db_path, "metadata.pkl")
        
        print(f"💾 正在保存元数据文件: {os.path.abspath(metadata_file)}")
        
        metadata = {
            'documents': self.documents,
            'embedding_model': self.embedding_model_name,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'created_at': datetime.now().isoformat(),
            'total_chunks': len(self.documents),
            'vector_db_path': os.path.abspath(self.vector_db_path)
        }
        
        with open(metadata_file, 'wb') as f:
            pickle.dump(metadata, f)
        
        # 验证文件是否保存成功
        if os.path.exists(metadata_file):
            file_size = os.path.getsize(metadata_file) / (1024 * 1024)  # MB
            print(f"✅ 元数据已保存: {os.path.abspath(metadata_file)} ({file_size:.2f} MB)")
            print(f"📊 元数据信息: {len(self.documents)} 个文档块")
        else:
            raise RuntimeError(f"元数据文件保存失败: {metadata_file}")
    
    def _load_vector_db(self):
        """加载向量数据库"""
        try:
            # 加载FAISS索引
            index_file = os.path.join(self.vector_db_path, "faiss_index.bin")
            self.vector_index = faiss.read_index(index_file)
            
            # 加载元数据
            metadata_file = os.path.join(self.vector_db_path, "metadata.pkl")
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
    
    def query(self, question: str, max_context_length: int = 4000) -> Dict[str, Any]:
        """
        查询医疗问题
        
        Args:
            question: 用户问题
            max_context_length: 最大上下文长度
            
        Returns:
            查询结果
        """
        try:
            print(f"🔍 正在查询: {question}")
            
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
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'total_documents': len(self.documents),
            'vector_db_path': self.vector_db_path,
            'medical_data_path': self.medical_data_path,
            'vector_index_size': self.vector_index.ntotal if self.vector_index else 0
        }

def main():
    """主函数 - 测试RAG系统"""
    print("🏥 医疗RAG系统测试 - 版本1")
    print("=" * 60)
    
    try:
        # 初始化RAG系统
        rag_system = MedicalRAGSystem()
        
        # 显示系统信息
        info = rag_system.get_system_info()
        print(f"\n📊 系统信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # 测试查询
        test_questions = [
            "什么是高血压？",
            "感冒的症状有哪些？",
            "如何预防糖尿病？",
            "心脏病的早期症状是什么？"
        ]
        
        for question in test_questions:
            print(f"\n🔍 测试问题: {question}")
            result = rag_system.query(question)
            
            print(f"📝 回答: {result['answer'][:200]}...")
            print(f"🎯 置信度: {result['confidence']:.2f}")
            print(f"📚 来源数量: {len(result['sources'])}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
