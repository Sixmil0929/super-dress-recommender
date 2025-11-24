import requests

API_KEY = "leg5vspgBFgpSKwJ8VARaHRn"
SECRET_KEY = "sZz46uR51QwySaLm6KIEbqwbfoQPuAer"

def get_token():
    """
    使用 AK，SK 向百度云请求 Access Token
    :return: access_token (str) 或是 None (如果出错)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials", 
        "client_id": API_KEY, 
        "client_secret": SECRET_KEY
    }
    
    try:
        response = requests.post(url, params=params)
        # 检查 HTTP 状态码
        if response.status_code == 200:
            return str(response.json().get("access_token"))
        else:
            print(f"鉴权失败，服务器返回: {response.text}")
            return None
    except Exception as e:
        print(f"获取 Token 时发生网络错误: {e}")
        return None