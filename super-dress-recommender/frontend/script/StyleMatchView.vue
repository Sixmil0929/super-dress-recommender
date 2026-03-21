<script setup>
import { computed, ref } from 'vue'

const genderOptions = [
  { zh: '男生', en: 'male', value: 'male' },
  { zh: '女生', en: 'female', value: 'female' }
]

const emit = defineEmits(['back-to-home'])

const styleOptions = [
  { zh: '运动风', en: 'sporty', value: 'sporty' },
  { zh: '正式风', en: 'formal', value: 'formal' },
  { zh: '休闲/日常风', en: 'casual', value: 'casual' },
  { zh: '复古风', en: 'vintage', value: 'vintage' },
  { zh: '街头风', en: 'streetwear', value: 'streetwear' },
  { zh: '约会风', en: 'romantic dating', value: 'romantic dating' },
  { zh: '轻商务', en: 'business casual', value: 'business casual' },
  { zh: '极简风', en: 'minimalist', value: 'minimalist' },
  { zh: '户外风', en: 'outdoor', value: 'outdoor' },
  { zh: '甜美风', en: 'sweet', value: 'sweet' },
  { zh: '性感风', en: 'sexy', value: 'sexy' }
]

const colorOptions = [
  { zh: '黑色', en: 'black', value: 'black' },
  { zh: '白色', en: 'white', value: 'white' },
  { zh: '灰色', en: 'gray', value: 'gray' },
  { zh: '红色', en: 'red', value: 'red' },
  { zh: '蓝色', en: 'blue', value: 'blue' },
  { zh: '绿色', en: 'green', value: 'green' },
  { zh: '黄色', en: 'yellow', value: 'yellow' },
  { zh: '粉色', en: 'pink', value: 'pink' },
  { zh: '棕色', en: 'brown', value: 'brown' },
  { zh: '紫色', en: 'purple', value: 'purple' },
  { zh: '卡其色', en: 'khaki', value: 'khaki' },
  { zh: '多色', en: 'multi-color', value: 'multi-color' }
]

const seasonOptions = [
  { zh: '春季', en: 'spring', value: 'spring' },
  { zh: '夏季', en: 'summer', value: 'summer' },
  { zh: '秋季', en: 'autumn', value: 'autumn' },
  { zh: '冬季', en: 'winter', value: 'winter' }
]

const sceneOptions = [
  { zh: '办公通勤', en: 'office workplace', value: 'office workplace' },
  { zh: '宴会婚礼', en: 'formal banquet or wedding', value: 'formal banquet or wedding' },
  { zh: '居家休闲', en: 'home relaxing', value: 'home relaxing' },
  { zh: '室内健身', en: 'indoor gym', value: 'indoor gym' },
  { zh: '海边度假', en: 'beach vacation', value: 'beach vacation' },
  { zh: '露营散步', en: 'park camping', value: 'park camping' },
  { zh: '日常出行', en: 'daily commute', value: 'street shopping' },
  { zh: '户外运动', en: 'outdoor sports', value: 'outdoor sports' }
]

// 🚀 核心改动 1：style 和 color 必须初始化为数组 []，支持多选！
const selected = ref({
  gender: '',
  style: [], // 数组！
  color: [], // 数组！
  season: '',
  scene: ''
})

const resultLooks = ref([])
const showResults = ref(false)
const resultVersion = ref(0)
const hasGenerated = ref(false)

// 🚀 核心改动 2：多选切换逻辑 (被 @click="toggleMulti('style', item.value)" 调用)
// ⚠️ 注意：你需要去你的 <template> 里，把 style 和 color 的点击事件改成调用这个函数！
// 例如：@click="toggleMulti('style', item.value)"
const toggleMulti = (category, value) => {
  const index = selected.value[category].indexOf(value);
  if (index > -1) {
    selected.value[category].splice(index, 1); // 存在就踢出
  } else {
    selected.value[category].push(value); // 不在就加入
  }
}

