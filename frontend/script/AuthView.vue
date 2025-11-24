<script setup>
import { ref } from 'vue';

// 1. 定义组件可以发出的事件
const emit = defineEmits(['login-success']); // 定义一个名为 'login-success' 的事件

const isLoginMode = ref(true); 

// 2. 模拟登录逻辑
const handleLogin = () => {
  // 实际项目中这里会调用后端 API 进行验证
  // 假设验证通过：
  
  // 3. 触发事件，通知父组件切换状态
  emit('login-success'); 
};

// 3. 模拟注册逻辑
const handleRegister = () => {
  // 实际项目中这里会调用后端 API 进行注册
  // 假设注册成功，流程是：注册成功 => 自动登录 => 跳转到资料完善页
  
  // 4. 触发事件，通知父组件切换状态
  emit('login-success'); 
};

// ... 模板代码不变 ...
</script>

<template>
  <div class="auth-wrapper">
    <h2>{{ isLoginMode ? '欢迎回来，请登录' : '新用户注册' }}</h2>

    <div class="form-container">
      
      <form v-if="isLoginMode" @submit.prevent="handleLogin">
        <input type="text" placeholder="账号/用户名" required />
        <input type="password" placeholder="密码" required />
        <button type="submit" class="primary-btn">登录</button>
      </form>

      <form v-else @submit.prevent="handleRegister">
        <input type="text" placeholder="设置账号/用户名" required />
        <input type="password" placeholder="设置密码" required />
        <input type="password" placeholder="确认密码" required />
        <button type="submit" class="primary-btn">注册</button>
      </form>
      
      <p class="switch-link">
        {{ isLoginMode ? '还没有账号？' : '已有账号？' }}
        <a href="#" @click.prevent="isLoginMode = !isLoginMode">
          {{ isLoginMode ? '去注册' : '去登录' }}
        </a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrapper {
  max-width: 400px;
  margin: 80px auto;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  color: #007bff;
  margin-bottom: 30px;
}

.form-container {
  display: flex;
  flex-direction: column;
}

input {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box; /* 确保 padding 不撑开 input 宽度 */
}

.primary-btn {
  padding: 12px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  transition: background-color 0.3s;
}

.primary-btn:hover {
  background-color: #0056b3;
}

.switch-link {
  margin-top: 20px;
  font-size: 0.9em;
  color: #666;
}

.switch-link a {
  color: #007bff;
  text-decoration: none;
  font-weight: bold;
}
</style>