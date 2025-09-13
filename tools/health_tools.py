#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能健康管理助手 - 工具链实现

实现健康管理相关的各种工具，包括症状查询、药物信息、健康数据分析等。
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from qwen_agent.tools.base import BaseTool, register_tool

logger = logging.getLogger(__name__)

# ====== 症状查询工具 ======

@register_tool('query_symptoms')
class SymptomQueryTool(BaseTool):
    """
    症状查询工具 - 快速查询症状的可能原因和初步建议
    """
    description = '查询症状的可能原因和初步建议，适用于快速症状咨询'
    parameters = [{
        'name': 'symptoms',
        'type': 'array',
        'description': '症状列表，如["头痛", "发热", "咳嗽"]',
        'required': True
    }, {
        'name': 'severity',
        'type': 'string',
        'description': '症状严重程度：轻度、中度、重度',
        'required': False
    }, {
        'name': 'duration',
        'type': 'string',
        'description': '症状持续时间，如"2天"、"1周"等',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        """执行症状查询"""
        try:
            args = json.loads(params)
            symptoms = args.get('symptoms', [])
            severity = args.get('severity', '中度')
            duration = args.get('duration', '未知')
            
            # 症状数据库（实际应用中应连接真实医疗数据库）
            symptom_database = {
                "头痛": {
                    "possible_causes": ["紧张性头痛", "偏头痛", "感冒", "高血压", "睡眠不足"],
                    "urgency": "低",
                    "suggestions": ["休息", "多喝水", "避免强光", "如持续严重请就医"]
                },
                "发热": {
                    "possible_causes": ["病毒感染", "细菌感染", "感冒", "流感", "炎症"],
                    "urgency": "中",
                    "suggestions": ["多休息", "多喝水", "物理降温", "如体温超过38.5°C请就医"]
                },
                "咳嗽": {
                    "possible_causes": ["感冒", "支气管炎", "过敏", "哮喘", "肺炎"],
                    "urgency": "低",
                    "suggestions": ["多喝水", "避免刺激性食物", "如持续超过2周请就医"]
                },
                "胸痛": {
                    "possible_causes": ["心绞痛", "心肌梗死", "肺栓塞", "气胸", "肌肉拉伤"],
                    "urgency": "高",
                    "suggestions": ["立即就医", "拨打急救电话", "保持冷静"]
                },
                "呼吸困难": {
                    "possible_causes": ["哮喘", "肺炎", "肺栓塞", "心力衰竭", "过敏反应"],
                    "urgency": "高",
                    "suggestions": ["立即就医", "保持坐位", "如严重请拨打急救电话"]
                }
            }
            
            result = f"症状分析报告：\n"
            result += f"症状：{', '.join(symptoms)}\n"
            result += f"严重程度：{severity}\n"
            result += f"持续时间：{duration}\n\n"
            
            for symptom in symptoms:
                if symptom in symptom_database:
                    data = symptom_database[symptom]
                    result += f"【{symptom}】\n"
                    result += f"可能原因：{', '.join(data['possible_causes'])}\n"
                    result += f"紧急程度：{data['urgency']}\n"
                    result += f"建议：{', '.join(data['suggestions'])}\n\n"
                else:
                    result += f"【{symptom}】\n"
                    result += "未找到相关信息，建议咨询专业医生\n\n"
            
            # 添加通用建议
            result += "⚠️ 重要提醒：\n"
            result += "- 以上信息仅供参考，不能替代专业医疗诊断\n"
            result += "- 如症状持续或加重，请及时就医\n"
            result += "- 紧急情况请立即拨打急救电话120\n"
            
            return result
            
        except Exception as e:
            logger.error(f"症状查询失败: {str(e)}")
            return f"症状查询失败：{str(e)}"

# ====== 药物信息工具 ======

@register_tool('query_medication')
class MedicationInfoTool(BaseTool):
    """
    药物信息工具 - 查询药物详细信息
    """
    description = '查询药物的用法、副作用、相互作用等详细信息'
    parameters = [{
        'name': 'medication_name',
        'type': 'string',
        'description': '药物名称，如"阿司匹林"、"布洛芬"等',
        'required': True
    }, {
        'name': 'query_type',
        'type': 'string',
        'description': '查询类型：用法、副作用、相互作用、禁忌症',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        """执行药物信息查询"""
        try:
            args = json.loads(params)
            medication_name = args.get('medication_name', '')
            query_type = args.get('query_type', 'all')
            
            # 药物数据库（实际应用中应连接真实药物数据库）
            medication_database = {
                "阿司匹林": {
                    "用法": "成人每次100-300mg，每日1-3次，饭后服用",
                    "副作用": "胃肠道不适、出血风险、过敏反应",
                    "相互作用": "与华法林、肝素等抗凝药物合用增加出血风险",
                    "禁忌症": "活动性出血、严重肝肾功能不全、过敏体质"
                },
                "布洛芬": {
                    "用法": "成人每次200-400mg，每日3-4次，饭后服用",
                    "副作用": "胃肠道刺激、头痛、皮疹",
                    "相互作用": "与降压药合用可能影响降压效果",
                    "禁忌症": "严重心功能不全、活动性消化道溃疡"
                },
                "对乙酰氨基酚": {
                    "用法": "成人每次500-1000mg，每日3-4次，最大剂量4g/日",
                    "副作用": "肝毒性（过量时）、皮疹",
                    "相互作用": "与酒精合用增加肝毒性风险",
                    "禁忌症": "严重肝功能不全、对本品过敏"
                }
            }
            
            if medication_name not in medication_database:
                return f"未找到药物 '{medication_name}' 的信息。请确认药物名称是否正确。"
            
            data = medication_database[medication_name]
            result = f"药物信息：{medication_name}\n\n"
            
            if query_type == 'all':
                for key, value in data.items():
                    result += f"【{key}】\n{value}\n\n"
            elif query_type in data:
                result += f"【{query_type}】\n{data[query_type]}\n"
            else:
                result += f"未找到查询类型 '{query_type}' 的信息。\n"
                result += f"可用查询类型：{', '.join(data.keys())}\n"
            
            result += "⚠️ 重要提醒：\n"
            result += "- 以上信息仅供参考，具体用药请遵医嘱\n"
            result += "- 用药前请仔细阅读药品说明书\n"
            result += "- 如有疑问请咨询专业药师或医生\n"
            
            return result
            
        except Exception as e:
            logger.error(f"药物信息查询失败: {str(e)}")
            return f"药物信息查询失败：{str(e)}"

# ====== 健康数据分析工具 ======

@register_tool('analyze_health_data')
class HealthDataAnalysisTool(BaseTool):
    """
    健康数据分析工具 - 分析健康数据趋势和模式
    """
    description = '分析健康数据趋势和模式，提供数据洞察'
    parameters = [{
        'name': 'data_type',
        'type': 'string',
        'description': '数据类型：血压、血糖、心率、体重、体温等',
        'required': True
    }, {
        'name': 'time_range',
        'type': 'string',
        'description': '时间范围：最近一周、一个月、三个月等',
        'required': True
    }, {
        'name': 'user_id',
        'type': 'string',
        'description': '用户ID，用于获取用户数据',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        """执行健康数据分析"""
        try:
            args = json.loads(params)
            data_type = args.get('data_type', '')
            time_range = args.get('time_range', '')
            user_id = args.get('user_id', 'default')
            
            # 模拟健康数据分析（实际应用中应连接真实数据）
            analysis_result = f"健康数据分析报告\n"
            analysis_result += f"数据类型：{data_type}\n"
            analysis_result += f"分析时间范围：{time_range}\n\n"
            
            # 根据数据类型提供分析
            if data_type == "血压":
                analysis_result += "【血压分析】\n"
                analysis_result += "正常范围：收缩压90-140mmHg，舒张压60-90mmHg\n"
                analysis_result += "趋势分析：您的血压在正常范围内波动\n"
                analysis_result += "建议：保持规律作息，适量运动，低盐饮食\n\n"
                
            elif data_type == "血糖":
                analysis_result += "【血糖分析】\n"
                analysis_result += "正常范围：空腹3.9-6.1mmol/L，餐后2小时<7.8mmol/L\n"
                analysis_result += "趋势分析：血糖水平相对稳定\n"
                analysis_result += "建议：控制饮食，规律运动，定期监测\n\n"
                
            elif data_type == "心率":
                analysis_result += "【心率分析】\n"
                analysis_result += "正常范围：60-100次/分钟\n"
                analysis_result += "趋势分析：心率在正常范围内\n"
                analysis_result += "建议：保持规律运动，避免过度疲劳\n\n"
                
            elif data_type == "体重":
                analysis_result += "【体重分析】\n"
                analysis_result += "BMI计算：体重(kg) / 身高(m)²\n"
                analysis_result += "正常范围：18.5-23.9\n"
                analysis_result += "趋势分析：体重变化趋势稳定\n"
                analysis_result += "建议：保持均衡饮食，适量运动\n\n"
                
            else:
                analysis_result += f"【{data_type}分析】\n"
                analysis_result += "数据趋势：整体稳定\n"
                analysis_result += "建议：继续监测，如有异常请及时就医\n\n"
            
            # 添加通用分析建议
            analysis_result += "📊 数据洞察：\n"
            analysis_result += "- 数据整体趋势良好\n"
            analysis_result += "- 建议继续保持健康生活方式\n"
            analysis_result += "- 定期监测，及时发现异常\n\n"
            
            analysis_result += "⚠️ 重要提醒：\n"
            analysis_result += "- 以上分析基于提供的数据，仅供参考\n"
            analysis_result += "- 如有异常或不适，请及时咨询专业医生\n"
            analysis_result += "- 健康数据应结合临床症状综合判断\n"
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"健康数据分析失败: {str(e)}")
            return f"健康数据分析失败：{str(e)}"

# ====== 健康风险评估工具 ======

@register_tool('assess_health_risk')
class RiskAssessmentTool(BaseTool):
    """
    健康风险评估工具 - 评估特定疾病的风险
    """
    description = '评估特定疾病的风险，提供预防建议'
    parameters = [{
        'name': 'disease_type',
        'type': 'string',
        'description': '疾病类型：糖尿病、高血压、心血管疾病、癌症等',
        'required': True
    }, {
        'name': 'risk_factors',
        'type': 'object',
        'description': '风险因素：年龄、家族史、生活方式等',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        """执行健康风险评估"""
        try:
            args = json.loads(params)
            disease_type = args.get('disease_type', '')
            risk_factors = args.get('risk_factors', {})
            
            result = f"健康风险评估报告\n"
            result += f"评估疾病：{disease_type}\n\n"
            
            # 风险因素分析
            result += "【风险因素分析】\n"
            risk_score = 0
            max_score = 10
            
            # 年龄因素
            age = risk_factors.get('age', 0)
            if age > 65:
                risk_score += 3
                result += f"- 年龄：{age}岁（高风险年龄段）\n"
            elif age > 45:
                risk_score += 2
                result += f"- 年龄：{age}岁（中等风险年龄段）\n"
            else:
                result += f"- 年龄：{age}岁（低风险年龄段）\n"
            
            # 家族史
            family_history = risk_factors.get('family_history', False)
            if family_history:
                risk_score += 2
                result += "- 家族史：有相关疾病家族史（增加风险）\n"
            else:
                result += "- 家族史：无相关疾病家族史\n"
            
            # 生活方式
            smoking = risk_factors.get('smoking', False)
            if smoking:
                risk_score += 2
                result += "- 吸烟：是（增加风险）\n"
            else:
                result += "- 吸烟：否\n"
            
            exercise = risk_factors.get('exercise', '无')
            if exercise == '无':
                risk_score += 1
                result += "- 运动：缺乏运动（增加风险）\n"
            else:
                result += f"- 运动：{exercise}\n"
            
            diet = risk_factors.get('diet', '不健康')
            if diet == '不健康':
                risk_score += 1
                result += "- 饮食：不健康（增加风险）\n"
            else:
                result += f"- 饮食：{diet}\n"
            
            # 风险等级评估
            risk_percentage = (risk_score / max_score) * 100
            
            result += f"\n【风险评估结果】\n"
            result += f"风险评分：{risk_score}/{max_score} ({risk_percentage:.1f}%)\n"
            
            if risk_percentage >= 70:
                risk_level = "高风险"
                result += f"风险等级：{risk_level}\n"
                result += "建议：立即采取预防措施，定期体检，咨询专业医生\n"
            elif risk_percentage >= 40:
                risk_level = "中等风险"
                result += f"风险等级：{risk_level}\n"
                result += "建议：改善生活方式，定期监测，预防为主\n"
            else:
                risk_level = "低风险"
                result += f"风险等级：{risk_level}\n"
                result += "建议：保持健康生活方式，定期体检\n"
            
            # 预防建议
            result += f"\n【预防建议】\n"
            if disease_type == "糖尿病":
                result += "- 控制体重，维持健康BMI\n"
                result += "- 低糖低脂饮食，多吃蔬菜水果\n"
                result += "- 规律运动，每周至少150分钟中等强度运动\n"
                result += "- 定期监测血糖，早期发现异常\n"
            elif disease_type == "高血压":
                result += "- 低盐饮食，每日盐摄入量<6g\n"
                result += "- 规律运动，控制体重\n"
                result += "- 戒烟限酒，保持良好作息\n"
                result += "- 定期监测血压，早期干预\n"
            elif disease_type == "心血管疾病":
                result += "- 健康饮食，减少饱和脂肪摄入\n"
                result += "- 规律运动，增强心肺功能\n"
                result += "- 控制血压、血糖、血脂\n"
                result += "- 戒烟限酒，管理压力\n"
            else:
                result += "- 保持健康生活方式\n"
                result += "- 定期体检，早期筛查\n"
                result += "- 避免已知危险因素\n"
                result += "- 及时就医，规范治疗\n"
            
            result += "\n⚠️ 重要提醒：\n"
            result += "- 以上评估仅供参考，不能替代专业医疗诊断\n"
            result += "- 如有疑问请咨询专业医生\n"
            result += "- 定期体检是预防疾病的重要手段\n"
            
            return result
            
        except Exception as e:
            logger.error(f"健康风险评估失败: {str(e)}")
            return f"健康风险评估失败：{str(e)}"

# ====== 健康计划生成工具 ======

@register_tool('generate_health_plan')
class HealthPlanGeneratorTool(BaseTool):
    """
    健康计划生成工具 - 生成个性化健康计划
    """
    description = '根据用户健康状况和目标生成个性化健康计划'
    parameters = [{
        'name': 'goal_type',
        'type': 'string',
        'description': '目标类型：减肥、增肌、血压控制、血糖管理、健康维护等',
        'required': True
    }, {
        'name': 'current_condition',
        'type': 'object',
        'description': '当前健康状况和限制条件',
        'required': True
    }, {
        'name': 'time_frame',
        'type': 'string',
        'description': '计划时间框架：1个月、3个月、6个月、1年',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        """执行健康计划生成"""
        try:
            args = json.loads(params)
            goal_type = args.get('goal_type', '')
            current_condition = args.get('current_condition', {})
            time_frame = args.get('time_frame', '3个月')
            
            result = f"个性化健康计划\n"
            result += f"目标：{goal_type}\n"
            result += f"计划周期：{time_frame}\n\n"
            
            # 根据目标类型生成计划
            if goal_type == "减肥":
                result += self._generate_weight_loss_plan(current_condition, time_frame)
            elif goal_type == "增肌":
                result += self._generate_muscle_gain_plan(current_condition, time_frame)
            elif goal_type == "血压控制":
                result += self._generate_blood_pressure_plan(current_condition, time_frame)
            elif goal_type == "血糖管理":
                result += self._generate_blood_sugar_plan(current_condition, time_frame)
            else:
                result += self._generate_general_health_plan(current_condition, time_frame)
            
            result += "\n⚠️ 重要提醒：\n"
            result += "- 以上计划仅供参考，具体执行请根据个人情况调整\n"
            result += "- 如有慢性疾病，请咨询专业医生后再执行\n"
            result += "- 计划执行过程中如有不适，请及时调整或就医\n"
            
            return result
            
        except Exception as e:
            logger.error(f"健康计划生成失败: {str(e)}")
            return f"健康计划生成失败：{str(e)}"
    
    def _generate_weight_loss_plan(self, condition: Dict, time_frame: str) -> str:
        """生成减肥计划"""
        plan = "【减肥计划】\n\n"
        plan += "饮食计划：\n"
        plan += "- 控制总热量摄入，每日减少500-750卡路里\n"
        plan += "- 增加蛋白质摄入，每餐包含优质蛋白\n"
        plan += "- 多吃蔬菜水果，增加膳食纤维\n"
        plan += "- 减少精制糖和加工食品\n"
        plan += "- 多喝水，每日至少8杯水\n\n"
        
        plan += "运动计划：\n"
        plan += "- 有氧运动：每周5次，每次30-45分钟\n"
        plan += "- 力量训练：每周2-3次，每次20-30分钟\n"
        plan += "- 日常活动：增加步行，减少久坐\n"
        plan += "- 循序渐进，避免过度运动\n\n"
        
        plan += "监测指标：\n"
        plan += "- 每周称重1-2次\n"
        plan += "- 记录饮食和运动\n"
        plan += "- 监测体脂率和肌肉量\n"
        plan += "- 关注身体感受和能量水平\n"
        
        return plan
    
    def _generate_muscle_gain_plan(self, condition: Dict, time_frame: str) -> str:
        """生成增肌计划"""
        plan = "【增肌计划】\n\n"
        plan += "饮食计划：\n"
        plan += "- 增加蛋白质摄入，每日1.6-2.2g/kg体重\n"
        plan += "- 适量增加碳水化合物，提供训练能量\n"
        plan += "- 健康脂肪摄入，支持激素合成\n"
        plan += "- 分餐制，每日5-6餐\n"
        plan += "- 训练后及时补充蛋白质和碳水化合物\n\n"
        
        plan += "训练计划：\n"
        plan += "- 力量训练：每周4-5次，每次45-60分钟\n"
        plan += "- 复合动作为主：深蹲、硬拉、卧推、引体向上\n"
        plan += "- 渐进超负荷，逐步增加重量和次数\n"
        plan += "- 充分休息，肌肉需要48-72小时恢复\n\n"
        
        plan += "监测指标：\n"
        plan += "- 记录训练重量和次数\n"
        plan += "- 监测体重和体脂率\n"
        plan += "- 拍照记录身体变化\n"
        plan += "- 关注力量和耐力提升\n"
        
        return plan
    
    def _generate_blood_pressure_plan(self, condition: Dict, time_frame: str) -> str:
        """生成血压控制计划"""
        plan = "【血压控制计划】\n\n"
        plan += "饮食计划：\n"
        plan += "- DASH饮食：多吃蔬菜、水果、全谷物\n"
        plan += "- 低钠饮食：每日盐摄入量<6g\n"
        plan += "- 增加钾摄入：香蕉、橙子、菠菜等\n"
        plan += "- 限制酒精摄入：男性<2杯/日，女性<1杯/日\n"
        plan += "- 减少饱和脂肪和反式脂肪\n\n"
        
        plan += "生活方式：\n"
        plan += "- 规律运动：每周至少150分钟中等强度运动\n"
        plan += "- 控制体重：维持健康BMI\n"
        plan += "- 戒烟：完全戒烟\n"
        plan += "- 管理压力：冥想、瑜伽、深呼吸\n"
        plan += "- 充足睡眠：每晚7-9小时\n\n"
        
        plan += "监测指标：\n"
        plan += "- 每日监测血压，记录数据\n"
        plan += "- 定期体检，检查相关指标\n"
        plan += "- 记录症状和用药情况\n"
        plan += "- 与医生保持沟通\n"
        
        return plan
    
    def _generate_blood_sugar_plan(self, condition: Dict, time_frame: str) -> str:
        """生成血糖管理计划"""
        plan = "【血糖管理计划】\n\n"
        plan += "饮食计划：\n"
        plan += "- 控制碳水化合物摄入，选择低GI食物\n"
        plan += "- 增加膳食纤维：蔬菜、全谷物、豆类\n"
        plan += "- 适量蛋白质，每餐包含\n"
        plan += "- 控制餐量，少食多餐\n"
        plan += "- 避免高糖食物和饮料\n\n"
        
        plan += "运动计划：\n"
        plan += "- 有氧运动：每周至少150分钟\n"
        plan += "- 力量训练：每周2-3次\n"
        plan += "- 餐后散步：每次餐后15-30分钟\n"
        plan += "- 避免空腹运动\n\n"
        
        plan += "监测指标：\n"
        plan += "- 定期监测血糖：空腹、餐后2小时\n"
        plan += "- 记录饮食和运动\n"
        plan += "- 监测体重和腰围\n"
        plan += "- 定期检查糖化血红蛋白\n"
        
        return plan
    
    def _generate_general_health_plan(self, condition: Dict, time_frame: str) -> str:
        """生成一般健康计划"""
        plan = "【健康维护计划】\n\n"
        plan += "饮食计划：\n"
        plan += "- 均衡饮食：多样化食物选择\n"
        plan += "- 多吃蔬菜水果：每日5份以上\n"
        plan += "- 适量蛋白质：鱼、肉、蛋、豆类\n"
        plan += "- 全谷物：选择全麦、糙米等\n"
        plan += "- 限制加工食品和含糖饮料\n\n"
        
        plan += "运动计划：\n"
        plan += "- 有氧运动：每周至少150分钟中等强度\n"
        plan += "- 力量训练：每周2次以上\n"
        plan += "- 柔韧性训练：每周2-3次\n"
        plan += "- 日常活动：多步行，少久坐\n\n"
        
        plan += "生活方式：\n"
        plan += "- 充足睡眠：每晚7-9小时\n"
        plan += "- 管理压力：找到适合自己的减压方式\n"
        plan += "- 戒烟限酒：避免有害物质\n"
        plan += "- 定期体检：预防胜于治疗\n"
        
        return plan
