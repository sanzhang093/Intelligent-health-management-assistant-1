#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能健康管理助手 - 用户画像管理

管理用户健康画像，包括基本信息、健康状况、生活方式等。
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class RiskTolerance(Enum):
    """风险承受能力"""
    CONSERVATIVE = "保守型"
    MODERATE = "稳健型"
    AGGRESSIVE = "积极型"

class HealthGoal(Enum):
    """健康目标"""
    WEIGHT_LOSS = "减肥"
    MUSCLE_GAIN = "增肌"
    BLOOD_PRESSURE_CONTROL = "血压控制"
    BLOOD_SUGAR_MANAGEMENT = "血糖管理"
    GENERAL_HEALTH = "健康维护"
    CHRONIC_DISEASE_MANAGEMENT = "慢性病管理"

@dataclass
class Demographics:
    """人口统计学信息"""
    age: int
    gender: str  # "male", "female", "other"
    height: float  # cm
    weight: float  # kg
    occupation: str = ""
    location: str = ""
    
    def calculate_bmi(self) -> float:
        """计算BMI"""
        if self.height <= 0:
            return 0
        return self.weight / ((self.height / 100) ** 2)
    
    def get_bmi_category(self) -> str:
        """获取BMI分类"""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "超重"
        else:
            return "肥胖"

@dataclass
class HealthStatus:
    """健康状况"""
    chronic_conditions: List[str] = None
    allergies: List[str] = None
    current_medications: List[str] = None
    recent_symptoms: List[str] = None
    medical_history: List[str] = None
    
    def __post_init__(self):
        if self.chronic_conditions is None:
            self.chronic_conditions = []
        if self.allergies is None:
            self.allergies = []
        if self.current_medications is None:
            self.current_medications = []
        if self.recent_symptoms is None:
            self.recent_symptoms = []
        if self.medical_history is None:
            self.medical_history = []

@dataclass
class Lifestyle:
    """生活方式"""
    exercise_frequency: str = "无"  # "无", "偶尔", "每周1-2次", "每周3-4次", "每周5次以上"
    exercise_type: str = ""  # "有氧", "力量训练", "瑜伽", "游泳"等
    diet_type: str = "普通饮食"  # "普通饮食", "素食", "低盐", "低糖", "地中海饮食"等
    sleep_hours: float = 7.0
    sleep_quality: str = "一般"  # "很好", "好", "一般", "差", "很差"
    stress_level: str = "中等"  # "很低", "低", "中等", "高", "很高"
    smoking: bool = False
    alcohol_consumption: str = "无"  # "无", "偶尔", "每周1-2次", "每周3-4次", "每天"
    work_schedule: str = "规律"  # "规律", "轮班", "夜班", "不规律"

@dataclass
class HealthGoals:
    """健康目标"""
    primary_goals: List[str] = None
    target_weight: Optional[float] = None
    target_bp_systolic: Optional[int] = None  # 收缩压目标
    target_bp_diastolic: Optional[int] = None  # 舒张压目标
    target_blood_sugar: Optional[float] = None  # 血糖目标
    timeline: str = "3个月"  # 目标时间框架
    
    def __post_init__(self):
        if self.primary_goals is None:
            self.primary_goals = []

@dataclass
class RiskProfile:
    """风险偏好"""
    medical_risk_tolerance: RiskTolerance = RiskTolerance.MODERATE
    lifestyle_change_tolerance: RiskTolerance = RiskTolerance.MODERATE
    exercise_intensity_preference: str = "中等"  # "低", "中等", "高"
    diet_change_willingness: str = "中等"  # "低", "中等", "高"

@dataclass
class DataSources:
    """数据来源"""
    wearable_devices: List[str] = None
    health_apps: List[str] = None
    medical_records: bool = False
    lab_results: bool = False
    
    def __post_init__(self):
        if self.wearable_devices is None:
            self.wearable_devices = []
        if self.health_apps is None:
            self.health_apps = []

