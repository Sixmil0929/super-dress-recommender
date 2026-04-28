import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const data = response.data
    // 用户系统接口走 code/message 规范，推荐接口沿用原始 status/data 结构
    if (typeof data?.code === 'number' && data.code === 200) {
      return data
    }
    if (typeof data?.code === 'number') {
      const msg = data.message || '操作失败'
      alert(msg)
      return Promise.reject(new Error(msg))
    }

    return response
  },
  (error) => {
    // 处理网络错误或服务器返回状态码错误
    let msg = '请求失败，请检查后端服务是否启动'
    if (error.response && error.response.data && error.response.data.detail) {
        // FastAPI 校验失败返回的 detail
        msg = JSON.stringify(error.response.data.detail)
    }
    alert(msg)
    return Promise.reject(error)
  }
)

export default api
