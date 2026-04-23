<script setup>
import { computed, nextTick, ref, onMounted, onUnmounted } from 'vue'
import api from '../src/api'
import Sidebar from './Sidebar.vue'
import RecommendationList from './RecommendationList.vue'

const emit = defineEmits(['go-to-style-match', 'go-to-profile'])

const activeTab = ref('全部')
const activeFilters = ref({
  season: '',
  style: '',
  category: ''
})
const tabs = ['全部', '上装', '下装', '裙装']

const recommendedItems = ref([])
const isLoading = ref(false)
const selectedItem = ref(null)
const detailStats = ref(createEmptyStats())
const detailBehavior = ref(createEmptyBehavior())
const isDetailLoading = ref(false)
const detailOpenedAt = ref(0)
const userPhone = ref('')
const behaviorStateMap = ref({})
const detailMediaFrameRef = ref(null)
const detailImageRef = ref(null)
const detailInfoVisible = ref(false)
const detailImageVisible = ref(true)
const motionImage = ref(null)
let motionTimer = null
const BEHAVIOR_STORAGE_KEY = 'dress-select-item-behavior'

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
  romantic: '浪漫风'
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

const cloneRect = (rect) =>
  rect
    ? {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height
      }
    : null

// 🌟 新增：中英文分类翻译机 (确保顶部 Tab 按钮能正确筛选)
const categoryMap = {
  'top': '上装',
  'bottom': '下装',
  'one_piece': '裙装'
}

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

const formatDisplayValue = (value, fallback = '未标注') => {
  if (!value) return fallback
  return String(value).replace(/,\s*/g, ' / ')
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

  const season = normalizeChineseList(selectedItem.value.season, seasonLabelMap, '多季节')
  const style = normalizeChineseList(selectedItem.value.style, styleLabelMap, '简约风')
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

const fetchLooks = async () => {
  if (isLoading.value) return
  isLoading.value = true
  
  try {
    const res = await api.get('/api/random_looks?limit=48')
    const payload = res.data
    const items = Array.isArray(payload?.data) ? payload.data : []

    if (payload?.status !== 'success') {
      throw new Error(payload?.message || '首页推荐加载失败')
    }
    
    const newItems = items.map((item, index) => {
      const mappedType = categoryMap[item.category] || '上装'
      
      return {
        id: `${item.filename}-${Date.now()}-${index}`,
        filename: item.filename,
        title: item.brand && item.brand !== 'Unknown' ? item.brand : 'Dress Select 严选单品',
        price: item.price,
        category: mappedType,
        type: mappedType,

        season: item.season,
        style: item.style,
        color: item.color,
        gender: item.gender,

        desc: '智能穿搭引擎精选',
        image: `${api.defaults.baseURL}/images/${item.filename}`,
        span: Math.random() > 0.8 ? 'large' : 'default'
      }
    })
    
    recommendedItems.value.push(...newItems)

  } catch (error) {
    console.error("首页盲抽崩了：", error)
  } finally {
    isLoading.value = false
  }
}

// 3. 滚动条监听雷达
const handleScroll = () => {
  if (selectedItem.value) return
  if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300) {
    fetchLooks()
  }
}

const fetchDetailStats = async (filename) => {
  isDetailLoading.value = true

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
  } finally {
    isDetailLoading.value = false
  }
}

const postBehaviorRecord = async (duration = 0) => {
  if (!selectedItem.value) return

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

const openItemDetail = async (payload) => {
  const item = payload?.item || payload
  const imageRect = payload?.imageRect || null

  if (selectedItem.value?.filename === item.filename) return

  if (selectedItem.value) {
    await flushDetailStay()
  }

  selectedItem.value = item
  detailStats.value = createEmptyStats()
  detailBehavior.value = getCachedBehavior(item.filename)
  detailOpenedAt.value = Date.now()
  document.body.style.overflow = 'hidden'
  await startDetailMotion(imageRect, item.image)
  await fetchDetailStats(item.filename)
}

const closeItemDetail = async () => {
  clearMotionTimer()
  await flushDetailStay()
  motionImage.value = null
  detailInfoVisible.value = false
  detailImageVisible.value = true
  selectedItem.value = null
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
  fetchLooks()
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('keydown', handleEscClose)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('keydown', handleEscClose)
  clearMotionTimer()
  if (selectedItem.value) {
    flushDetailStay()
  }
  document.body.style.overflow = ''
})

const goToStyleMatch = () => emit('go-to-style-match')
const goToProfile = () => emit('go-to-profile')
const setTab = (tab) => {
  activeTab.value = tab
}

const clearAllFilters = () => {
  activeFilters.value = {
    season: '',
    style: '',
    category: ''
  }
  activeTab.value = '全部'
}