const generateLooks = async () => {
  hasGenerated.value = true
  showResults.value = false
  resultVersion.value += 1

  try {
    const payload = {
      // 🚀 核心改动 3：解开硬编码的封印！读取用户的真实选择
      gender: selected.value.gender || "", 
      season: selected.value.season || "",
      scene: selected.value.scene || "",
      style: selected.value.style,  // 本来就是数组了，直接传
      preferred_colors: selected.value.color // 本来就是数组了，直接传
    };

    console.log("📤 发送给后端的数据:", payload);

    const response = await fetch('http://127.0.0.1:8000/api/recommend_by_survey', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (result.status === 'success') {
      console.log("🔥 拿到后端真实数据了！", result.data.outfits);
      
      const formattedLooks = result.data.outfits.map((outfit, index) => {
        if (outfit.type === 'single' || outfit.type === 'one_piece') {
          return {
            id: index + 1,
            type: 'dress', 
            items: [{ 
              category: outfit.item.category || '推荐单品', 
              brand: outfit.item.brand || '未知品牌', 
              price: outfit.item.price || '¥299',
              image: `http://127.0.0.1:8000/images/${outfit.item.filename}` 
            }]
          }
        } 
        else if (outfit.type === 'combo') {
          return {
            id: index + 1,
            type: 'separate',
            items: [
              { 
                category: '上衣', 
                brand: outfit.top.brand || '未知品牌', 
                price: outfit.top.price || '¥199', 
                image: `http://127.0.0.1:8000/images/${outfit.top.filename}` 
              },
              { 
                category: '下装', 
                brand: outfit.bottom.brand || '未知品牌', 
                price: outfit.bottom.price || '¥259', 
                image: `http://127.0.0.1:8000/images/${outfit.bottom.filename}` 
              }
            ]
          }
        }
      });

      resultLooks.value = formattedLooks;
    } else {
      console.error("后端报错了：", result.message);
      alert("后端报错啦，去 Python 终端看一眼！");
    }

  } catch (error) {
    console.error("请求失败！Python 服务器没开？或者跨域没配？", error);
    alert("连不上后端，请检查你的 api_server.py 是否在运行！");
  } finally {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        showResults.value = true
      })
    })
  }
}

// 🚀 核心改动 4：兼容多选的 UI 摘要渲染
const selectedSummary = computed(() => {
  const parts = []

  // 处理单选
  if (selected.value.gender) {
    const gMap = {'male': '男生', 'female': '女生'};
    parts.push(gMap[selected.value.gender]);
  }
  const seasonMap = seasonOptions.find(i => i.value === selected.value.season)
  const sceneMap = sceneOptions.find(i => i.value === selected.value.scene)
  if (seasonMap) parts.push(seasonMap.zh)
  if (sceneMap) parts.push(sceneMap.zh)

  // 处理多选 (风格和颜色是数组)
  if (selected.value.style.length > 0) {
    const styleZhs = styleOptions.filter(i => selected.value.style.includes(i.value)).map(i => i.zh);
    parts.push(...styleZhs);
  }
  if (selected.value.color.length > 0) {
    const colorZhs = colorOptions.filter(i => selected.value.color.includes(i.value)).map(i => i.zh);
    parts.push(...colorZhs);
  }

  if (parts.length === 0) {
    return '未设置筛选条件，点击生成后将随机推荐。'
  }

  return `已选择：${parts.join(' / ')}`
})

const boardClasses = ['board-a', 'board-b', 'board-c', 'board-d']
</script>

