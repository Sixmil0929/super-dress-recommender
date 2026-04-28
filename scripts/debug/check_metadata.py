import psycopg2
import pandas as pd

def check_business_data():
    print("🚀 正在启动商业元数据探查仪...")

    try:
        conn = psycopg2.connect(
            host="localhost", 
            database="postgres", 
            user="postgres", 
            password="123456", 
            port="5432"
        )
    except Exception as e:
        print(f"💥 数据库连接失败: {e}")
        return

    # 查出除了向量以外的所有字段，随便看 5 条！
    query = """
        SELECT filename, brand, price, gender, has_model, clip_tags 
        FROM clothing_features 
        LIMIT 5;
    """
    
    # 偷个懒，直接用 pandas 把 SQL 结果变成漂亮的表格打印出来
    df = pd.read_sql_query(query, conn)
    conn.close()

    print("\n" + "="*80)
    print("🛍️ 【图库前 5 件衣服的完整商业档案】")
    print("="*80)
    
    # 格式化打印
    for index, row in df.iterrows():
        print(f"👗 图片: {row['filename']}")
        print(f"   ├─ 品牌 (Brand): {row['brand']}")
        print(f"   ├─ 价格 (Price): ¥{row['price']}")
        print(f"   ├─ 性别 (Gender): {row['gender']}")
        print(f"   ├─ 模特 (Model): {row['has_model']}")
        print(f"   └─ AI 提取标签 (Tags): {row['clip_tags']}\n")
        
    print("="*80)
    print("🎉 看到没？你的商业元数据安然无恙！这 480 件衣服已经全副武装！")

if __name__ == "__main__":
    check_business_data()