const handleFilterChange = (filters) => {
  activeFilters.value = filters

  // 侧边栏有传值过来（比如 'top'）
  if (filters.category) {
    activeTab.value = categoryMap[filters.category] || '全部'
  } else {
    // 🚨 核心修复：如果是空字符串（代表取消选中），强制把顶部 Tab 拨回“全部”！
    activeTab.value = '全部' 
  }
}

const filteredItems = computed(() => {
  return recommendedItems.value.filter((item) => { 
    // 判断品类
    const matchTab = activeTab.value === '全部' || item.type === activeTab.value
    
    // 🚀 核心修复 3：用 includes 判断！因为数据库里的 season 可能是 "spring, summer"
    const matchSeason = !activeFilters.value.season || (item.season && item.season.includes(activeFilters.value.season))
    
    // 同理，判断风格
    const matchStyle = !activeFilters.value.style || (item.style && item.style.includes(activeFilters.value.style))

    return matchTab && matchSeason && matchStyle
  })
})

const hasActiveFilters = computed(() => {
  return Boolean(
    activeFilters.value.season ||
      activeFilters.value.style ||
      activeFilters.value.category ||
      activeTab.value !== '全部'
  )
})

const activeFilterText = computed(() => {
  const parts = []
  if (activeFilters.value.season) parts.push(activeFilters.value.season)
  if (activeFilters.value.style) parts.push(activeFilters.value.style)
  if (activeFilters.value.category) parts.push(activeFilters.value.category)
  if (parts.length === 0 && activeTab.value !== '全部') parts.push(activeTab.value)
  return parts.join(' / ')
})
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="brand">Dress Select</div>
      <nav class="nav">
        <button type="button" class="nav-link" @click="setTab('全部')">今日推荐</button>
        <button type="button" class="nav-link" @click="goToStyleMatch">风格匹配</button>
        <button type="button" class="setting-link" @click="goToProfile">资料设置</button>
      </nav>
    </header>

    <section class="hero">
      <div class="hero-card">
        <div class="hero-text">
          <p class="eyebrow">PERSONAL STYLE EDIT</p>
          <h1>把每日穿搭从“凑合”变成“有章法”</h1>
          <p class="subtitle">
            根据你的基础信息和偏好，自动筛出更适合当前季节与场景的搭配，减少试错时间。
          </p>
          <div class="hero-pills">
            <span>本周精选 {{ recommendedItems.length }} 套</span>
            <span>支持按季节/风格筛选</span>
          </div>
          <div class="hero-actions">
            <button type="button" class="primary-btn" @click="goToStyleMatch">为我搭配</button>
            <button type="button" class="secondary-btn" @click="setTab('全部')">查看推荐</button>
          </div>
        </div>

        <div class="hero-visual">
          <img
            src="/editorial/home-banner.jpg"
            alt="首页专题图"
            class="hero-visual-image"
          />
        </div>
      </div>
    </section>

    <main class="content">
      <aside class="sidebar-wrap">
        <Sidebar
          :active-filters="activeFilters"
          @filter-change="handleFilterChange"
          @clear-filters="clearAllFilters"
        />
      </aside>

      <section class="main-area">
        <div class="section-head">
          <div>
            <p class="section-kicker">CURATED SELECTION</p>
            <h2>为你推荐的服装</h2>
            <p v-if="hasActiveFilters" class="active-filter-text">
              当前筛选：{{ activeFilterText || '全部' }}
            </p>
          </div>

          <div class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab"
              type="button"
              class="tab"
              :class="{ active: activeTab === tab }"
              @click="setTab(tab)"
            >
              {{ tab }}
            </button>
          </div>
        </div>

        <RecommendationList
          :items="filteredItems"
          @open-detail="openItemDetail"
          @reset-filters="clearAllFilters"
        />
      </section>
    </main>

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
                <h3>{{ selectedItem.title }}</h3>
                <p class="detail-price">{{ selectedItem.price }}</p>
                <p v-if="normalizeGenderLabel(selectedItem.gender)" class="detail-gender-tag">
                  {{ normalizeGenderLabel(selectedItem.gender) }}
                </p>
                <p class="detail-summary">{{ detailSummary }}</p>
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
.page {
  --bg: #f6f2eb;
  --card: #fffcf8;
  --text: #1f1b17;
  --muted: #6f665d;
  --line: #e7ddd1;
  --accent: #2f261f;
  --soft-accent: #efe4d7;
  min-height: 100vh;
  background:
    radial-gradient(circle at 15% 10%, rgba(234, 221, 205, 0.55), transparent 240px),
    radial-gradient(circle at 88% 18%, rgba(228, 214, 196, 0.42), transparent 220px),
    var(--bg);
  color: var(--text);
}

