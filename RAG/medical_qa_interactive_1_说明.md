# 医疗RAG问答系统 - 交互式问答 (版本1)

## 修复内容

### 问题描述
原始 `medical_qa_interactive.py` 文件在运行时出现以下错误：
```
加载向量数据库失败: Error in __cdecl faiss::FileIOReader::FileIOReader(const char *) at D:\a\faiss-wheels\faiss-wheels\faiss\faiss\impl\io.cpp:68: Error: 'f' failed: could not open d:\HuaweiMoveData\Users\hao\Desktop\1随堂练习\12-Agent智能体系统的设计与应用\CASE-智能健康管理助手\RAG\vector_db\faiss_index.bin for reading: No such file or directory
```

### 修复方案

#### 1. 添加自动构建向量数据库功能
- 当向量数据库文件不存在时，系统会自动尝试构建新的向量数据库
- 从 `medical_rag_system_1.py` 中复制了完整的向量数据库构建逻辑

#### 2. 增强错误处理机制
- 在 `_load_vector_db()` 方法中添加了文件存在性检查
- 当文件不存在时，自动调用 `_build_vector_db()` 方法
- 添加了多层错误处理，确保系统稳定性

#### 3. 新增的方法
- `_build_vector_db()`: 构建向量数据库
- `_load_medical_data()`: 加载医学数据集
- `_process_documents()`: 处理文档，生成文档块
- `_generate_embeddings()`: 生成文档嵌入向量
- `_build_faiss_index()`: 构建FAISS索引
- `_save_metadata()`: 保存元数据

## 主要改进

### 1. 智能路径处理
- 支持多个可能的医学数据文件路径
- 自动检测和定位数据文件位置
- 提供详细的路径调试信息

### 2. 进度显示
- 添加了详细的进度显示信息
- 包括文档处理进度、嵌入向量生成进度等
- 提供时间估算信息

### 3. 错误恢复
- 当向量数据库加载失败时，自动尝试重新构建
- 提供详细的错误信息和调试信息
- 确保系统能够从错误中恢复

### 4. 文件验证
- 验证向量索引文件和元数据文件是否成功保存
- 显示文件大小和保存路径信息
- 确保数据完整性

## 使用方法

### 运行系统
```bash
python medical_qa_interactive_1.py
```

### 系统特性
1. **自动初始化**: 系统会自动检查并构建必要的向量数据库
2. **交互式问答**: 支持实时医疗问题问答
3. **智能搜索**: 基于向量相似度的智能文档检索
4. **专业回答**: 基于医学知识库的专业医疗建议

### 支持的命令
- `quit` / `exit` / `退出`: 退出系统
- `info` / `信息`: 查看系统信息
- `help` / `帮助`: 查看帮助信息

## 技术特点

### 1. 向量数据库
- 使用 FAISS 进行高效的向量检索
- 支持余弦相似度计算
- 自动归一化处理

### 2. 嵌入模型
- 使用 `sentence-transformers/all-MiniLM-L6-v2` 模型
- 支持批量处理，提高效率
- 自动进度显示

### 3. 文档处理
- 智能文本分割，支持中文标点符号
- 可配置的分块大小和重叠度
- 完整的元数据管理

### 4. 大模型集成
- 集成 Qwen-Max 模型
- 专业的医疗系统提示词
- 智能回答提取和处理

## 注意事项

1. **首次运行**: 首次运行时会自动构建向量数据库，可能需要较长时间
2. **API密钥**: 需要配置 `DASHSCOPE_API_KEY` 环境变量
3. **数据文件**: 确保医学数据文件 `train.json` 存在于正确路径
4. **内存要求**: 构建向量数据库需要足够的内存空间

## 文件结构

```
RAG/
├── medical_qa_interactive.py          # 原始文件（保留）
├── medical_qa_interactive_1.py        # 修复版本
├── medical_qa_interactive_1_说明.md   # 本说明文档
├── medical_rag_system_1.py            # 向量数据库构建系统
└── vector_db/                         # 向量数据库目录
    ├── faiss_index.bin               # FAISS索引文件
    └── metadata.pkl                  # 元数据文件
```

## 版本信息

- **版本**: 1.0
- **修复日期**: 2024年
- **修复内容**: 向量数据库加载失败问题
- **兼容性**: 与原始系统完全兼容
