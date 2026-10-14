<template>
  <view class="game">
    <!-- 顶部积分卡 -->
    <view class="score-card">
      <view class="score-card-bg"></view>
      <view class="score-card-body">
        <view class="flex-1">
          <text class="score-label">我的累计积分</text>
          <view class="score-value-row">
            <text class="score-value">{{ totalScore }}</text>
            <text class="score-unit">分</text>
          </view>
        </view>
        <view class="rank-badge">
          <text class="rank-badge-text">{{ currentRank }}</text>
        </view>
      </view>
      <text class="score-tip">答题闯关赢积分，向“非遗大师”段位冲刺</text>
    </view>

    <!-- 功能入口 -->
    <view class="entry-list">
      <view class="entry-row card" @click="goLevels">
        <view class="entry-icon" style="background: linear-gradient(135deg, #b03a2e, #d45a4a)">
          <text>🗺️</text>
        </view>
        <view class="flex-1">
          <text class="entry-name">闯关地图</text>
          <text class="entry-desc">五大关卡，从学徒到大师</text>
        </view>
        <text class="entry-arrow">›</text>
      </view>

      <view class="entry-row card" @click="goRank">
        <view class="entry-icon" style="background: linear-gradient(135deg, #c9a063, #ddc08f)">
          <text>🏆</text>
        </view>
        <view class="flex-1">
          <text class="entry-name">积分排行榜</text>
          <text class="entry-desc">看看谁是非遗知识达人</text>
        </view>
        <text class="entry-arrow">›</text>
      </view>

      <view class="entry-row card" @click="goWrong">
        <view class="entry-icon" style="background: linear-gradient(135deg, #3f6f6a, #5d8a85)">
          <text>📕</text>
        </view>
        <view class="flex-1">
          <text class="entry-name">我的错题本</text>
          <text class="entry-desc">错题回顾，查漏补缺</text>
        </view>
        <text class="entry-arrow">›</text>
      </view>
    </view>

    <!-- 玩法说明卡 -->
    <view class="rules card">
      <text class="rules-title">玩法说明</text>
      <view class="rule-item" v-for="(rule, i) in rules" :key="i">
        <text class="rule-index">{{ i + 1 }}</text>
        <text class="rule-text">{{ rule }}</text>
      </view>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { getLevels } from '@/api/game'

/* ---------- 数据 ---------- */
const userStore = useUserStore()
const levels = ref([])

/* 当前累计积分 */
const totalScore = computed(() => userStore.totalScore)

/* 根据积分与关卡 need_score 推导当前段位 */
const currentRank = computed(() => {
  const score = totalScore.value
  let rank = '初学者'
  // 关卡按 need_score 升序排列，取已解锁的最高段位
  const sorted = levels.value.slice().sort((a, b) => a.need_score - b.need_score)
  for (const lv of sorted) {
    if (score >= lv.need_score) rank = lv.rank
  }
  return rank
})

/* 玩法说明列表 */
const rules = [
  '每关 10 道题，涵盖单选、判断与识图三种题型',
  '答题立即反馈解析，答对按难度获得 10/15/20 积分',
  '累计积分达到关卡要求即可解锁后续关卡',
  '错题自动收入错题本，可随时回顾复习'
]

/* ---------- 页面跳转 ---------- */
function goLevels() {
  uni.navigateTo({ url: '/pages/game/levels' })
}
function goRank() {
  uni.navigateTo({ url: '/pages/game/rank' })
}
function goWrong() {
  uni.navigateTo({ url: '/pages/game/wrong' })
}

/* ---------- 生命周期 ---------- */

/* 加载关卡数据（用于推导段位），tab 页每次显示刷新 */
async function loadLevels() {
  try {
    levels.value = await getLevels() || []
  } catch (e) {
    levels.value = []
  }
}

// onShow：每次 tab 显示时刷新积分与段位
onShow(loadLevels)
</script>

<style lang="scss" scoped>
.game {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
}

/* ---------- 积分卡 ---------- */
.score-card {
  position: relative;
  border-radius: $radius-xl;
  overflow: hidden;
  padding: 40rpx 36rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 12rpx 32rpx rgba(176, 58, 46, 0.22);
}
.score-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #b03a2e 0%, #8e2b21 100%);
}
.score-card-bg::after {
  content: '';
  position: absolute;
  top: -80rpx;
  right: -40rpx;
  width: 280rpx;
  height: 280rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
}
.score-card-body {
  display: flex;
  position: relative;
  flex-direction: row;
  align-items: center;
}
.score-label {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.85);
}
.score-value-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-top: 8rpx;
}
.score-value {
  font-size: 72rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1.1;
}
.score-unit {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-left: 8rpx;
}
.rank-badge {
  background: rgba(255, 255, 255, 0.18);
  border: 1rpx solid rgba(255, 255, 255, 0.4);
  border-radius: $radius-pill;
  padding: 12rpx 28rpx;
}
.rank-badge-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 600;
}
.score-tip {
  position: relative;
  display: block;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 20rpx;
}

/* ---------- 入口列表 ---------- */
.entry-list {
  margin-bottom: 32rpx;
}
.entry-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 24rpx;
  min-height: 128rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
  transition: transform 0.1s ease;
  &:active { transform: scale(0.99); }
}
.entry-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 26rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
  box-shadow: $shadow-xs;
}
.entry-name {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
}
.entry-desc {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 6rpx;
}
.entry-arrow {
  font-size: 44rpx;
  color: $ink-faint;
  margin-left: 16rpx;
}

/* ---------- 玩法说明 ---------- */
.rules {
  padding: 32rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.rules-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
  margin-bottom: 20rpx;
  position: relative;
  padding-left: 20rpx;
}
.rules-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8rpx;
  height: 28rpx;
  border-radius: 4rpx;
  background: linear-gradient(180deg, $primary, $primary-light);
}
.rule-item {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 16rpx;
}
.rule-item:last-child {
  margin-bottom: 0;
}
.rule-index {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: $primary-bg;
  color: $primary;
  font-size: 20rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
  margin-top: 4rpx;
  flex-shrink: 0;
}
.rule-text {
  flex: 1;
  font-size: 24rpx;
  color: $ink-light;
  line-height: 1.6;
}

.bottom-gap {
  height: 60rpx;
}
</style>
