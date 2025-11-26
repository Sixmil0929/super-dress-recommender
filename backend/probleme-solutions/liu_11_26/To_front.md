### 第一部分：代码逻辑解析

#### 1. 保存/更新用户信息 (`POST /profile`)

```python
@router.post("/profile", summary="保存/更新用户信息")
async def update_profile(profile: UserProfile):
```
*   **功能**：这是“存档口”。
*   **输入 (`profile: UserProfile`)**：它要求前端必须发送一个符合 `UserProfile` 模型格式的 JSON 数据（包含 user_id, gender, age 等）。如果格式不对（比如年龄发了字符串），FastAPI 会直接报错拦截，保护数据库。
*   **逻辑**：
    1.  `profile.dict()`：把验证好的数据转成 Python 字典。
    2.  `save_user_data(user_data)`：调用工具函数把数据写进 `users.json` 文件。
*   **返回**：如果成功，返回状态 `success` 和保存时间。

#### 2. 获取单个用户信息 (`GET /{user_id}`)

```python
@router.get("/{user_id}", summary="获取单个用户信息")
async def get_user(user_id: str):
```
*   **功能**：这是“查询口”。
*   **输入 (`{user_id}`)**：它从 URL 路径里直接获取 ID。例如请求 `/api/user/user_001`，这里的 `user_id` 就是 `user_001`。
*   **逻辑**：
    1.  `load_all_users()`：读取所有数据。
    2.  `for user in users`：遍历查找匹配的 ID。
*   **返回**：找不到返回 404 错误，找到了返回用户数据。

---

### 第二部分：前端 (Vue) 如何调用

假设你的后端运行在 `http://127.0.0.1:8000`，并且在 `main.py` 中注册路由时设置了前缀 `prefix="/api/user"`。

前端通常使用 `axios` 来发起请求。

#### 场景一：用户填写完资料，点击“保存”按钮

前端需要发送 **POST** 请求。

**前端代码示例：**

```javascript
import axios from 'axios';

// 1. 准备要发送的数据 (对应 UserProfile 模型)
const userData = {
  user_id: "phone_13800138000",  // 必填
  gender: "female",              // 必填
  age: 22,                       // 必填 (数字)
  height: 165.5,                 // 必填 (数字)
  weight: 48.0,                  // 必填 (数字)
  style_preferences: ["韩系", "简约"] // 选填 (数组)
};

// 2. 发送请求
// 完整 URL: http://127.0.0.1:8000/api/user/profile
axios.post('http://127.0.0.1:8000/api/user/profile', userData)
  .then(response => {
    // 请求成功
    console.log("保存成功:", response.data);
    alert("资料保存成功！");
  })
  .catch(error => {
    // 请求失败
    console.error("保存失败:", error.response.data);
    alert("保存出错，请检查数据格式");
  });
```

---

#### 场景二：用户进入“个人中心”，回显数据

前端需要发送 **GET** 请求，**ID 放在 URL 后面**。

**前端代码示例：**

```javascript
import axios from 'axios';

const currentUserId = "phone_13800138000"; // 当前登录用户的ID

// 1. 发送请求
// 注意：user_id 是直接拼接到 URL 后面的
// 完整 URL: http://127.0.0.1:8000/api/user/phone_13800138000
axios.get(`http://127.0.0.1:8000/api/user/${currentUserId}`)
  .then(response => {
    // 请求成功，拿到数据
    const userInfo = response.data.data;
    console.log("获取到的用户信息:", userInfo);
    
    // 这里可以将数据赋值给 Vue 的变量，例如:
    // this.form.age = userInfo.age;
  })
  .catch(error => {
    if (error.response && error.response.status === 404) {
      console.log("用户不存在，可能是新用户");
    } else {
      console.error("网络错误:", error);
    }
  });
```

### 总结给前端的一句话

*   **保存数据**：请用 `POST` 请求 `/api/user/profile`，Body 里放 JSON 对象。
*   **获取数据**：请用 `GET` 请求 `/api/user/{你的用户ID}`。