<template>
  <div class="match-page">
    <header class="match-topbar">
      <button class="back-btn" @click="emit('back-to-home')">返回首页</button>
      <div class="match-brand">Dress Select</div>
      <div class="topbar-placeholder"></div>
    </header>

    <section class="hero-section">
      <p class="hero-kicker">STYLE MATCH</p>
      <h1>为我搭配</h1>

    </section>

    <section class="workspace">
      <div class="picker-panel">
        <div class="picker-grid">
         <section class="picker-card gender-card">
        <h3>性别 Gender</h3>
        <div class="chip-list">
          <button
            v-for="item in genderOptions"
            :key="item.value"
            class="chip"
            :class="{ active: selected.gender === item.value }"
            @click="selected.gender = item.value"
          >
            <span class="chip-zh">{{ item.zh }}</span>
            <span class="chip-en">{{ item.en }}</span>
          </button>
        </div>
      </section> 
          <section class="picker-card">  
            <h3>风格 Style</h3>
            <div class="chip-list">
              <button
                v-for="item in styleOptions"
                :key="item.value"
                class="chip"
                :class="{ active: selected.style.includes(item.value) }"
                @click="toggleMulti('style', item.value)"
              >
                <span class="chip-zh">{{ item.zh }}</span>
                <span class="chip-en">{{ item.en }}</span>
              </button>
            </div>
          </section>

          <section class="picker-card">
            <h3>颜色 Color</h3>
            <div class="chip-list">
              <button
                v-for="item in colorOptions"
                :key="item.value"
                class="chip"
                :class="{ active: selected.color.includes(item.value) }"
                @click="toggleMulti('color', item.value)"
              >
                <span class="chip-zh">{{ item.zh }}</span>
                <span class="chip-en">{{ item.en }}</span>
              </button>
            </div>
          </section>

          <section class="picker-card compact-card">
            <h3>季节 Season</h3>
            <div class="chip-list">
              <button
                v-for="item in seasonOptions"
                :key="item.value"
                class="chip"
                :class="{ active: selected.season === item.value }"
                @click="selected.season = selected.season === item.value ? '' : item.value"
              >
                <span class="chip-zh">{{ item.zh }}</span>
                <span class="chip-en">{{ item.en }}</span>
              </button>
            </div>
          </section>

          <section class="picker-card compact-card">
            <h3>场景 Scene</h3>
            <div class="chip-list">
              <button
                v-for="item in sceneOptions"
                :key="item.value"
                class="chip"
                :class="{ active: selected.scene === item.value }"
                @click="selected.scene = selected.scene === item.value ? '' : item.value"
              >
                <span class="chip-zh">{{ item.zh }}</span>
                <span class="chip-en">{{ item.en }}</span>
              </button>
            </div>
          </section>
        </div>

        <div class="action-row">
          <p class="summary-text">{{ selectedSummary }}</p>
          <button class="generate-btn" @click="generateLooks">生成搭配</button>
        </div>
      </div>

      <aside class="result-panel">
        <div class="result-head">
          <p class="result-kicker">OUTFIT BOARD</p>
          <h2>搭配结果</h2>
        </div>

        <div v-if="!hasGenerated" class="result-empty">
            <p>点击“生成搭配”，这里会出现四套推荐结果。</p>
        </div>

        <div v-else class="result-board">
            <section
                v-for="(look, index) in resultLooks"
                :key="`${resultVersion}-${look.id}`"
                class="look-group"
                :class="[
                    boardClasses[index % boardClasses.length],
                    showResults ? 'animate-in' : '',
                    `delay-${index + 1}`
                ]"
            >
                <template v-if="look.type === 'separate'">
                    <article
                        v-for="(item, itemIndex) in look.items"
                        :key="`${look.id}-${itemIndex}`"
                        class="single-item-card"
                    >
                        <img
                            v-if="item.image"
                            :src="item.image"
                            class="image-box"
                            alt=""
                        />
                        <div v-else class="image-box"></div>

                        <div class="item-meta">
                            <span class="item-brand">{{ item.brand }}</span>
                            <span class="item-price">{{ item.price }}</span>
                        </div>
                    </article>
                </template>

                <template v-else>
                    <article class="single-item-card dress-card">
                        <img
                            v-if="look.items[0].image"
                            :src="look.items[0].image"
                            class="image-box"
                            alt=""
                        />
                        <div v-else class="image-box"></div>

                        <div class="item-meta">
                            <span class="item-brand">{{ look.items[0].brand }}</span>
                            <span class="item-price">{{ look.items[0].price }}</span>
                        </div>
                    </article>
                </template>
            </section>
        </div>
      </aside>
    </section>
  </div>
</template>

<style scoped>
.match-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(230, 222, 208, 0.42), transparent 260px),
    radial-gradient(circle at bottom right, rgba(233, 226, 216, 0.46), transparent 240px),
    #f5f5f3;
  color: #1f1f1f;
  padding-bottom: 18px;
}

.match-topbar {
  height: 56px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #e8e5df;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  height: 34px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid #ddd6ca;
  background: #fff;
  cursor: pointer;
  color: #1f1f1f;
}

.match-brand {
  font-size: 18px;
  font-weight: 700;
}

.topbar-placeholder {
  width: 80px;
}

.hero-section {
  max-width: 1700px;
  margin: 0 auto;
  padding: 14px 18px 8px;
}

.hero-kicker,
.result-kicker {
  margin: 0 0 5px;
  font-size: 11px;
  letter-spacing: 1.6px;
  color: #8b7355;
}

.hero-section h1 {
  margin: 0 0 4px;
  font-size: 32px;
  line-height: 1.1;
}

.hero-desc {
  margin: 0;
  max-width: 760px;
  color: #666;
  line-height: 1.6;
  font-size: 13px;
}

.workspace {
  max-width: 1700px;
  margin: 0 auto;
  padding: 0 18px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 760px;
  gap: 16px;
  align-items: start;
}

.picker-panel {
  min-width: 0;
}

.picker-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.picker-card {
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid #e6ddd0;
  border-radius: 20px;
  padding: 14px;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.03);
}

