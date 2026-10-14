<template>
  <view class="wrong">
    <!-- 加载态 -->
    <view v-if="loading" class="loading-card card">
      <text class="loading-text">正在加载错题…</text>
    </view>

    <!-- 错题列表 -->
    <view v-else-if="list.length">
      <view v-for="item in list" :key="item.id" class="wrong-card card">
        <!-- 卡片头部：类型徽章 + 错误次数 + 掌握按钮 -->
        <view class="wrong-header">
          <view class="type-badge" :class="'type-' + item.question_type">
            <text>{{ typeLabel(item.question_type) }}</text>
          </view>
          <text class="wrong-count">错 {{ item.wrong_count }} 次</text>
          <view class="flex-1"></view>
          <view class="master-btn" @click="onRemove(item)">
            <text>已掌握</text>
          </view>
        </view>

        <!-- 题干（点击展开解析） -->
        <view class="wrong-body" @click="toggleExpand(item.id)">
          <text class="wrong-text">{{ item.question_text }}</text>
          <text class="expand-hint">{{ expandedId === item.id ? '收起解析 ▲' : '查看解析 ▼' }}</text>
        </view>

        <!-- 解析区（展开时显示） -->
        <view v-if="expandedId === item.id" class="analysis">
          <view class="analysis-row">
            <text class="analysis-label">正确答案</text>
            <text class="analysis-answer">{{ item.answer }}</text>
          </view>
          <view class="analysis-row">
            <text class="analysis-label">解析</text>
            <text class="analysis-text">{{ item.analysis }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空态 -->
    <empty v-else icon="🎉" text="太棒了，暂无错题记录" btn-text="去闯关" @action="goLevels" />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { getWrongBook, removeWrong } from '@/api/game'

/* ---------- 数据 ---------- */
const loading = ref(true)
const list = ref([])
const expandedId = ref(null) // 当前展开解析的错题 id

/* ---------- 工具函数 ---------- */

/* 题型徽章文案 */
function typeLabel(type) {
  const map = { single: '单选', judge: '判断', image: '识图' }
  return map[type] || '单选'
}

/* ---------- 交互 ---------- */

/* 展开 / 收起解析 */
function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

/* 移除错题（已掌握） */
async function onRemove(item) {
  uni.showModal({
    title: '移除错题',
    content: '确认已掌握这道题？移除后不再出现在错题本中',
    confirmColor: '#b03a2e',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await removeWrong(item.id)
        list.value = list.value.filter((w) => w.id !== item.id)
        if (expandedId.value === item.id) expandedId.value = null
        uni.showToast({ title: '已移除', icon: 'success' })
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    }
  })
}

/* 去闯关 */
function goLevels() {
  uni.navigateTo({ url: '/pages/game/levels' })
}

/* ---------- 数据加载 ---------- */
async function loadWrongBook() {
  loading.value = true
  try {
    list.value = await getWrongBook() || []
  } catch (e) {
    list.value = []
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/* ---------- 生命周期 ---------- */
onLoad(loadWrongBook)

/* onShow：从答题页返回时刷新错题数据 */
onShow(() => {
  if (!loading.value) loadWrongBook()
})
</script>

<style lang="scss" scoped>
.wrong {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 加载态 ---------- */
.loading-card {
  display: flex;
  padding: 120rpx 32rpx;
  align-items: center;
  margin-top: 100rpx;
}
.loading-text {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- 错题卡 ---------- */
.wrong-card {
  padding: 24rpx 28rpx;
  margin-bottom: 20rpx;
}
.wrong-header {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.type-badge {
  border-radius: 8rpx;
  padding: 4rpx 16rpx;
  margin-right: 16rpx;
}
.type-badge text {
  font-size: 20rpx;
  font-weight: 600;
}
.type-badge.type-single {
  background: $primary-bg;
}
.type-badge.type-single text {
  color: $primary;
}
.type-badge.type-judge {
  background: #e8f0fa;
}
.type-badge.type-judge text {
  color: #3a5a8c;
}
.type-badge.type-image {
  background: #f0eaf8;
}
.type-badge.type-image text {
  color: #7a5a9e;
}
.wrong-count {
  font-size: 20rpx;
  color: $warning;
}
.master-btn {
  border-radius: 999rpx;
  border: 1rpx solid $success;
  padding: 6rpx 24rpx;
}
.master-btn text {
  font-size: 22rpx;
  color: $success;
  font-weight: 600;
}

/* 题干区 */
.wrong-body {
  margin-top: 16rpx;
}
.wrong-text {
  font-size: 28rpx;
  font-weight: 600;
  color: $ink;
  line-height: 1.7;
}
.expand-hint {
  display: block;
  font-size: 20rpx;
  color: $ink-light;
  margin-top: 10rpx;
}

/* 解析区 */
.analysis {
  margin-top: 16rpx;
  background: $paper;
  border-radius: $radius-sm;
  padding: 20rpx 24rpx;
}
.analysis-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 12rpx;
}
.analysis-row:last-child {
  margin-bottom: 0;
}
.analysis-label {
  font-size: 22rpx;
  color: $ink-light;
  width: 112rpx;
  flex-shrink: 0;
  margin-top: 4rpx;
}
.analysis-answer {
  font-size: 26rpx;
  font-weight: 700;
  color: $success;
}
.analysis-text {
  flex: 1;
  font-size: 24rpx;
  color: $ink;
  line-height: 1.7;
}
</style>
