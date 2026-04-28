import cv2
import numpy as np

def analyze_body_shape(json_data, cv_img):
    user_h, user_w = 175, 52  #用户身高和体重，实际应用中应传入或获取
    if not json_data or 'person_info' not in json_data: return
    parts = json_data['person_info'][0]['body_parts']
    
    # 创建用于调试的图像副本
    debug_img = cv_img.copy()
    debug_edges = None
    
    # 1. 提取 21 个核心点
    p = {n: np.array([parts[n]['x'], parts[n]['y']]) for n in parts.keys() if n in parts}
    
    # 在调试图像上标记关键点
    for name, point in p.items():
        x, y = int(point[0]), int(point[1])
        cv2.circle(debug_img, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(debug_img, name, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    # 计算 BMI 和物理宽度基准 (核心：每个人身材不一，以此确定扫描范围)
    bmi = user_w / ((user_h / 100) ** 2)
    # 动态肉体补偿系数 (瘦人1.05，胖人1.30)
    body_factor = 1.05 + (bmi - 18) * 0.02 if bmi > 18 else 1.05

    # 2. 图像预处理
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (7,7), 0), 30, 100)
    
    # 创建边缘检测的调试图像
    debug_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # 3. 稳健扫描函数：多行采样 + 物理剔除异常
    def get_robust_width(y_list, center_x, bone_w, mode='body', scan_color=(0, 255, 0)):
        widths = []
        # 物理限制：视觉宽度不能超过骨骼宽度的 1.5 倍（防止扫到背景植物）
        limit = int(bone_w * 1.5) 
        
        # 记录所有找到的边界点，用于绘制平均线
        found_left_points = []
        found_right_points = []
        
        for y in y_list:
            y_coord = int(np.clip(y, 0, cv_img.shape[0]-1))
            row = edges[y_coord, :]
            left, right = center_x, center_x
            
            # 在调试图像上绘制扫描线
            cv2.line(debug_img, (0, y_coord), (debug_img.shape[1], y_coord), scan_color, 1)
            if debug_edges is not None:
                cv2.line(debug_edges, (0, y_coord), (debug_edges.shape[1], y_coord), scan_color, 1)
            
            for x in range(int(center_x), max(0, int(center_x - limit)), -1):
                if row[x] > 0: 
                    left = x
                    # 标记找到的左边界点
                    cv2.circle(debug_img, (left, y_coord), 3, (0, 255, 255), -1)
                    if debug_edges is not None:
                        cv2.circle(debug_edges, (left, y_coord), 3, (0, 255, 255), -1)
                    break
                    
            for x in range(int(center_x), min(cv_img.shape[1]-1, int(center_x + limit))):
                if row[x] > 0: 
                    right = x
                    # 标记找到的右边界点
                    cv2.circle(debug_img, (right, y_coord), 3, (0, 255, 255), -1)
                    if debug_edges is not None:
                        cv2.circle(debug_edges, (right, y_coord), 3, (0, 255, 255), -1)
                    break
            
            w = right - left
            # 过滤掉扫到躯干内部（太细）或撞到墙角（太粗）的干扰
            if bone_w * 0.8 < w < bone_w * 1.8:
                widths.append(w)
                found_left_points.append((left, y_coord))
                found_right_points.append((right, y_coord))
        
        # 如果没扫到有效点，用 BMI 基准补偿 (这是关键！)
        if not widths:
            avg_width = bone_w * body_factor
        else:
            avg_width = np.mean(widths)
            # 绘制平均宽度线
            if found_left_points and found_right_points:
                avg_left = int(np.mean([p[0] for p in found_left_points]))
                avg_right = int(np.mean([p[0] for p in found_right_points]))
                avg_y = int(np.mean([p[1] for p in found_left_points]))
                
                # 绘制平均宽度线
                cv2.line(debug_img, (avg_left, avg_y), (avg_right, avg_y), (0, 255, 255), 2)
                cv2.putText(debug_img, f'{mode}: {avg_width:.1f}px', 
                           (avg_left, avg_y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # 返回平均值，平滑边缘毛刺
        return avg_width

    # --- 4. 建立扫描带 ---
    # 利用关键点确定垂直范围
    sh_center_x = (p['left_shoulder'][0] + p['right_shoulder'][0]) / 2
    px_total_h = abs(p['left_ankle'][1] - p['top_head'][1])
    
    # 在调试图像上绘制中心线
    cv2.line(debug_img, (int(sh_center_x), 0), (int(sh_center_x), debug_img.shape[0]), (255, 0, 0), 1)
    
    # 肩宽：在脖根(neck)到肩关节之间测量
    bone_sh_w = np.linalg.norm(p['left_shoulder'] - p['right_shoulder'])
    sh_y_range = np.linspace(p['neck'][1]+5, p['left_shoulder'][1]+10, 5)
    px_sh_w = get_robust_width(sh_y_range, sh_center_x, bone_sh_w, 'shoulder', (255, 0, 0))

    # 腰宽：手肘上下寻找最细平均区域
    bone_hip_w = np.linalg.norm(p['left_hip'] - p['right_hip'])
    y_waist_mid = (p['left_elbow'][1] + p['right_elbow'][1]) / 2
    waist_y_range = np.linspace(y_waist_mid - 10, y_waist_mid + 10, 5)
    px_waist_w = get_robust_width(waist_y_range, sh_center_x, bone_hip_w * 0.7, 'waist', (0, 255, 0))

    # 臀宽：从胯部向下移动 10% 身高进行区域扫描 (抓取大腿曲线)
    y_hip_start = p['left_hip'][1]
    y_hip_end = y_hip_start + (px_total_h * 0.1)
    hip_y_range = np.linspace(y_hip_start, y_hip_end, 8)
    
    # 在调试图像上标记臀部扫描区域
    cv2.rectangle(debug_img, (0, int(y_hip_start)), (debug_img.shape[1], int(y_hip_end)), (0, 165, 255), 2)
    cv2.putText(debug_img, 'Hip Scan Area', (10, int(y_hip_start)-10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
    
    px_hip_w = get_robust_width(hip_y_range, sh_center_x, bone_hip_w, 'hip', (0, 165, 255))

    # --- 5. BMI 最终平衡逻辑 ---
    # 物理防呆：臀比腰细在普通模特身上不科学，强制回弹到合理最小值
    ratio_h = px_hip_w / px_waist_w
    if ratio_h < 1.1:
        px_hip_w = px_waist_w * 1.35 


    ratio_s = px_sh_w / px_waist_w
    ratio_h = px_hip_w / px_waist_w
    
    # 在调试图像上显示最终结果
    cv2.putText(debug_img, f"BMI: {bmi:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(debug_img, f"Shoulder: {px_sh_w:.1f}px", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(debug_img, f"Waist: {px_waist_w:.1f}px", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(debug_img, f"Hip: {px_hip_w:.1f}px", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(debug_img, f"Ratios: {ratio_s:.2f}:1:{ratio_h:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # 显示调试图像
    cv2.imshow('Debug - Body Analysis', debug_img)
    if debug_edges is not None:
        cv2.imshow('Debug - Edge Detection', debug_edges)

    """为了能直接返回数据取消了显示图像，想看图像处理结果需要取消下面两行注释"""
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    head_length = px_total_h / 8
    head_body_ratio = px_total_h / head_length if head_length > 0 else 0

    # 计算肩臀比和腰臀比（注意：这里使用实际测量值）
    shoulder_hip_ratio = px_sh_w / px_hip_w if px_hip_w > 0 else 0
    waist_hip_ratio = px_waist_w / px_hip_w if px_hip_w > 0 else 0

    # 根据计算结果进行判定
    body_type_code = "unknown"
    shape_name = "未知"

    if shoulder_hip_ratio > 1.05:
        shape_name = "倒三角形 (V型 / 草莓型)"
        body_type_code = "inverted_triangle"
    elif shoulder_hip_ratio < 0.92:
        shape_name = "正三角形 (A型 / 梨型)"
        body_type_code = "pear"
    else:
        if waist_hip_ratio < 0.78:
            shape_name = "沙漏型 (X型)"
            body_type_code = "hourglass"
        else:
            shape_name = "矩形 (H型)"
            body_type_code = "rectangle"
    # 在调试图像上显示身材类型
    if 'debug_img' in locals():
        cv2.putText(debug_img, f"Type: {shape_name}", (10, 180), 
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # 返回标准数据结构
    return {
        "status": "success",
        "data": {
            "type": body_type_code,    # 后端匹配衣服用
            "type_name": shape_name,   # 前端展示文案用
            "ratios": {                # 数据可视化用
                "shoulder_hip": round(shoulder_hip_ratio, 2),
                "head_body": round(head_body_ratio, 1),
                "waist_hip": round(waist_hip_ratio, 2)
            }
        }
    }