class HealthProfile:
    """用户健康画像"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 初始化各个组件
        self.demographics = Demographics(age=0, gender="", height=0.0, weight=0.0)
        self.health_status = HealthStatus()
        self.lifestyle = Lifestyle()
        self.health_goals = HealthGoals()
        self.risk_profile = RiskProfile()
        self.data_sources = DataSources()
        
        # 健康数据历史
        self.health_data_history = {}
        
    def update_demographics(self, **kwargs) -> bool:
        """更新人口统计学信息"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.demographics, key):
                    setattr(self.demographics, key, value)
            self.updated_at = datetime.now()
            logger.info(f"用户 {self.user_id} 人口统计学信息已更新")
            return True
        except Exception as e:
            logger.error(f"更新人口统计学信息失败: {str(e)}")
            return False
    
    def update_health_status(self, **kwargs) -> bool:
        """更新健康状况"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.health_status, key):
                    setattr(self.health_status, key, value)
            self.updated_at = datetime.now()
            logger.info(f"用户 {self.user_id} 健康状况已更新")
            return True
        except Exception as e:
            logger.error(f"更新健康状况失败: {str(e)}")
            return False
    
    def update_lifestyle(self, **kwargs) -> bool:
        """更新生活方式"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.lifestyle, key):
                    setattr(self.lifestyle, key, value)
            self.updated_at = datetime.now()
            logger.info(f"用户 {self.user_id} 生活方式已更新")
            return True
        except Exception as e:
            logger.error(f"更新生活方式失败: {str(e)}")
            return False
    
    def update_health_goals(self, **kwargs) -> bool:
        """更新健康目标"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.health_goals, key):
                    setattr(self.health_goals, key, value)
            self.updated_at = datetime.now()
            logger.info(f"用户 {self.user_id} 健康目标已更新")
            return True
        except Exception as e:
            logger.error(f"更新健康目标失败: {str(e)}")
            return False
    
    def add_health_data(self, data_type: str, value: Any, timestamp: Optional[datetime] = None) -> bool:
        """添加健康数据"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            if data_type not in self.health_data_history:
                self.health_data_history[data_type] = []
            
            data_point = {
                'timestamp': timestamp.isoformat(),
                'value': value
            }
            
            self.health_data_history[data_type].append(data_point)
            self.updated_at = datetime.now()
            logger.info(f"用户 {self.user_id} 的 {data_type} 数据已添加")
            return True
        except Exception as e:
            logger.error(f"添加健康数据失败: {str(e)}")
            return False
    
    def get_health_data(self, data_type: str, days: int = 30) -> List[Dict]:
        """获取指定时间范围内的健康数据"""
        try:
            if data_type not in self.health_data_history:
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days)
            data = self.health_data_history[data_type]
            
            filtered_data = [
                point for point in data 
                if datetime.fromisoformat(point['timestamp']) >= cutoff_date
            ]
            
            return filtered_data
        except Exception as e:
            logger.error(f"获取健康数据失败: {str(e)}")
            return []
    
    def get_latest_health_data(self, data_type: str) -> Optional[Dict]:
        """获取最新的健康数据"""
        try:
            if data_type not in self.health_data_history:
                return None
            
            data = self.health_data_history[data_type]
            if not data:
                return None
            
            # 按时间戳排序，返回最新的
            sorted_data = sorted(data, key=lambda x: x['timestamp'], reverse=True)
            return sorted_data[0]
        except Exception as e:
            logger.error(f"获取最新健康数据失败: {str(e)}")
            return None
    
    def calculate_health_score(self) -> Dict[str, Any]:
        """计算健康评分"""
        try:
            score = 0
            max_score = 100
            details = {}
            
            # BMI评分 (20分)
            bmi = self.demographics.calculate_bmi()
            if 18.5 <= bmi <= 24:
                bmi_score = 20
            elif 24 < bmi <= 28:
                bmi_score = 15
            elif 28 < bmi <= 32:
                bmi_score = 10
            else:
                bmi_score = 5
            score += bmi_score
            details['BMI评分'] = f"{bmi_score}/20 (BMI: {bmi:.1f})"
            
            # 运动评分 (20分)
            exercise_mapping = {
                "无": 0, "偶尔": 5, "每周1-2次": 10, 
                "每周3-4次": 15, "每周5次以上": 20
            }
            exercise_score = exercise_mapping.get(self.lifestyle.exercise_frequency, 0)
            score += exercise_score
            details['运动评分'] = f"{exercise_score}/20"
            
            # 睡眠评分 (15分)
            if 7 <= self.lifestyle.sleep_hours <= 9:
                sleep_score = 15
            elif 6 <= self.lifestyle.sleep_hours < 7 or 9 < self.lifestyle.sleep_hours <= 10:
                sleep_score = 10
            else:
                sleep_score = 5
            score += sleep_score
            details['睡眠评分'] = f"{sleep_score}/15 (睡眠: {self.lifestyle.sleep_hours}小时)"
            
            # 压力评分 (15分)
            stress_mapping = {
                "很低": 15, "低": 12, "中等": 8, "高": 4, "很高": 0
            }
            stress_score = stress_mapping.get(self.lifestyle.stress_level, 8)
            score += stress_score
            details['压力评分'] = f"{stress_score}/15"
            
            # 生活方式评分 (15分)
            lifestyle_score = 15
            if self.lifestyle.smoking:
                lifestyle_score -= 10
            if self.lifestyle.alcohol_consumption in ["每天", "每周3-4次"]:
                lifestyle_score -= 5
            score += lifestyle_score
            details['生活方式评分'] = f"{lifestyle_score}/15"
            
            # 慢性病评分 (15分)
            chronic_score = 15
            if self.health_status.chronic_conditions:
                chronic_score -= len(self.health_status.chronic_conditions) * 3
            score += max(0, chronic_score)
            details['慢性病评分'] = f"{max(0, chronic_score)}/15"
            
            # 健康等级
            if score >= 85:
                health_level = "优秀"
            elif score >= 70:
                health_level = "良好"
            elif score >= 55:
                health_level = "一般"
            else:
                health_level = "需要改善"
            
            return {
                'total_score': score,
                'max_score': max_score,
                'health_level': health_level,
                'details': details,
                'recommendations': self._generate_recommendations(score, details)
            }
        except Exception as e:
            logger.error(f"计算健康评分失败: {str(e)}")
            return {'total_score': 0, 'max_score': 100, 'health_level': '无法评估', 'details': {}, 'recommendations': []}
    
    def _generate_recommendations(self, score: int, details: Dict) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        if score < 70:
            recommendations.append("整体健康状况需要改善，建议制定综合健康计划")
        
        # 基于各项评分给出具体建议
        for key, value in details.items():
            if "BMI评分" in key and "5/" in value:
                recommendations.append("BMI超标，建议控制饮食和增加运动")
            elif "运动评分" in key and "0/" in value:
                recommendations.append("缺乏运动，建议每周至少进行150分钟中等强度运动")
            elif "睡眠评分" in key and "5/" in value:
                recommendations.append("睡眠不足或过多，建议调整作息时间")
            elif "压力评分" in key and "0/" in value:
                recommendations.append("压力过大，建议学习压力管理技巧")
            elif "生活方式评分" in key and "0/" in value:
                recommendations.append("生活方式不健康，建议戒烟限酒")
            elif "慢性病评分" in key and "0/" in value:
                recommendations.append("有慢性疾病，建议定期监测和规范治疗")
        
        return recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'demographics': asdict(self.demographics),
            'health_status': asdict(self.health_status),
            'lifestyle': asdict(self.lifestyle),
            'health_goals': asdict(self.health_goals),
            'risk_profile': asdict(self.risk_profile),
            'data_sources': asdict(self.data_sources),
            'health_data_history': self.health_data_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthProfile':
        """从字典创建健康画像"""
        profile = cls(data['user_id'])
        profile.created_at = datetime.fromisoformat(data['created_at'])
        profile.updated_at = datetime.fromisoformat(data['updated_at'])
        
        # 恢复各个组件
        profile.demographics = Demographics(**data['demographics'])
        profile.health_status = HealthStatus(**data['health_status'])
        profile.lifestyle = Lifestyle(**data['lifestyle'])
        profile.health_goals = HealthGoals(**data['health_goals'])
        profile.risk_profile = RiskProfile(**data['risk_profile'])
        profile.data_sources = DataSources(**data['data_sources'])
        profile.health_data_history = data.get('health_data_history', {})
        
        return profile
    
    def save_to_file(self, filepath: str) -> bool:
        """保存到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"用户 {self.user_id} 健康画像已保存到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存健康画像失败: {str(e)}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['HealthProfile']:
        """从文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"加载健康画像失败: {str(e)}")
            return None

