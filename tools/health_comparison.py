#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康指标客观对比分析工具

基于健康指标标准数据库，对用户健康画像进行客观数据对比分析
只显示用户数据与标准范围的对比情况，不进行评分评价
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.user_profile import HealthProfile

class HealthComparison:
    """健康指标客观对比分析器"""
    
    def __init__(self, standards_file: str = None):
        if standards_file is None:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            standards_file = os.path.join(project_root, "data", "health_standards.json")
        self.standards_file = standards_file
        self.standards = self.load_standards()
    
    def load_standards(self) -> Dict[str, Any]:
        """加载健康指标标准"""
        try:
            with open(self.standards_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载健康标准失败: {e}")
            return {}
    
    def get_age_group(self, age: int) -> str:
        """根据年龄获取年龄段"""
        for age_range, info in self.standards.get('age_groups', {}).items():
            if info['min'] <= age <= info['max']:
                return age_range
        return "76+"  # 默认返回最高年龄段
    
    def _calculate_deviation(self, value: float, normal_range: List[float]) -> Dict[str, Any]:
        """计算与正常范围的偏差"""
        min_val, max_val = normal_range
        
        if value < min_val:
            deviation_type = 'below'
            deviation_value = min_val - value
            deviation_percent = (deviation_value / min_val) * 100
        elif value > max_val:
            deviation_type = 'above'
            deviation_value = value - max_val
            deviation_percent = (deviation_value / max_val) * 100
        else:
            deviation_type = 'normal'
            deviation_value = 0
            deviation_percent = 0
        
        return {
            'type': deviation_type,
            'value': deviation_value,
            'percent': deviation_percent,
            'description': self._get_deviation_description(deviation_type, deviation_value, deviation_percent)
        }
    
    def _get_deviation_description(self, deviation_type: str, deviation_value: float, deviation_percent: float) -> str:
        """获取偏差描述"""
        if deviation_type == 'normal':
            return '在正常范围内'
        elif deviation_type == 'below':
            return f'低于正常范围 {deviation_value:.1f} ({deviation_percent:.1f}%)'
        else:  # above
            return f'高于正常范围 {deviation_value:.1f} ({deviation_percent:.1f}%)'
    
    def compare_bmi(self, bmi: float, age: int, gender: str) -> Dict[str, Any]:
        """对比BMI指标与标准范围"""
        age_group = self.get_age_group(age)
        ranges = self.standards['health_indicators']['bmi']['ranges'][gender][age_group]
        
        # 判断是否在正常范围内
        is_normal = ranges['normal'][0] <= bmi <= ranges['normal'][1]
        
        # 确定具体分类
        if bmi < ranges['normal'][0]:
            category = 'underweight'
            status = '偏瘦'
        elif bmi <= ranges['normal'][1]:
            category = 'normal'
            status = '正常'
        elif bmi <= ranges['overweight'][1]:
            category = 'overweight'
            status = '超重'
        else:
            category = 'obese'
            status = '肥胖'
        
        return {
            'indicator': 'BMI',
            'user_value': bmi,
            'unit': 'kg/m²',
            'age_group': age_group,
            'gender': gender,
            'normal_range': ranges['normal'],
            'is_normal': is_normal,
            'category': category,
            'status': status,
            'deviation': self._calculate_deviation(bmi, ranges['normal']),
            'standard_info': {
                'underweight_range': [0, ranges['normal'][0]],
                'normal_range': ranges['normal'],
                'overweight_range': [ranges['normal'][1], ranges['overweight'][1]],
                'obese_range': [ranges['overweight'][1], 100]
            }
        }
    
    def compare_blood_pressure(self, systolic: int, diastolic: int, age: int, gender: str) -> Dict[str, Any]:
        """对比血压指标与标准范围"""
        age_group = self.get_age_group(age)
        ranges = self.standards['health_indicators']['blood_pressure']['ranges'][gender][age_group]
        
        # 判断收缩压是否在正常范围内
        systolic_normal = ranges['normal'][0] <= systolic <= ranges['normal'][1]
        
        # 确定收缩压分类
        if systolic < ranges['normal'][0]:
            category = 'low'
            status = '偏低'
        elif systolic <= ranges['normal'][1]:
            category = 'normal'
            status = '正常'
        elif systolic <= ranges['high_normal'][1]:
            category = 'high_normal'
            status = '正常高值'
        else:
            category = 'hypertension'
            status = '高血压'
        
        return {
            'indicator': '血压',
            'user_value': f"{systolic}/{diastolic}",
            'unit': 'mmHg',
            'age_group': age_group,
            'gender': gender,
            'systolic': systolic,
            'diastolic': diastolic,
            'normal_range': ranges['normal'],
            'is_normal': systolic_normal,
            'category': category,
            'status': status,
            'deviation': self._calculate_deviation(systolic, ranges['normal']),
            'standard_info': {
                'low_range': [0, ranges['normal'][0]],
                'normal_range': ranges['normal'],
                'high_normal_range': [ranges['normal'][1], ranges['high_normal'][1]],
                'hypertension_range': [ranges['high_normal'][1], 200]
            }
        }
    
    def compare_heart_rate(self, heart_rate: int, age: int, gender: str) -> Dict[str, Any]:
        """对比心率指标与标准范围"""
        age_group = self.get_age_group(age)
        ranges = self.standards['health_indicators']['heart_rate']['ranges'][gender][age_group]
        
        # 判断是否在正常范围内
        is_normal = ranges['normal'][0] <= heart_rate <= ranges['normal'][1]
        
        # 确定分类
        if heart_rate < ranges['normal'][0]:
            category = 'low'
            status = '偏低'
        elif heart_rate <= ranges['normal'][1]:
            category = 'normal'
            status = '正常'
        else:
            category = 'high'
            status = '偏高'
        
        return {
            'indicator': '心率',
            'user_value': heart_rate,
            'unit': '次/分钟',
            'age_group': age_group,
            'gender': gender,
            'normal_range': ranges['normal'],
            'is_normal': is_normal,
            'category': category,
            'status': status,
            'deviation': self._calculate_deviation(heart_rate, ranges['normal']),
            'standard_info': {
                'low_range': [0, ranges['normal'][0]],
                'normal_range': ranges['normal'],
                'high_range': [ranges['normal'][1], 200]
            }
        }
    
    def compare_sleep(self, sleep_hours: float, age: int, gender: str) -> Dict[str, Any]:
        """对比睡眠指标与标准范围"""
        age_group = self.get_age_group(age)
        ranges = self.standards['health_indicators']['sleep_hours']['ranges'][gender][age_group]
        
        # 判断是否在最佳范围内
        is_optimal = ranges['optimal'][0] <= sleep_hours <= ranges['optimal'][1]
        
        # 确定分类
        if sleep_hours < ranges['optimal'][0]:
            category = 'insufficient'
            status = '不足'
        elif sleep_hours <= ranges['optimal'][1]:
            category = 'optimal'
            status = '充足'
        elif sleep_hours <= ranges['acceptable'][1]:
            category = 'acceptable'
            status = '可接受'
        else:
            category = 'excessive'
            status = '过多'
        
        return {
            'indicator': '睡眠时间',
            'user_value': sleep_hours,
            'unit': '小时',
            'age_group': age_group,
            'gender': gender,
            'optimal_range': ranges['optimal'],
            'is_optimal': is_optimal,
            'category': category,
            'status': status,
            'deviation': self._calculate_deviation(sleep_hours, ranges['optimal']),
            'standard_info': {
                'insufficient_range': [0, ranges['optimal'][0]],
                'optimal_range': ranges['optimal'],
                'acceptable_range': [ranges['optimal'][1], ranges['acceptable'][1]],
                'excessive_range': [ranges['acceptable'][1], 24]
            }
        }
    
    def compare_lifestyle(self, profile: HealthProfile) -> Dict[str, Any]:
        """对比生活方式指标与标准"""
        lifestyle = profile.lifestyle
        
        # 运动频率对比
        exercise_standard = self.standards['lifestyle_standards']['exercise_frequency']['categories']
        exercise_info = exercise_standard.get(lifestyle.exercise_frequency, {})
        
        # 睡眠质量对比
        sleep_standard = self.standards['lifestyle_standards']['sleep_quality']['categories']
        sleep_info = sleep_standard.get(lifestyle.sleep_quality, {})
        
        # 压力水平对比
        stress_standard = self.standards['lifestyle_standards']['stress_level']['categories']
        stress_info = stress_standard.get(lifestyle.stress_level, {})
        
        # 饮酒频率对比
        alcohol_standard = self.standards['lifestyle_standards']['alcohol_consumption']['categories']
        alcohol_info = alcohol_standard.get(lifestyle.alcohol_consumption, {})
        
        # 吸烟对比
        smoking_status = '不吸烟' if not lifestyle.smoking else '吸烟'
        
        return {
            'exercise_frequency': {
                'user_value': lifestyle.exercise_frequency,
                'standard_info': exercise_info,
                'is_optimal': lifestyle.exercise_frequency in ['每周3-4次', '每周5次以上']
            },
            'sleep_quality': {
                'user_value': lifestyle.sleep_quality,
                'standard_info': sleep_info,
                'is_optimal': lifestyle.sleep_quality in ['好', '很好']
            },
            'stress_level': {
                'user_value': lifestyle.stress_level,
                'standard_info': stress_info,
                'is_optimal': lifestyle.stress_level in ['低', '很低']
            },
            'alcohol_consumption': {
                'user_value': lifestyle.alcohol_consumption,
                'standard_info': alcohol_info,
                'is_optimal': lifestyle.alcohol_consumption in ['无', '偶尔']
            },
            'smoking': {
                'user_value': smoking_status,
                'is_optimal': not lifestyle.smoking
            }
        }
    
    def compare_health_risks(self, profile: HealthProfile) -> Dict[str, Any]:
        """对比健康风险因素"""
        risk_factors = []
        
        # 慢性病风险
        for condition in profile.health_status.chronic_conditions:
            if condition in self.standards['health_risk_factors']['chronic_diseases']:
                risk_info = self.standards['health_risk_factors']['chronic_diseases'][condition]
                risk_factors.append({
                    'type': 'chronic_disease',
                    'name': condition,
                    'level': risk_info['risk_level'],
                    'prevention': risk_info['prevention'],
                    'has_condition': True
                })
        
        # 生活方式风险
        if profile.lifestyle.smoking:
            risk_factors.append({
                'type': 'lifestyle',
                'name': '吸烟',
                'level': 'high',
                'prevention': self.standards['health_risk_factors']['lifestyle_risks']['smoking']['prevention'],
                'has_condition': True
            })
        
        if profile.lifestyle.exercise_frequency == '无':
            risk_factors.append({
                'type': 'lifestyle',
                'name': '缺乏运动',
                'level': 'medium',
                'prevention': self.standards['health_risk_factors']['lifestyle_risks']['sedentary']['prevention'],
                'has_condition': True
            })
        
        if profile.lifestyle.sleep_quality in ['很差', '差']:
            risk_factors.append({
                'type': 'lifestyle',
                'name': '睡眠质量差',
                'level': 'medium',
                'prevention': self.standards['health_risk_factors']['lifestyle_risks']['poor_sleep']['prevention'],
                'has_condition': True
            })
        
        if profile.lifestyle.stress_level in ['很高', '高']:
            risk_factors.append({
                'type': 'lifestyle',
                'name': '压力过大',
                'level': 'medium',
                'prevention': self.standards['health_risk_factors']['lifestyle_risks']['high_stress']['prevention'],
                'has_condition': True
            })
        
        return {
            'risk_factors': risk_factors,
            'total_risk_factors': len(risk_factors),
            'chronic_diseases': len([r for r in risk_factors if r['type'] == 'chronic_disease']),
            'lifestyle_risks': len([r for r in risk_factors if r['type'] == 'lifestyle'])
        }
    
    def comprehensive_comparison(self, profile: HealthProfile) -> Dict[str, Any]:
        """综合健康指标对比分析"""
        age = profile.demographics.age
        gender = profile.demographics.gender
        
        # 基础指标对比
        bmi_comparison = self.compare_bmi(profile.demographics.calculate_bmi(), age, gender)
        
        # 生活方式对比
        lifestyle_comparison = self.compare_lifestyle(profile)
        
        # 健康风险对比
        risk_comparison = self.compare_health_risks(profile)
        
        # 统计不符合标准的指标
        abnormal_indicators = []
        
        # 检查BMI
        if not bmi_comparison['is_normal']:
            abnormal_indicators.append({
                'indicator': 'BMI',
                'user_value': bmi_comparison['user_value'],
                'normal_range': bmi_comparison['normal_range'],
                'deviation': bmi_comparison['deviation']
            })
        
        # 检查生活方式
        for key, value in lifestyle_comparison.items():
            if not value.get('is_optimal', True):
                abnormal_indicators.append({
                    'indicator': key,
                    'user_value': value['user_value'],
                    'is_optimal': value['is_optimal']
                })
        
        return {
            'user_id': profile.user_id,
            'age': age,
            'gender': gender,
            'age_group': bmi_comparison['age_group'],
            'comparison_date': profile.updated_at.isoformat(),
            'bmi_comparison': bmi_comparison,
            'lifestyle_comparison': lifestyle_comparison,
            'risk_comparison': risk_comparison,
            'abnormal_indicators': abnormal_indicators,
            'total_abnormal': len(abnormal_indicators),
            'summary': self._generate_comparison_summary(abnormal_indicators, risk_comparison)
        }
    
    def _generate_comparison_summary(self, abnormal_indicators: List[Dict], risk_comparison: Dict) -> Dict[str, Any]:
        """生成对比分析摘要"""
        summary = {
            'total_indicators_checked': 6,  # BMI + 5个生活方式指标
            'abnormal_count': len(abnormal_indicators),
            'normal_count': 6 - len(abnormal_indicators),
            'abnormal_percentage': (len(abnormal_indicators) / 6) * 100,
            'risk_factors_count': risk_comparison['total_risk_factors'],
            'chronic_diseases_count': risk_comparison['chronic_diseases'],
            'lifestyle_risks_count': risk_comparison['lifestyle_risks']
        }
        
        # 生成状态描述
        if len(abnormal_indicators) == 0:
            summary['status'] = '所有指标均在正常范围内'
        elif len(abnormal_indicators) <= 2:
            summary['status'] = '大部分指标正常，少数指标需要关注'
        elif len(abnormal_indicators) <= 4:
            summary['status'] = '多项指标偏离正常范围，需要改善'
        else:
            summary['status'] = '多项指标异常，建议全面调整生活方式'
        
        return summary
    

def main():
    """主函数 - 测试健康对比分析"""
    print("🏥 健康指标客观对比分析工具")
    print("=" * 50)
    
    # 初始化对比分析器
    comparator = HealthComparison()
    
    if not comparator.standards:
        print("❌ 无法加载健康标准数据")
        return
    
    print("✅ 健康标准数据加载成功")
    
    print("\n💡 使用方法:")
    print("1. 在 data_manager.py 中选择查看用户详情")
    print("2. 使用 HealthComparison 类进行客观对比分析")
    print("3. 调用 comprehensive_comparison() 方法获取对比结果")
    
    print("\n📋 支持的健康指标对比:")
    for indicator, info in comparator.standards['health_indicators'].items():
        print(f"  - {info['name']} ({info['unit']})")
    
    print("\n🎯 对比维度:")
    print("  - BMI指标对比")
    print("  - 血压指标对比") 
    print("  - 心率指标对比")
    print("  - 睡眠指标对比")
    print("  - 生活方式对比")
    print("  - 健康风险因素对比")
    print("  - 异常指标统计")
    
    print("\n📊 功能特点:")
    print("  - 客观数据对比，不进行评分")
    print("  - 显示用户数据与标准范围的偏差")
    print("  - 统计不符合标准的指标数量")
    print("  - 提供详细的对比分析报告")

if __name__ == '__main__':
    main()
