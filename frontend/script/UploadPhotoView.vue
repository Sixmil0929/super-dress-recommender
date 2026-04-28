<script setup>
import { ref } from 'vue'

const emit = defineEmits(['back-to-home'])

const uploadedImage = ref(null)
const formData = ref({
  shoulderWidth: '',
  bust: '',
  waist: '',
  hip: '',
  legLength: ''
})

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (!file.type.startsWith('image/')) return

  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const submitUpload = () => {
  emit('back-to-home')
}
</script>

<template>
  <div class="upload-page">
    <header class="upload-topbar">
      <button class="back-btn" @click="emit('back-to-home')">返回</button>
      <h1>上传参考照片</h1>
      <div class="placeholder"></div>
    </header>

    <section class="upload-hero">
      <p class="upload-kicker">PHOTO REFERENCE</p>
      <h2>上传照片并补充尺寸信息，生成更贴合的推荐结果</h2>
      <p class="upload-desc">
        建议上传清晰的全身参考照片，并可选填写身体数据，用于优化服装推荐与版型建议。
      </p>
    </section>

    <section class="upload-content">
      <div class="upload-card">
        <h3>参考照片</h3>
        <p class="card-desc">建议使用光线自然、背景简洁的站姿照片。</p>

        <label class="upload-box" :class="{ filled: uploadedImage }">
            <input type="file" accept="image/*" @change="handleFileUpload" hidden />

            <img v-if="uploadedImage" :src="uploadedImage" class="preview-img" />

            <div v-if="uploadedImage" class="image-overlay">
                <span>重新上传</span>
            </div>

            <div v-else class="upload-placeholder">
                <div class="upload-icon">+</div>
                <span class="upload-title">点击上传图片</span>
                <span class="upload-tip">支持 JPG / PNG</span>
            </div>
        </label>
      </div>

      <div class="form-card">
        <h3>补充尺寸（可选）</h3>
        <p class="card-desc">填写越完整，推荐结果越容易贴合你的需求。</p>

        <div class="form-grid">
          <div class="input-group">
            <label>肩宽</label>
            <input v-model="formData.shoulderWidth" type="number" placeholder="cm" />
          </div>
          <div class="input-group">
            <label>胸围</label>
            <input v-model="formData.bust" type="number" placeholder="cm" />
          </div>
          <div class="input-group">
            <label>腰围</label>
            <input v-model="formData.waist" type="number" placeholder="cm" />
          </div>
          <div class="input-group">
            <label>臀围</label>
            <input v-model="formData.hip" type="number" placeholder="cm" />
          </div>
          <div class="input-group full-width">
            <label>腿长</label>
            <input v-model="formData.legLength" type="number" placeholder="cm" />
          </div>
        </div>
      </div>
    </section>

    <div class="action-bar">
      <button class="submit-btn" @click="submitUpload">生成推荐</button>
    </div>
  </div>
</template>

<style scoped>
.upload-page {
  min-height: 100vh;
  background: #f5f5f3;
  color: #1f1f1f;
}

.upload-topbar {
  height: 72px;
  padding: 0 32px;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #e8e5df;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.upload-topbar h1 {
  margin: 0;
  font-size: 24px;
}

.back-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: 10px;
  border: 1px solid #ddd6ca;
  background: #fff;
  cursor: pointer;
}

.placeholder {
  width: 64px;
}

.upload-hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 20px;
}

.upload-kicker {
  margin: 0 0 10px;
  font-size: 12px;
  letter-spacing: 1.6px;
  color: #8b7355;
}

.upload-hero h2 {
  margin: 0 0 12px;
  font-size: 34px;
  line-height: 1.2;
}

.upload-desc {
  margin: 0;
  max-width: 760px;
  color: #666;
  line-height: 1.8;
  font-size: 14px;
}

.upload-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.upload-card,
.form-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}

.upload-card h3,
.form-card h3 {
  margin: 0 0 6px;
  font-size: 24px;
}

.card-desc {
  margin: 0 0 18px;
  color: #777;
  font-size: 14px;
}

.upload-box {
  position: relative;
  display: block;
  width: 100%;
  height: 420px;
  border-radius: 18px;
  border: 1px dashed #d6cec0;
  background: linear-gradient(135deg, #faf9f7, #f1ede7);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
}

.upload-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
  border-color: #bca88b;
}

.upload-box.filled {
  border-style: solid;
}

.upload-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #666;
  transition: all 0.25s ease;
}

.upload-box:hover .upload-placeholder {
  transform: scale(1.02);
}

.upload-icon {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34px;
  color: #8b7355;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.06);
}

.upload-title {
  font-size: 18px;
  font-weight: 600;
}

.upload-tip {
  font-size: 13px;
  color: #888;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.upload-box:hover .preview-img {
  transform: scale(1.03);
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(20, 20, 20, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.upload-box:hover .image-overlay {
  opacity: 1;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.input-group input {
  height: 46px;
  padding: 0 14px;
  border: 1px solid #ddd8cf;
  border-radius: 10px;
  outline: none;
  font-size: 14px;
  background: #fff;
}

.input-group input:focus {
  border-color: #8b7355;
  box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.12);
}

.full-width {
  grid-column: span 2;
}

.action-bar {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 40px;
}

.submit-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  border: none;
  background: #1f1f1f;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 900px) {
  .upload-content {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: span 1;
  }
}
</style>