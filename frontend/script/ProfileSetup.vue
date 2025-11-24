
<script setup>
import { ref, computed } from 'vue';

// --- 静态选项数据 ---
const emit = defineEmits(['profile-complete']); // 定义一个名为 'profile-complete' 的事件

// ... 其他静态数据和响应式数据不变 ...

const bodyTypes = [
  'A 型 (梨形/三角形)', 
  'V 型 (倒三角形)', 
  'H 型 (矩形)', 
  'X 型 (沙漏形)', 
  'O 型 (苹果形)'
];
const styleOptions = [
  '休闲 (Casual)', 
  '韩系/日系 (K-Pop/J-Style)', 
  '商务休闲 (Business Casual)', 
  '复古/Vintage', 
  '极简主义 (Minimalist)', 
  '街头潮流 (Streetwear)'
];

// --- 响应式用户数据 ---
const userProfile = ref({
  gender: '',
  age: null,
  height: null, // cm
  weight: null, // kg
  bodyType: [], // 使用数组存储，方便多选
  stylePreferences: [], // 使用数组存储，方便多选
});

// 模拟提交函数
const submitProfile = () => {
    // 检查必填项
    if (!userProfile.value.gender || !userProfile.value.age || !userProfile.value.height || !userProfile.value.weight) {
        alert('请填写所有必填信息！');
        return;
    }
    
    // 模拟数据提交
    console.log('提交的用户资料:', userProfile.value);
    
    // 通知父组件切换到主页
    emit('profile-complete');
};
  
  // 2. 模拟将数据发送给后端
  console.log('提交的用户资料:', userProfile.value);
  alert('资料完善成功！即将进入主页...');
  
  // 实际项目中，这里会触发父组件的事件，跳转到主页


// 样式多选框的辅助函数
const toggleStyle = (style) => {
  const index = userProfile.value.stylePreferences.indexOf(style);
  if (index === -1) {
    // 未选中，则添加
    userProfile.value.stylePreferences.push(style);
  } else {
    // 已选中，则移除
    userProfile.value.stylePreferences.splice(index, 1);
  }
};
</script>

<template>
  <div class="profile-setup-wrapper">
    <h2>👤 完善您的个人资料</h2>
    <p class="required-note">（* 为必填项，有助于更精准的推荐）</p>

    <form @submit.prevent="submitProfile" class="profile-form">
      
      <fieldset class="required-fields">
        <legend>基础信息 *</legend>

        <div class="form-group">
          <label>性别 *:</label>
          <div class="radio-group">
            <input type="radio" id="male" value="male" v-model="userProfile.gender">
            <label for="male">男</label>
            <input type="radio" id="female" value="female" v-model="userProfile.gender">
            <label for="female">女</label>
          </div>
        </div>

        <div class="form-group">
          <label for="age">年龄 *:</label>
          <input id="age" type="number" v-model.number="userProfile.age" min="15" placeholder="请填写您的年龄" required>
        </div>

        <div class="form-group">
          <label for="height">身高 (cm) *:</label>
          <input id="height" type="number" v-model.number="userProfile.height" min="100" placeholder="例如: 175" required>
        </div>

        <div class="form-group">
          <label for="weight">体重 (kg) *:</label>
          <input id="weight" type="number" v-model.number="userProfile.weight" min="30" placeholder="例如: 65" required>
        </div>
      </fieldset>
      
      <fieldset class="optional-fields">
        <legend>体型与风格 (选填)</legend>

        <div class="form-group">
          <label>您的主要体型:</label>
          <select v-model="userProfile.bodyType">
            <option disabled value="">请选择</option>
            <option v-for="type in bodyTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>喜欢的着装风格（可多选）:</label>
          <div class="style-tags">
            <span 
              v-for="style in styleOptions" 
              :key="style" 
              @click="toggleStyle(style)"
              :class="{ 'selected': userProfile.stylePreferences.includes(style) }"
              class="style-tag"
            >
              {{ style }}
            </span>
          </div>
        </div>
      </fieldset>

      <button type="submit" class="primary-btn">完成资料并进入推荐主页</button>
      <button type="button" class="skip-btn" @click="submitProfile">稍后完善</button>
      
    </form>
  </div>
</template>

<style scoped>
.profile-setup-wrapper {
  max-width: 600px;
  margin: 40px auto;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #007bff;
  text-align: center;
  margin-bottom: 5px;
}

.required-note {
  text-align: center;
  color: #888;
  margin-bottom: 30px;
  font-size: 0.9em;
}

.profile-form fieldset {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
}

.profile-form legend {
  font-weight: bold;
  color: #333;
  padding: 0 10px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: #555;
}

input[type="number"], select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
}

.radio-group input[type="radio"] {
  width: auto;
  margin-right: 5px;
}

.radio-group label {
  display: inline-block;
  margin-right: 20px;
  font-weight: normal;
}

.style-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.style-tag {
  padding: 8px 15px;
  border: 1px solid #ccc;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9em;
  color: #666;
  background-color: #f8f8f8;
}

.style-tag.selected {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.primary-btn, .skip-btn {
  width: 100%;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  margin-top: 10px;
}

.primary-btn {
  background-color: #007bff;
  color: white;
}

.skip-btn {
  background-color: #f0f0f0;
  color: #555;
}
</style>