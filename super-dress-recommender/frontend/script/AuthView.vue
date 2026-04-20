<script setup>
import { ref, reactive } from 'vue'
import api from '../src/api'

const emit = defineEmits(['login-success'])
const isLoginMode = ref(true)
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const showConfirmPassword = ref(false)

// 登录表单数据
const loginForm = ref({
  phone: '',
  password: ''
})

// 注册表单数据
const registerForm = reactive({
  phone: '',
  password: '',
  confirmPassword: ''
})

// 页面内提示信息
const registerMessage = ref('')
const registerMessageType = ref('') // 'error' | 'success'

const loginMessage = ref('')
const loginMessageType = ref('') // 可选

// 清空提示
const clearRegisterMessage = () => {
  registerMessage.value = ''
  registerMessageType.value = ''
}

const clearLoginMessage = () => {
  loginMessage.value = ''
  loginMessageType.value = ''
}

// 切换登录/注册时清空提示
const switchMode = () => {
  isLoginMode.value = !isLoginMode.value
  clearRegisterMessage()
  clearLoginMessage()
}

// 登录逻辑
const handleLogin = async () => {
  clearLoginMessage()

  if (!loginForm.value.phone || !loginForm.value.password) {
    loginMessage.value = '请填写手机号和密码'
    loginMessageType.value = 'error'
    return
  }

  try {
    console.log('正在登录...', loginForm.value)
    const res = await api.post('/api/user/login', {
      phone: loginForm.value.phone,
      password: loginForm.value.password
    })
    
    // 登录成功，存储手机号
    localStorage.setItem('user_phone', loginForm.value.phone)
    emit('login-success', res.data)
  } catch (err) {
    console.error('登录失败', err)
  }
}

