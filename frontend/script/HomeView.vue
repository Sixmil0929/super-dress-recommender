<script setup>
import Sidebar from './Sidebar.vue'; 
import RecommendationList from './RecommendationList.vue'; 

const emit = defineEmits(['upload-photo-clicked']);

const goToUploadPhoto = () => {
  emit('upload-photo-clicked');
};

// ⭐️ 模拟推荐商品数据
// 模拟推荐商品数据
const recommendedItems = [
  // 1. 确保 image: 的值是字符串，并且正确闭合。
  { id: 1, title: '羊羔毛外套', price: '¥599', category: '冬季推荐', image: '', span: 'large' },
  // 2. 这里的 image 字段必须用引号包裹，并检查是否有额外的换行或符号。
  { id: 2, title: '修身牛仔裤', price: '¥268', category: '下装', image: '', span: 'default' },
  
  { id: 3, title: '复古运动鞋', price: '¥450', category: '鞋履', image: '', span: 'default' },
  { id: 4, title: '高领毛衣', price: '¥320', category: '上装', image: '', span: 'default' },
  { id: 5, title: 'AI 专属适配款：阔腿裤', price: '¥399', category: '专属推荐', image: '', span: 'large' },
  
  // 6. 之前代码中省略的部分也请确保正确闭合
  { id: 6, title: '简约风衬衫', price: '¥189', category: '上装', image: '', span: 'default' },
  { id: 7, title: '时尚手提包', price: '¥650', category: '配饰', image: '', span: 'default' },
  { id: 8, title: '经典风衣', price: '¥799', category: '春季新款', image: '', span: 'large' },
];
</script>

<template>
  <div class="home-container">
    <header class="main-header">
      <h1>👕 智能服装推荐系统</h1>
      <button class="upload-btn" @click="goToUploadPhoto">
        📸 上传照片，获取专属推荐
      </button>
    </header>

    <main class="main-content">
      <Sidebar />
      <RecommendationList :items="recommendedItems" />
    </main>
  </div>
</template>
