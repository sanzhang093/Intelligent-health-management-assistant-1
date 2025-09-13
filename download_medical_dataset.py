#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载医学推理数据集
从Hugging Face下载FreedomIntelligence/medical-o1-reasoning-SFT数据集
"""

import os
import json
from datasets import load_dataset
from huggingface_hub import hf_hub_download

def download_medical_dataset(config_name="zh"):
    """下载医学推理数据集"""
    print("🏥 开始下载医学推理数据集...")
    print("=" * 60)
    
    # 创建数据目录
    data_dir = "data"
    medical_data_dir = os.path.join(data_dir, "medical_dataset")
    
    if not os.path.exists(medical_data_dir):
        os.makedirs(medical_data_dir)
        print(f"📁 创建数据目录: {medical_data_dir}")
    
    try:
        # 数据集名称
        dataset_name = "FreedomIntelligence/medical-o1-reasoning-SFT"
        
        print(f"📥 正在下载数据集: {dataset_name}")
        print(f"📋 配置: {config_name}")
        print("这可能需要几分钟时间，请耐心等待...")
        
        # 下载数据集
        dataset = load_dataset(dataset_name, config_name)
        
        print("✅ 数据集下载成功！")
        print(f"📊 数据集信息:")
        print(f"   - 数据集名称: {dataset_name}")
        print(f"   - 分割数量: {len(dataset)}")
        
        # 保存各个分割的数据
        for split_name, split_data in dataset.items():
            print(f"\n📋 处理分割: {split_name}")
            print(f"   - 样本数量: {len(split_data)}")
            
            # 保存为JSON文件
            output_file = os.path.join(medical_data_dir, f"{split_name}.json")
            
            # 转换为列表并保存
            data_list = []
            for i, item in enumerate(split_data):
                data_list.append(item)
                if (i + 1) % 1000 == 0:
                    print(f"   - 已处理 {i + 1}/{len(split_data)} 个样本")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ 已保存到: {output_file}")
            print(f"   📊 文件大小: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
        
        # 创建数据集信息文件
        info_file = os.path.join(medical_data_dir, "dataset_info.json")
        dataset_info = {
            "dataset_name": dataset_name,
            "description": "医学推理数据集，用于训练医学LLM的复杂推理能力",
            "splits": list(dataset.keys()),
            "total_samples": sum(len(split) for split in dataset.values()),
            "download_date": str(pd.Timestamp.now()),
            "source": "https://huggingface.co/datasets/FreedomIntelligence/medical-o1-reasoning-SFT"
        }
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 数据集信息已保存到: {info_file}")
        
        # 显示样本预览
        print(f"\n📖 数据集样本预览:")
        print("=" * 60)
        
        # 显示第一个样本
        first_split = list(dataset.keys())[0]
        first_sample = dataset[first_split][0]
        
        print(f"分割: {first_split}")
        print(f"样本字段: {list(first_sample.keys())}")
        print(f"\n问题示例:")
        print(f"问题: {first_sample.get('Question', 'N/A')[:200]}...")
        print(f"\n推理链示例:")
        print(f"推理: {first_sample.get('Complex_CoT', 'N/A')[:300]}...")
        print(f"\n回答示例:")
        print(f"回答: {first_sample.get('Response', 'N/A')[:200]}...")
        
        print(f"\n🎉 数据集下载完成！")
        print(f"📁 数据保存在: {medical_data_dir}")
        
        return medical_data_dir
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_dataset():
    """分析下载的数据集"""
    print("\n🔍 分析数据集...")
    print("=" * 60)
    
    medical_data_dir = os.path.join("data", "medical_dataset")
    
    if not os.path.exists(medical_data_dir):
        print("❌ 数据集目录不存在，请先下载数据集")
        return
    
    # 读取数据集信息
    info_file = os.path.join(medical_data_dir, "dataset_info.json")
    if os.path.exists(info_file):
        with open(info_file, 'r', encoding='utf-8') as f:
            info = json.load(f)
        
        print(f"📊 数据集统计:")
        print(f"   - 数据集名称: {info['dataset_name']}")
        print(f"   - 总样本数: {info['total_samples']}")
        print(f"   - 分割: {', '.join(info['splits'])}")
        print(f"   - 下载时间: {info['download_date']}")
    
    # 分析各个分割
    for filename in os.listdir(medical_data_dir):
        if filename.endswith('.json') and filename != 'dataset_info.json':
            split_name = filename.replace('.json', '')
            filepath = os.path.join(medical_data_dir, filename)
            
            print(f"\n📋 分割: {split_name}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"   - 样本数量: {len(data)}")
                print(f"   - 文件大小: {os.path.getsize(filepath) / 1024 / 1024:.2f} MB")
                
                if data:
                    sample = data[0]
                    print(f"   - 字段: {list(sample.keys())}")
                    
                    # 统计字段长度
                    for field in ['Question', 'Complex_CoT', 'Response']:
                        if field in sample:
                            avg_length = sum(len(str(item.get(field, ''))) for item in data[:100]) / min(100, len(data))
                            print(f"   - {field} 平均长度: {avg_length:.0f} 字符")
                
            except Exception as e:
                print(f"   ❌ 分析失败: {e}")

def main():
    """主函数"""
    print("🏥 医学推理数据集下载工具")
    print("=" * 60)
    print("数据集: FreedomIntelligence/medical-o1-reasoning-SFT")
    print("用途: 训练医学LLM的复杂推理能力")
    print("=" * 60)
    
    # 显示可用的配置选项
    available_configs = ['en', 'zh', 'en_mix', 'zh_mix']
    print(f"\n📋 可用的数据集配置:")
    for i, config in enumerate(available_configs, 1):
        print(f"   {i}. {config}")
    
    # 选择配置
    while True:
        try:
            choice = input(f"\n请选择配置 (1-{len(available_configs)}) 或直接输入配置名: ").strip()
            
            if choice.isdigit():
                config_index = int(choice) - 1
                if 0 <= config_index < len(available_configs):
                    config_name = available_configs[config_index]
                    break
                else:
                    print("❌ 无效选择，请重新输入")
            elif choice in available_configs:
                config_name = choice
                break
            else:
                print("❌ 无效配置名，请重新输入")
        except ValueError:
            print("❌ 无效输入，请重新输入")
    
    print(f"✅ 已选择配置: {config_name}")
    
    # 检查是否已存在数据集
    medical_data_dir = os.path.join("data", "medical_dataset")
    if os.path.exists(medical_data_dir) and os.listdir(medical_data_dir):
        print("📁 检测到已存在的数据集")
        choice = input("是否重新下载？(y/n): ").strip().lower()
        if choice != 'y':
            print("📊 分析现有数据集...")
            analyze_dataset()
            return
    
    # 下载数据集
    result = download_medical_dataset(config_name)
    
    if result:
        # 分析数据集
        analyze_dataset()
        
        print(f"\n✅ 数据集下载和分析完成！")
        print(f"📁 数据位置: {result}")
        print(f"💡 您可以在健康管理系统中使用这些医学推理数据来增强AI的医学知识")
    else:
        print("❌ 数据集下载失败")

if __name__ == '__main__':
    import pandas as pd
    main()
