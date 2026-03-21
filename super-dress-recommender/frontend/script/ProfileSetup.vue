<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['profile-complete'])

const bodyTypes = [
  'A 型（梨形/三角形）',
  'V 型（倒三角形）',
  'H 型（矩形）',
  'X 型（沙漏形）',
  'O 型（苹果形）'
]

const styleOptions = [
  '休闲',
  '韩系/日系',
  '轻商务',
  '复古',
  '极简',
  '街头'
]

const savedProfile = localStorage.getItem('dress-select-profile')

const userProfile = ref(
  savedProfile
    ? JSON.parse(savedProfile)
    : {
        gender: '',
        age: null,
        height: null,
        weight: null,
        bodyType: '',
        stylePreferences: []
      }
)

const errorMessage = ref('')
watch(
  userProfile,
  (newValue) => {
    localStorage.setItem('dress-select-profile', JSON.stringify(newValue))
  },
  { deep: true }
)

const submitProfile = () => {
  if (
    !userProfile.value.gender ||
    !userProfile.value.age ||
    !userProfile.value.height ||
    !userProfile.value.weight
  ) {
    errorMessage.value = '请先填写完整的基础信息后再进入推荐页'
    return
  }

  errorMessage.value = ''
  emit('profile-complete')
}

const toggleStyle = (style) => {
  const index = userProfile.value.stylePreferences.indexOf(style)
  if (index === -1) {
    userProfile.value.stylePreferences.push(style)
  } else {
    userProfile.value.stylePreferences.splice(index, 1)
  }
}
</script>

<template>
  <div class="profile-page">
    <div class="profile-card">
      <div class="page-head">
        <div class="head-copy">
            <p class="kicker">PROFILE SETTINGS</p>
            <h1>完善个人资料</h1>
            <p class="desc">用于生成更贴合你的服装推荐与风格建议。</p>
        </div>
      </div>

      <div class="form-section">
        <h2>基础信息</h2>

        <div class="form-group">
            <label>性别</label>
            <div class="gender-switch">
                <button
                    type="button"
                    class="gender-btn"
                    :class="{ active: userProfile.gender === 'male' }"
                    @click="userProfile.gender = 'male'"
                >
                    男
                </button>
                <button
                    type="button"
                    class="gender-btn"
                    :class="{ active: userProfile.gender === 'female' }"
                    @click="userProfile.gender = 'female'"
                >
                    女
                </button>
            </div>
        </div>

        <div class="grid-two">
          <div class="form-group">
            <label>年龄</label>
            <input type="number" v-model.number="userProfile.age" placeholder="请输入年龄" />
          </div>

          <div class="form-group">
            <label>身高（cm）</label>
            <input type="number" v-model.number="userProfile.height" placeholder="例如 175" />
          </div>
        </div>

        <div class="form-group">
          <label>体重（kg）</label>
          <input type="number" v-model.number="userProfile.weight" placeholder="例如 65" />
        </div>
      </div>

      <div class="form-section">
        <h2>体型与风格</h2>

        <div class="form-group">
          <label>主要体型</label>
          <select v-model="userProfile.bodyType">
            <option disabled value="">请选择</option>
            <option v-for="type in bodyTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>偏好风格（可多选）</label>
          <div class="style-tags">
            <button
              type="button"
              v-for="style in styleOptions"
              :key="style"
              class="style-tag"
              :class="{ selected: userProfile.stylePreferences.includes(style) }"
              @click="toggleStyle(style)"
            >
              {{ style }}
            </button>
          </div>
        </div>
      </div>

      <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>

      <div class="action-row">
        <button class="primary-btn" @click="submitProfile">保存并进入推荐页</button>
        <button class="secondary-btn" @click="submitProfile">稍后完善</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f5f3;
  padding: 20px 20px;
}

.profile-card {
  max-width: 860px;
  margin: 0 auto;
  background: #fff;
  border-radius: 24px;
  padding: 28px 32px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.06);
}

.page-head {
  margin-bottom: 18px;
}

.kicker {
  margin: 0 0 6px;
  font-size: 11px;
  letter-spacing: 1.6px;
  color: #8b7355;
}

.page-head h1 {
  margin: 0 0 6px;
  font-size: 30px;
  color: #1f1f1f;
}

.desc {
  margin: 0;
  color: #777;
  font-size: 13px;
}

.form-section {
  border: 1px solid #ebe6de;
  border-radius: 18px;
  padding: 18px 20px;
  margin-bottom: 14px;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.form-section:hover {
  transform: translateY(-2px);
  border-color: #ddd2c2;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.04);
}

.form-section h2 {
  margin: 0 0 14px;
  font-size: 20px;
  color: #1f1f1f;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

input,
select {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  border: 1px solid #ddd8cf;
  border-radius: 10px;
  outline: none;
  font-size: 14px;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.18s ease;
}

input:hover,
select:hover {
  border-color: #cdbfae;
}

input:focus,
select:focus {
  border-color: #8b7355;
  box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.12);
  transform: translateY(-1px);
}

.gender-switch {
  display: flex;
  gap: 10px;
}

.gender-btn {
  min-width: 84px;
  height: 40px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid #ddd6ca;
  background: #fff;
  color: #555;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.22s ease;
}

.gender-btn:hover {
  transform: translateY(-1px);
  border-color: #bfae98;
  background: #faf7f2;
}

.gender-btn.active {
  background: #1f1f1f;
  color: #fff;
  border-color: #1f1f1f;
  box-shadow: 0 8px 16px rgba(31, 31, 31, 0.16);
}

.style-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.style-tag {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #ddd6ca;
  background: #fff;
  color: #555;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.style-tag:hover {
  transform: translateY(-1px);
  border-color: #bfae98;
  background: #faf7f2;
}

.style-tag.selected {
  background: #1f1f1f;
  color: #fff;
  border-color: #1f1f1f;
  box-shadow: 0 6px 12px rgba(31, 31, 31, 0.10);
}

.action-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.primary-btn,
.secondary-btn {
  height: 46px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.primary-btn {
  border: none;
  background: #1f1f1f;
  color: #fff;
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 14px rgba(31, 31, 31, 0.12);
}

.secondary-btn {
  border: 1px solid #ddd6ca;
  background: #fff;
  color: #1f1f1f;
}

.secondary-btn:hover {
  transform: translateY(-1px);
  background: #faf7f2;
}

.form-error {
  margin: 6px 0 0;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f8ece8;
  border: 1px solid #e6c7bd;
  color: #8b3a2f;
  font-size: 14px;
  line-height: 1.6;
}

</style>