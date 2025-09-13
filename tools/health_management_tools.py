#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康管理工具集

为健康管理Agent提供各种健康分析和管理功能
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qwen_agent.tools.base import BaseTool, register_tool
from src.user_profile import HealthProfile, HealthProfileManager
from tools.health_comparison import HealthComparison

logger = logging.getLogger(__name__)

class HealthDataExtractor:
    """健康数据提取器"""
    
    def __init__(self, profiles_dir: str = "data/profiles"):
        self.profiles_dir = profiles_dir
        self.profile_manager = HealthProfileManager(profiles_dir)
        self.comparison_tool = HealthComparison()
        # 初始化时加载所有用户数据
        self._load_profiles()
    
    def _load_profiles(self):
        """加载所有用户数据"""
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            profiles_path = os.path.join(project_root, self.profiles_dir)
            
            if os.path.exists(profiles_path):
                self.profile_manager.load_all_profiles(profiles_path)
                logger.info(f"成功加载 {len(self.profile_manager.profiles)} 个用户数据")
            else:
                logger.warning(f"用户数据目录不存在: {profiles_path}")
        except Exception as e:
            logger.error(f"加载用户数据失败: {e}")
    
    def get_user_profile(self, user_id: str) -> Optional[HealthProfile]:
        """获取用户健康画像"""
        try:
            # 从已加载的数据中获取
            profile = self.profile_manager.get_profile(user_id)
            if profile:
                return profile
            
            # 如果内存中没有，尝试从文件加载
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            filepath = os.path.join(project_root, self.profiles_dir, f"{user_id}_profile.json")
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return HealthProfile.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"获取用户画像失败: {e}")
            return None
    
    def get_user_health_comparison(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户健康对比分析结果"""
        try:
            profile = self.get_user_profile(user_id)
            if profile:
                return self.comparison_tool.comprehensive_comparison(profile)
            return None
        except Exception as e:
            logger.error(f"获取健康对比分析失败: {e}")
            return None
    
    def get_user_health_trend(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取用户健康趋势数据"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                return {"error": "用户数据不存在"}
            
            trend_data = {}
            
            # 获取各种健康数据的历史趋势
            for data_type in ['血压', '体重', '心率', '步数', '睡眠']:
                if data_type in profile.health_data_history:
                    data_points = profile.health_data_history[data_type]
                    # 获取最近N天的数据
                    recent_data = data_points[-days:] if len(data_points) >= days else data_points
                    trend_data[data_type] = recent_data
            
            return {
                "user_id": user_id,
                "trend_period": f"最近{days}天",
                "data_points": trend_data,
                "summary": self._analyze_trend_summary(trend_data)
            }
        except Exception as e:
            logger.error(f"获取健康趋势失败: {e}")
            return {"error": str(e)}
    
    def _analyze_trend_summary(self, trend_data: Dict[str, List]) -> Dict[str, Any]:
        """分析趋势摘要"""
        summary = {}
        
        for data_type, data_points in trend_data.items():
            if not data_points:
                continue
                
            values = []
            for point in data_points:
                if isinstance(point.get('value'), (int, float)):
                    values.append(point['value'])
                elif isinstance(point.get('value'), dict):
                    # 处理血压等复合数据
                    if 'systolic' in point['value']:
                        values.append(point['value']['systolic'])
            
            if values:
                summary[data_type] = {
                    "count": len(values),
                    "latest": values[-1],
                    "average": sum(values) / len(values),
                    "trend": self._calculate_trend(values)
                }
        
        return summary
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算数据趋势"""
        if len(values) < 2:
            return "数据不足"
        
        # 简单线性趋势分析
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change_percent = ((second_avg - first_avg) / first_avg) * 100
        
        if abs(change_percent) < 2:
            return "稳定"
        elif change_percent > 0:
            return f"上升 {change_percent:.1f}%"
        else:
            return f"下降 {abs(change_percent):.1f}%"

class HealthAnalysisEngine:
    """健康分析引擎"""
    
    def __init__(self):
        self.data_extractor = HealthDataExtractor()
    
    def analyze_health_trend(self, user_id: str) -> Dict[str, Any]:
        """分析健康趋势"""
        try:
            # 获取用户对比分析
            comparison = self.data_extractor.get_user_health_comparison(user_id)
            if not comparison:
                return {"error": "无法获取用户健康对比数据"}
            
            # 获取健康趋势数据
            trend_data = self.data_extractor.get_user_health_trend(user_id)
            
            # 综合分析
            analysis = {
                "user_id": user_id,
                "analysis_date": datetime.now().isoformat(),
                "current_status": comparison,
                "trend_analysis": trend_data,
                "key_findings": self._extract_key_findings(comparison, trend_data),
                "recommendations": self._generate_recommendations(comparison, trend_data)
            }
            
            return analysis
        except Exception as e:
            logger.error(f"健康趋势分析失败: {e}")
            return {"error": str(e)}
    
    def _extract_key_findings(self, comparison: Dict, trend_data: Dict) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 基于对比分析的关键发现
        if comparison.get('total_abnormal', 0) > 0:
            findings.append(f"发现{comparison['total_abnormal']}项指标偏离正常范围")
        
        if comparison.get('risk_comparison', {}).get('total_risk_factors', 0) > 0:
            findings.append(f"存在{comparison['risk_comparison']['total_risk_factors']}个健康风险因素")
        
        # 基于趋势分析的关键发现
        if 'summary' in trend_data:
            for data_type, summary in trend_data['summary'].items():
                if summary.get('trend') != '稳定':
                    findings.append(f"{data_type}呈现{summary['trend']}趋势")
        
        return findings
    
    def _generate_recommendations(self, comparison: Dict, trend_data: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于异常指标的建议
        for indicator in comparison.get('abnormal_indicators', []):
            if indicator['indicator'] == 'BMI':
                if indicator['user_value'] > 25:
                    recommendations.append("建议控制饮食，增加运动，适当减重")
                else:
                    recommendations.append("建议增加营养摄入，适当增重")
        
        # 基于风险因素的建议
        for risk in comparison.get('risk_comparison', {}).get('risk_factors', []):
            recommendations.extend(risk.get('prevention', []))
        
        return list(set(recommendations))  # 去重

class HealthPlanGenerator:
    """健康计划生成器"""
    
    def __init__(self):
        self.data_extractor = HealthDataExtractor()
    
    def generate_personalized_plan(self, user_id: str) -> Dict[str, Any]:
        """生成个性化健康计划"""
        try:
            comparison = self.data_extractor.get_user_health_comparison(user_id)
            if not comparison:
                return {"error": "无法获取用户健康数据"}
            
            profile = self.data_extractor.get_user_profile(user_id)
            if not profile:
                return {"error": "无法获取用户画像"}
            
            plan = {
                "user_id": user_id,
                "plan_date": datetime.now().isoformat(),
                "target_period": "3个月",
                "current_status": {
                    "bmi_status": comparison['bmi_comparison']['status'],
                    "abnormal_indicators": comparison['total_abnormal'],
                    "risk_factors": comparison['risk_comparison']['total_risk_factors']
                },
                "goals": self._generate_goals(comparison, profile),
                "action_plan": self._generate_action_plan(comparison, profile),
                "monitoring_plan": self._generate_monitoring_plan(profile),
                "timeline": self._generate_timeline()
            }
            
            return plan
        except Exception as e:
            logger.error(f"生成健康计划失败: {e}")
            return {"error": str(e)}
    
    def _generate_goals(self, comparison: Dict, profile: HealthProfile) -> List[Dict[str, Any]]:
        """生成健康目标"""
        goals = []
        
        # BMI目标
        current_bmi = comparison['bmi_comparison']['user_value']
        if current_bmi > 25:
            target_bmi = max(22, current_bmi - 2)
            goals.append({
                "type": "体重管理",
                "current": f"BMI {current_bmi:.1f}",
                "target": f"BMI {target_bmi:.1f}",
                "timeline": "3个月"
            })
        
        # 生活方式目标
        lifestyle = comparison['lifestyle_comparison']
        if not lifestyle['exercise_frequency']['is_optimal']:
            goals.append({
                "type": "运动习惯",
                "current": lifestyle['exercise_frequency']['user_value'],
                "target": "每周3-4次",
                "timeline": "1个月"
            })
        
        return goals
    
    def _generate_action_plan(self, comparison: Dict, profile: HealthProfile) -> List[Dict[str, Any]]:
        """生成行动计划"""
        actions = []
        
        # 基于异常指标的行动
        for indicator in comparison.get('abnormal_indicators', []):
            if indicator['indicator'] == 'BMI':
                actions.append({
                    "category": "饮食管理",
                    "action": "控制每日热量摄入",
                    "frequency": "每日",
                    "description": "减少高热量食物，增加蔬菜水果"
                })
                actions.append({
                    "category": "运动锻炼",
                    "action": "有氧运动",
                    "frequency": "每周3-4次",
                    "description": "每次30-45分钟中等强度运动"
                })
        
        return actions
    
    def _generate_monitoring_plan(self, profile: HealthProfile) -> Dict[str, Any]:
        """生成监测计划"""
        return {
            "daily": ["体重", "血压", "步数"],
            "weekly": ["运动频率", "睡眠质量"],
            "monthly": ["BMI", "健康评估"]
        }
    
    def _generate_timeline(self) -> List[Dict[str, Any]]:
        """生成时间线"""
        return [
            {"week": "1-2周", "focus": "建立健康习惯", "target": "适应新的饮食和运动计划"},
            {"week": "3-4周", "focus": "巩固习惯", "target": "形成稳定的健康生活方式"},
            {"week": "5-8周", "focus": "优化调整", "target": "根据效果调整计划"},
            {"week": "9-12周", "focus": "长期维持", "target": "建立长期健康管理机制"}
        ]

class HealthRiskAssessment:
    """健康风险评估器"""
    
    def __init__(self):
        self.data_extractor = HealthDataExtractor()
    
    def assess_disease_risk(self, user_id: str) -> Dict[str, Any]:
        """评估疾病风险"""
        try:
            comparison = self.data_extractor.get_user_health_comparison(user_id)
            if not comparison:
                return {"error": "无法获取用户健康数据"}
            
            profile = self.data_extractor.get_user_profile(user_id)
            if not profile:
                return {"error": "无法获取用户画像"}
            
            risk_assessment = {
                "user_id": user_id,
                "assessment_date": datetime.now().isoformat(),
                "overall_risk_level": self._calculate_overall_risk(comparison),
                "disease_risks": self._assess_specific_risks(comparison, profile),
                "risk_factors": self._analyze_risk_factors(comparison),
                "prevention_recommendations": self._generate_prevention_plan(comparison, profile)
            }
            
            return risk_assessment
        except Exception as e:
            logger.error(f"疾病风险评估失败: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_risk(self, comparison: Dict) -> str:
        """计算总体风险等级"""
        abnormal_count = comparison.get('total_abnormal', 0)
        risk_factors = comparison.get('risk_comparison', {}).get('total_risk_factors', 0)
        
        if abnormal_count >= 4 or risk_factors >= 3:
            return "高风险"
        elif abnormal_count >= 2 or risk_factors >= 2:
            return "中风险"
        else:
            return "低风险"
    
    def _assess_specific_risks(self, comparison: Dict, profile: HealthProfile) -> List[Dict[str, Any]]:
        """评估具体疾病风险"""
        risks = []
        
        # 心血管疾病风险
        bmi = comparison['bmi_comparison']['user_value']
        if bmi > 25:
            risks.append({
                "disease": "心血管疾病",
                "risk_level": "中等",
                "factors": ["超重", "可能的高血压"],
                "probability": "15-25%"
            })
        
        # 糖尿病风险
        if bmi > 28:
            risks.append({
                "disease": "2型糖尿病",
                "risk_level": "中等",
                "factors": ["肥胖", "缺乏运动"],
                "probability": "10-20%"
            })
        
        return risks
    
    def _analyze_risk_factors(self, comparison: Dict) -> Dict[str, Any]:
        """分析风险因素"""
        return {
            "modifiable": [rf['name'] for rf in comparison.get('risk_comparison', {}).get('risk_factors', []) if rf['type'] == 'lifestyle'],
            "non_modifiable": [rf['name'] for rf in comparison.get('risk_comparison', {}).get('risk_factors', []) if rf['type'] == 'chronic_disease']
        }
    
    def _generate_prevention_plan(self, comparison: Dict, profile: HealthProfile) -> List[str]:
        """生成预防计划"""
        recommendations = []
        
        for risk in comparison.get('risk_comparison', {}).get('risk_factors', []):
            recommendations.extend(risk.get('prevention', []))
        
        return list(set(recommendations))

# 工具类，供Agent调用
from qwen_agent.tools import BaseTool

@register_tool('get_user_health_analysis')
class HealthAnalysisTool(BaseTool):
    """健康分析工具"""
    
    description = "获取用户健康分析数据，包括当前状态、趋势分析和关键发现"
    parameters = [
        {
            "name": "user_id",
            "type": "string",
            "description": "用户ID",
            "required": True
        }
    ]
    
    def call(self, params: str, **kwargs) -> str:
        """调用健康分析"""
        try:
            args = json.loads(params)
            user_id = args['user_id']
            engine = HealthAnalysisEngine()
            result = engine.analyze_health_trend(user_id)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"健康分析工具调用失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

@register_tool('generate_health_plan')
class HealthPlanTool(BaseTool):
    """健康计划工具"""
    
    description = "生成个性化健康计划，包括目标设定、行动计划和监测安排"
    parameters = [
        {
            "name": "user_id",
            "type": "string",
            "description": "用户ID",
            "required": True
        }
    ]
    
    def call(self, params: str, **kwargs) -> str:
        """调用健康计划生成"""
        try:
            args = json.loads(params)
            user_id = args['user_id']
            generator = HealthPlanGenerator()
            result = generator.generate_personalized_plan(user_id)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"健康计划工具调用失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

@register_tool('assess_health_risk')
class HealthRiskTool(BaseTool):
    """健康风险工具"""
    
    description = "评估用户疾病风险，包括总体风险等级和具体疾病风险"
    parameters = [
        {
            "name": "user_id",
            "type": "string",
            "description": "用户ID",
            "required": True
        }
    ]
    
    def call(self, params: str, **kwargs) -> str:
        """调用健康风险评估"""
        try:
            args = json.loads(params)
            user_id = args['user_id']
            assessor = HealthRiskAssessment()
            result = assessor.assess_disease_risk(user_id)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"健康风险工具调用失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)
