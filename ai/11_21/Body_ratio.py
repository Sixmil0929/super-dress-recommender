import json
import math

def analyze_body_shape(json_data):
    """
    输入：百度API返回的完整JSON数据
    输出：更加精准的身材分析（利用手肘优化腰部计算）
    """
    if not json_data or 'person_info' not in json_data:
        print("数据格式错误：未找到 person_info")
        return

    parts = json_data['person_info'][0]['body_parts']

    def get_point(name):
        if name in parts:
            return parts[name]['x'], parts[name]['y']
        return None

    def dist(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    # --- 1. 获取关键点 ---
    top_head = get_point('top_head')
    nose = get_point('nose')
    
    l_shoulder = get_point('left_shoulder')
    r_shoulder = get_point('right_shoulder')
    
    # 新增：获取手肘数据 (用于定位腰线高度)
    l_elbow = get_point('left_elbow')
    r_elbow = get_point('right_elbow')
    
    l_hip = get_point('left_hip')
    r_hip = get_point('right_hip')
    
    l_ankle = get_point('left_ankle')
    r_ankle = get_point('right_ankle')
    
    # 辅助点：嘴巴 (用于估算下巴)
    l_mouth = get_point('left_mouth_corner')
    r_mouth = get_point('right_mouth_corner')
    mouth = ((l_mouth[0]+r_mouth[0])/2, (l_mouth[1]+r_mouth[1])/2) if l_mouth and r_mouth else None

    # 检查核心数据
    if not (top_head and l_shoulder and r_shoulder and l_hip and r_hip and l_ankle):
        print("关键点缺失，无法计算。")
        return

    # --- 2. 基础高度计算 ---
    # 估算下巴
    chin_y = mouth[1] + (mouth[1] - nose[1]) if (nose and mouth) else top_head[1] + (l_shoulder[1] - top_head[1])*0.4
    
    head_length = chin_y - top_head[1]
    foot_bottom_y = (l_ankle[1] + r_ankle[1]) / 2
    total_height = foot_bottom_y - top_head[1]
    leg_length = foot_bottom_y - (l_hip[1] + r_hip[1]) / 2

    # --- 3. 高级宽度计算 (核心修改部分) ---
    
    # A. 肩宽 & 臀宽
    w_shoulder = dist(l_shoulder, r_shoulder)
    w_hip = dist(l_hip, r_hip)
    
    # B. 智能腰宽计算 (Smart Waist Estimation)
    
    # 第一步：确定腰线的垂直位置 (y_waist)
    # 如果有手肘数据，取手肘高度；如果没有，取肩臀中间偏下的位置 (0.6处)
    if l_elbow and r_elbow:
        y_waist = (l_elbow[1] + r_elbow[1]) / 2
    else:
        y_shoulder_avg = (l_shoulder[1] + r_shoulder[1]) / 2
        y_hip_avg = (l_hip[1] + r_hip[1]) / 2
        y_waist = y_shoulder_avg + (y_hip_avg - y_shoulder_avg) * 0.6 # 经验值：腰在躯干下部
    
    # 第二步：计算“梯形插值宽度”
    # 假设身体是一个从肩到臀的梯形，计算在 y_waist 高度处的理论直线宽度
    y_s = (l_shoulder[1] + r_shoulder[1]) / 2
    y_h = (l_hip[1] + r_hip[1]) / 2
    
    # 计算腰线在肩臀垂直距离中的比例 t (0.0=肩位置, 1.0=臀位置)
    # 避免除以0
    if y_h != y_s:
        t = (y_waist - y_s) / (y_h - y_s)
    else:
        t = 0.5
        
    # 限制 t 在 0 到 1 之间 (防止手肘举过头顶导致计算错误)
    t = max(0.0, min(1.0, t))
    
    # 梯形几何宽度 = 肩宽 + (臀宽 - 肩宽) * 比例
    w_trapezoid_at_waist = w_shoulder + (w_hip - w_shoulder) * t
    
    # 第三步：应用人体曲线收缩系数
    # 骨骼不是直上直下的，腰部有内收。
    w_waist_calculated = w_trapezoid_at_waist * 0.82 
    
    # 第四步：【关键】逻辑钳位 (Safety Clamp)
    # 修复“倒三角”身材导致腰比臀宽的Bug。
    # 逻辑：对于穿衣推荐，腰宽(骨骼)不应超过臀宽。
    # 如果计算出的腰 > 臀，强制将其设为 臀宽 * 0.9
    if w_waist_calculated > w_hip:
        w_waist = w_hip * 0.9
    else:
        w_waist = w_waist_calculated

    # --- 4. 计算比率 ---
    head_body_ratio = total_height / head_length if head_length > 0 else 0
    leg_body_ratio = leg_length / total_height if total_height > 0 else 0
    shoulder_hip_ratio = w_shoulder / w_hip if w_hip > 0 else 0
    
    # 归一化宽度比
    r_s = w_shoulder / w_hip
    r_w = w_waist / w_hip
    r_h = 1.0

    # --- 5. 输出报告 ---
    print("-" * 35)
    print("【AI 身材深度分析报告】")
    print("-" * 35)
    
    # 头身比
    print(f"1. 头身比: {head_body_ratio:.1f} 头身")
    
    # 腿身比
    print(f"2. 腿身比: {(leg_body_ratio * 100):.1f}%")
    if leg_body_ratio > 0.47:
        print("   -> 腿长优势明显")
    else:
        print("   -> 比例正常")

    # 核心：三围与体型
    print(f"\n3. 核心体型数据")
    print(f"   肩臀比: {shoulder_hip_ratio:.2f}")
    print(f"   宽度比 (肩 : 腰 : 臀) -> {r_s:.2f} : {r_w:.2f} : {r_h:.2f}")

    # 智能体型判断逻辑
    shape = "未知"
    advice = ""
    
    if shoulder_hip_ratio > 1.05: # 倒三角
        shape = "倒三角形 (V型 / 草莓型)"
        
    elif shoulder_hip_ratio < 0.92: # 梨型
        shape = "正三角形 (A型 / 梨型)"
        
    else: # 矩形 或 沙漏
        # 这里的腰围判断更准了
        if r_w < 0.78: # 腰明显细
            shape = "沙漏型 (X型)"
        else:
            shape = "矩形 (H型)"

    print(f"\n   >>> 判定体型: {shape}")
    print("-" * 35)

# --- 测试专用 (模拟倒三角身材) ---
if __name__ == '__main__':
    # 构造一个肩极宽、臀极窄的数据来测试Bug是否修复
    # 肩宽约 180, 臀宽约 100
    test_data = {
        "person_info": [{
            "body_parts": {
                "top_head": {"x": 500, "y": 100},
                "nose": {"x": 500, "y": 200},
                "left_shoulder": {"x": 410, "y": 300}, # 左肩
                "right_shoulder": {"x": 590, "y": 300}, # 右肩 (肩宽大)
                "left_elbow": {"x": 400, "y": 450},     # 左手肘
                "right_elbow": {"x": 600, "y": 450},    # 右手肘
                "left_hip": {"x": 450, "y": 600},       # 左臀
                "right_hip": {"x": 550, "y": 600},      # 右臀 (臀宽小)
                "left_ankle": {"x": 450, "y": 900},
                "right_ankle": {"x": 550, "y": 900},
                # 补充空数据防报错
                "left_mouth_corner": {"x": 500,"y":220}, "right_mouth_corner": {"x":500,"y":220}
            }
        }]
    }
    print("正在测试‘倒三角’极端数据...")
    analyze_body_shape(test_data)