import psycopg2
from psycopg2.extras import RealDictCursor
import json
import uuid

# 统一数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': '123456',
    'database': 'postgres',
    'port': 5432
}

def get_db_connection():
    # RealDictCursor 会让查询结果直接变成字典，这样前端拿到的 JSON 结构就不会变
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def get_user_by_phone(phone: str):
    """根据手机号获取用户。返回值格式必须与之前一致"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE phone = %s", (phone,))
        user = cur.fetchone()
        if user:
            # 这里的 user 已经是一个字典了，RealDictCursor 的功劳
            return dict(user) 
        return None
    finally:
        cur.close()
        conn.close()

def save_user_data(user_dict: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. 准备复杂字段
    style_prefs = json.dumps(user_dict.get("style_preferences", []), ensure_ascii=False)
    
    # 2. 确保 UUID 是字符串格式
    u_id = user_dict.get("user_id")
    if not u_id:
        u_id = str(uuid.uuid4())
    else:
        u_id = str(u_id)

    # 3. 构造数据字典 (键名对应 SQL 中的 %(key)s)
    # 注意：这里不包含 created_at，让数据库自动处理
    data_to_save = {
        "phone": user_dict['phone'],
        "password": user_dict['password'],
        "user_id": u_id,
        "gender": user_dict.get('gender'),
        "age": user_dict.get('age', 0),
        "height": user_dict.get('height', 0.0),
        "weight": user_dict.get('weight', 0.0),
        "body_type": user_dict.get('body_type', ''),
        "style": style_prefs
    }

    # 4. 🌟 使用命名占位符 (更鲁棒，不会报 index out of range)
    sql = """
    INSERT INTO users (
        phone, password, user_id, gender, 
        age, height, weight, body_type, style_preferences
    )
    VALUES (
        %(phone)s, %(password)s, %(user_id)s, %(gender)s, 
        %(age)s, %(height)s, %(weight)s, %(body_type)s, %(style)s
    )
    ON CONFLICT (phone) DO UPDATE SET
        password = EXCLUDED.password,
        gender = EXCLUDED.gender,
        age = EXCLUDED.age,
        height = EXCLUDED.height,
        weight = EXCLUDED.weight,
        body_type = EXCLUDED.body_type,
        style_preferences = EXCLUDED.style_preferences;
    """
    
    try:
        # 传入字典而不是元组，psycopg2 会自动匹配键名
        cur.execute(sql, data_to_save)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL Error: {e}")
        raise e
    finally:
        cur.close()
        conn.close()