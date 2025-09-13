# 智能健康管理主控制器 (main_choice.py) 说明文档

## 功能概述

`main_choice.py` 是一个智能健康管理主控制器，它能够自动分析用户的健康问题并调用相应的专业Agent进行处理。该系统使用Qwen-Max模型进行智能问题分类，确保用户的问题能够得到最专业的处理。

## 核心功能

### 1. 智能问题分类
- 使用Qwen-Max模型分析用户问题内容
- 自动判断问题属于症状问诊还是健康管理场景
- 提供分类置信度和理由说明

### 2. 专业Agent调用
- **症状问诊类问题** → 调用 `health_ask_quickly.py`
- **健康管理类问题** → 调用 `health_management_agent_enhanced.py`

### 3. 统一用户管理
- 支持用户选择和切换
- 统一的用户信息管理
- 自动同步用户状态到各个Agent

## 问题分类规则

### 症状问诊Agent适用场景
- 具体症状描述（头痛、发热、咳嗽、胸痛等）
- 症状原因询问
- 症状严重程度评估
- 紧急医疗情况判断
- 用药相关问题
- 疾病诊断相关咨询
- 急性症状处理建议

**关键词示例：**
- 症状类：头痛、发热、咳嗽、胸痛、腹痛、恶心、呕吐、腹泻、皮疹、瘙痒
- 疾病类：感冒、发烧、高血压、糖尿病、心脏病、胃病
- 紧急类：胸痛、呼吸困难、意识不清、严重出血
- 用药类：药物副作用、用药方法、药物相互作用

### 健康管理Agent适用场景
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

## 系统架构

```
用户问题输入
    ↓
Qwen-Max分类器
    ↓
问题分类判断
    ↓
┌─────────────────┬─────────────────┐
│   症状问诊      │   健康管理      │
│   Agent         │   Agent         │
│                 │                 │
│ health_ask_     │ health_manage-  │
│ quickly.py      │ ment_agent_     │
│                 │ enhanced.py     │
└─────────────────┴─────────────────┘
    ↓
统一结果输出
```

## 主要类和方法

### HealthMainController类

#### 初始化方法
- `__init__()`: 初始化主控制器
- `_init_classifier()`: 初始化问题分类器
- `_init_symptom_agent()`: 初始化症状问诊Agent
- `_init_health_agent()`: 初始化健康管理Agent

#### 核心方法
- `classify_health_query(query)`: 使用Qwen-Max对问题进行分类
- `process_health_query(query, user_id)`: 处理健康查询的主入口
- `set_current_user(user_id)`: 设置当前用户
- `get_available_users()`: 获取可用用户列表

#### 辅助方法
- `_extract_classification(response)`: 提取分类结果
- `_parse_text_classification(content)`: 从文本解析分类结果
- `_get_classifier_prompt()`: 获取分类器系统提示词

## 使用示例

### 基本使用
```python
from main_choice import HealthMainController

# 初始化控制器
controller = HealthMainController()

# 设置用户
controller.set_current_user("user_001")

# 处理健康查询
result = controller.process_health_query("我最近经常头痛，这是什么原因？")

print(f"分类: {result['category']}")
print(f"回答: {result['agent_result']['answer']}")
```

### 交互式使用
```bash
python main_choice.py
```

## 输出格式

### 分类结果格式
```json
{
    "category": "症状问诊" 或 "健康管理",
    "confidence": 0.0-1.0之间的数值,
    "reason": "分类理由的简要说明"
}
```

### 处理结果格式
```json
{
    "category": "症状问诊" 或 "健康管理",
    "classification_confidence": 0.85,
    "classification_reason": "问题涉及具体症状描述",
    "agent_result": {
        "answer": "专业回答内容",
        "confidence": 0.90,
        "sources_count": 3
    },
    "timestamp": "2024-01-01T12:00:00"
}
```

## 错误处理

### 分类失败处理
- 当分类过程出现错误时，默认选择"症状问诊"以确保用户安全
- 提供详细的错误信息和分类理由

### Agent调用失败处理
- 当Agent初始化或调用失败时，返回错误信息
- 保持系统稳定性，不会导致程序崩溃

## 配置要求

### 环境变量
- `DASHSCOPE_API_KEY`: 阿里云DashScope API密钥

### 依赖模块
- `qwen_agent`: Qwen Agent框架
- `dashscope`: 阿里云DashScope SDK
- `health_ask_quickly`: 症状问诊Agent
- `health_management_agent_enhanced`: 健康管理Agent

## 测试

### 运行测试
```bash
python test_main_choice.py
```

### 测试内容
1. 问题分类功能测试
2. Agent初始化功能测试
3. 完整处理流程测试

## 注意事项

1. **安全性优先**: 当分类不确定时，优先选择症状问诊以确保用户安全
2. **用户管理**: 确保在调用Agent前正确设置用户ID
3. **错误处理**: 系统具有完善的错误处理机制，确保稳定性
4. **性能优化**: Agent采用懒加载方式，只在需要时初始化

## 扩展性

该系统设计具有良好的扩展性：
- 可以轻松添加新的问题分类类别
- 可以集成更多的专业Agent
- 支持自定义分类规则和提示词
- 支持多种输出格式和接口

## 版本信息

- 版本: 1.0
- 创建时间: 2024年
- 作者: AI Assistant
- 依赖: Python 3.8+, Qwen-Max模型

