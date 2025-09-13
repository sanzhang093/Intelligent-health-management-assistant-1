# 智能医疗分析系统 Prompt 设计

## 🎯 Prompt 设计目标

基于用户查询、身体状况信息、RAG检索结果，通过Qwen-Max进行综合症状分析和健康建议生成。

## 📋 核心 Prompt 模板

### 1. 主分析 Prompt

```
你是一位专业的医疗AI分析专家，具有丰富的临床经验和医学知识。请基于以下信息进行综合分析和建议：

## 用户基本信息
- 用户ID: {user_id}
- 年龄: {age}
- 性别: {gender}
- 分析时间: {timestamp}

## 用户当前查询
用户问题: {user_query}

## 用户近期身体状况信息
### 生命体征 (最近30天)
{recent_vital_signs}

### 症状记录
{recent_symptoms}

### 用药情况
{current_medications}

### 生活方式
{lifestyle_factors}

### 病史记录
{medical_history}

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

## 回答要求
1. 基于提供的医学知识库进行专业分析
2. 结合用户的具体情况进行个性化建议
3. 对于紧急情况，明确建议立即就医
4. 避免给出具体诊断，建议咨询专业医生
5. 提供可操作的具体建议
6. 引用相关的医学知识来源

请以结构化的方式提供分析结果。
```

### 2. 症状分析专用 Prompt

```
作为专业的症状分析专家，请基于以下信息进行深度症状分析：

## 症状信息
用户描述的症状: {symptoms_description}
症状持续时间: {symptom_duration}
症状严重程度: {symptom_severity}
伴随症状: {accompanying_symptoms}

## 用户背景
{user_background}

## 相关医学知识
{medical_knowledge}

## 分析要求
请进行以下分析：

### 症状模式识别
- 主要症状特征
- 症状组合模式
- 时间特征分析
- 严重程度评估

### 可能原因分析
- 最可能的原因 (按概率排序)
- 需要排除的严重疾病
- 相关风险因素
- 诱发因素分析

### 紧急程度评估
- 是否需要立即就医
- 是否需要紧急处理
- 观察期建议
- 预警信号识别

请提供专业的症状分析结果。
```

### 3. 风险评估专用 Prompt

```
作为健康风险评估专家，请基于以下信息进行综合风险评估：

## 用户健康数据
{health_data}

## 症状分析结果
{symptom_analysis}

## 医学知识参考
{medical_reference}

## 风险评估任务
请评估以下风险：

### 即时风险 (24-48小时)
- 急性并发症风险
- 症状恶化风险
- 紧急医疗需求
- 风险等级评估

### 短期风险 (1-4周)
- 疾病进展风险
- 并发症发生风险
- 生活质量影响
- 医疗干预需求

### 长期风险 (1-12个月)
- 慢性疾病风险
- 健康恶化趋势
- 预防性措施需求
- 长期监测计划

### 风险缓解建议
- 即时风险控制措施
- 预防性干预建议
- 监测指标建议
- 医疗咨询建议

请提供详细的风险评估报告。
```

### 4. 个性化建议生成 Prompt

```
作为个性化健康顾问，请基于以下信息生成针对性的健康建议：

## 用户画像
{user_profile}

## 分析结果
{analysis_results}

## 风险评估
{risk_assessment}

## 建议生成任务
请生成以下建议：

### 即时行动建议
- 需要立即采取的行动
- 紧急情况处理
- 症状缓解措施
- 医疗咨询建议

### 生活方式调整
- 饮食建议
- 运动建议
- 作息调整
- 压力管理

### 监测计划
- 需要监测的指标
- 监测频率建议
- 预警信号识别
- 记录方法建议

### 医疗咨询建议
- 建议咨询的科室
- 需要进行的检查
- 咨询时机建议
- 问题准备建议

### 长期健康管理
- 健康目标设定
- 预防措施建议
- 定期检查计划
- 健康改善计划

请提供具体、可操作的建议。
```

### 5. 用户档案更新 Prompt

