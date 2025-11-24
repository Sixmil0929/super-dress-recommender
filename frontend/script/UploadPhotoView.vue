<script setup>
import { ref } from 'vue';

// 定义事件，用于通知父组件返回主页
const emit = defineEmits(['back-to-home']);

// 响应式数据：用于存储用户上传的图片文件或URL
const uploadedImage = ref(null); 
const isUploading = ref(false);

// 响应式数据：用于存储手动输入的身材指标
const manualMetrics = ref({
    shoulderWidth: null, // 肩宽
    legLength: null,    // 腿长
    bust: null,         // 胸围
    waist: null,        // 腰围
    hip: null,          // 臀围
});

// 模拟文件上传逻辑
const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 检查文件类型，确保是图片
    if (!file.type.startsWith('image/')) {
        alert('请上传图片格式的文件！');
        return;
    }
    
    // 使用 FileReader 显示图片预览
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedImage.value = e.target.result; // 图片预览 URL
    };
    reader.readAsDataURL(file);
    
    console.log('文件已选择:', file.name);
};

// 模拟调用 AI 分析并提交数据的函数
const analyzeAndSubmit = () => {
    isUploading.value = true;
    console.log('手动输入数据:', manualMetrics.value);
    
    // 实际项目中：
    // 1. 如果有 uploadedImage，调用百度 AI API
    // 2. 如果有 manualMetrics，直接调用后端计算函数
    
    // 模拟 2 秒的分析时间
    setTimeout(() => {
        isUploading.value = false;
        alert('AI 分析完成，即将为您生成专属推荐！');
        // 实际：提交成功后，返回主页
        emit('back-to-home');
    }, 2000);
};
</script>

<template>
  <div class="upload-view-container">
    <header class="upload-header">
        <h2>📸 AI 身材分析与推荐</h2>
        <button class="back-btn" @click="emit('back-to-home')">返回主页</button>
    </header>

    <div class="analysis-area">
      
      <div class="tip-card">
        <h3>💡 照片拍摄指南</h3>
        <p>请确保照片清晰，露出全身，并尽量避免穿着过于宽松的衣物，以提高分析准确性。</p>
      </div>

      <div class="content-wrapper">
        
        <div class="upload-section">
          <h3>上传全身照片</h3>
          <div 
            class="image-drop-zone" 
            @click="$refs.fileInput.click()"
            :class="{'has-image': uploadedImage}"
          >
            <input 
              type="file" 
              ref="fileInput" 
              @change="handleFileUpload" 
              accept="image/*" 
              style="display: none;" 
            />
            
            <img v-if="uploadedImage" :src="uploadedImage" alt="用户全身照" class="uploaded-image-preview" />
            
            <div v-else class="upload-placeholder-text">
                点击或拖放图片至此上传
                <p class="small-text">（JPG/PNG 格式，最大 5MB）</p>
            </div>
          </div>
          
        </div>

        <div class="manual-input-section">
          <h3>或 手动输入身材数据</h3>
          <form class="metrics-form">
            <div class="form-group">
              <label>肩宽 (cm):</label>
              <input type="number" v-model.number="manualMetrics.shoulderWidth" placeholder="如 42">
            </div>
            <div class="form-group">
              <label>腿长 (cm):</label>
              <input type="number" v-model.number="manualMetrics.legLength" placeholder="如 105">
            </div>
            <div class="form-group">
              <label>胸围 (cm):</label>
              <input type="number" v-model.number="manualMetrics.bust" placeholder="如 90">
            </div>
            <div class="form-group">
              <label>腰围 (cm):</label>
              <input type="number" v-model.number="manualMetrics.waist" placeholder="如 70">
            </div>
            <div class="form-group">
              <label>臀围 (cm):</label>
              <input type="number" v-model.number="manualMetrics.hip" placeholder="如 95">
            </div>
          </form>
          
        </div>
      </div>
      
      <button 
        class="submit-analysis-btn" 
        @click="analyzeAndSubmit"
        :disabled="isUploading"
      >
        {{ isUploading ? '正在分析中...' : '启动 AI 分析并推荐' }}
      </button>

    </div>
  </div>
</template>

<style scoped>
.upload-view-container {
    padding: 0;
    margin: 0;
    min-height: 100vh;
    background-color: #f4f7f9;
}
.upload-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 30px;
    background-color: #6c757d; 
    color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.upload-header h2 {
    margin: 0;
}
.back-btn {
    padding: 8px 15px;
    background-color: #f0ad4e;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.analysis-area {
    max-width: 900px;
    margin: 40px auto;
    padding: 30px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.tip-card {
    background-color: #eaf5ff;
    border: 1px solid #b3d9ff;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 25px;
}
.tip-card h3 {
    color: #007bff;
    margin-top: 0;
}

.content-wrapper {
    display: flex;
    gap: 30px;
    margin-bottom: 30px;
}

.upload-section, .manual-input-section {
    flex: 1;
}

/* --- 图片上传区样式 --- */
.image-drop-zone {
    height: 350px;
    border: 3px dashed #ccc;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    background-color: #fafafa;
    overflow: hidden;
}

.image-drop-zone.has-image {
    border: none;
}

.uploaded-image-preview {
    max-height: 100%;
    max-width: 100%;
    object-fit: contain;
}

.upload-placeholder-text {
    color: #888;
    text-align: center;
}

.small-text {
    font-size: 0.8em;
    color: #aaa;
    margin-top: 5px;
}

/* --- 手动输入区样式 --- */
.metrics-form .form-group {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}
.metrics-form input {
    width: 60%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

/* --- 提交按钮样式 --- */
.submit-analysis-btn {
    width: 100%;
    padding: 15px;
    background-color: #dc3545; /* 醒目的红色 */
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.2em;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s;
}

.submit-analysis-btn:hover:not(:disabled) {
    background-color: #c82333;
}

.submit-analysis-btn:disabled {
    background-color: #ff9999;
    cursor: not-allowed;
}
</style>
