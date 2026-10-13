<template>
  <view class="works">
    <!-- 类型筛选 chips -->
    <view class="filter-row">
      <view
        v-for="t in filters"
        :key="t.value"
        class="chip"
        :class="{ active: activeFilter === t.value }"
        @click="switchFilter(t.value)"
      >
        <text>{{ t.label }}</text>
      </view>
    </view>

    <!-- 加载态 -->
    <view v-if="loading" class="loading-card card">
      <text class="loading-text">正在加载作品…</text>
    </view>

    <!-- 作品列表 -->
    <view v-else-if="filteredWorks.length">
      <view v-for="w in filteredWorks" :key="w.id" class="work-card card">
        <!-- 删除按钮 -->
        <view class="work-delete" @click="onDelete(w)">
          <text>🗑</text>
        </view>

        <!-- 图片类作品（纹样 / 画作） -->
        <block v-if="w.type !== 'script'">
          <view class="work-cover" :style="{ background: workGradient(w) }">
            <text class="work-cover-text">{{ (w.style || '作').slice(0, 2) }}</text>
            <view class="ai-badge">
              <text>AI创作</text>
            </view>
          </view>
          <view class="work-info">
            <text class="work-title text-ellipsis">{{ w.title || typeLabel(w.type) }}</text>
            <view class="work-meta">
              <text class="tag">{{ typeLabel(w.type) }}</text>
              <text class="work-style">{{ w.style || '' }}</text>
              <text class="work-time">{{ fromNow(w.create_time) }}</text>
            </view>
          </view>
        </block>

        <!-- 剧本类作品 -->
        <block v-else>
          <view class="work-script">
            <view class="work-script-header">
              <text class="work-title text-ellipsis flex-1">《{{ w.title || w.theme }}》</text>
              <view class="ai-badge inline">
                <text>AI创作</text>
              </view>
            </view>
            <text class="work-abstract text-ellipsis-2">{{ w.content || '' }}</text>
            <view class="work-meta">
              <text class="tag">{{ typeLabel(w.type) }}</text>
              <text class="work-time">{{ fromNow(w.create_time) }}</text>
            </view>
          </view>
        </block>
      </view>
    </view>

    <!-- 空态 -->
    <empty
      v-else
      icon="🎨"
      text="还没有作品，去创作你的第一件非遗作品吧"
      btn-text="去创作"
      @action="goCreate"
    />
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { getWorks, deleteWork } from '@/api/ai'
import { fromNow } from '@/utils/util'

/* ---------- 数据 ---------- */
const loading = ref(true)
const allWorks = ref([])
const activeFilter = ref('all')

/* 筛选选项 */
const filters = [
  { value: 'all', label: '全部' },
  { value: 'pattern', label: '纹样' },
  { value: 'script', label: '剧本' },
  { value: 'painting', label: '画作' }
]

/* 筛选后的作品列表 */
const filteredWorks = computed(() => {
  if (activeFilter.value === 'all') return allWorks.value
  return allWorks.value.filter((w) => w.type === activeFilter.value)
})

/* ---------- 工具函数 ---------- */

/* 类型标签 */
function typeLabel(type) {
  const map = { pattern: '纹样', script: '剧本', painting: '画作' }
  return map[type] || '作品'
}

/* 作品占位图渐变色（按类型取不同色系） */
function workGradient(w) {
  const map = {
    pattern: 'linear-gradient(135deg, #b03a2e, #d45a4a)',
    painting: 'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    script: 'linear-gradient(135deg, #c9a063, #ddc08f)'
  }
  return map[w.type] || map.pattern
}

/* ---------- 交互 ---------- */

/* 切换筛选 */
function switchFilter(value) {
  activeFilter.value = value
}

/* 删除作品 */
async function onDelete(work) {
  uni.showModal({
    title: '删除作品',
    content: '确定要删除「' + (work.title || typeLabel(work.type)) + '」吗？',
    confirmColor: '#b03a2e',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await deleteWork(work.id)
        allWorks.value = allWorks.value.filter((w) => w.id !== work.id)
        uni.showToast({ title: '已删除', icon: 'success' })
      } catch (e) {
        uni.showToast({ title: '删除失败', icon: 'none' })
      }
    }
  })
}

/* 去创作（switchTab 到创作 tab） */
function goCreate() {
  uni.switchTab({ url: '/pages/create/create' })
}

/* ---------- 数据加载 ---------- */
async function loadWorks() {
  loading.value = true
  try {
    allWorks.value = await getWorks() || []
  } catch (e) {
    allWorks.value = []
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/* ---------- 生命周期 ---------- */
onLoad(loadWorks)

/* onShow：从创作页保存新作品返回时刷新 */
onShow(() => {
  if (!loading.value) loadWorks()
})
</script>

<style lang="scss" scoped>
.works {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 筛选 chips ---------- */
.filter-row {
  flex-direction: row;
  margin-bottom: 24rpx;
}
.chip {
  display: inline-block;
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: $card;
  border: 1rpx solid $border;
  font-size: 24rpx;
  color: $ink-light;
  margin-right: 16rpx;
  line-height: 40rpx;
  min-height: 64rpx;
  text-align: center;
}
.chip.active {
  background: $primary;
  border-color: $primary;
  color: #fff;
  font-weight: 600;
}

/* ---------- 加载态 ---------- */
.loading-card {
  padding: 120rpx 32rpx;
  align-items: center;
  margin-top: 40rpx;
}
.loading-text {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- 作品卡 ---------- */
.work-card {
  padding: 0;
  overflow: hidden;
  margin-bottom: 24rpx;
  position: relative;
}
.work-delete {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  align-items: center;
  justify-content: center;
  z-index: 2;
}
.work-delete text {
  font-size: 28rpx;
}

/* 图片类作品 */
.work-cover {
  height: 280rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.work-cover-text {
  font-size: 72rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 8rpx;
  text-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.22);
}
.ai-badge {
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 999rpx;
  padding: 4rpx 16rpx;
}
.ai-badge text {
  font-size: 18rpx;
  color: #fff;
}
.work-info {
  padding: 20rpx 24rpx 24rpx;
}
.work-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
}
.work-meta {
  flex-direction: row;
  align-items: center;
  margin-top: 10rpx;
}
.work-meta .tag {
  margin-bottom: 0;
  margin-right: 12rpx;
}
.work-style {
  font-size: 20rpx;
  color: $teal;
  margin-right: 16rpx;
}
.work-time {
  font-size: 20rpx;
  color: $ink-light;
}

/* 剧本类作品 */
.work-script {
  padding: 28rpx 24rpx 24rpx;
}
.work-script-header {
  flex-direction: row;
  align-items: center;
}
.ai-badge.inline {
  position: static;
  background: $primary-bg;
  margin-left: 12rpx;
  flex-shrink: 0;
}
.ai-badge.inline text {
  color: $primary;
  font-size: 18rpx;
  font-weight: 600;
}
.work-abstract {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.6;
  margin-top: 12rpx;
  background: $paper;
  border-radius: $radius-sm;
  padding: 16rpx 20rpx;
}
</style>
