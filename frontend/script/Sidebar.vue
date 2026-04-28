<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['filter-change'])

// 🚀 核心修复 1：把纯中文数组，变成带英文 value 的对象数组！
const seasons = [
  { zh: '春季', value: 'spring' },
  { zh: '夏季', value: 'summer' },
  { zh: '秋季', value: 'autumn' },
  { zh: '冬季', value: 'winter' }
]

const styles = [
  { zh: '休闲/日常', value: 'casual' },
  { zh: '轻商务', value: 'business casual' },
  { zh: '街头', value: 'streetwear' },
  { zh: '运动', value: 'sporty' }
]

const categories = [
  { zh: '上装', value: 'top' },
  { zh: '下装', value: 'bottom' },
  { zh: '裙装', value: 'one_piece' }
]

// 里面存的将会是英文，比如 'summer'
const activeSeason = ref('')
const activeStyle = ref('')
const activeCategory = ref('')

const toggleFilter = (type, value) => {
  if (type === 'season') {
    activeSeason.value = activeSeason.value === value ? '' : value
  }
  if (type === 'style') {
    activeStyle.value = activeStyle.value === value ? '' : value
  }
  if (type === 'category') {
    activeCategory.value = activeCategory.value === value ? '' : value
  }
}

watch([activeSeason, activeStyle, activeCategory], () => {
  emit('filter-change', {
    season: activeSeason.value,
    style: activeStyle.value,
    category: activeCategory.value
  })
})
</script>

<template>
  <aside class="filter-panel">
    <div class="filter-header">
      <p class="filter-kicker">FILTERS</p>
      <h3>筛选条件</h3>
    </div>

    <section class="filter-block">
      <p class="block-title">季节</p>
      <div class="chip-list">
        <button
          v-for="item in seasons"
          :key="item.value"
          class="chip"
          :class="{ active: activeSeason === item.value }"
          @click="toggleFilter('season', item.value)"
        >
          {{ item.zh }}
        </button>
      </div>
    </section>

    <section class="filter-block">
      <p class="block-title">风格</p>
      <div class="chip-list">
        <button
          v-for="item in styles"
          :key="item.value"
          class="chip"
          :class="{ active: activeStyle === item.value }"
          @click="toggleFilter('style', item.value)"
        >
          {{ item.zh }}
        </button>
      </div>
    </section>

    <section class="filter-block">
      <p class="block-title">品类</p>
      <div class="chip-list">
        <button
          v-for="item in categories"
          :key="item.value"
          class="chip"
          :class="{ active: activeCategory === item.value }"
          @click="toggleFilter('category', item.value)"
        >
          {{ item.zh }}
        </button>
      </div>
    </section>

  </aside>
</template>

<style scoped>
.filter-panel {
  background: #fff;
  border: 1px solid #ebe6de;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.filter-header {
  margin-bottom: 22px;
}

.filter-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 1.4px;
  color: #8b7355;
}

.filter-header h3 {
  margin: 0;
  font-size: 26px;
  color: #1f1f1f;
}

.filter-block {
  margin-bottom: 24px;
}

.block-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  padding: 9px 14px;
  border-radius: 999px;
  border: 1px solid #ddd6ca;
  background: #faf9f7;
  color: #444;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.chip:hover {
  background: #f0ece6;
}

.chip.active {
  background: #1f1f1f;
  color: #fff;
  border-color: #1f1f1f;
}

</style>
