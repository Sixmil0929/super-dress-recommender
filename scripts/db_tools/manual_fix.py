import psycopg2

# ==========================================
# 🎯 修改名单：在这里写你要修改的衣服和正确标签
# 格式: "图片名": {"字段名": "正确的值", "字段名": "正确的值"}
# ==========================================
OVERRIDES = {
    # "img_0454.jpg": {"season": "spring,summer"},
    "img_0203.jpg": {"style": "sporty, outdoor"}
    # "img_0802.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0803.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0806.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0807.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0808.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0809.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0810.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0874.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0875.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0881.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0883.jpg": {"style": "casual, outdoor","scene": "street shopping","season":"winter"},
    # "img_0805.jpg": {"scene": "outdoor sports, park camping"},
    # "img_0811.jpg": {"scene": "outdoor sports, park camping"},
    # "img_0031.jpg": {"style": "casual, minimalist"},
    # "img_0060.jpg": {"style": "casual, minimalist","scene": "street shopping"}
    # "img_0436.jpg": {"item_category": "top"}
}

def sniper_fix():
    print("🔭 准备修改指定标签...")
    try:
        conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
        cursor = conn.cursor()

        for filename, fixes in OVERRIDES.items():
            # 动态生成 SQL (比如: UPDATE clothing_features SET season=%s, color=%s WHERE filename=%s)
            set_clause = ", ".join([f"{key} = %s" for key in fixes.keys()])
            values = list(fixes.values()) + [filename]
            
            sql = f"UPDATE clothing_features SET {set_clause} WHERE filename = %s"
            
            cursor.execute(sql, values)
            conn.commit()
            print(f"✅ 成功: {filename} 已更新 -> {fixes}")

        cursor.close()
        conn.close()
        print("🎉 任务完成，系统恢复纯净！")

    except Exception as e:
        print(f"💥 出错了: {e}")

if __name__ == "__main__":
    sniper_fix()