.compact-card {
  min-height: 170px;
}

.picker-card h3 {
  margin: 0 0 10px;
  font-size: 17px;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border: 1px solid #ddd6ca;
  background: #fffdfb;
  border-radius: 14px;
  padding: 8px 12px;
  cursor: pointer;
  min-height: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  transition: all 0.2s ease;
}

.chip:hover {
  transform: translateY(-2px);
  border-color: #bfae98;
  background: #faf7f2;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
}

.chip.active {
  background: #1f1f1f;
  border-color: #1f1f1f;
  color: #fff;
}

.chip-zh {
  font-size: 13px;
  font-weight: 600;
}

.chip-en {
  font-size: 11px;
  opacity: 0.78;
}

.action-row {
  margin-top: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid #ebe6de;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.summary-text {
  margin: 0;
  color: #3f3f3f;
  font-size: 15px;
  line-height: 1.5;
  font-weight: 600;
}

.generate-btn {
  flex-shrink: 0;
  height: 42px;
  padding: 0 20px;
  border: none;
  border-radius: 12px;
  background: #1f1f1f;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.generate-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(31, 31, 31, 0.15);
}

.result-panel {
  position: sticky;
  top: 66px;
  background: rgba(255, 251, 247, 0.88);
  border: 1px solid #e8dfd2;
  border-radius: 24px;
  padding: 16px;
  min-height: 760px;
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.result-head {
  margin-bottom: 10px;
}

.result-head h2 {
  margin: 0;
  font-size: 24px;
}

.result-empty {
  min-height: 680px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f5efe7, #eee5d8);
  border: 1px dashed #d8cbb9;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
}

.result-empty p {
  margin: 0;
  max-width: 260px;
  color: #6c6258;
  line-height: 1.7;
  font-size: 14px;
}

.result-board {
  height: 680px;
  min-height: 680px;
  position: relative;
}

.look-group {
  position: absolute;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  opacity: 0;
  will-change: transform, opacity;
}

.board-a {
  top: 10px;
  left: 10px;
  transform: rotate(-4deg);
}

.board-b {
  top: 28px;
  left: 380px;
  transform: rotate(3deg);
}

.board-c {
  top: 360px;
  left: 32px;
  transform: rotate(-2deg);
}

.board-d {
  top: 388px;
  left: 390px;
  transform: rotate(4deg);
}

.single-item-card {
  width: 170px;
  background: #fffdfa;
  border: 1px solid #e8dfd2;
  border-radius: 22px;
  padding: 12px;
  box-shadow: 0 18px 28px rgba(0, 0, 0, 0.08);
}

.dress-card {
  width: 220px;
}

.animate-in {
  animation: stickerIn 0.72s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  animation-delay: var(--delay, 0s);
}

.delay-1 {
  --delay: 0.02s;
}

.delay-2 {
  --delay: 0.14s;
}

.delay-3 {
  --delay: 0.26s;
}

.delay-4 {
  --delay: 0.38s;
}

@keyframes stickerIn {
  0% {
    opacity: 0;
    transform: translateY(80px) scale(0.7) rotate(-10deg);
  }
  65% {
    opacity: 1;
    transform: translateY(-8px) scale(1.02) rotate(2deg);
  }
  100% {
    opacity: 1;
  }
}

.image-box {
  width: 100%;
  aspect-ratio: 1 / 1; /* 保持正方形 */
  border-radius: 18px;
  background: #fdfbf8; /* 给个淡淡的底色，防止留白太丑 */
  border: 1px solid #e4d7c5;
  
  /* 🚀 核心修复：把 cover 改成 contain */
  object-fit: contain; 
  
  display: block;
  padding: 10px; /* 💡 可选：加一点内边距，让衣服离边框远一点，更有高级感 */
}

.item-meta {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-brand {
  font-size: 14px;
  color: #666;
}

.item-price {
  font-size: 30px;
  font-weight: 700;
  color: #7a4134;
  line-height: 1.1;
}

@media (max-width: 1500px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .result-panel {
    position: static;
    min-height: auto;
  }

  .result-board {
    height: auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }

  .look-group {
    position: static;
    opacity: 1;
    transform: none !important;
    animation: none;
  }
}

@media (max-width: 980px) {
  .picker-grid {
    grid-template-columns: 1fr;
  }

  .action-row {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 720px) {
  .result-board {
    grid-template-columns: 1fr;
  }

  .look-group {
    flex-wrap: wrap;
  }
}
</style>