<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue' 
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

// 🌟 新增：中英文分类翻译机 (确保顶部 Tab 按钮能正确筛选)
const categoryMap = {
  'top': '上装',
  'bottom': '下装',
  'one_piece': '裙装'
}

// 2. 核心抽卡函数
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
        id: Date.now() + index, 
        title: item.brand && item.brand !== 'Unknown' ? item.brand : 'V7.0 严选单品', 
        price: item.price, 
        category: mappedType, 
        type: mappedType,
        
        // 🚀 核心修复 1：接收后端真实的英文标签，坚决不写死！
        season: item.season, 
        style: item.style,
        
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
  if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300) {
    fetchLooks()
  }
}

// 4. 页面开机自启
onMounted(() => {
  fetchLooks() 
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
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
          @reset-filters="clearAllFilters"
        />
      </section>
    </main>
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
}
</style>