// 注册逻辑
const handleRegister = async () => {
  clearRegisterMessage()

  if (!registerForm.phone || !registerForm.password || !registerForm.confirmPassword) {
    registerMessage.value = '请完善注册信息'
    registerMessageType.value = 'error'
    return
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    registerMessage.value = '两次输入的密码不一致'
    registerMessageType.value = 'error'
    return
  }

  try {
    console.log('正在注册...', registerForm)
    await api.post('/api/user/register', {
      phone: registerForm.phone,
      password: registerForm.password
    })

    registerMessage.value = '注册成功，正在跳转登录'
    registerMessageType.value = 'success'

    // 清空注册表单
    registerForm.phone = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''

    // 延迟切回登录页
    setTimeout(() => {
      isLoginMode.value = true
      clearRegisterMessage()
    }, 1200)
  } catch (err) {
    console.error('注册失败', err)
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-left">
      <div class="auth-left-layout">
        <div class="auth-visual-card">
          <img
            src="/editorial/login-visual.jpg"
            alt="登录页主视觉"
            class="auth-visual-image"
          />
        </div>

        <div class="auth-copy-card">
          <p class="brand-mark">DRESS SELECT</p>
          <h1>让穿搭选择更贴近你的日常风格</h1>
          <p class="auth-desc">
            通过基础资料与偏好设置，整理更适合你的服装推荐与搭配方向。
          </p>
        </div>
      </div>
    </div>

    <div class="auth-card">
      <div class="auth-card-inner">
        <h2>{{ isLoginMode ? '欢迎回来' : '创建账号' }}</h2>
        <p class="auth-subtitle">
          {{ isLoginMode ? '登录后继续查看你的推荐结果' : '注册后即可开始完善资料' }}
        </p>

        <form v-if="isLoginMode" class="auth-form" @submit.prevent="handleLogin">
          <input
            v-model="loginForm.phone"
            type="text"
            placeholder="手机号"
            class="auth-input"
            required
          />
          <div class="password-field">
            <input
              v-model="loginForm.password"
              :type="showLoginPassword ? 'text' : 'password'"
              placeholder="密码"
              class="auth-input password-input"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showLoginPassword = !showLoginPassword"
              :aria-label="showLoginPassword ? '隐藏密码' : '显示密码'"
            >
              <svg
                v-if="showLoginPassword"
                viewBox="0 0 24 24"
                class="password-toggle-icon"
                aria-hidden="true"
              >
                <path
                  d="M3 5.5 19 21.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.7"
                />
                <path
                  d="M10.58 10.7A2 2 0 0 0 13.3 13.42"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.7"
                />
                <path
                  d="M9.88 5.12A10.94 10.94 0 0 1 12 4.9c5.05 0 8.72 3.66 9.9 6.3a1.82 1.82 0 0 1 0 1.6 12.45 12.45 0 0 1-3.36 4.28"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.7"
                />
                <path
                  d="M6.23 7.2A12.51 12.51 0 0 0 2.1 11.2a1.82 1.82 0 0 0 0 1.6c1.18 2.64 4.85 6.3 9.9 6.3a11.4 11.4 0 0 0 3.2-.45"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.7"
                />
              </svg>
              <svg
                v-else
                viewBox="0 0 24 24"
                class="password-toggle-icon"
                aria-hidden="true"
              >
                <path
                  d="M2.1 12.8a1.82 1.82 0 0 1 0-1.6c1.18-2.64 4.85-6.3 9.9-6.3s8.72 3.66 9.9 6.3a1.82 1.82 0 0 1 0 1.6c-1.18 2.64-4.85 6.3-9.9 6.3S3.28 15.44 2.1 12.8Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.7"
                />
                <circle
                  cx="12"
                  cy="12"
                  r="3.1"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                />
              </svg>
            </button>
          </div>

          <p
            v-if="loginMessage"
            class="form-message"
            :class="loginMessageType"
          >
            {{ loginMessage }}
          </p>

          <button type="submit" class="auth-button">登录</button>
        </form>

        <form v-else class="auth-form" @submit.prevent="handleRegister">
          <input
            v-model="registerForm.phone"
            type="text"
            placeholder="手机号"
            class="auth-input"
            required
            @input="clearRegisterMessage"
          />
          <div class="password-field">
            <input
              v-model="registerForm.password"
              :type="showRegisterPassword ? 'text' : 'password'"
              placeholder="设置密码"
              class="auth-input password-input"
              required
              @input="clearRegisterMessage"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showRegisterPassword = !showRegisterPassword"
              :aria-label="showRegisterPassword ? '隐藏密码' : '显示密码'"
            >
              <svg
                v-if="showRegisterPassword"
                viewBox="0 0 24 24"
                class="password-toggle-icon"
                aria-hidden="true"
              >
                <path d="M3 5.5 19 21.5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <path d="M10.58 10.7A2 2 0 0 0 13.3 13.42" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <path d="M9.88 5.12A10.94 10.94 0 0 1 12 4.9c5.05 0 8.72 3.66 9.9 6.3a1.82 1.82 0 0 1 0 1.6 12.45 12.45 0 0 1-3.36 4.28" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <path d="M6.23 7.2A12.51 12.51 0 0 0 2.1 11.2a1.82 1.82 0 0 0 0 1.6c1.18 2.64 4.85 6.3 9.9 6.3a11.4 11.4 0 0 0 3.2-.45" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
              </svg>
              <svg
                v-else
                viewBox="0 0 24 24"
                class="password-toggle-icon"
                aria-hidden="true"
              >
                <path d="M2.1 12.8a1.82 1.82 0 0 1 0-1.6c1.18-2.64 4.85-6.3 9.9-6.3s8.72 3.66 9.9 6.3a1.82 1.82 0 0 1 0 1.6c-1.18 2.64-4.85 6.3-9.9 6.3S3.28 15.44 2.1 12.8Z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <circle cx="12" cy="12" r="3.1" fill="none" stroke="currentColor" stroke-width="1.7" />
              </svg>
            </button>
          </div>
          <div class="password-field">
            <input
              v-model="registerForm.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="确认密码"
              class="auth-input password-input"
              required
              @input="clearRegisterMessage"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showConfirmPassword = !showConfirmPassword"
              :aria-label="showConfirmPassword ? '隐藏密码' : '显示密码'"
            >
              <svg
                v-if="showConfirmPassword"
                viewBox="0 0 24 24"
                class="password-toggle-icon"
                aria-hidden="true"
              >
                <path d="M3 5.5 19 21.5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <path d="M10.58 10.7A2 2 0 0 0 13.3 13.42" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <path d="M9.88 5.12A10.94 10.94 0 0 1 12 4.9c5.05 0 8.72 3.66 9.9 6.3a1.82 1.82 0 0 1 0 1.6 12.45 12.45 0 0 1-3.36 4.28" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <path d="M6.23 7.2A12.51 12.51 0 0 0 2.1 11.2a1.82 1.82 0 0 0 0 1.6c1.18 2.64 4.85 6.3 9.9 6.3a11.4 11.4 0 0 0 3.2-.45" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
              </svg>
              <svg
                v-else
                viewBox="0 0 24 24"
                class="password-toggle-icon"
                aria-hidden="true"
              >
                <path d="M2.1 12.8a1.82 1.82 0 0 1 0-1.6c1.18-2.64 4.85-6.3 9.9-6.3s8.72 3.66 9.9 6.3a1.82 1.82 0 0 1 0 1.6c-1.18 2.64-4.85 6.3-9.9 6.3S3.28 15.44 2.1 12.8Z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7" />
                <circle cx="12" cy="12" r="3.1" fill="none" stroke="currentColor" stroke-width="1.7" />
              </svg>
            </button>
          </div>

          <p
            v-if="registerMessage"
            class="form-message"
            :class="registerMessageType"
          >
            {{ registerMessage }}
          </p>

          <button type="submit" class="auth-button">立即注册</button>
        </form>

        <p class="switch-link">
          {{ isLoginMode ? '还没有账号？' : '已有账号？' }}
          <a href="#" class="auth-link" @click.prevent="switchMode">
            {{ isLoginMode ? '去注册' : '去登录' }}
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  padding: 32px 40px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  align-items: center;
  gap: 56px;
  background:
    radial-gradient(circle at top left, rgba(230, 222, 208, 0.48), transparent 220px),
    radial-gradient(circle at bottom right, rgba(233, 226, 216, 0.42), transparent 220px),
    #f5f5f3;
  overflow: hidden;
}

.auth-left {
  min-width: 0;
}

.auth-left-layout {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 38px;
  align-items: center;
  max-width: 1080px;
}

.auth-visual-card {
  width: 360px;
  height: 520px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.10);
  background: #efe7da;
}

