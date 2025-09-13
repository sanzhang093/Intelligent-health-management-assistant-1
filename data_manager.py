#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据管理工具

用于管理用户健康画像数据，包括数据统计、查询、导出等功能
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.user_profile import HealthProfile, HealthProfileManager

class DataManager:
    """数据管理器"""
    
    def __init__(self, profiles_dir: str = "data/profiles"):
        self.profiles_dir = profiles_dir
        self.profile_manager = HealthProfileManager()
        self.profiles = []
        self.load_profiles()
    
    def load_profiles(self):
        """加载所有用户画像"""
        self.profiles = []
        
        if not os.path.exists(self.profiles_dir):
            print(f"目录 {self.profiles_dir} 不存在")
            return
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('_profile.json'):
                filepath = os.path.join(self.profiles_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    profile = HealthProfile.from_dict(data)
                    self.profiles.append(profile)
                except Exception as e:
                    print(f"加载 {filename} 失败: {e}")
        
        print(f"✅ 成功加载 {len(self.profiles)} 个用户画像")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        if not self.profiles:
            return {}
        
        stats = {
            'total_users': len(self.profiles),
            'age_range': {
                'min': min(p.demographics.age for p in self.profiles),
                'max': max(p.demographics.age for p in self.profiles),
                'avg': sum(p.demographics.age for p in self.profiles) / len(self.profiles)
            },
            'gender_distribution': Counter(p.demographics.gender for p in self.profiles),
            'bmi_distribution': Counter(p.demographics.get_bmi_category() for p in self.profiles),
            'exercise_distribution': Counter(p.lifestyle.exercise_frequency for p in self.profiles),
            'chronic_conditions': Counter(
                condition for p in self.profiles 
                for condition in p.health_status.chronic_conditions
            ),
            'health_goals': Counter(
                goal for p in self.profiles 
                for goal in p.health_goals.primary_goals
            ),
            'health_scores': [p.calculate_health_score()['total_score'] for p in self.profiles]
        }
        
        return stats
    
    def print_statistics(self):
        """打印统计信息"""
        stats = self.get_statistics()
        if not stats:
            print("❌ 无数据可统计")
            return
        
        print("=" * 60)
        print("📊 用户画像数据统计")
        print("=" * 60)
        
        print(f"总用户数: {stats['total_users']}")
        
        age_range = stats['age_range']
        print(f"\n👥 年龄分布:")
        print(f"  - 年龄范围: {age_range['min']}-{age_range['max']}岁")
        print(f"  - 平均年龄: {age_range['avg']:.1f}岁")
        
        print(f"\n⚥ 性别分布:")
        for gender, count in stats['gender_distribution'].items():
            print(f"  - {gender}: {count}人 ({count/stats['total_users']*100:.1f}%)")
        
        print(f"\n📏 BMI分布:")
        for category, count in stats['bmi_distribution'].items():
            print(f"  - {category}: {count}人 ({count/stats['total_users']*100:.1f}%)")
        
        print(f"\n🏃 运动习惯分布:")
        for freq, count in stats['exercise_distribution'].items():
            print(f"  - {freq}: {count}人 ({count/stats['total_users']*100:.1f}%)")
        
        if stats['chronic_conditions']:
            print(f"\n🏥 慢性病分布 (前10):")
            for condition, count in stats['chronic_conditions'].most_common(10):
                print(f"  - {condition}: {count}人")
        
        print(f"\n🎯 健康目标分布 (前10):")
        for goal, count in stats['health_goals'].most_common(10):
            print(f"  - {goal}: {count}人")
        
        if stats['health_scores']:
            avg_score = sum(stats['health_scores']) / len(stats['health_scores'])
            print(f"\n💯 健康评分:")
            print(f"  - 平均评分: {avg_score:.1f}/100")
            print(f"  - 评分范围: {min(stats['health_scores'])}-{max(stats['health_scores'])}")
    
    def search_users(self, criteria: Dict[str, Any]) -> List[HealthProfile]:
        """根据条件搜索用户"""
        results = []
        
        for profile in self.profiles:
            match = True
            
            # 年龄范围
            if 'age_min' in criteria and profile.demographics.age < criteria['age_min']:
                match = False
            if 'age_max' in criteria and profile.demographics.age > criteria['age_max']:
                match = False
            
            # 性别
            if 'gender' in criteria and profile.demographics.gender != criteria['gender']:
                match = False
            
            # BMI范围
            bmi = profile.demographics.calculate_bmi()
            if 'bmi_min' in criteria and bmi < criteria['bmi_min']:
                match = False
            if 'bmi_max' in criteria and bmi > criteria['bmi_max']:
                match = False
            
            # 慢性病
            if 'chronic_condition' in criteria:
                if criteria['chronic_condition'] not in profile.health_status.chronic_conditions:
                    match = False
            
            # 运动习惯
            if 'exercise_frequency' in criteria and profile.lifestyle.exercise_frequency != criteria['exercise_frequency']:
                match = False
            
            # 健康目标
            if 'health_goal' in criteria and criteria['health_goal'] not in profile.health_goals.primary_goals:
                match = False
            
            if match:
                results.append(profile)
        
        return results
    
    def export_to_csv(self, output_file: str = "user_profiles.csv"):
        """导出数据到CSV文件"""
        import csv
        
        if not self.profiles:
            print("❌ 无数据可导出")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'user_id', 'age', 'gender', 'height', 'weight', 'bmi', 'bmi_category',
                'occupation', 'location', 'chronic_conditions', 'allergies', 'medications',
                'exercise_frequency', 'exercise_type', 'diet_type', 'sleep_hours',
                'sleep_quality', 'stress_level', 'smoking', 'alcohol_consumption',
                'health_goals', 'health_score', 'health_level'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for profile in self.profiles:
                score_data = profile.calculate_health_score()
                row = {
                    'user_id': profile.user_id,
                    'age': profile.demographics.age,
                    'gender': profile.demographics.gender,
                    'height': profile.demographics.height,
                    'weight': profile.demographics.weight,
                    'bmi': round(profile.demographics.calculate_bmi(), 1),
                    'bmi_category': profile.demographics.get_bmi_category(),
                    'occupation': profile.demographics.occupation,
                    'location': profile.demographics.location,
                    'chronic_conditions': ';'.join(profile.health_status.chronic_conditions),
                    'allergies': ';'.join(profile.health_status.allergies),
                    'medications': ';'.join(profile.health_status.current_medications),
                    'exercise_frequency': profile.lifestyle.exercise_frequency,
                    'exercise_type': profile.lifestyle.exercise_type,
                    'diet_type': profile.lifestyle.diet_type,
                    'sleep_hours': profile.lifestyle.sleep_hours,
                    'sleep_quality': profile.lifestyle.sleep_quality,
                    'stress_level': profile.lifestyle.stress_level,
                    'smoking': profile.lifestyle.smoking,
                    'alcohol_consumption': profile.lifestyle.alcohol_consumption,
                    'health_goals': ';'.join(profile.health_goals.primary_goals),
                    'health_score': score_data['total_score'],
                    'health_level': score_data['health_level']
                }
                writer.writerow(row)
        
        print(f"✅ 数据已导出到 {output_file}")
    
    def get_user_by_id(self, user_id: str) -> Optional[HealthProfile]:
        """根据用户ID获取用户画像"""
        for profile in self.profiles:
            if profile.user_id == user_id:
                return profile
        return None
    
    def show_user_details(self, user_id: str):
        """显示用户详细信息"""
        profile = self.get_user_by_id(user_id)
        if not profile:
            print(f"❌ 未找到用户 {user_id}")
            return
        
        print(f"\n" + "=" * 60)
        print(f"👤 用户详细信息: {profile.user_id}")
        print("=" * 60)
        
        print(f"📋 基本信息:")
        print(f"  - 年龄: {profile.demographics.age}岁")
        print(f"  - 性别: {profile.demographics.gender}")
        print(f"  - 身高: {profile.demographics.height}cm")
        print(f"  - 体重: {profile.demographics.weight}kg")
        print(f"  - BMI: {profile.demographics.calculate_bmi():.1f} ({profile.demographics.get_bmi_category()})")
        print(f"  - 职业: {profile.demographics.occupation}")
        print(f"  - 地区: {profile.demographics.location}")
        
        print(f"\n🏥 健康状况:")
        print(f"  - 慢性病: {', '.join(profile.health_status.chronic_conditions) if profile.health_status.chronic_conditions else '无'}")
        print(f"  - 过敏: {', '.join(profile.health_status.allergies) if profile.health_status.allergies else '无'}")
        print(f"  - 当前用药: {', '.join(profile.health_status.current_medications) if profile.health_status.current_medications else '无'}")
        print(f"  - 近期症状: {', '.join(profile.health_status.recent_symptoms) if profile.health_status.recent_symptoms else '无'}")
        
        print(f"\n🏃 生活方式:")
        print(f"  - 运动频率: {profile.lifestyle.exercise_frequency}")
        print(f"  - 运动类型: {profile.lifestyle.exercise_type if profile.lifestyle.exercise_type else '无'}")
        print(f"  - 饮食类型: {profile.lifestyle.diet_type}")
        print(f"  - 睡眠时间: {profile.lifestyle.sleep_hours}小时")
        print(f"  - 睡眠质量: {profile.lifestyle.sleep_quality}")
        print(f"  - 压力水平: {profile.lifestyle.stress_level}")
        print(f"  - 吸烟: {'是' if profile.lifestyle.smoking else '否'}")
        print(f"  - 饮酒: {profile.lifestyle.alcohol_consumption}")
        
        print(f"\n🎯 健康目标:")
        print(f"  - 主要目标: {', '.join(profile.health_goals.primary_goals)}")
        print(f"  - 时间框架: {profile.health_goals.timeline}")
        
        # 健康评分
        score_data = profile.calculate_health_score()
        print(f"\n💯 健康评分: {score_data['total_score']}/100 ({score_data['health_level']})")
        print(f"详细评分:")
        for key, value in score_data['details'].items():
            print(f"  - {key}: {value}")
        
        if score_data['recommendations']:
            print(f"\n💡 健康建议:")
            for rec in score_data['recommendations']:
                print(f"  - {rec}")

def main():
    """主函数"""
    print("🏥 智能健康管理助手 - 数据管理工具")
    print("=" * 50)
    
    dm = DataManager()
    
    if not dm.profiles:
        print("❌ 未找到用户数据，请先运行数据生成脚本")
        return
    
    while True:
        print(f"\n📋 请选择操作:")
        print("1. 查看数据统计")
        print("2. 搜索用户")
        print("3. 查看用户详情")
        print("4. 导出数据到CSV")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == '1':
            dm.print_statistics()
        
        elif choice == '2':
            print("\n🔍 搜索用户")
            print("请输入搜索条件 (留空表示不限制):")
            
            criteria = {}
            age_min = input("最小年龄: ").strip()
            if age_min:
                criteria['age_min'] = int(age_min)
            
            age_max = input("最大年龄: ").strip()
            if age_max:
                criteria['age_max'] = int(age_max)
            
            gender = input("性别 (male/female): ").strip()
            if gender:
                criteria['gender'] = gender
            
            chronic_condition = input("慢性病: ").strip()
            if chronic_condition:
                criteria['chronic_condition'] = chronic_condition
            
            health_goal = input("健康目标: ").strip()
            if health_goal:
                criteria['health_goal'] = health_goal
            
            results = dm.search_users(criteria)
            print(f"\n✅ 找到 {len(results)} 个匹配的用户:")
            for profile in results[:10]:  # 只显示前10个
                score_data = profile.calculate_health_score()
                print(f"  - {profile.user_id}: {profile.demographics.age}岁, {profile.demographics.gender}, "
                      f"BMI {profile.demographics.calculate_bmi():.1f}, 健康评分 {score_data['total_score']}")
            
            if len(results) > 10:
                print(f"  ... 还有 {len(results) - 10} 个用户")
        
        elif choice == '3':
            user_id = input("\n请输入用户ID (如 user_001): ").strip()
            dm.show_user_details(user_id)
        
        elif choice == '4':
            output_file = input("\n请输入输出文件名 (默认: user_profiles.csv): ").strip()
            if not output_file:
                output_file = "user_profiles.csv"
            dm.export_to_csv(output_file)
        
        elif choice == '5':
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == '__main__':
    main()
