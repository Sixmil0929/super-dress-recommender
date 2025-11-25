import base64
import urllib
import requests
import json

import Access_token
import Body_ratio   

def get_file_content_as_base64(path, urlencoded=False): #工具函数：读取图片并转换为 Base64
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def main():
    token = Access_token.get_token()
    if not token:
        print("程序终止：无法获取 Access Token。")
        return

    img_path = input("请输入图片文件的路径 (例如 ./test.jpg): ").strip()
    
    try:
        img_base64 = get_file_content_as_base64(img_path, urlencoded=True)
        payload = "image=" + img_base64
        
    except FileNotFoundError:
        print(f"错误：找不到文件 '{img_path}'，请检查路径。")
        return
    except Exception as e:
        print(f"读取文件出错: {e}")
        return

    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis?access_token=" + token
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(request_url, headers=headers, data=payload)
        response_data = response.json()
        
        # 检查百度是否返回了错误信息
        if "error_code" in response_data:
            print(f"API 调用错误: {response_data['error_msg']}")
            return

        #调用你的分析模块
        Body_ratio.analyze_body_shape(response_data)

    except Exception as e:
        print(f"请求或处理过程中发生未知错误: {e}")

if __name__ == '__main__':
    main()