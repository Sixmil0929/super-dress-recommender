<script setup>
// 1. 接收父组件传递来的 props
// defineProps 是 Vue 3 setup 语法糖中用于声明组件 props 的宏。
const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  }
});
</script>

<template>
  <section class="list-container">
    <h2>✨ 为您推荐的服装</h2>
    <div class="recommendation-grid">
      <div 
        v-for="item in props.items" 
        :key="item.id" 
        class="product-card" 
        :class="{'card-large': item.span === 'large'}"
      >
        <div class="card-image">{{ item.image }}</div>
        <p class="card-category">{{ item.category }}</p>
        <h3 class="card-title">{{ item.title }}</h3>
        <p class="card-price">{{ item.price }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.list-container {
  flex-grow: 1; 
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

/* ⭐️ Bento 风格核心：使用 CSS Grid */
.recommendation-grid {
  display: grid;
  /* 基础网格：分为 3 列，每列最小 200px */
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); 
  grid-auto-rows: 250px; /* 设定行高，保持视觉统一 */
  gap: 15px; /* 缩小间隙 */
}

/* 默认卡片样式 */
.product-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px; /* 圆角矩形 */
  padding: 10px;
  background-color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden; /* 确保内容不溢出圆角 */
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

/* ⭐️ 大卡片样式 (Bento) */
.card-large {
  grid-column: span 2; /* 占据两列 */
}

.card-image {
  flex-grow: 1; /* 图片区域占据大部分空间 */
  background-color: #f0f4f7;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  border-radius: 8px;
  font-size: 0.9em;
}

.card-category {
  font-size: 0.75em;
  color: #007bff;
  font-weight: bold;
  margin: 0 0 4px 0;
}

.card-title {
  font-weight: bold;
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1.1em;
}

.card-price {
  color: #e60023;
  font-size: 1.2em;
  font-weight: bold;
}
</style>