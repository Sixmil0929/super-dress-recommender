from flask import Flask, request, jsonify
import os
import json
# 导入搭档改好后的模块
from Body_Analysis import process_image 

app = Flask(__name__)

# 加载服装库
def get_clothes(body_type):
    with open('clothes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get(body_type, [])

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # 1. 接收图片
    if 'image' not in request.files:
        return jsonify({"code": 400, "msg": "未上传图片"})
    
    file = request.files['image']
    
    # 2. 保存临时文件
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    
    # 3. 调用搭档的 AI 代码进行分析
    # 注意：这里不需要传身高了，因为你搭档的代码是基于比例的，不需要真实身高也能算体型
    ai_result = process_image(file_path)
    
    # 4. 处理结果
    if ai_result['status'] == 'success':
        body_type = ai_result['data']['type'] # 例如 "pear"
        
        # 5. 匹配衣服
        clothes = get_clothes(body_type)
        
        return jsonify({
            "code": 200,
            "data": {
                "analysis": ai_result['data'],
                "recommendations": clothes
            }
        })
    else:
        return jsonify({"code": 500, "msg": ai_result.get('msg', '分析失败')})

if __name__ == '__main__':
    app.run(port=5001)