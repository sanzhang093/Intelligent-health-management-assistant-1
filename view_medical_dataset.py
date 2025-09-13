#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
查看医学推理数据集样本
"""

import json
import os

def view_dataset_samples():
    """查看数据集样本"""
    dataset_file = "data/medical_dataset/train.json"
    
    if not os.path.exists(dataset_file):
        print("❌ 数据集文件不存在，请先下载数据集")
        return
    
    print("📊 医学推理数据集样本预览")
    print("=" * 60)
    
    with open(dataset_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"总样本数: {len(data)}")
    print(f"字段: {list(data[0].keys())}")
    
    # 显示前3个样本
    for i in range(min(3, len(data))):
        sample = data[i]
        print(f"\n📋 样本 {i+1}:")
        print("-" * 40)
        print(f"问题: {sample['Question'][:200]}...")
        print(f"\n推理链: {sample['Complex_CoT'][:300]}...")
        print(f"\n回答: {sample['Response'][:200]}...")
        print("-" * 40)
    
    # 统计信息
    print(f"\n📈 数据集统计:")
    question_lengths = [len(sample['Question']) for sample in data[:1000]]
    cot_lengths = [len(sample['Complex_CoT']) for sample in data[:1000]]
    response_lengths = [len(sample['Response']) for sample in data[:1000]]
    
    print(f"问题平均长度: {sum(question_lengths)/len(question_lengths):.0f} 字符")
    print(f"推理链平均长度: {sum(cot_lengths)/len(cot_lengths):.0f} 字符")
    print(f"回答平均长度: {sum(response_lengths)/len(response_lengths):.0f} 字符")

if __name__ == '__main__':
    view_dataset_samples()
