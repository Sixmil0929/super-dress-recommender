import base64
import urllib
import requests
import json
from . import Access_token
from . import Body_ratio   

def get_file_content_as_base64(path, urlencoded=False):
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def process_image(image_path):
    """
    Web接口调用的主入口
    参数: image_path (图片在服务器上的本地路径)
    返回: 包含分析结果的字典
    """
    # 1. 获取 Token 
    token = Access_token.get_token()
    if not token:
        return {"status": "error", "msg": "Token获取失败"}

    # 2. 读取文件 (去除了 input) 
    try:
        # 直接使用传入的参数 image_path
        img_base64 = get_file_content_as_base64(image_path, urlencoded=True)
        payload = "image=" + img_base64
    except Exception as e:
        return {"status": "error", "msg": f"文件读取失败: {str(e)}"}

    # 3. 发请求给百度 [cite: 83]
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis?access_token=" + token
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(request_url, headers=headers, data=payload)
        response_data = response.json()
        
        # 错误处理 [cite: 89]
        if "error_code" in response_data:
            return {"status": "error", "msg": response_data.get('error_msg', '百度API调用失败')}

        # 4. 调用算法模块 (接收返回值!) 
        # 现在 Body_ratio 会返回一个字典，而不是打印
        analysis_result = Body_ratio.analyze_body_shape(response_data)
        return analysis_result

    except Exception as e:
        return {"status": "error", "msg": f"分析过程发生异常: {str(e)}"}

# 本地测试代码 (仅在直接运行时执行，被导入时不执行)
if __name__ == '__main__':
    # 可以在这里手动写一个路径测试一下
    test_path = "test.jpg" 
    print("正在本地测试 process_image...")
    # result = process_image(test_path)
    # print(result)