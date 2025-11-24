import json
import math

def analyze_body_shape(json_data):
    """
    输入：百度API返回的完整JSON数据
    输出：包含体型分析结果的字典 (不再直接打印)
    """
    # 1. 数据校验
    if not json_data or 'person_info' not in json_data:
        return {"status": "error", "msg": "API数据格式错误或未检测到人体"}

    parts = json_data['person_info'][0]['body_parts']

    def get_point(name):
        if name in parts:
            return parts[name]['x'], parts[name]['y']
        return None

    def dist(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    # --- 获取关键点 ---
    top_head = get_point('top_head')
    nose = get_point('nose')
    l_shoulder = get_point('left_shoulder')
    r_shoulder = get_point('right_shoulder')
    l_elbow = get_point('left_elbow')
    r_elbow = get_point('right_elbow')
    l_hip = get_point('left_hip')
    r_hip = get_point('right_hip')
    l_ankle = get_point('left_ankle')
    r_ankle = get_point('right_ankle')
    l_mouth = get_point('left_mouth_corner')
    r_mouth = get_point('right_mouth_corner')
    mouth = ((l_mouth[0]+r_mouth[0])/2, (l_mouth[1]+r_mouth[1])/2) if l_mouth and r_mouth else None

    # 检查核心数据完整性
    if not (top_head and l_shoulder and r_shoulder and l_hip and r_hip and l_ankle):
        return {"status": "error", "msg": "关键点缺失，无法计算。"}

    # 估算下巴
    chin_y = mouth[1] + (mouth[1] - nose[1]) if (nose and mouth) else top_head[1] + (l_shoulder[1] - top_head[1])*0.4
    head_length = chin_y - top_head[1]
    foot_bottom_y = (l_ankle[1] + r_ankle[1]) / 2
    total_height = foot_bottom_y - top_head[1]
    
    # 宽度计算
    w_shoulder = dist(l_shoulder, r_shoulder)
    w_hip = dist(l_hip, r_hip)
    
    # 智能腰宽计算
    if l_elbow and r_elbow:
        y_waist = (l_elbow[1] + r_elbow[1]) / 2
    else:
        y_shoulder_avg = (l_shoulder[1] + r_shoulder[1]) / 2
        y_hip_avg = (l_hip[1] + r_hip[1]) / 2
        y_waist = y_shoulder_avg + (y_hip_avg - y_shoulder_avg) * 0.6
    
    y_s = (l_shoulder[1] + r_shoulder[1]) / 2
    y_h = (l_hip[1] + r_hip[1]) / 2
    
    if y_h != y_s:
        t = (y_waist - y_s) / (y_h - y_s)
    else:
        t = 0.5
    t = max(0.0, min(1.0, t))
    
    w_trapezoid_at_waist = w_shoulder + (w_hip - w_shoulder) * t
    w_waist_calculated = w_trapezoid_at_waist * 0.82 
    
    if w_waist_calculated > w_hip:
        w_waist = w_hip * 0.9
    else:
        w_waist = w_waist_calculated

    # 比率计算
    head_body_ratio = total_height / head_length if head_length > 0 else 0
    shoulder_hip_ratio = w_shoulder / w_hip if w_hip > 0 else 0
    r_w = w_waist / w_hip

    body_type_code = "unknown"
    shape_name = "未知"

    # 根据计算结果进行判定
    if shoulder_hip_ratio > 1.05:
        shape_name = "倒三角形 (V型 / 草莓型)"
        body_type_code = "inverted_triangle"
    elif shoulder_hip_ratio < 0.92:
        shape_name = "正三角形 (A型 / 梨型)"
        body_type_code = "pear"
    else:
        if r_w < 0.78:
            shape_name = "沙漏型 (X型)"
            body_type_code = "hourglass"
        else:
            shape_name = "矩形 (H型)"
            body_type_code = "rectangle"

    # 返回标准数据结构
    return {
        "status": "success",
        "data": {
            "type": body_type_code,    # 后端匹配衣服用
            "type_name": shape_name,   # 前端展示文案用
            "ratios": {                # 数据可视化用
                "shoulder_hip": round(shoulder_hip_ratio, 2),
                "head_body": round(head_body_ratio, 1),
                "waist_hip": round(r_w, 2)
            }
        }
    }