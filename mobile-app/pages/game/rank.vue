<template>
  <view class="rank">
    <!-- 加载态 -->
    <view v-if="loading" class="loading-card card">
      <text class="loading-text">正在加载排行榜…</text>
    </view>

    <!-- 排行榜列表 -->
    <view v-else-if="list.length" class="rank-list card">
      <view
        v-for="item in list"
        :key="item.rank + '-' + item.nickname"
        class="rank-item"
        :class="{ me: item.me, top: item.rank <= 3 }"
      >
        <!-- 排名（前三特殊奖牌色） -->
        <view class="rank-num" :class="'medal-' + item.rank" v-if="item.rank <= 3">
          <text>{{ rankMedal(item.rank) }}</text>
        </view>
        <text v-else class="rank-num-text">{{ item.rank }}</text>

        <!-- 头像占位 -->
        <view class="rank-avatar" :style="{ background: avatarGradient(item.rank) }">
          <text>{{ item.nickname.slice(0, 1) }}</text>
        </view>

        <!-- 昵称 -->
        <text class="rank-name flex-1 text-ellipsis" :class="{ 'name-me': item.me }">
          {{ item.nickname }}{{ item.me ? '（我）' : '' }}
        </text>

        <!-- 分数 -->
        <text class="rank-score">{{ item.score }}</text>
      </view>
    </view>

    <!-- 空态 -->
    <empty v-else icon="🏆" text="暂无排行榜数据" />

    <!-- 底部分享按钮 -->
    <view class="share-btn btn-primary safe-bottom" @click="onShare">
      <text>📤 分享我的成绩</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getRankList } from '@/api/game'
import { shareText } from '@/utils/util'

/* ---------- 数据 ---------- */
const loading = ref(true)
const list = ref([])

/* ---------- 工具函数 ---------- */

/* 前三奖牌图标 */
function rankMedal(rank) {
  return ['🥇', '🥈', '🥉'][rank - 1] || rank
}

/* 头像占位渐变色（按排名轮换色系） */
function avatarGradient(rank) {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)',
    'linear-gradient(135deg, #c9a063, #ddc08f)',
    'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    'linear-gradient(135deg, #9c6b9e, #b98cb9)',
    'linear-gradient(135deg, #3d3529, #5c5344)'
  ]
  return palettes[(rank - 1) % palettes.length]
}

/* ---------- 交互 ---------- */

/* 分享成绩 */
function onShare() {
  const me = list.value.find((item) => item.me)
  const myScore = me ? me.score : 0
  const myRank = me ? me.rank : '-'
  shareText('我在 Heritouch 非遗闯关中排名第 ' + myRank + '！', '累计积分 ' + myScore + ' 分，快来挑战我吧')
}

/* ---------- 生命周期 ---------- */
onLoad(async () => {
  try {
    list.value = await getRankList() || []
  } catch (e) {
    list.value = []
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
.rank {
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

/* ---------- 排行榜 ---------- */
.rank-list {
  padding: 8rpx 0;
}
.rank-item {
  flex-direction: row;
  align-items: center;
  padding: 24rpx 28rpx;
  min-height: 120rpx;
}
.rank-item + .rank-item {
  border-top: 1rpx solid $border;
}
/* “我”的行高亮 */
.rank-item.me {
  background: $primary-bg;
  border-radius: $radius-md;
  border-top: none;
  margin: 12rpx 16rpx;
}
/* 排名 */
.rank-num {
  width: 64rpx;
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
}
.rank-num text {
  font-size: 44rpx;
}
.rank-num-text {
  width: 64rpx;
  text-align: center;
  font-size: 30rpx;
  font-weight: 700;
  color: $ink-light;
  margin-right: 12rpx;
}

/* 头像占位 */
.rank-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 700;
  color: #fff;
  margin-right: 20rpx;
  flex-shrink: 0;
}

/* 昵称与分数 */
.rank-name {
  font-size: 28rpx;
  color: $ink;
}
.rank-name.name-me {
  font-weight: 700;
  color: $primary;
}
.rank-score {
  font-size: 32rpx;
  font-weight: 700;
  color: $gold;
  margin-left: 16rpx;
}
.rank-item.me .rank-score {
  color: $primary;
}

/* ---------- 分享按钮 ---------- */
.share-btn {
  margin-top: 48rpx;
  min-height: 92rpx;
  line-height: 92rpx;
}
.share-btn text {
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}
</style>