# 用户画像管理器
class HealthProfileManager:
    """健康画像管理器"""
    
    def __init__(self, profiles_dir: str = "data/profiles"):
        self.profiles: Dict[str, HealthProfile] = {}
        self.profiles_dir = profiles_dir
    
    def create_profile(self, user_id: str) -> HealthProfile:
        """创建新的健康画像"""
        profile = HealthProfile(user_id)
        self.profiles[user_id] = profile
        logger.info(f"为用户 {user_id} 创建了新的健康画像")
        return profile
    
    def create_default_profile(self, user_id: str) -> HealthProfile:
        """创建默认健康画像"""
        profile = self.create_profile(user_id)
        # 设置默认值
        profile.demographics = Demographics(
            age=30,
            gender="unknown",
            height=170.0,
            weight=70.0
        )
        logger.info(f"为用户 {user_id} 创建了默认健康画像")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[HealthProfile]:
        """获取健康画像"""
        return self.profiles.get(user_id)
    
    def save_profile(self, profile: HealthProfile) -> bool:
        """保存健康画像"""
        try:
            import os
            if not profile:
                return False
            
            # 确保目录存在
            os.makedirs(self.profiles_dir, exist_ok=True)
            
            # 保存到文件
            filepath = os.path.join(self.profiles_dir, f"{profile.user_id}_profile.json")
            return profile.save_to_file(filepath)
            
        except Exception as e:
            logger.error(f"保存健康画像失败: {e}")
            return False
    
    def update_profile(self, user_id: str, **kwargs) -> bool:
        """更新健康画像"""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        
        # 根据参数类型更新不同组件
        if 'demographics' in kwargs:
            return profile.update_demographics(**kwargs['demographics'])
        elif 'health_status' in kwargs:
            return profile.update_health_status(**kwargs['health_status'])
        elif 'lifestyle' in kwargs:
            return profile.update_lifestyle(**kwargs['lifestyle'])
        elif 'health_goals' in kwargs:
            return profile.update_health_goals(**kwargs['health_goals'])
        else:
            # 直接更新字段
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.now()
            return True
    
    def add_health_data(self, user_id: str, data_type: str, value: Any, timestamp: Optional[datetime] = None) -> bool:
        """添加健康数据"""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        return profile.add_health_data(data_type, value, timestamp)
    
    def get_health_data(self, user_id: str, data_type: str, days: int = 30) -> List[Dict]:
        """获取健康数据"""
        profile = self.get_profile(user_id)
        if not profile:
            return []
        return profile.get_health_data(data_type, days)
    
    def calculate_health_score(self, user_id: str) -> Optional[Dict[str, Any]]:
        """计算健康评分"""
        profile = self.get_profile(user_id)
        if not profile:
            return None
        return profile.calculate_health_score()
    
    def save_all_profiles(self, directory: str) -> bool:
        """保存所有健康画像"""
        try:
            import os
            os.makedirs(directory, exist_ok=True)
            
            for user_id, profile in self.profiles.items():
                filepath = os.path.join(directory, f"{user_id}_profile.json")
                profile.save_to_file(filepath)
            
            logger.info(f"所有健康画像已保存到 {directory}")
            return True
        except Exception as e:
            logger.error(f"保存所有健康画像失败: {str(e)}")
            return False
    
    def load_all_profiles(self, directory: str) -> bool:
        """加载所有健康画像"""
        try:
            import os
            import glob
            
            if not os.path.exists(directory):
                return False
            
            pattern = os.path.join(directory, "*_profile.json")
            files = glob.glob(pattern)
            
            for filepath in files:
                profile = HealthProfile.load_from_file(filepath)
                if profile:
                    self.profiles[profile.user_id] = profile
            
            logger.info(f"从 {directory} 加载了 {len(self.profiles)} 个健康画像")
            return True
        except Exception as e:
            logger.error(f"加载所有健康画像失败: {str(e)}")
            return False