```
作为健康档案管理专家，请基于以下信息更新用户健康档案：

## 当前档案信息
{current_profile}

## 新的分析结果
{new_analysis}

## 健康变化
{health_changes}

## 档案更新任务
请更新以下信息：

### 症状记录更新
- 新增症状记录
- 症状变化趋势
- 症状缓解情况
- 症状严重程度变化

### 健康指标更新
- 生命体征变化
- 健康指标趋势
- 异常指标记录
- 改善指标记录

### 风险评估更新
- 风险等级变化
- 新增风险因素
- 风险缓解情况
- 风险趋势分析

### 建议记录更新
- 新建议记录
- 建议执行情况
- 建议效果评估
- 建议调整记录

### 生活方式更新
- 生活方式变化
- 习惯改善情况
- 环境因素变化
- 社会因素影响

请提供详细的档案更新建议。
```

## 🔄 Prompt 使用流程

### 1. 数据准备阶段
```python
def prepare_analysis_data(user_id, user_query):
    # 获取用户基本信息
    user_info = get_user_basic_info(user_id)
    
    # 获取近期身体状况
    health_data = get_recent_health_data(user_id, days=30)
    
    # RAG检索相关医学知识
    rag_results = rag_system.search(user_query, top_k=5)
    
    # 构建分析上下文
    analysis_context = {
        'user_id': user_id,
        'user_query': user_query,
        'user_info': user_info,
        'health_data': health_data,
        'rag_knowledge': rag_results
    }
    
    return analysis_context
```

### 2. 分析执行阶段
```python
def execute_analysis(analysis_context):
    # 1. 症状分析
    symptom_prompt = build_symptom_analysis_prompt(analysis_context)
    symptom_result = qwen_model.analyze(symptom_prompt)
    
    # 2. 风险评估
    risk_prompt = build_risk_assessment_prompt(analysis_context, symptom_result)
    risk_result = qwen_model.analyze(risk_prompt)
    
    # 3. 建议生成
    recommendation_prompt = build_recommendation_prompt(analysis_context, symptom_result, risk_result)
    recommendation_result = qwen_model.analyze(recommendation_prompt)
    
    # 4. 档案更新
    profile_update_prompt = build_profile_update_prompt(analysis_context, symptom_result, risk_result, recommendation_result)
    profile_update_result = qwen_model.analyze(profile_update_prompt)
    
    return {
        'symptom_analysis': symptom_result,
        'risk_assessment': risk_result,
        'recommendations': recommendation_result,
        'profile_updates': profile_update_result
    }
```

### 3. 结果整合阶段
```python
def integrate_results(analysis_results):
    # 整合所有分析结果
    comprehensive_report = {
        'timestamp': datetime.now(),
        'analysis_results': analysis_results,
        'confidence_score': calculate_confidence(analysis_results),
        'summary': generate_summary(analysis_results)
    }
    
    # 更新用户档案
    update_user_profile(comprehensive_report)
    
    return comprehensive_report
```

## 📊 Prompt 优化策略

### 1. 上下文管理
- 保持上下文长度在合理范围内
- 重要信息优先放置
- 使用结构化格式提高可读性

### 2. 角色定义
- 明确AI的专业角色
- 设定分析目标和范围
- 定义回答格式要求

### 3. 示例引导
- 提供分析示例
- 展示期望的输出格式
- 给出质量标准

### 4. 迭代优化
- 根据实际效果调整prompt
- 收集用户反馈进行改进
- 持续优化分析质量

## 🎯 预期输出格式

### 分析报告结构
```json
{
    "analysis_id": "unique_id",
    "timestamp": "2024-01-01T00:00:00Z",
    "user_id": "user_001",
    "symptom_analysis": {
        "main_symptoms": ["symptom1", "symptom2"],
        "possible_causes": ["cause1", "cause2"],
        "severity": "moderate",
        "urgency": "low"
    },
    "risk_assessment": {
        "immediate_risk": "low",
        "long_term_risk": "moderate",
        "risk_factors": ["factor1", "factor2"]
    },
    "recommendations": {
        "immediate_actions": ["action1", "action2"],
        "lifestyle_changes": ["change1", "change2"],
        "medical_consultation": "recommended"
    },
    "profile_updates": {
        "new_symptoms": ["symptom1"],
        "health_indicators": ["indicator1"],
        "follow_up_plan": ["plan1", "plan2"]
    },
    "confidence_score": 0.85
}
```

这个prompt设计为您的智能医疗分析系统提供了完整的分析框架，您可以根据实际需求进行调整和优化。

