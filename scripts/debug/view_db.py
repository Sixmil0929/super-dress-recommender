import psycopg2

try:
    # 连上咱们的数据库
    conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
    cursor = conn.cursor()

    # 查询前 5 条数据（我们不打印超级向量，因为它有 768 个数字，会把屏幕刷满）
    cursor.execute("SELECT id, filename, brand, clip_tags FROM clothing_features LIMIT 5;")
    rows = cursor.fetchall()

    print("\n🎉 数据库里的衣服长这样（前 5 件）：")
    print("-" * 70)
    for row in rows:
        print(f"👚 ID: {row[0]} | 图片: {row[1]} | 品牌: {row[2]}")
        print(f"🤖 AI 打的标签: {row[3]}")
        print("-" * 70)

    # 查一下总数，看看是不是 100 张全进去了
    cursor.execute("SELECT count(*) FROM clothing_features;")
    total = cursor.fetchone()[0]
    print(f"\n✅ 当前数据库总共稳稳入库了 {total} 件衣服的完整数据！")

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ 查询失败了:", e)
    