.topbar {
  min-height: 72px;
  padding: 10px 32px;
  background: rgba(255, 252, 247, 0.9);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  backdrop-filter: blur(10px);
  z-index: 20;
}

.brand {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 0.3px;
}

.nav {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-link,
.setting-link {
  height: 38px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--text);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.nav-link:hover,
.setting-link:hover {
  background: #f8f1e8;
  border-color: #d9c9b5;
}

.setting-link {
  border-color: var(--accent);
  background: var(--accent);
  color: #fff;
}

.setting-link:hover {
  background: #18120d;
  border-color: #18120d;
}

.hero {
  max-width: 1360px;
  margin: 0 auto;
  padding: 20px 24px 12px;
}

.hero-card {
  background: var(--card);
  border-radius: 24px;
  padding: 26px 30px;
  border: 1px solid var(--line);
  box-shadow: 0 12px 28px rgba(34, 26, 16, 0.08);
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 28px;
  align-items: center;
}

.hero-text {
  min-width: 0;
}

.eyebrow,
.section-kicker {
  font-size: 12px;
  letter-spacing: 1.8px;
  color: #927555;
  margin: 0 0 10px;
}

.hero h1 {
  margin: 0 0 12px;
  max-width: 640px;
  font-size: 40px;
  line-height: 1.12;
}

.subtitle {
  max-width: 620px;
  margin: 0;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.75;
}

.hero-pills {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-pills span {
  border-radius: 999px;
  border: 1px solid #ddcfbe;
  background: var(--soft-accent);
  color: #5c4c3c;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
}

.hero-actions {
  margin-top: 18px;
  display: flex;
  gap: 12px;
}

.primary-btn,
.secondary-btn {
  height: 46px;
  padding: 0 22px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn {
  border: none;
  background: var(--accent);
  color: #fff;
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 20px rgba(24, 18, 13, 0.2);
}

.secondary-btn {
  border: 1px solid var(--line);
  background: #fff;
  color: var(--text);
}

.secondary-btn:hover {
  background: #f8f1e8;
}

.hero-visual {
  width: 100%;
  height: 270px;
  border-radius: 22px;
  overflow: hidden;
  background: #efe7da;
}

.hero-visual-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.content {
  max-width: 1360px;
  margin: 0 auto;
  padding: 0 24px 36px;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 18px;
}

.sidebar-wrap {
  align-self: start;
  position: sticky;
  top: 96px;
}

.main-area {
  min-width: 0;
}

.section-head {
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
}

.section-head h2 {
  margin: 0;
  font-size: 30px;
}

.active-filter-text {
  margin: 6px 0 0;
  color: #856c53;
  font-size: 13px;
}

.tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tab {
  padding: 8px 14px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid var(--line);
  color: #5f554b;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab:hover {
  background: #f6eee4;
}

.tab.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.detail-layer {
  position: fixed;
  inset: 0;
  z-index: 60;
  padding: 32px;
  background: rgba(33, 24, 15, 0.36);
  backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-motion-image {
  position: fixed;
  z-index: 62;
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

.detail-info h3 {
  margin: 0;
  font-size: 42px;
  line-height: 1.08;
  color: #211a13;
}

.detail-headline {
  display: block;
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

@media (max-width: 1100px) {
  .hero-card {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    height: 320px;
  }

  .content {
    grid-template-columns: 1fr;
  }

  .sidebar-wrap {
    position: static;
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

@media (max-width: 760px) {
  .topbar {
    padding: 10px 14px;
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }

  .nav {
    width: 100%;
    justify-content: space-between;
  }

  .nav-link,
  .setting-link {
    flex: 1;
  }

  .hero {
    padding: 14px 14px 8px;
  }

  .hero-card {
    padding: 18px 16px;
  }

  .hero h1 {
    font-size: 30px;
  }

  .content {
    padding: 0 14px 24px;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-layer {
    padding: 14px;
  }

  .detail-panel {
    border-radius: 24px;
  }

  .detail-media {
    padding: 18px 18px 0;
  }

  .detail-media-frame {
    min-height: 280px;
    padding: 18px;
  }

  .detail-image {
    height: 250px;
  }

  .detail-info {
    padding: 26px 18px 22px;
  }

  .detail-headline {
    display: block;
  }

  .detail-info h3 {
    font-size: 32px;
  }

  .detail-price {
    font-size: 26px;
  }

  .detail-summary {
    font-size: 16px;
    line-height: 1.8;
  }

  .detail-action-row {
    grid-template-columns: 1fr;
  }
}
</style>
