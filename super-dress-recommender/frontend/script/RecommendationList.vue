<script setup>
const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  }
})
</script>

<template>
  <section class="list-container">
    <div class="recommendation-grid">
      <article
        v-for="item in props.items"
        :key="item.id"
        class="product-card"
        :class="{ 'card-large': item.span === 'large' }"
      >
        <div class="card-image">
          <span class="image-tag">LOOK</span>
          <img v-if="item.image" :src="item.image" class="item-main-img" alt="product" />
        </div>

        <div class="card-body">
          <p class="card-category">{{ item.category }}</p>
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-desc">{{ item.desc }}</p>
          <div class="card-footer">
            <p class="card-price">{{ item.price }}</p>
            <button class="detail-btn">查看详情</button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
/* --- 以下保留你所有的原始样式 --- */
.list-container {
  width: 100%;
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(240px, 1fr));
  gap: 20px;
}

.product-card {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid #ece7df;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.08);
}

.card-large {
  grid-column: span 2;
}

.card-image {
  height: 250px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.30), rgba(0, 0, 0, 0.03)),
    linear-gradient(135deg, #ece8e1, #d8d1c7);
  position: relative;
  overflow: hidden;
}

/* 🚀 核心新增：图片样式 */
.item-main-img {
  width: 100%;
  height: 100%;
  /* 🚀 核心修改：从 cover 改为 contain */
  /* contain 会保证图片在不被裁剪、不缩放变形的前提下，完整地展示在框内 */
  object-fit: contain; 
  
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 0;
  
  /* 💡 可选：如果图片没撑满留白了，给个底色让它更好看 */
  background-color: #f9f9f7; 
}

.card-image::before {
  content: "";
  position: absolute;
  inset: 18px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.38);
  z-index: 1; /* 浮在图上 */
}

.card-image::after {
  content: "";
  position: absolute;
  left: 22px;
  right: 22px;
  bottom: 22px;
  height: 38%;
  border-radius: 18px;
  background: linear-gradient(
    to top,
    rgba(255, 255, 255, 0.18),
    rgba(255, 255, 255, 0)
  );
  z-index: 1; /* 浮在图上 */
}

.card-large .card-image {
  height: 280px;
}

.image-tag {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.86);
  font-size: 12px;
  color: #666;
  letter-spacing: 1px;
  z-index: 2; /* 最顶层 */
}

.card-body {
  padding: 16px 18px 18px;
}

.card-category {
  margin: 0 0 8px;
  color: #8b7355;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.6px;
}

.card-title {
  margin: 0 0 8px;
  font-size: 20px;
  color: #1f1f1f;
}

.card-desc {
  margin: 0 0 14px;
  color: #6b6b6b;
  font-size: 14px;
  line-height: 1.65;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-price {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #7a4134;
}

.detail-btn {
  height: 36px;
  padding: 0 14px;
  border: 1px solid #ddd6ca;
  border-radius: 999px;
  background: #fcfbf9;
  cursor: pointer;
  color: #4a433b;
  font-size: 13px;
  transition: all 0.2s ease;
}

.detail-btn:hover {
  background: #f2ede7;
  border-color: #cfc5b7;
}

@media (max-width: 1100px) {
  .recommendation-grid {
    grid-template-columns: repeat(2, minmax(220px, 1fr));
  }
  .card-large {
    grid-column: span 1;
  }
}

@media (max-width: 700px) {
  .recommendation-grid {
    grid-template-columns: 1fr;
  }
}
</style>
