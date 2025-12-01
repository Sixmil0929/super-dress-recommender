<script setup>
import { ref } from "vue";

// 保持队友定义的事件，用于返回主页
const emit = defineEmits(["back-to-home"]);

// 响应式数据
const uploadedImage = ref(null);
const isUploading = ref(false);

// 保持队友定义的手动输入数据结构
const manualMetrics = ref({
  shoulderWidth: null, // 肩宽
  legLength: null, // 腿长
  bust: null, // 胸围
  waist: null, // 腰围
  hip: null, // 臀围
});

// 文件上传逻辑 (逻辑保持不变，只是为了适配新UI微调了变量名)
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  if (!file.type.startsWith("image/")) {
    alert("请上传图片格式的文件！");
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    uploadedImage.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

// 提交逻辑
const analyzeAndSubmit = () => {
  // 简单的校验：要么传了图，要么填了数据
  const hasManualData = Object.values(manualMetrics.value).some(
    (val) => val !== null && val !== ""
  );

  if (!uploadedImage.value && !hasManualData) {
    alert("请至少上传一张照片，或填写一项身材数据");
    return;
  }

  isUploading.value = true;
  console.log("提交的数据:", {
    img: uploadedImage.value,
    metrics: manualMetrics.value,
  });

  // 模拟 AI 分析过程
  setTimeout(() => {
    isUploading.value = false;
    alert("✨ 分析完成！即将为您生成专属推荐");
    emit("back-to-home");
  }, 1500);
};
</script>

<template>
  <div class="page-container">
    <!-- 顶部导航栏 (毛玻璃效果) -->
    <nav class="navbar">
      <div class="nav-content">
        <button class="icon-btn" @click="emit('back-to-home')">← 返回</button>
        <span class="nav-title">身材分析</span>
        <div style="width: 40px"></div>
        <!-- 占位，让标题居中 -->
      </div>
    </nav>

    <!-- 内容区域 -->
    <div class="main-content">
      <div class="header-text">
        <h2>开启智能穿搭</h2>
        <p>AI 自动识别或手动录入，为您定制专属风格</p>
      </div>

      <div class="cards-wrapper">
        <!-- 左侧：图片上传卡片 -->
        <div class="glass-card upload-card">
          <div class="card-header">
            <span class="emoji">📸</span>
            <h3>上传全身照</h3>
          </div>

          <div
            class="upload-zone"
            @click="$refs.fileInput.click()"
            :class="{ 'has-image': uploadedImage }"
          >
            <input
              type="file"
              ref="fileInput"
              @change="handleFileUpload"
              accept="image/*"
              style="display: none"
            />

            <img
              v-if="uploadedImage"
              :src="uploadedImage"
              class="preview-img"
            />

            <div v-else class="placeholder">
              <div class="icon-plus">+</div>
              <p>点击选择图片</p>
              <span>支持 JPG / PNG</span>
            </div>
          </div>
        </div>

        <!-- 右侧：手动输入卡片 -->
        <div class="glass-card metrics-card">
          <div class="card-header">
            <span class="emoji">✏️</span>
            <h3>手动微调数据 (可选)</h3>
          </div>

          <div class="form-grid">
            <div class="input-group">
              <label>肩宽</label>
              <input
                type="number"
                v-model.number="manualMetrics.shoulderWidth"
                placeholder="cm"
              />
            </div>
            <div class="input-group">
              <label>胸围</label>
              <input
                type="number"
                v-model.number="manualMetrics.bust"
                placeholder="cm"
              />
            </div>
            <div class="input-group">
              <label>腰围</label>
              <input
                type="number"
                v-model.number="manualMetrics.waist"
                placeholder="cm"
              />
            </div>
            <div class="input-group">
              <label>臀围</label>
              <input
                type="number"
                v-model.number="manualMetrics.hip"
                placeholder="cm"
              />
            </div>
            <div class="input-group full-width">
              <label>腿长</label>
              <input
                type="number"
                v-model.number="manualMetrics.legLength"
                placeholder="cm"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 底部提交按钮 -->
      <div class="action-area">
        <button
          class="analyze-btn"
          @click="analyzeAndSubmit"
          :disabled="isUploading"
        >
          <span v-if="isUploading" class="loading-dots">正在分析...</span>
          <span v-else>✨ 开始 AI 分析</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 全局容器：Apple 高级灰背景 */
.page-container {
  min-height: 100vh;
  background-color: #f5f5f7;
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
  padding-top: 60px; /* 留出导航栏高度 */
}

/* 顶部导航栏：毛玻璃 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.nav-content {
  max-width: 1000px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.nav-title {
  font-weight: 600;
  font-size: 17px;
  color: #1d1d1f;
}

.icon-btn {
  background: none;
  border: none;
  color: #0071e3;
  font-size: 16px;
  cursor: pointer;
  font-weight: 500;
}

/* 主内容区 */
.main-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header-text {
  text-align: center;
  margin-bottom: 40px;
}

.header-text h2 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1d1d1f;
}

.header-text p {
  color: #86868b;
  font-size: 18px;
}

/* 卡片布局 */
.cards-wrapper {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
}

@media (max-width: 768px) {
  .cards-wrapper {
    flex-direction: column;
  }
}

/* 通用玻璃卡片 */
.glass-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
  flex: 1;
  transition: transform 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.emoji {
  font-size: 24px;
  margin-right: 10px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

/* 上传区域样式 */
.upload-zone {
  border: 2px dashed #d2d2d7;
  border-radius: 16px;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  background: #fafafa;
  transition: all 0.3s;
  overflow: hidden;
  position: relative;
}

.upload-zone:hover {
  background: #f0f8ff;
  border-color: #0071e3;
}

.placeholder {
  text-align: center;
  color: #86868b;
}

.icon-plus {
  font-size: 40px;
  color: #0071e3;
  margin-bottom: 10px;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 手动输入表单样式 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.full-width {
  grid-column: span 2;
}

.input-group label {
  display: block;
  font-size: 13px;
  color: #86868b;
  margin-bottom: 8px;
  font-weight: 500;
}

.input-group input {
  width: 100%;
  padding: 12px;
  background: #f5f5f7;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  color: #1d1d1f;
  box-sizing: border-box;
  transition: background 0.2s;
}

.input-group input:focus {
  background: #e8e8ed;
  outline: none;
}

/* 底部大按钮 */
.action-area {
  text-align: center;
}

.analyze-btn {
  background: #0071e3;
  color: white;
  font-size: 18px;
  font-weight: 600;
  padding: 16px 60px;
  border: none;
  border-radius: 99px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 113, 227, 0.4);
  transition: all 0.2s;
}

.analyze-btn:hover {
  background: #0077ed;
  transform: scale(1.02);
}

.analyze-btn:active {
  transform: scale(0.98);
}

.analyze-btn:disabled {
  background: #a1a1a6;
  box-shadow: none;
  cursor: not-allowed;
}
</style>