.auth-visual-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.auth-copy-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 520px;
}

.brand-mark {
  margin: 0 0 18px;
  font-size: 13px;
  letter-spacing: 2px;
  color: #a88964;
}

.auth-copy-card h1 {
  margin: 0 0 18px;
  max-width: 680px;
  font-size: 74px;
  line-height: 1.05;
  font-weight: 800;
  color: #1f1f1f;
  letter-spacing: -1px;
}

.auth-desc {
  margin: 0;
  max-width: 900px;
  font-size: 18px;
  line-height: 1.7;
  color: #6a6a6a;
  white-space: nowrap;
}

.auth-card {
  justify-self: end;
  width: 100%;
  max-width: 420px;
}

.auth-card-inner {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 28px;
  padding: 36px 34px 30px;
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(10px);
}

.auth-card-inner h2 {
  margin: 0 0 8px;
  font-size: 36px;
  color: #1f1f1f;
}

.auth-subtitle {
  margin: 0 0 24px;
  font-size: 15px;
  color: #8a8a8a;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.auth-input {
  width: 100%;
  height: 56px;
  padding: 0 18px;
  box-sizing: border-box;
  border-radius: 14px;
  border: 1px solid #ded8cf;
  background: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.auth-input::-ms-reveal,
.auth-input::-ms-clear {
  display: none;
}

.password-field {
  position: relative;
  width: 100%;
}

.password-input {
  padding-right: 72px;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  color: #9e917f;
  cursor: pointer;
  padding: 6px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.18s ease, color 0.18s ease;
}

.password-toggle:hover {
  color: #1f1f1f;
  background: rgba(31, 31, 31, 0.05);
}

.password-toggle-icon {
  width: 18px;
  height: 18px;
}

.auth-input:focus {
  border-color: #bca78a;
  box-shadow: 0 0 0 4px rgba(188, 167, 138, 0.12);
}

.auth-button {
  height: 54px;
  margin-top: 4px;
  border: none;
  border-radius: 14px;
  background: #1f1f1f;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.auth-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 20px rgba(31, 31, 31, 0.14);
}

.form-message {
  margin: -2px 0 2px;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.form-message.error {
  color: #c74646;
  background: #fff1f1;
  border: 1px solid #f1caca;
}

.form-message.success {
  color: #237a4b;
  background: #eefaf2;
  border: 1px solid #cdebd7;
}

.switch-link {
  margin: 18px 0 0;
  font-size: 15px;
  color: #8a8a8a;
}

.auth-link {
  margin-left: 6px;
  color: #1f1f1f;
  font-weight: 700;
  cursor: pointer;
}

@media (max-width: 1400px) {
  .auth-left-layout {
    grid-template-columns: 300px minmax(0, 1fr);
    max-width: 860px;
  }

  .auth-visual-card {
    width: 300px;
    height: 450px;
  }

  .auth-copy-card {
    min-height: 450px;
  }

  .auth-copy-card h1 {
    font-size: 62px;
    max-width: 560px;
  }

  .auth-desc {
    font-size: 19px;
    white-space: normal;
  }
}

@media (max-width: 1200px) {
  .auth-page {
    grid-template-columns: 1fr;
    gap: 36px;
    padding: 28px 24px;
  }

  .auth-left-layout {
    max-width: none;
  }

  .auth-card {
    justify-self: start;
    max-width: 460px;
  }
}

@media (max-width: 860px) {
  .auth-left-layout {
    grid-template-columns: 1fr;
    gap: 22px;
  }

  .auth-visual-card {
    width: 100%;
    max-width: 360px;
    height: 460px;
  }

  .auth-copy-card {
    min-height: auto;
  }

  .auth-copy-card h1 {
    font-size: 44px;
    max-width: none;
  }

  .auth-desc {
    font-size: 16px;
    white-space: normal;
  }

  .auth-card {
    max-width: none;
    justify-self: stretch;
  }
}
</style>
