<template>
  <view class="levels">
    <!-- 加载态 -->
    <view v-if="loading" class="loading-card card">
      <text class="loading-text">正在加载关卡…</text>
    </view>

    <!-- 段位分组展示 -->
    <view v-else>
      <view v-for="group in groupedLevels" :key="group.rank" class="rank-group">
        <!-- 组标题 -->
        <view class="group-header">
          <view class="group-badge" :style="{ background: rankColor(group.rank) }">
            <text>{{ group.rank }}</text>
          </view>
          <text class="group-title">{{ group.rank }}段位</text>
          <text class="group-count">{{ group.levels.length }} 关</text>
        </view>

        <!-- 关卡卡 -->
        <view
          v-for="lv in group.levels"
          :key="lv.id"
          class="level-card card"
          :class="{ locked: !lv.unlocked }"
          @click="onLevelClick(lv)"
        >
          <!-- 关卡图标 -->
          <view class="level-icon" :style="{ background: lv.unlocked ? rankColor(lv.rank) : '#e5ddd0' }">
            <text>{{ lv.unlocked ? lv.icon : '🔒' }}</text>
          </view>

          <view class="flex-1 level-info">
            <view class="level-name-row">
              <text class="level-name">{{ lv.name }}</text>
              <!-- 已通关徽章 -->
              <view v-if="lv.passed" class="pass-badge">
                <text>已通关</text>
              </view>
            </view>
            <text class="level-subtitle">{{ lv.subtitle }}</text>
            <view class="level-meta">
              <text class="level-theme">{{ lv.theme }}</text>
              <text class="level-count">{{ lv.question_count }} 题</text>
            </view>
            <!-- 底部状态行 -->
            <view v-if="lv.unlocked" class="level-status">
              <text class="level-best">最佳 {{ lv.bestScore }} 分</text>
            </view>
            <view v-else class="level-status">
              <text class="level-locked">再得 {{ lv.need_score }} 分解锁</text>
            </view>
          </view>
          <text class="level-arrow">{{ lv.unlocked ? '›' : '' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onLoad } from '@dcloudio/uni-app'
import { getLevels } from '@/api/game'

/* ---------- 数据 ---------- */
const loading = ref(true)
const levels = ref([])

/* 按 rank 分组（保持关卡顺序） */
const groupedLevels = computed(() => {
  const groups = []
  levels.value.forEach((lv) => {
    let g = groups.find((item) => item.rank === lv.rank)
    if (!g) {
      g = { rank: lv.rank, levels: [] }
      groups.push(g)
    }
    g.levels.push(lv)
  })
  return groups
})

/* ---------- 工具函数 ---------- */

/* 段位配色 */
function rankColor(rank) {
  const map = {
    学徒: 'linear-gradient(135deg, #8c9a5b, #a8b678)',
    弟子: 'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    匠人: 'linear-gradient(135deg, #c9a063, #ddc08f)',
    大师: 'linear-gradient(135deg, #b03a2e, #d45a4a)'
  }
  return map[rank] || 'linear-gradient(135deg, #9a8f7d, #b5aa96)'
}

/* ---------- 交互 ---------- */

/* 点击关卡 */
function onLevelClick(lv) {
  if (!lv.unlocked) {
    uni.showToast({ title: '再得 ' + lv.need_score + ' 分解锁', icon: 'none' })
    return
  }
  uni.navigateTo({
    url: '/pages/game/play?levelId=' + lv.id + '&levelName=' + encodeURIComponent(lv.name)
  })
}

/* ---------- 生命周期 ---------- */
onLoad(async () => {
  try {
    levels.value = await getLevels() || []
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
.levels {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 加载态 ---------- */
.loading-card {
  padding: 120rpx 32rpx;
  align-items: center;
  margin-top: 100rpx;
}
.loading-text {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- 段位分组 ---------- */
.rank-group {
  margin-bottom: 40rpx;
}
.group-header {
  flex-direction: row;
  align-items: center;
  margin-bottom: 24rpx;
}
.group-badge {
  border-radius: 12rpx;
  padding: 6rpx 20rpx;
  margin-right: 16rpx;
}
.group-badge text {
  font-size: 22rpx;
  color: #fff;
  font-weight: 700;
}
.group-title {
  flex: 1;
  font-size: 32rpx;
  font-weight: 700;
  color: $ink;
}
.group-count {
  font-size: 22rpx;
  color: $ink-light;
}

/* ---------- 关卡卡 ---------- */
.level-card {
  flex-direction: row;
  align-items: center;
  margin-bottom: 20rpx;
  padding: 24rpx;
  min-height: 168rpx;
}
.level-card.locked {
  opacity: 0.75;
}
.level-icon {
  width: 104rpx;
  height: 104rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 52rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
}
.level-info {
  min-width: 0;
}
.level-name-row {
  flex-direction: row;
  align-items: center;
}
.level-name {
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
}
.pass-badge {
  background: #eaf4ec;
  border-radius: 999rpx;
  padding: 4rpx 16rpx;
  margin-left: 12rpx;
}
.pass-badge text {
  font-size: 18rpx;
  color: $success;
  font-weight: 600;
}
.level-subtitle {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 6rpx;
}
.level-meta {
  flex-direction: row;
  align-items: center;
  margin-top: 10rpx;
}
.level-theme {
  font-size: 20rpx;
  color: $primary;
  background: $primary-bg;
  border-radius: 8rpx;
  padding: 2rpx 14rpx;
  margin-right: 12rpx;
}
.level-count {
  font-size: 20rpx;
  color: $ink-light;
}
.level-status {
  margin-top: 10rpx;
}
.level-best {
  font-size: 22rpx;
  color: $success;
  font-weight: 600;
}
.level-locked {
  font-size: 22rpx;
  color: $warning;
}
.level-arrow {
  font-size: 48rpx;
  color: $ink-light;
  margin-left: 8rpx;
}
</style>
