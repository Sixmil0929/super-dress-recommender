<script setup>
import { ref } from 'vue';
import AuthView from './components/AuthView.vue';
import ProfileSetup from './components/ProfileSetup.vue';
import HomeView from './components/HomeView.vue'; // 导入主页组件
// import UploadPhotoView from './components/UploadPhotoView.vue'; // 暂时不导入上传页面，但先预留

// 1. 定义页面状态
// 可选值: 'auth' (登录/注册), 'profile' (资料完善), 'home' (主页), 'upload' (上传照片)
const currentPage = ref('auth'); // 默认从登录/注册页面开始

// 2. 状态切换函数
const handleLoginSuccess = () => {
  currentPage.value = 'profile'; 
  console.log('登录成功，切换到资料完善页面');
};

const handleProfileComplete = () => {
  currentPage.value = 'home';
  console.log('资料完善成功，切换到主页');
};

const handleUploadPhotoClicked = () => {
  currentPage.value = 'upload'; // 切换到上传照片页面
  console.log('点击上传照片，切换到上传页面');
};

// 模拟从上传页面返回的函数
const handleBackToHome = () => {
  currentPage.value = 'home';
  console.log('从上传页面返回主页');
};
//导入组件
import UploadPhotoView from './components/UploadPhotoView.vue';
</script>

<template>
  <div id="app-container">
    
    <AuthView 
      v-if="currentPage === 'auth'" 
      @login-success="handleLoginSuccess"
    />

    <ProfileSetup 
      v-else-if="currentPage === 'profile'"
      @profile-complete="handleProfileComplete"
    />

    <HomeView 
      v-else-if="currentPage === 'home'"
      @upload-photo-clicked="handleUploadPhotoClicked"
    />
    
    <UploadPhotoView
    v-else-if="currentPage === 'upload'"
    @back-to-home="handleBackToHome"
/>

  </div>
</template>

<style>
/* 保持我们之前修复布局的样式，确保 body 和 html 全屏 */
* {
  box-sizing: border-box; 
}
html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}
body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f4f7f9;
}
#app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}


</style>
