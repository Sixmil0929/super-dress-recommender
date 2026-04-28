#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PostgreSQL数据库初始化脚本
创建服装库存表并启用pgvector插件
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# ========== 数据库配置 ==========
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': '123456',  # 根据你的PostgreSQL密码修改
    'port': 5432
}

DATABASE_NAME = 'dress_recommender'

# ========== 数据库初始化SQL ==========
INIT_SQL = """
-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建服装库存表
CREATE TABLE IF NOT EXISTS clothing_inventory (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    brand TEXT,
    price DECIMAL(10, 2),
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Unisex')),
    has_model BOOLEAN,
    style_tags TEXT[],
    -- CLIP特征向量 (512维)
    clip_vector vector(512),
    -- DINO特征向量 (768维)
    dino_vector vector(768),
    -- 融合后的超级向量 (768维) - HSVS融合
    super_vector vector(768),
    -- 索引用于快速相似度搜索
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为向量列创建索引，支持快速相似度搜索
CREATE INDEX IF NOT EXISTS idx_super_vector ON clothing_inventory 
USING ivfflat (super_vector vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_filename ON clothing_inventory (filename);
CREATE INDEX IF NOT EXISTS idx_brand ON clothing_inventory (brand);
CREATE INDEX IF NOT EXISTS idx_gender ON clothing_inventory (gender);

-- 创建特征缓存表（用于临时存储原始特征）
CREATE TABLE IF NOT EXISTS feature_cache (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    clip_feature BYTEA,  -- 存储CLIP特征的二进制数据
    dino_feature BYTEA,  -- 存储DINO特征的二进制数据
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建样式标签表（用于存储CLIP识别出的标签）
CREATE TABLE IF NOT EXISTS style_tags_mapping (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    tag TEXT,
    confidence DECIMAL(5, 4),
    FOREIGN KEY (filename) REFERENCES clothing_inventory(filename)
);

CREATE INDEX IF NOT EXISTS idx_tags_filename ON style_tags_mapping (filename);
"""

def connect_to_postgres(database=None):
    """连接到PostgreSQL"""
    config = DB_CONFIG.copy()
    if database:
        config['database'] = database
    
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None

def create_database():
    """创建数据库"""
    try:
        # 连接到默认的postgres数据库
        conn = connect_to_postgres()
        if not conn:
            return False
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"""
            SELECT 1 FROM pg_database 
            WHERE datname = '{DATABASE_NAME}'
        """)
        
        if cursor.fetchone():
            print(f"✓ 数据库 '{DATABASE_NAME}' 已存在")
        else:
            print(f"创建数据库 '{DATABASE_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
            print(f"✓ 数据库 '{DATABASE_NAME}' 创建成功")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

def init_tables():
    """初始化表结构"""
    try:
        conn = connect_to_postgres(DATABASE_NAME)
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # 执行初始化SQL脚本
        cursor.execute(INIT_SQL)
        conn.commit()
        
        print("✓ 数据库表创建成功")
        print("✓ pgvector扩展已启用")
        print("✓ 向量索引已创建")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 初始化表失败: {e}")
        return False

def test_connection():
    """测试数据库连接"""
    try:
        conn = connect_to_postgres(DATABASE_NAME)
        if not conn:
            return False
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"\n✓ 数据库连接成功")
        print(f"✓ PostgreSQL版本: {version[0]}")
        
        # 检查pgvector
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
        if cursor.fetchone():
            print("✓ pgvector扩展已安装")
        else:
            print("⚠ pgvector扩展未安装，尝试创建...")
        
        # 显示表信息
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"\n✓ 已创建的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试连接失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("PostgreSQL 数据库初始化")
    print("=" * 60)
    
    print("\n[1/3] 创建数据库...")
    if not create_database():
        sys.exit(1)
    
    print("\n[2/3] 初始化表结构...")
    if not init_tables():
        sys.exit(1)
    
    print("\n[3/3] 测试连接...")
    if not test_connection():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ 数据库初始化完成!")
    print("=" * 60)
    print("\n数据库配置:")
    print(f"  主机: {DB_CONFIG['host']}")
    print(f"  端口: {DB_CONFIG['port']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print(f"  数据库: {DATABASE_NAME}")
