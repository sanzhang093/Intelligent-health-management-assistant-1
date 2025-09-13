#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitHub上传前安全检查脚本
检查代码中是否包含敏感信息
"""

import os
import re
import sys
from pathlib import Path

def check_api_keys():
    """检查代码中是否包含API密钥"""
    print("🔍 检查API密钥...")
    
    # 要检查的文件类型
    file_extensions = ['.py', '.md', '.txt', '.json', '.yaml', '.yml']
    
    # 敏感信息模式
    sensitive_patterns = [
        r'sk-[a-zA-Z0-9]{20,}(?!["\']?\s*#)',  # 真实的API密钥模式（排除注释）
    ]
    
    # 示例代码模式（应该忽略）
    example_patterns = [
        r'your[_-]?api[_-]?key',
        r'your[_-]?dashscope[_-]?api[_-]?key',
        r'your[_-]?secret',
        r'your[_-]?password',
        r'your[_-]?token',
        r'your[_-]?actual[_-]?api[_-]?key',
        r'your[_-]?api[_-]?key[_-]?here',
    ]
    
    issues = []
    
    for file_path in Path('.').rglob('*'):
        if file_path.is_file() and file_path.suffix in file_extensions:
            # 跳过.git目录和虚拟环境
            if '.git' in str(file_path) or 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in sensitive_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # 过滤掉示例代码
                        real_matches = []
                        for match in matches:
                            is_example = False
                            for example_pattern in example_patterns:
                                if re.search(example_pattern, match, re.IGNORECASE):
                                    is_example = True
                                    break
                            if not is_example:
                                real_matches.append(match)
                        
                        if real_matches:
                            issues.append({
                                'file': str(file_path),
                                'pattern': pattern,
                                'matches': real_matches
                            })
            except Exception as e:
                print(f"⚠️ 无法读取文件 {file_path}: {e}")
    
    if issues:
        print("❌ 发现敏感信息:")
        for issue in issues:
            print(f"   文件: {issue['file']}")
            print(f"   匹配: {issue['matches']}")
        return False
    else:
        print("✅ 未发现敏感信息")
        return True

def check_gitignore():
    """检查.gitignore文件"""
    print("\n🔍 检查.gitignore文件...")
    
    gitignore_file = Path('.gitignore')
    if not gitignore_file.exists():
        print("❌ .gitignore文件不存在")
        return False
    
    # 检查必要的忽略项
    required_ignores = [
        '.env',
        '__pycache__',
        '*.pyc',
        '*.log',
        'venv/',
        '.vscode/',
        '.idea/'
    ]
    
    with open(gitignore_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_ignores = []
    for ignore in required_ignores:
        if ignore not in content:
            missing_ignores.append(ignore)
    
    if missing_ignores:
        print(f"❌ .gitignore缺少以下项: {missing_ignores}")
        return False
    else:
        print("✅ .gitignore配置正确")
        return True

def check_env_files():
    """检查环境配置文件"""
    print("\n🔍 检查环境配置文件...")
    
    env_file = Path('.env')
    env_example = Path('env_example.txt')
    
    if env_file.exists():
        print("⚠️ 发现.env文件，请确保已添加到.gitignore")
    
    if not env_example.exists():
        print("❌ env_example.txt文件不存在")
        return False
    
    print("✅ 环境配置文件检查通过")
    return True

def check_documentation():
    """检查文档完整性"""
    print("\n🔍 检查文档...")
    
    required_docs = [
        'README.md',
        '安全配置说明.md',
        'setup_env.py'
    ]
    
    missing_docs = []
    for doc in required_docs:
        if not Path(doc).exists():
            missing_docs.append(doc)
    
    if missing_docs:
        print(f"❌ 缺少文档: {missing_docs}")
        return False
    else:
        print("✅ 文档检查通过")
        return True

def main():
    """主函数"""
    print("🔒 GitHub上传前安全检查")
    print("=" * 50)
    
    checks = [
        check_api_keys,
        check_gitignore,
        check_env_files,
        check_documentation
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有检查通过！可以安全上传到GitHub")
        print("\n📋 上传前最后确认:")
        print("1. 确保.env文件已添加到.gitignore")
        print("2. 确保所有敏感信息已移除")
        print("3. 确保文档完整")
        print("4. 测试应用可以正常运行")
    else:
        print("❌ 检查未通过，请修复问题后再上传")
        sys.exit(1)

if __name__ == "__main__":
    main()
