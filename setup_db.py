import psycopg2

# 刚才在 Docker 里设置的数据库账号密码
DB_HOST = "localhost"
DB_NAME = "postgres"  # 默认数据库名
DB_USER = "postgres"  # 默认用户名
DB_PASS = "123456"
DB_PORT = "5432"

try:
    # 1. 敲门连接数据库
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)
    conn.autocommit = True  # 自动提交修改，不用手动 commit
    cursor = conn.cursor()
    
    # 2. 激活向量超级能力！
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("✅ 向量插件 pgvector 激活成功！")
    
    # 3. 建立咱们的专属服装表
    create_table_query = """
    CREATE TABLE IF NOT EXISTS clothing_features (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        brand VARCHAR(100),
        price DECIMAL(10, 2),
        gender VARCHAR(50),
        has_model INTEGER,
        clip_tags TEXT,              -- 存放 CLIP 打的文字标签
        super_vector vector(768)     -- 存放 CLIP + DINOv3 融合的超级向量
    );
    """
    cursor.execute(create_table_query)
    print("✅ 服装数据库表 clothing_features 创建成功！")
    
    cursor.close()
    conn.close()
    print("🎉 数据库基础设施搭建完毕，可以开始导数据啦！")

except Exception as e:
    print("❌ 哎呀，出错了：", e)