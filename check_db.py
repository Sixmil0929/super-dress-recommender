import psycopg2
import os
import matplotlib.pyplot as plt
from PIL import Image

# ==========================================
# 🔍 数据库 X 光透视镜 (查杀智障标签专用)
# ==========================================

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] 
plt.rcParams['axes.unicode_minus'] = False 

def xray_clothing(search_keyword, img_base_dir):
    print(f"🕵️‍♂️ 正在全库通缉包含 '{search_keyword}' 的衣服...")
    
    conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="123456", port="5432")
    cursor = conn.cursor()
    
    # 模糊搜索文件名
    cursor.execute(f"""
        SELECT filename, item_category, color, season, style, scene 
        FROM clothing_features 
        WHERE filename ILIKE '%{search_keyword}%';
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not rows:
        print("💥 没找到这张图！请检查文件名有没有拼错！")
        return
        
    print(f"🎯 抓到 {len(rows)} 个嫌疑犯，正在生成透视报告...")
    
    # 画图展示
    fig, axes = plt.subplots(1, len(rows), figsize=(5 * len(rows), 6))
    if len(rows) == 1: axes = [axes]
    
    for ax, row in zip(axes, rows):
        filename, category, color, season, style, scene = row
        img_path = os.path.join(img_base_dir, filename)
        
        try: ax.imshow(Image.open(img_path).convert('RGB'))
        except: ax.text(0.5, 0.5, '图丢了', ha='center')
        
        ax.axis('off')
        
        # 如果是裤子却被打成了 one_piece，标红警告！
        cat_color = 'red' if category == 'one_piece' else 'green'
        
        report = (
            f"📁 文件名: {filename}\n"
            f"👑 品类分类: {category}\n"
            f"🎨 识别颜色: {color}\n"
            f"❄️ 识别季节: {season}\n"
            f"✨ 识别风格: {style}\n"
            f"🌴 识别场景: {scene}"
        )
        
        ax.set_title(f"品类: {category}", color=cat_color, fontsize=14, fontweight='bold')
        ax.text(0.5, -0.15, report, transform=ax.transAxes, ha='center', fontsize=11, 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    img_dir = r"D:\dress_recommender\images\images" 
    
    # 👇 在这里填入那条“出轨”裤子的文件名（比如填 "0123.jpg" 或直接填 "0123"）
    suspect_filename = "img_0043.jpg" 
    
    xray_clothing(suspect_filename, img_dir)