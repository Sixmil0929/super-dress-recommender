<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import api from '../src/api'

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
const selectedItem = ref(null)
const detailMeta = ref(createEmptyDetailMeta())
const detailStats = ref(createEmptyStats())
const detailBehavior = ref(createEmptyBehavior())
const detailOpenedAt = ref(0)
const userPhone = ref('')
const behaviorStateMap = ref({})
const isDetailLoading = ref(false)
const detailMediaFrameRef = ref(null)
const detailImageRef = ref(null)
const detailInfoVisible = ref(false)
const detailImageVisible = ref(true)
const motionImage = ref(null)
let motionTimer = null
const BEHAVIOR_STORAGE_KEY = 'dress-select-item-behavior'

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

const seasonLabelMap = {
  spring: '春季',
  summer: '夏季',
  autumn: '秋季',
  fall: '秋季',
  winter: '冬季'
}

const styleLabelMap = {
  sporty: '运动风',
  streetwear: '街头风',
  minimalist: '极简风',
  casual: '休闲风',
  formal: '正式风',
  business: '商务风',
  outdoor: '户外风',
  vintage: '复古风',
  elegant: '优雅风',
  romantic: '浪漫风',
  sweet: '甜美风',
  sexy: '性感风',
  'business casual': '轻商务',
  'romantic dating': '约会风'
}

const genderLabelMap = {
  male: '男装',
  female: '女装',
  unisex: '中性'
}

function createEmptyStats() {
  return {
    total_likes: 0,
    total_collects: 0,
    total_shares: 0,
    total_views: 0,
    total_stay_time: 0
  }
}

function createEmptyBehavior() {
  return {
    is_like: false,
    is_collect: false,
    is_share: false
  }
}

function createEmptyDetailMeta() {
  return {
    filename: '',
    category: '',
    color: '',
    brand: '',
    price: '',
    season: '',
    style: '',
    gender: ''
  }
}

const cloneRect = (rect) =>
  rect
    ? {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height
      }
    : null

