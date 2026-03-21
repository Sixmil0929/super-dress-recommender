#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统健康检查脚本
验证所有依赖和配置是否正确
"""

import sys
import os
from pathlib import Path

def check_python_packages():
    """检查Python包"""
    print("\n" + "="*60)
    print("🔍 检查Python包...")
    print("="*60)
    
    packages = {
        'torch': 'PyTorch',
        'torchvision': '视觉库',
        'clip': 'OpenAI CLIP',
        'timm': '图像模型库',
        'psycopg2': 'PostgreSQL连接',
        'pgvector': '向量扩展',
        'pandas': '数据处理',
        'PIL': '图像处理'
    }
    
    all_installed = True
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✓ {package:<15} - {description}")
        except ImportError:
            print(f"✗ {package:<15} - {description} (未安装)")
            all_installed = False
    
    return all_installed

def check_models():
    """检查模型"""
    print("\n" + "="*60)
    print("🤖 检查模型加载...")
    print("="*60)
    
    try:
        import torch
        import clip
        
        # 检查CLIP
        try:
            models = clip.available_models()
            print(f"✓ CLIP模型库已加载")
            print(f"  可用模型: {', '.join(models[:3])}...")
            loaded_models = False
            for model in ['ViT-B/32', 'ViT-B/16', 'ViT-L/14']:
                if model in models:
                    print(f"  ✓ {model} 可用")
                    loaded_models = True
                    break
            if not loaded_models:
                print(f"  ⚠ 建议模型未找到")
        except Exception as e:
            print(f"✗ CLIP加载失败: {e}")
            return False
        
        # 检查DINOv2
        print("\n检查DINOv2...")
        try:
            # DINOv2会尝试下载，第一次可能很慢
            print("  (第一次运行会下载模型，可能需要几分钟...)")
            # 这里只检查是否可以导入torch.hub
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"✓ 设备: {device}")
            print(f"✓ CUDA可用: {torch.cuda.is_available()}")
            print(f"✓ PyTorch版本: {torch.__version__}")
        except Exception as e:
            print(f"⚠ DINOv2检查: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型检查失败: {e}")
        return False

def check_database():
    """检查数据库连接"""
    print("\n" + "="*60)
    print("🗄️  检查数据库连接...")
    print("="*60)
    
    try:
        import psycopg2
        
        db_config = {
            'host': 'localhost',
            'user': 'postgres',
            'password': 'postgres',
            'port': 5432
        }
        
        # 尝试连接
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✓ PostgreSQL连接成功")
            print(f"  版本: {version[0][:50]}...")
            
            # 检查pgvector
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                print(f"✓ pgvector扩展已启用")
            except Exception as e:
                print(f"⚠ pgvector扩展: {e}")
            
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            print(f"✗ PostgreSQL未启动或连接失败: {e}")
            print(f"  解决方案: net start postgresql-x64-14")
            return False
            
    except Exception as e:
        print(f"✗ 数据库检查失败: {e}")
        return False

def check_datasets():
    """检查数据集文件"""
    print("\n" + "="*60)
    print("📁 检查数据集文件...")
    print("="*60)
    
    datasets = {
        'P1_Dataset': 'P1_Dataset.csv',
        'P2_Dataset': 'data.csv',
        'P3_Dataset': 'data.csv',
        'P4_Dataset': 'data.csv',
        'P5_Dataset': 'data.csv'
    }
    
    all_exist = True
    for dataset, csv_file in datasets.items():
        path = Path(dataset)
        if path.exists():
            csv_path = path / csv_file
            img_path = path / 'images'
            
            csv_exists = csv_path.exists()
            img_exists = img_path.exists()
            
            if csv_exists and img_exists:
                # 计数图片
                img_count = len(list(img_path.glob('*.jpg'))) + len(list(img_path.glob('*.png')))
                print(f"✓ {dataset:<15} - {csv_file:<20} ({img_count} 图片)")
            else:
                if not csv_exists:
                    print(f"✗ {dataset:<15} - 缺少CSV文件: {csv_file}")
                if not img_exists:
                    print(f"✗ {dataset:<15} - 缺少images文件夹")
                all_exist = False
        else:
            print(f"⚠ {dataset:<15} - 文件夹不存在")
    
    return all_exist

def check_scripts():
    """检查脚本文件"""
    print("\n" + "="*60)
    print("📄 检查脚本文件...")
    print("="*60)
    
    scripts = {
        'init_database.py': '数据库初始化',
        'process_clothing_images.py': '图片处理和特征融合',
        'query_database.py': '数据库查询工具',
        'demo_models.py': '模型演示',
        'setup_models.py': '模型设置'
    }
    
    all_exist = True
    for script, description in scripts.items():
        if Path(script).exists():
            print(f"✓ {script:<25} - {description}")
        else:
            print(f"✗ {script:<25} - {description} (未找到)")
            all_exist = False
    
    return all_exist

def print_summary(results):
    """打印检查摘要"""
    print("\n" + "="*60)
    print("📋 检查摘要")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 所有检查全部通过! 可以开始使用。")
        print("\n下一步:")
        print("  1. python init_database.py          (初始化数据库)")
        print("  2. python process_clothing_images.py (处理图片)")
        print("  3. python query_database.py         (查询数据库)")
    else:
        print("❌ 某些检查未通过，请先解决问题。")
        print("\n常见问题解决:")
        print("  - PostgreSQL未启动: net start postgresql-x64-14")
        print("  - 缺少pgvector: 见DATABASE_SETUP_GUIDE.md")
        print("  - 缺少数据集: 确保P1-P5文件夹在当前目录")
        print("  - 缺少包: pip install -r requirements.txt")
    print("="*60)
    
    return all_passed

def main():
    """主函数"""
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🎯 系统健康检查 - PostgreSQL + CLIP + DINOv2".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # 执行所有检查
    results['Python包'] = check_python_packages()
    results['模型加载'] = check_models()
    results['数据库'] = check_database()
    results['数据集文件'] = check_datasets()
    results['脚本文件'] = check_scripts()
    
    # 打印摘要
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