const parseBehaviorStorage = () => {
  try {
    const raw = localStorage.getItem(BEHAVIOR_STORAGE_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch (error) {
    console.warn('读取本地行为缓存失败：', error)
    return {}
  }
}

const persistBehaviorStorage = () => {
  localStorage.setItem(BEHAVIOR_STORAGE_KEY, JSON.stringify(behaviorStateMap.value))
}

const getCurrentUserPhone = () => userPhone.value || localStorage.getItem('user_phone') || 'guest'
const getBehaviorCacheKey = (filename) => `${getCurrentUserPhone()}::${filename}`

const getCachedBehavior = (filename) => {
  const state = behaviorStateMap.value[getBehaviorCacheKey(filename)]
  return state ? { ...createEmptyBehavior(), ...state } : createEmptyBehavior()
}

const setCachedBehavior = (filename, state) => {
  behaviorStateMap.value = {
    ...behaviorStateMap.value,
    [getBehaviorCacheKey(filename)]: { ...state }
  }
  persistBehaviorStorage()
}

const normalizeChineseList = (value, dictionary, fallback) => {
  if (!value) return fallback

  const tokens = String(value)
    .split(',')
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean)

  if (tokens.length === 0) return fallback

  return tokens
    .map((token) => dictionary[token] || token)
    .join('、')
}

const normalizeGenderLabel = (value) => {
  if (!value) return ''
  return genderLabelMap[String(value).trim().toLowerCase()] || String(value)
}

const detailSummary = computed(() => {
  if (!selectedItem.value) return ''

  const season = normalizeChineseList(detailMeta.value.season, seasonLabelMap, '多季节')
  const style = normalizeChineseList(detailMeta.value.style, styleLabelMap, '简约风')
  return `适合 ${season} 穿着，整体更偏 ${style}，适合作为日常搭配中的主视觉单品。`
})

const motionImageStyle = computed(() => {
  if (!motionImage.value) return {}

  const rect = motionImage.value.atEnd ? motionImage.value.end : motionImage.value.start
  return {
    top: `${rect.top}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    height: `${rect.height}px`,
    borderRadius: '0px'
  }
})

const generateLooks = async () => {
  hasGenerated.value = true
  showResults.value = false
  resultVersion.value += 1

  try {
    const payload = {
      gender: selected.value.gender || "", 
      season: selected.value.season || "",
      scene: selected.value.scene || "",
      style: selected.value.style,  
      preferred_colors: selected.value.color 
    };

    console.log("📤 发送给后端的数据:", payload);

    const res = await api.post('/api/recommend_by_survey', payload)
    const responseData = res.data

    if (responseData?.status !== 'success') {
      throw new Error(responseData?.message || '推荐失败')
    }

    const outfits = responseData?.data?.outfits || []

    console.log("🔥 拿到后端真实数据了！", outfits);
    
    const createLookItem = (rawItem, category = '推荐单品') => ({
      filename: rawItem.filename,
      title: rawItem.brand || 'Dress Select 严选单品',
      brand: rawItem.brand || '未知品牌',
      price: rawItem.price || '¥199',
      category,
      image: `${api.defaults.baseURL}/images/${rawItem.filename}`
    })

    const formattedLooks = outfits.map((outfit, index) => {
      if (outfit.type === 'single' || outfit.type === 'one_piece') {
        return {
          id: index + 1,
          type: 'dress', 
          items: [createLookItem(outfit.item, outfit.item.category || '推荐单品')]
        }
      } 
      else if (outfit.type === 'combo') {
        return {
          id: index + 1,
          type: 'separate',
          items: [
            createLookItem(outfit.top, '上衣'),
            createLookItem(outfit.bottom, '下装')
          ]
        }
      }
    });

    resultLooks.value = formattedLooks;

  } catch (error) {
    console.error("请求失败！", error);
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

const fetchDetailMeta = async (filename) => {
  isDetailLoading.value = true
  try {
    const res = await api.get(`/api/item/detail/${encodeURIComponent(filename)}`)
    const payload = res.data

    if (payload?.status !== 'success') {
      throw new Error(payload?.message || '详情信息加载失败')
    }

    detailMeta.value = {
      ...createEmptyDetailMeta(),
      ...(payload.data || {})
    }
  } catch (error) {
    console.error('加载衣服详情失败：', error)
    detailMeta.value = createEmptyDetailMeta()
  } finally {
    isDetailLoading.value = false
  }
}

const fetchDetailStats = async (filename) => {
  try {
    const res = await api.get(`/api/item/stats/${encodeURIComponent(filename)}`)
    const payload = res.data

    if (payload?.status !== 'success') {
      throw new Error(payload?.message || '详情统计加载失败')
    }

    detailStats.value = {
      ...createEmptyStats(),
      ...(payload.data || {})
    }
  } catch (error) {
    console.error('加载衣服统计失败：', error)
    detailStats.value = createEmptyStats()
  }
}

const postBehaviorRecord = async (duration = 0) => {
  if (!selectedItem.value?.filename) return

  const res = await api.post('/api/behavior/record', {
    user_phone: getCurrentUserPhone(),
    filename: selectedItem.value.filename,
    stay_duration: Math.max(0, Math.round(duration)),
    ...detailBehavior.value
  })

  const payload = res.data
  if (payload?.status !== 'success') {
    throw new Error(payload?.message || '行为记录失败')
  }
}

const updateStatsForBehavior = (previousState, nextState) => {
  if (nextState.is_like !== previousState.is_like) {
    detailStats.value.total_likes = Math.max(
      0,
      detailStats.value.total_likes + (nextState.is_like ? 1 : -1)
    )
  }

  if (nextState.is_collect !== previousState.is_collect) {
    detailStats.value.total_collects = Math.max(
      0,
      detailStats.value.total_collects + (nextState.is_collect ? 1 : -1)
    )
  }

  if (nextState.is_share && !previousState.is_share) {
    detailStats.value.total_shares += 1
  }
}

const flushDetailStay = async () => {
  if (!selectedItem.value || !detailOpenedAt.value) return

  const duration = Math.max(1, Math.round((Date.now() - detailOpenedAt.value) / 1000))

  try {
    await postBehaviorRecord(duration)
    detailStats.value.total_views += 1
    detailStats.value.total_stay_time += duration
  } catch (error) {
    console.error('记录停留时长失败：', error)
  } finally {
    detailOpenedAt.value = 0
  }
}

const clearMotionTimer = () => {
  if (motionTimer) {
    window.clearTimeout(motionTimer)
    motionTimer = null
  }
}

const startDetailMotion = async (imageRect, imageSrc) => {
  clearMotionTimer()
  detailInfoVisible.value = false
  detailImageVisible.value = !imageRect
  motionImage.value = null

  if (!imageRect) {
    requestAnimationFrame(() => {
      detailInfoVisible.value = true
      detailImageVisible.value = true
    })
    return
  }

  await nextTick()
  await new Promise((resolve) => requestAnimationFrame(() => resolve()))
  await new Promise((resolve) => requestAnimationFrame(() => resolve()))

  const targetRect =
    detailImageRef.value?.getBoundingClientRect?.() ||
    detailMediaFrameRef.value?.getBoundingClientRect?.()
  if (!targetRect) {
    detailInfoVisible.value = true
    detailImageVisible.value = true
    return
  }

  motionImage.value = {
    src: imageSrc,
    start: cloneRect(imageRect),
    end: cloneRect(targetRect),
    atEnd: false
  }

  await nextTick()

  requestAnimationFrame(() => {
    if (!motionImage.value) return
    motionImage.value = {
      ...motionImage.value,
      atEnd: true
    }
    detailInfoVisible.value = true
  })

  motionTimer = null
}

const openItemDetail = async (item, event) => {
  const imageEl = event?.currentTarget?.querySelector('.image-box')
  const imageRect = imageEl?.getBoundingClientRect?.() || null

  if (selectedItem.value?.filename === item.filename) return

  if (selectedItem.value) {
    await flushDetailStay()
  }

  selectedItem.value = { ...item }
  detailMeta.value = createEmptyDetailMeta()
  detailStats.value = createEmptyStats()
  detailBehavior.value = getCachedBehavior(item.filename)
  detailOpenedAt.value = Date.now()
  document.body.style.overflow = 'hidden'
  await startDetailMotion(imageRect, item.image)

  await Promise.all([
    fetchDetailMeta(item.filename),
    fetchDetailStats(item.filename)
  ])
}

const closeItemDetail = async () => {
  clearMotionTimer()
  await flushDetailStay()
  motionImage.value = null
  detailInfoVisible.value = false
  detailImageVisible.value = true
  selectedItem.value = null
  detailMeta.value = createEmptyDetailMeta()
  detailStats.value = createEmptyStats()
  detailBehavior.value = createEmptyBehavior()
  document.body.style.overflow = ''
}

const handleBehaviorToggle = async (field) => {
  if (!selectedItem.value) return

  const previousState = { ...detailBehavior.value }
  const nextState = { ...detailBehavior.value }

  if (field === 'is_share') {
    if (nextState.is_share) return
    nextState.is_share = true
  } else {
    nextState[field] = !nextState[field]
  }

  detailBehavior.value = nextState
  setCachedBehavior(selectedItem.value.filename, nextState)
  updateStatsForBehavior(previousState, nextState)

  try {
    await postBehaviorRecord(0)
    if (field === 'is_share' && navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(selectedItem.value.image)
    }
  } catch (error) {
    console.error('更新互动状态失败：', error)
    detailBehavior.value = previousState
    setCachedBehavior(selectedItem.value.filename, previousState)
    updateStatsForBehavior(nextState, previousState)
  }
}

const handleEscClose = (event) => {
  if (event.key === 'Escape' && selectedItem.value) {
    closeItemDetail()
  }
}

onMounted(() => {
  userPhone.value = localStorage.getItem('user_phone') || 'guest'
  behaviorStateMap.value = parseBehaviorStorage()
  window.addEventListener('keydown', handleEscClose)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscClose)
  clearMotionTimer()
  if (selectedItem.value) {
    flushDetailStay()
  }
  document.body.style.overflow = ''
})
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
                        role="button"
                        tabindex="0"
                        @click="openItemDetail(item, $event)"
                        @keydown.enter.prevent="openItemDetail(item, $event)"
                        @keydown.space.prevent="openItemDetail(item, $event)"
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
                    <article
                      class="single-item-card dress-card"
                      role="button"
                      tabindex="0"
                      @click="openItemDetail(look.items[0], $event)"
                      @keydown.enter.prevent="openItemDetail(look.items[0], $event)"
                      @keydown.space.prevent="openItemDetail(look.items[0], $event)"
                    >
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

    <Transition name="detail-shell">
      <div
        v-if="selectedItem"
        class="detail-layer"
        @click.self="closeItemDetail"
      >
        <img
          v-if="motionImage"
          :src="motionImage.src"
          alt=""
          class="detail-motion-image"
          :style="motionImageStyle"
        />
        <section class="detail-panel">
          <button type="button" class="detail-close" @click="closeItemDetail" aria-label="关闭详情">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M6 6 18 18M18 6 6 18" />
            </svg>
          </button>

          <div class="detail-media">
            <div ref="detailMediaFrameRef" class="detail-media-frame">
              <img
                ref="detailImageRef"
                :src="selectedItem.image"
                :alt="selectedItem.title"
                class="detail-image"
                :class="{ 'detail-image-hidden': !detailImageVisible }"
              />
            </div>
          </div>

          <div class="detail-info" :class="{ 'detail-info-visible': detailInfoVisible }">
            <div class="detail-headline">
              <div>
                <h3>{{ detailMeta.brand || selectedItem.title }}</h3>
                <p class="detail-price">{{ detailMeta.price || selectedItem.price }}</p>
                <p v-if="normalizeGenderLabel(detailMeta.gender)" class="detail-gender-tag">
                  {{ normalizeGenderLabel(detailMeta.gender) }}
                </p>
                <p class="detail-summary">
                  {{ isDetailLoading ? '正在整理这件单品的搭配信息...' : detailSummary }}
                </p>
              </div>
            </div>

            <div class="detail-action-row">
              <button
                type="button"
                class="engagement-btn"
                :class="{ active: detailBehavior.is_like }"
                @click.stop="handleBehaviorToggle('is_like')"
              >
                <span class="engagement-icon">♥</span>
                <span>点赞</span>
                <strong>{{ detailStats.total_likes }}</strong>
              </button>
              <button
                type="button"
                class="engagement-btn"
                :class="{ active: detailBehavior.is_collect }"
                @click.stop="handleBehaviorToggle('is_collect')"
              >
                <span class="engagement-icon">★</span>
                <span>收藏</span>
                <strong>{{ detailStats.total_collects }}</strong>
              </button>
              <button
                type="button"
                class="engagement-btn"
                :class="{ active: detailBehavior.is_share }"
                @click.stop="handleBehaviorToggle('is_share')"
              >
                <span class="engagement-icon">↗</span>
                <span>{{ detailBehavior.is_share ? '已转发' : '转发' }}</span>
                <strong>{{ detailStats.total_shares }}</strong>
              </button>
            </div>
          </div>
        </section>
      </div>
    </Transition>
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
  cursor: pointer;
  outline: none;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.single-item-card:hover {
  transform: translateY(-4px);
  border-color: #d4c2ad;
  box-shadow: 0 20px 34px rgba(0, 0, 0, 0.11);
}

.single-item-card:focus-visible {
  box-shadow: 0 0 0 3px rgba(122, 65, 52, 0.18), 0 20px 34px rgba(0, 0, 0, 0.11);
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

.detail-layer {
  position: fixed;
  inset: 0;
  z-index: 80;
  padding: 32px;
  background: rgba(33, 24, 15, 0.36);
  backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-motion-image {
  position: fixed;
  z-index: 82;
  object-fit: contain;
  filter: drop-shadow(0 18px 34px rgba(40, 26, 16, 0.12));
  pointer-events: none;
  will-change: top, left, width, height;
  transition:
    top 0.68s cubic-bezier(0.16, 0.9, 0.2, 1),
    left 0.68s cubic-bezier(0.16, 0.9, 0.2, 1),
    width 0.68s cubic-bezier(0.16, 0.9, 0.2, 1),
    height 0.68s cubic-bezier(0.16, 0.9, 0.2, 1),
    border-radius 0.68s cubic-bezier(0.16, 0.9, 0.2, 1),
    opacity 0.26s ease;
}

.detail-panel {
  position: relative;
  width: min(1240px, 100%);
  min-height: min(78vh, 760px);
  max-height: min(88vh, 920px);
  background: rgba(255, 252, 248, 0.98);
  border: 1px solid rgba(235, 225, 213, 0.92);
  border-radius: 30px;
  box-shadow: 0 32px 70px rgba(19, 14, 10, 0.22);
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 0.84fr);
  overflow: hidden;
}

.detail-close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1px solid rgba(223, 211, 197, 0.9);
  background: rgba(255, 252, 247, 0.86);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.detail-close:hover {
  transform: translateY(-1px);
  background: #fff;
  border-color: #d3c3af;
}

.detail-close svg {
  width: 18px;
  height: 18px;
  stroke: #4d4032;
  stroke-width: 2.1;
  fill: none;
  stroke-linecap: round;
}

.detail-media {
  padding: 34px;
  background:
    radial-gradient(circle at 12% 12%, rgba(238, 226, 210, 0.78), transparent 260px),
    linear-gradient(160deg, #f7f0e6 0%, #efe4d6 46%, #e7dbcc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
}

.detail-media-frame {
  width: 100%;
  min-height: min(70vh, 680px);
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.82);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.22)),
    rgba(249, 245, 239, 0.88);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55), 0 26px 48px rgba(72, 56, 39, 0.12);
  padding: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.45s cubic-bezier(0.2, 0.75, 0.2, 1);
}

.detail-image {
  width: 100%;
  height: min(64vh, 620px);
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 18px 34px rgba(40, 26, 16, 0.12));
  transition: transform 0.5s cubic-bezier(0.2, 0.75, 0.2, 1), opacity 0.35s ease;
}

.detail-image-hidden {
  opacity: 0;
}

.detail-info {
  padding: 42px 40px 42px 34px;
  overflow-y: auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  opacity: 0;
  transform: translateX(42px);
  transition: opacity 0.46s ease 0.34s, transform 0.58s cubic-bezier(0.16, 0.9, 0.2, 1) 0.34s;
}

.detail-info-visible {
  opacity: 1;
  transform: translateX(0);
}

.detail-headline {
  display: block;
}

.detail-info h3 {
  margin: 0;
  font-size: 42px;
  line-height: 1.08;
  color: #211a13;
}

.detail-price {
  margin: 12px 0 0;
  font-size: 30px;
  font-weight: 800;
  color: #7a4134;
}

.detail-gender-tag {
  margin: 10px 0 0;
  color: #7e6750;
  font-size: 17px;
  line-height: 1.6;
  font-weight: 500;
}

.detail-summary {
  margin: 16px 0 0;
  color: #685f56;
  font-size: 17px;
  line-height: 1.85;
  max-width: 520px;
}

.detail-action-row {
  margin-top: 34px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  position: relative;
}

.engagement-btn {
  min-height: 94px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid #e5d8c8;
  background: #fffdfa;
  color: #4f4438;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.engagement-btn:hover {
  transform: translateY(-2px);
  border-color: #d1bea8;
  box-shadow: 0 14px 24px rgba(56, 41, 23, 0.08);
}

.engagement-btn.active {
  border-color: rgba(122, 65, 52, 0.3);
  background: rgba(122, 65, 52, 0.08);
  color: #7a4134;
}

.engagement-icon {
  font-size: 24px;
  line-height: 1;
}

.engagement-btn span:not(.engagement-icon) {
  font-size: 15px;
  font-weight: 600;
}

.engagement-btn strong {
  font-size: 30px;
  line-height: 1.1;
}

.detail-shell-enter-active,
.detail-shell-leave-active {
  transition: opacity 0.28s ease;
}

.detail-shell-enter-active .detail-panel,
.detail-shell-leave-active .detail-panel {
  transition: transform 0.42s cubic-bezier(0.2, 0.75, 0.2, 1), opacity 0.35s ease;
}

.detail-shell-enter-from,
.detail-shell-leave-to {
  opacity: 0;
}

.detail-shell-enter-from .detail-panel,
.detail-shell-leave-to .detail-panel {
  transform: translateY(24px) scale(0.97);
  opacity: 0;
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

  .detail-panel {
    grid-template-columns: 1fr;
    max-height: 92vh;
  }

  .detail-media {
    padding: 24px 24px 0;
  }

  .detail-media-frame {
    min-height: 360px;
  }

  .detail-image {
    height: 320px;
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

  .detail-layer {
    padding: 16px;
  }

  .detail-panel {
    border-radius: 24px;
  }

  .detail-media {
    padding: 20px 20px 0;
  }

  .detail-info {
    padding: 28px 20px 24px;
  }

  .detail-headline {
    display: block;
  }

  .detail-info h3 {
    font-size: 34px;
  }

  .detail-price {
    font-size: 26px;
  }

  .detail-action-row {
    grid-template-columns: 1fr;
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
